import requests
import pandas as pd
from pathlib import Path
from typing import Optional, Union
from utils import log_message, handle_error, log_success, validate_data, validate_netflix_data
from config import NETFLIX_CSV_PATH, TIMEOUT, RETRY_COUNT

def extract_netflix_data(file_path: Optional[Union[str, Path]] = None) -> Optional[pd.DataFrame]:
    """
    Extracts Netflix data from CSV file with comprehensive validation.
    
    Parameters:
    file_path (str or Path, optional): Path to the Netflix CSV file. 
                                      Defaults to config.NETFLIX_CSV_PATH.
    
    Returns:
    pd.DataFrame: Raw Netflix data extracted from the CSV file.
    """
    if file_path is None:
        file_path = NETFLIX_CSV_PATH
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        handle_error(f"Netflix data file not found: {file_path}")
        return None
    
    try:
        log_message(f"Starting extraction from: {file_path}")
        
        # Read CSV with proper encoding handling
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # Basic validation
        if not validate_data(df):
            return None
        
        # Netflix-specific validation
        if not validate_netflix_data(df):
            return None
        
        log_success(f"Successfully extracted {len(df)} Netflix titles from {file_path.name}")
        log_message(f"Data shape: {df.shape}")
        log_message(f"Columns: {list(df.columns)}")
        
        return df
        
    except UnicodeDecodeError:
        try:
            # Try different encoding
            log_message("Trying alternative encoding (latin-1)")
            df = pd.read_csv(file_path, encoding='latin-1')
            log_success(f"Successfully extracted with latin-1 encoding: {len(df)} records")
            return df
        except Exception as e:
            handle_error(f"Failed to read file with alternative encoding: {e}")
            return None
    except Exception as e:
        handle_error(f"Error extracting Netflix data from {file_path}: {e}")
        return None

def extract_data(source_type: str, source: str) -> Optional[pd.DataFrame]:
    """
    Generic data extraction function supporting multiple sources.

    Parameters:
    source_type (str): Type of the source ('api', 'csv', or 'netflix').
    source (str): URL of the API or path to the CSV file.

    Returns:
    pd.DataFrame: Raw data extracted from the source.
    """
    log_message(f"Starting data extraction: {source_type} from {source}")
    
    if source_type == 'api':
        return extract_from_api(source)
    elif source_type == 'csv':
        return extract_csv(source)
    elif source_type == 'netflix':
        return extract_netflix_data(source)
    else:
        handle_error(f"Invalid source_type: {source_type}. Use 'api', 'csv', or 'netflix'.")
        return None

def extract_from_api(api_url: str) -> Optional[pd.DataFrame]:
    """
    Extract data from API with retry logic and proper error handling.
    
    Parameters:
    api_url (str): URL of the API endpoint.
    
    Returns:
    pd.DataFrame: Data extracted from the API.
    """
    for attempt in range(RETRY_COUNT):
        try:
            log_message(f"API request attempt {attempt + 1}/{RETRY_COUNT}: {api_url}")
            
            response = requests.get(api_url, timeout=TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data)
            
            if validate_data(df):
                log_success(f"Successfully extracted {len(df)} records from API")
                return df
            else:
                handle_error("API returned invalid data")
                return None
                
        except requests.exceptions.Timeout:
            handle_error(f"API request timeout (attempt {attempt + 1})")
        except requests.exceptions.RequestException as e:
            handle_error(f"API request failed (attempt {attempt + 1}): {e}")
        except ValueError as e:
            handle_error(f"Invalid JSON response (attempt {attempt + 1}): {e}")
        except Exception as e:
            handle_error(f"Unexpected error during API extraction (attempt {attempt + 1}): {e}")
    
    handle_error(f"Failed to extract data from API after {RETRY_COUNT} attempts")
    return None

def extract_csv(file_path: Union[str, Path]) -> Optional[pd.DataFrame]:
    """
    Extract data from CSV file with robust error handling.
    
    Parameters:
    file_path (str or Path): Path to the CSV file.
    
    Returns:
    pd.DataFrame: Data extracted from the CSV file.
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        handle_error(f"CSV file not found: {file_path}")
        return None
    
    try:
        log_message(f"Extracting data from CSV: {file_path}")
        
        # Try UTF-8 first
        df = pd.read_csv(file_path, encoding='utf-8')
        
        if validate_data(df):
            log_success(f"Successfully extracted {len(df)} records from {file_path.name}")
            return df
        else:
            return None
            
    except UnicodeDecodeError:
        try:
            # Fallback to latin-1
            log_message("Trying latin-1 encoding")
            df = pd.read_csv(file_path, encoding='latin-1')
            
            if validate_data(df):
                log_success(f"Successfully extracted {len(df)} records with latin-1 encoding")
                return df
            else:
                return None
                
        except Exception as e:
            handle_error(f"Failed to read CSV with alternative encoding: {e}")
            return None
    except Exception as e:
        handle_error(f"Error extracting data from {file_path}: {e}")
        return None