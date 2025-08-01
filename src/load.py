import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text, MetaData, Table, inspect
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Dict, Any
from pathlib import Path
from config import DATABASE_URL, TABLE_NAME, CHUNK_SIZE, OUTPUT_DIR
from utils import log_message, handle_error, log_success, get_data_quality_report

def load_to_postgres(df: pd.DataFrame, 
                    table_name: str = TABLE_NAME, 
                    db_url: str = DATABASE_URL,
                    if_exists: str = 'replace',
                    chunk_size: int = CHUNK_SIZE) -> bool:
    """
    Load DataFrame to PostgreSQL database with comprehensive error handling.
    
    Parameters:
    df (pd.DataFrame): Data to load
    table_name (str): Target table name
    db_url (str): Database connection URL
    if_exists (str): How to behave if table exists ('fail', 'replace', 'append')
    chunk_size (int): Number of rows to insert at a time
    
    Returns:
    bool: True if successful, False otherwise
    """
    if df is None or df.empty:
        handle_error("Cannot load empty or None DataFrame")
        return False
    
    try:
        log_message(f"Starting data load to PostgreSQL table: {table_name}")
        log_message(f"Data shape: {df.shape}")
        
        # Create database engine
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            log_message("Database connection successful")
        
        # Prepare data for loading
        df_to_load = prepare_data_for_db(df)
        
        # Load data in chunks for better performance
        log_message(f"Loading {len(df_to_load)} rows in chunks of {chunk_size}")
        
        df_to_load.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            chunksize=chunk_size,
            method='multi'  # Use multi-row INSERT statements
        )
        
        # Verify the load
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            row_count = result.scalar()
            
        log_success(f"Successfully loaded {row_count} rows to table {table_name}")
        
        # Generate and save load report
        load_report = generate_load_report(df_to_load, table_name, row_count)
        save_load_report(load_report)
        
        return True
        
    except SQLAlchemyError as e:
        handle_error(f"Database error during load: {e}")
        return False
    except Exception as e:
        handle_error(f"Unexpected error during load: {e}")
        return False
    finally:
        # Clean up engine
        if 'engine' in locals():
            engine.dispose()

