// src/components/DataRefreshButton.js

import React, { useState, useEffect } from 'react';
import {
  Button,
  Chip,
  Box,
  CircularProgress,
  Tooltip,
  Alert,
  Snackbar,
  Typography
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

const DataRefreshButton = ({ onDataRefreshed }) => {
  const [refreshStatus, setRefreshStatus] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [previousStatus, setPreviousStatus] = useState(null);

  // Poll for status updates when refresh is in progress
  useEffect(() => {
    let intervalId;

    const fetchStatus = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/refresh-status`);
        setRefreshStatus(response.data);

        const status = response.data.status;
        const wasRefreshing = previousStatus === 'fetching' || previousStatus === 'processing';
        setIsRefreshing(status === 'fetching' || status === 'processing');

        // If job just completed (was refreshing, now completed)
        if (status === 'completed' && wasRefreshing) {
          setSnackbar({
            open: true,
            message: 'Data refresh completed successfully! Reloading data...',
            severity: 'success'
          });

          // Trigger data reload in parent component
          if (onDataRefreshed) {
            setTimeout(() => {
              onDataRefreshed();
            }, 500); // Small delay to ensure files are written
          }
        } else if (status === 'failed' && wasRefreshing) {
          setSnackbar({
            open: true,
            message: `Data refresh failed: ${response.data.error || 'Unknown error'}`,
            severity: 'error'
          });
        }

        setPreviousStatus(status);
      } catch (error) {
        console.error('Error fetching refresh status:', error);
      }
    };

    // Initial fetch
    fetchStatus();

    // Poll every 3 seconds if refresh is in progress
    if (isRefreshing) {
      intervalId = setInterval(fetchStatus, 3000);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isRefreshing, snackbar.open, onDataRefreshed]);

  const handleRefresh = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/refresh-data`);

      if (response.data.success) {
        setIsRefreshing(true);
        setSnackbar({
          open: true,
          message: 'Data refresh started...',
          severity: 'info'
        });
      } else {
        setSnackbar({
          open: true,
          message: response.data.message || 'Failed to start refresh',
          severity: 'warning'
        });
      }
    } catch (error) {
      console.error('Error triggering refresh:', error);
      setSnackbar({
        open: true,
        message: 'Error starting refresh job',
        severity: 'error'
      });
    }
  };

  const handleReset = async () => {
    try {
      await axios.post(`${API_BASE_URL}/refresh-reset`);
      const response = await axios.get(`${API_BASE_URL}/refresh-status`);
      setRefreshStatus(response.data);
      setSnackbar({
        open: true,
        message: 'Status reset to idle',
        severity: 'info'
      });
    } catch (error) {
      console.error('Error resetting status:', error);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const getStatusChip = () => {
    if (!refreshStatus) return null;

    const { status, progress } = refreshStatus;

    const statusConfig = {
      idle: { label: 'Idle', color: 'default', icon: null },
      fetching: { label: 'Fetching Data', color: 'primary', icon: <CircularProgress size={14} /> },
      processing: { label: 'Processing', color: 'primary', icon: <CircularProgress size={14} /> },
      completed: { label: 'Completed', color: 'success', icon: <CheckCircleIcon fontSize="small" /> },
      failed: { label: 'Failed', color: 'error', icon: <ErrorIcon fontSize="small" /> }
    };

    const config = statusConfig[status] || statusConfig.idle;

    return (
      <Tooltip title={progress?.message || 'No refresh in progress'}>
        <Chip
          label={config.label}
          color={config.color}
          icon={config.icon}
          size="small"
          sx={{ ml: 1 }}
        />
      </Tooltip>
    );
  };

  const getLastRefreshTime = () => {
    if (!refreshStatus?.last_successful_refresh) return null;

    const lastRefresh = new Date(refreshStatus.last_successful_refresh);
    const now = new Date();
    const diffMs = now - lastRefresh;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    let timeAgo;
    if (diffDays > 0) {
      timeAgo = `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else if (diffHours > 0) {
      timeAgo = `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else if (diffMins > 0) {
      timeAgo = `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    } else {
      timeAgo = 'Just now';
    }

    return (
      <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
        Last refresh: {timeAgo}
      </Typography>
    );
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      {refreshStatus?.status === 'completed' || refreshStatus?.status === 'failed' ? (
        <Button
          variant="outlined"
          size="small"
          onClick={handleReset}
          sx={{ textTransform: 'none' }}
        >
          Reset
        </Button>
      ) : null}

      <Button
        variant="contained"
        color="primary"
        startIcon={isRefreshing ? <CircularProgress size={16} color="inherit" /> : <RefreshIcon />}
        onClick={handleRefresh}
        disabled={isRefreshing}
        sx={{ textTransform: 'none' }}
      >
        {isRefreshing ? 'Refreshing...' : 'Refresh Data'}
      </Button>

      {getStatusChip()}
      {getLastRefreshTime()}

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DataRefreshButton;
