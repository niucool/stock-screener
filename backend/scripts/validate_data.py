# backend/scripts/validate_data.py

import os
import json
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

PROCESSED_DIR = '../data/stocks/processed'

def validate_stock_data(data, symbol):
    """
    Validates stock data for completeness, accuracy, and freshness.
    Returns a dictionary with validation results.
    """
    issues = []
    warnings = []

    # Check required fields
    required_fields = ['Symbol', 'Date', 'Close', 'Volume']
    for field in required_fields:
        if field not in data or data[field] is None:
            issues.append(f"Missing required field: {field}")

    # Check data freshness
    if 'Date' in data and data['Date']:
        try:
            data_date = datetime.strptime(data['Date'], '%Y-%m-%d')
            age_days = (datetime.now() - data_date).days

            if age_days > 7:
                warnings.append(f"Data is {age_days} days old")

            data_age_in_file = data.get('Data_Age_Days')
            if data_age_in_file is not None and abs(data_age_in_file - age_days) > 1:
                warnings.append(f"Data age mismatch: calculated {age_days}, stored {data_age_in_file}")

        except ValueError:
            issues.append(f"Invalid date format: {data['Date']}")

    # Check for NaN/None values in key indicators
    key_indicators = ['RSI_14', 'RSI_21', 'MACD', 'ADX_14', 'ATR_14']
    none_count = 0
    for indicator in key_indicators:
        if indicator in data and data[indicator] is None:
            none_count += 1

    if none_count > len(key_indicators) * 0.3:  # More than 30% missing
        warnings.append(f"{none_count}/{len(key_indicators)} key indicators are None")

    # Check value ranges
    range_checks = {
        'RSI_14': (0, 100),
        'RSI_21': (0, 100),
        'Williams_R_14': (-100, 0),
        'Williams_R_21': (-100, 0),
        'Stoch_K': (0, 100),
        'Stoch_D': (0, 100),
        'MFI_14': (0, 100),
        'ADX_14': (0, 100),
        'BB_Position': (0, 100),
        'Range_52w_Position': (0, 100)
    }

    for indicator, (min_val, max_val) in range_checks.items():
        if indicator in data and data[indicator] is not None:
            value = data[indicator]
            if value < min_val or value > max_val:
                issues.append(f"{indicator} value {value:.2f} out of range [{min_val}, {max_val}]")

    # Check for suspicious values
    if 'Close' in data and data['Close'] is not None:
        if data['Close'] <= 0:
            issues.append(f"Invalid Close price: {data['Close']}")
        elif data['Close'] < 1:
            warnings.append(f"Very low Close price: {data['Close']}")

    if 'Volume' in data and data['Volume'] is not None:
        if data['Volume'] < 0:
            issues.append(f"Invalid Volume: {data['Volume']}")
        elif data['Volume'] == 0:
            warnings.append("Zero volume")

    # Check moving average alignment (basic sanity check)
    if all(k in data and data[k] is not None for k in ['Close', 'SMA_20', 'SMA_50', 'SMA_200']):
        # In a strong uptrend, MAs should be ordered: Close > SMA_20 > SMA_50 > SMA_200
        # In a strong downtrend: Close < SMA_20 < SMA_50 < SMA_200
        # This is just a sanity check for gross errors
        pass  # Complex validation can be added here

    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings
    }

def validate_all_data():
    """
    Validates all processed stock data files.
    Generates a validation report.
    """
    if not os.path.exists(PROCESSED_DIR):
        logging.error(f"Processed data directory not found: {PROCESSED_DIR}")
        return

    total_files = 0
    valid_files = 0
    files_with_warnings = 0
    invalid_files = 0

    validation_report = {
        'timestamp': datetime.now().isoformat(),
        'total_files': 0,
        'valid_files': 0,
        'files_with_warnings': 0,
        'invalid_files': 0,
        'details': {}
    }

    for filename in os.listdir(PROCESSED_DIR):
        if not filename.endswith('.json'):
            continue

        total_files += 1
        symbol = filename.replace('.json', '')
        file_path = os.path.join(PROCESSED_DIR, filename)

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            validation_result = validate_stock_data(data, symbol)

            if validation_result['valid']:
                if validation_result['warnings']:
                    files_with_warnings += 1
                    logging.warning(f"{symbol}: {len(validation_result['warnings'])} warnings")
                else:
                    valid_files += 1
            else:
                invalid_files += 1
                logging.error(f"{symbol}: {len(validation_result['issues'])} issues")

            # Store details for files with issues or warnings
            if validation_result['issues'] or validation_result['warnings']:
                validation_report['details'][symbol] = validation_result

        except Exception as e:
            invalid_files += 1
            logging.error(f"Error validating {symbol}: {e}")
            validation_report['details'][symbol] = {
                'valid': False,
                'issues': [f"Failed to load/parse file: {str(e)}"],
                'warnings': []
            }

    validation_report['total_files'] = total_files
    validation_report['valid_files'] = valid_files
    validation_report['files_with_warnings'] = files_with_warnings
    validation_report['invalid_files'] = invalid_files

    # Save validation report
    report_path = '../logs/validation_report.json'
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(validation_report, f, indent=2)

    # Print summary
    print("\n" + "="*60)
    print("DATA VALIDATION REPORT")
    print("="*60)
    print(f"Total files processed: {total_files}")
    print(f"Valid files: {valid_files} ({valid_files/total_files*100:.1f}%)")
    print(f"Files with warnings: {files_with_warnings} ({files_with_warnings/total_files*100:.1f}%)")
    print(f"Invalid files: {invalid_files} ({invalid_files/total_files*100:.1f}%)")
    print(f"\nDetailed report saved to: {report_path}")
    print("="*60 + "\n")

    return validation_report

if __name__ == "__main__":
    validate_all_data()