def prepare_data_for_db(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare DataFrame for database loading by handling data types and NaN values.
    
    Parameters:
    df (pd.DataFrame): Input DataFrame
    
    Returns:
    pd.DataFrame: Prepared DataFrame
    """
    log_message("Preparing data for database loading")
    
    df_prepared = df.copy()
    
    # Handle datetime columns
    datetime_columns = df_prepared.select_dtypes(include=['datetime64']).columns
    for col in datetime_columns:
        # Convert NaT to None for PostgreSQL compatibility
        df_prepared[col] = df_prepared[col].where(pd.notna(df_prepared[col]), None)
    
    # Handle boolean columns
    boolean_columns = df_prepared.select_dtypes(include=['bool']).columns
    for col in boolean_columns:
        # Convert to nullable boolean
        df_prepared[col] = df_prepared[col].astype('boolean')
    
    # Handle categorical columns
    categorical_columns = df_prepared.select_dtypes(include=['category']).columns
    for col in categorical_columns:
        # Convert categories to strings
        df_prepared[col] = df_prepared[col].astype(str)
        df_prepared[col] = df_prepared[col].replace('nan', None)
    
    # Handle object columns (strings)
    object_columns = df_prepared.select_dtypes(include=['object']).columns
    for col in object_columns:
        # Replace NaN with None for PostgreSQL
        df_prepared[col] = df_prepared[col].where(pd.notna(df_prepared[col]), None)
    
    # Handle numeric columns
    numeric_columns = df_prepared.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        # Replace inf and -inf with NaN, then with None
        df_prepared[col] = df_prepared[col].replace([np.inf, -np.inf], np.nan)
        df_prepared[col] = df_prepared[col].where(pd.notna(df_prepared[col]), None)
    
    log_message("Data preparation completed")
    return df_prepared

def create_database_schema(db_url: str = DATABASE_URL) -> bool:
    """
    Create database schema if it doesn't exist.
    
    Parameters:
    db_url (str): Database connection URL
    
    Returns:
    bool: True if successful, False otherwise
    """
    try:
        engine = create_engine(db_url)
        
        # Extract database name from URL
        db_name = db_url.split('/')[-1]
        
        # Create database if it doesn't exist
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
            
        log_success(f"Database schema ensured: {db_name}")
        return True
        
    except Exception as e:
        handle_error(f"Error creating database schema: {e}")
        return False
    finally:
        if 'engine' in locals():
            engine.dispose()

def get_table_info(table_name: str = TABLE_NAME, db_url: str = DATABASE_URL) -> Optional[Dict[str, Any]]:
    """
    Get information about a table in the database.
    
    Parameters:
    table_name (str): Name of the table
    db_url (str): Database connection URL
    
    Returns:
    Dict: Table information or None if error
    """
    try:
        engine = create_engine(db_url)
        inspector = inspect(engine)
        
        if not inspector.has_table(table_name):
            log_message(f"Table {table_name} does not exist")
            return None
        
        # Get table info
        columns = inspector.get_columns(table_name)
        indexes = inspector.get_indexes(table_name)
        
        # Get row count
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            row_count = result.scalar()
        
        table_info = {
            'table_name': table_name,
            'row_count': row_count,
            'columns': columns,
            'indexes': indexes,
            'column_count': len(columns)
        }
        
        log_message(f"Retrieved info for table {table_name}: {row_count} rows, {len(columns)} columns")
        return table_info
        
    except Exception as e:
        handle_error(f"Error getting table info: {e}")
        return None
    finally:
        if 'engine' in locals():
            engine.dispose()

def generate_load_report(df: pd.DataFrame, table_name: str, loaded_rows: int) -> Dict[str, Any]:
    """
    Generate a comprehensive load report.
    
    Parameters:
    df (pd.DataFrame): Source DataFrame
    table_name (str): Target table name
    loaded_rows (int): Number of rows loaded
    
    Returns:
    Dict: Load report
    """
    data_quality = get_data_quality_report(df)
    
    report = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'table_name': table_name,
        'source_rows': len(df),
        'loaded_rows': loaded_rows,
        'load_success_rate': (loaded_rows / len(df)) * 100 if len(df) > 0 else 0,
        'data_quality': data_quality,
        'columns_loaded': list(df.columns),
        'data_types': df.dtypes.to_dict()
    }
    
    return report

def save_load_report(report: Dict[str, Any]) -> None:
    """
    Save load report to file.
    
    Parameters:
    report (Dict): Load report to save
    """
    try:
        report_file = OUTPUT_DIR / f"load_report_{report['table_name']}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        log_success(f"Load report saved: {report_file}")
        
    except Exception as e:
        handle_error(f"Error saving load report: {e}")

def query_data(query: str, db_url: str = DATABASE_URL) -> Optional[pd.DataFrame]:
    """
    Execute a SQL query and return results as DataFrame.
    
    Parameters:
    query (str): SQL query to execute
    db_url (str): Database connection URL
    
    Returns:
    pd.DataFrame: Query results or None if error
    """
    try:
        engine = create_engine(db_url)
        
        log_message(f"Executing query: {query[:100]}...")
        df = pd.read_sql(query, engine)
        
        log_success(f"Query executed successfully: {len(df)} rows returned")
        return df
        
    except Exception as e:
        handle_error(f"Error executing query: {e}")
        return None
    finally:
        if 'engine' in locals():
            engine.dispose()

def load_data(transformed_data: pd.DataFrame, 
              table_name: str = TABLE_NAME,
              if_exists: str = 'replace') -> bool:
    """
    Main load function - wrapper for load_to_postgres.
    
    Parameters:
    transformed_data (pd.DataFrame): The cleaned and transformed data to be loaded
    table_name (str): Target table name
    if_exists (str): How to behave if table exists
    
    Returns:
    bool: True if successful, False otherwise
    """
    return load_to_postgres(transformed_data, table_name, if_exists=if_exists)