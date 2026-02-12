# backend/api/job_manager.py
"""
Background job manager for data refresh operations.
Handles execution of fetch and process scripts as background jobs.
"""

import threading
import subprocess
import json
import os
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

class DataRefreshJobManager:
    """
    Manages background data refresh jobs.
    Uses file-based state persistence for job status tracking.
    """

    def __init__(self, state_file='../logs/refresh_job_state.json'):
        self.state_file = state_file
        self.lock = threading.Lock()
        self.current_thread = None
        self._ensure_state_file()

    def _ensure_state_file(self):
        """Ensure state file and directory exist."""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        if not os.path.exists(self.state_file):
            self._save_state({
                'status': 'idle',
                'phase': None,
                'started_at': None,
                'completed_at': None,
                'last_successful_refresh': None,
                'error': None,
                'progress': {
                    'current_phase': None,
                    'message': 'No refresh in progress'
                }
            })

    def _load_state(self):
        """Load current job state from file."""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading job state: {e}")
            return {'status': 'idle', 'error': str(e)}

    def _save_state(self, state):
        """Save job state to file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving job state: {e}")

    def get_status(self):
        """Get current job status."""
        with self.lock:
            return self._load_state()

    def is_running(self):
        """Check if a job is currently running."""
        state = self.get_status()
        return state.get('status') in ['fetching', 'processing']

    def start_refresh(self):
        """
        Start a new data refresh job in the background.
        Returns: dict with success status and message.
        """
        with self.lock:
            # Check if job is running (without calling is_running to avoid nested lock)
            current_state = self._load_state()
            if current_state.get('status') in ['fetching', 'processing']:
                return {
                    'success': False,
                    'message': 'A refresh job is already running',
                    'status': current_state
                }

            # Update state to fetching
            state = {
                'status': 'fetching',
                'phase': 'fetch',
                'started_at': datetime.now().isoformat(),
                'completed_at': None,
                'last_successful_refresh': None,
                'error': None,
                'progress': {
                    'current_phase': 'Fetching stock data from NASDAQ',
                    'message': 'Incrementally updating data for S&P 500 stocks...'
                }
            }
            self._save_state(state)

            # Start background thread
            self.current_thread = threading.Thread(target=self._run_refresh_job, daemon=True)
            self.current_thread.start()

            return {
                'success': True,
                'message': 'Data refresh job started',
                'status': state
            }

    def _run_refresh_job(self):
        """
        Execute the data refresh job (fetch + process).
        Runs in a background thread.
        """
        scripts_dir = os.path.join(os.path.dirname(__file__), '../scripts')

        try:
            # Phase 1: Fetch stock data (incremental from NASDAQ)
            logging.info("Starting fetch phase...")
            self._update_progress('fetching', 'Fetching new stock data from NASDAQ API (incremental)...')

            fetch_result = subprocess.run(
                ['python', 'incremental_fetch.py'],
                cwd=scripts_dir,
                capture_output=True,
                text=True,
                timeout=900  # 15 minute timeout (increased for NASDAQ API)
            )

            if fetch_result.returncode != 0:
                raise Exception(f"Fetch failed: {fetch_result.stderr}")

            logging.info("Fetch phase completed successfully")

            # Phase 2: Process stock data (calculate indicators from SQLite)
            logging.info("Starting process phase...")
            self._update_progress('processing', 'Processing data and calculating technical indicators...')

            process_result = subprocess.run(
                ['python', 'process_indicators.py'],
                cwd=scripts_dir,
                capture_output=True,
                text=True,
                timeout=900  # 15 minute timeout
            )

            if process_result.returncode != 0:
                raise Exception(f"Processing failed: {process_result.stderr}")

            logging.info("Process phase completed successfully")

            # Job completed successfully
            completed_time = datetime.now().isoformat()
            state = {
                'status': 'completed',
                'phase': 'completed',
                'started_at': self._load_state().get('started_at'),
                'completed_at': completed_time,
                'last_successful_refresh': completed_time,
                'error': None,
                'progress': {
                    'current_phase': 'Completed',
                    'message': 'Data refresh completed successfully'
                }
            }
            self._save_state(state)
            logging.info("Data refresh job completed successfully")

        except subprocess.TimeoutExpired as e:
            error_msg = f"Job timed out during {self._load_state().get('phase')} phase"
            logging.error(error_msg)
            self._mark_failed(error_msg)

        except Exception as e:
            error_msg = str(e)
            logging.error(f"Data refresh job failed: {error_msg}")
            self._mark_failed(error_msg)

    def _update_progress(self, status, message):
        """Update job progress."""
        with self.lock:
            state = self._load_state()
            state['status'] = status
            state['phase'] = status
            state['progress'] = {
                'current_phase': status.capitalize(),
                'message': message
            }
            self._save_state(state)

    def _mark_failed(self, error_message):
        """Mark job as failed with error message."""
        with self.lock:
            state = self._load_state()
            state['status'] = 'failed'
            state['phase'] = 'failed'
            state['completed_at'] = datetime.now().isoformat()
            state['error'] = error_message
            state['progress'] = {
                'current_phase': 'Failed',
                'message': error_message
            }
            self._save_state(state)

    def reset_to_idle(self):
        """Reset job status to idle (for clearing completed/failed states)."""
        with self.lock:
            if self.is_running():
                return {
                    'success': False,
                    'message': 'Cannot reset while job is running'
                }

            state = self._load_state()
            # Preserve last successful refresh time
            last_refresh = state.get('last_successful_refresh')

            new_state = {
                'status': 'idle',
                'phase': None,
                'started_at': None,
                'completed_at': None,
                'last_successful_refresh': last_refresh,
                'error': None,
                'progress': {
                    'current_phase': None,
                    'message': 'No refresh in progress'
                }
            }
            self._save_state(new_state)

            return {
                'success': True,
                'message': 'Job status reset to idle'
            }


# Global job manager instance
job_manager = DataRefreshJobManager()
