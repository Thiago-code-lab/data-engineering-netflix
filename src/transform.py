import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, List
from utils import log_message, handle_error, log_success, get_data_quality_report

def transform_netflix_data(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Comprehensive transformation pipeline for Netflix data.
    
    Parameters:
    df (pd.DataFrame): Raw Netflix data
    
    Returns:
    pd.DataFrame: Cleaned and transformed Netflix data
    """
    if df is None or df.empty:
        handle_error("Cannot transform empty or None DataFrame")
        return None
    
    log_message("Starting Netflix data transformation pipeline")
    
    # Create a copy to avoid modifying original data
    df_transformed = df.copy()
    
    # Log initial data quality
    initial_report = get_data_quality_report(df_transformed)
    log_message(f"Initial data: {initial_report['total_linhas']} rows, {initial_report['linhas_duplicadas']} duplicates")
    
    # Step 1: Basic cleaning
    df_transformed = clean_basic_data(df_transformed)
    
    # Step 2: Handle date columns
    df_transformed = transform_dates(df_transformed)
    
    # Step 3: Clean and standardize text columns
    df_transformed = clean_text_columns(df_transformed)
    
    # Step 4: Feature engineering
    df_transformed = engineer_features(df_transformed)
    
    # Step 5: Handle categorical data
    df_transformed = process_categorical_data(df_transformed)
    
    # Step 6: Final validation and cleanup
    df_transformed = final_cleanup(df_transformed)
    
    # Log final data quality
    final_report = get_data_quality_report(df_transformed)
    log_success(f"Transformation complete: {final_report['total_linhas']} rows, {final_report['linhas_duplicadas']} duplicates")
    
    return df_transformed

def clean_basic_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform basic data cleaning operations.
    """
    log_message("Performing basic data cleaning")
    
    initial_rows = len(df)
    
    # Remove exact duplicates
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    if duplicates_removed > 0:
        log_message(f"Removed {duplicates_removed} duplicate rows")
    
    # Handle missing values strategically
    # Don't drop all NaN rows as some columns naturally have missing values
    
    # Remove rows where critical columns are missing
    critical_columns = ['show_id', 'title', 'type']
    before_critical = len(df)
    df = df.dropna(subset=critical_columns)
    critical_removed = before_critical - len(df)
    if critical_removed > 0:
        log_message(f"Removed {critical_removed} rows with missing critical data")
    
    return df

def transform_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform and clean date columns.
    """
    log_message("Transforming date columns")
    
    # Clean date_added column
    if 'date_added' in df.columns:
        # Remove leading/trailing whitespace
        df['date_added'] = df['date_added'].astype(str).str.strip()
        
        # Replace 'nan' strings with actual NaN
        df['date_added'] = df['date_added'].replace(['nan', 'None', ''], np.nan)
        
        # Convert to datetime
        df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
        
        # Extract additional date features
        df['date_added_year'] = df['date_added'].dt.year
        df['date_added_month'] = df['date_added'].dt.month
        df['date_added_day_of_week'] = df['date_added'].dt.day_name()
        
        log_message(f"Processed date_added column: {df['date_added'].notna().sum()} valid dates")
    
    # Clean release_year column
    if 'release_year' in df.columns:
        df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
        
        # Filter out unrealistic years
        current_year = datetime.now().year
        df.loc[(df['release_year'] < 1900) | (df['release_year'] > current_year + 2), 'release_year'] = np.nan
        
        # Create decade feature
        df['decade'] = (df['release_year'] // 10) * 10
        
        log_message(f"Processed release_year column: {df['release_year'].notna().sum()} valid years")
    
    return df

def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize text columns.
    """
    log_message("Cleaning text columns")
    
    text_columns = ['title', 'director', 'cast', 'country', 'rating', 'listed_in', 'description']
    
    for col in text_columns:
        if col in df.columns:
            # Convert to string and handle NaN
            df[col] = df[col].astype(str)
            df[col] = df[col].replace(['nan', 'None'], np.nan)
            
            # Clean whitespace
            df[col] = df[col].str.strip()
            
            # Replace empty strings with NaN
            df[col] = df[col].replace('', np.nan)
    
    # Special handling for specific columns
    if 'duration' in df.columns:
        df['duration'] = df['duration'].astype(str).str.strip()
        df['duration'] = df['duration'].replace(['nan', 'None', ''], np.nan)
    
    log_message("Text columns cleaned")
    return df

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create new features from existing data.
    """
    log_message("Engineering new features")
    
    # Extract duration information
    if 'duration' in df.columns:
        # Extract numeric duration and unit
        df['duration_value'] = df['duration'].str.extract(r'(\d+)').astype(float)
        df['duration_unit'] = df['duration'].str.extract(r'(min|Season|Seasons)$')
        
        # Standardize duration units
        df['is_movie'] = df['duration_unit'] == 'min'
        df['is_tv_show'] = df['duration_unit'].isin(['Season', 'Seasons'])
        
        log_message(f"Duration features: {df['is_movie'].sum()} movies, {df['is_tv_show'].sum()} TV shows")
    
    # Count features for list-like columns
    list_columns = ['cast', 'director', 'country', 'listed_in']
    for col in list_columns:
        if col in df.columns:
            # Count number of items (split by comma)
            df[f'{col}_count'] = df[col].str.count(',') + 1
            df.loc[df[col].isna(), f'{col}_count'] = 0
    
    # Content age analysis
    if 'release_year' in df.columns and 'date_added' in df.columns:
        df['content_age_when_added'] = df['date_added_year'] - df['release_year']
        log_message("Added content age analysis")
    
    # Text length features
    if 'description' in df.columns:
        df['description_length'] = df['description'].str.len()
        df['description_word_count'] = df['description'].str.split().str.len()
    
    # Rating categories
    if 'rating' in df.columns:
        df['rating_category'] = df['rating'].map({
            'G': 'Kids', 'TV-Y': 'Kids', 'TV-Y7': 'Kids', 'TV-Y7-FV': 'Kids',
            'PG': 'Family', 'TV-G': 'Family', 'TV-PG': 'Family',
            'PG-13': 'Teen', 'TV-14': 'Teen',
            'R': 'Adult', 'TV-MA': 'Adult', 'NC-17': 'Adult'
        })
        df['rating_category'] = df['rating_category'].fillna('Other')
    
    log_message("Feature engineering completed")
    return df

def process_categorical_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process and optimize categorical data.
    """
    log_message("Processing categorical data")
    
    # Convert appropriate columns to category type for memory efficiency
    categorical_columns = ['type', 'rating', 'rating_category', 'duration_unit', 'date_added_day_of_week']
    
    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].astype('category')
    
    # Handle country data - extract primary country
    if 'country' in df.columns:
        df['primary_country'] = df['country'].str.split(',').str[0].str.strip()
        df['is_international'] = df['country'].str.contains(',', na=False)
    
    # Handle genres - extract primary genre
    if 'listed_in' in df.columns:
        df['primary_genre'] = df['listed_in'].str.split(',').str[0].str.strip()
        df['genre_diversity'] = df['listed_in'].str.count(',') + 1
        df.loc[df['listed_in'].isna(), 'genre_diversity'] = 0
    
    log_message("Categorical data processing completed")
    return df

def final_cleanup(df: pd.DataFrame) -> pd.DataFrame:
    """
    Final cleanup and validation.
    """
    log_message("Performing final cleanup")
    
    # Remove any remaining exact duplicates that might have been created
    initial_rows = len(df)
    df = df.drop_duplicates()
    if len(df) < initial_rows:
        log_message(f"Removed {initial_rows - len(df)} duplicate rows in final cleanup")
    
    # Sort by date_added and show_id for consistency
    sort_columns = []
    if 'date_added' in df.columns:
        sort_columns.append('date_added')
    if 'show_id' in df.columns:
        sort_columns.append('show_id')
    
    if sort_columns:
        df = df.sort_values(sort_columns, na_position='last')
    
    # Reset index
    df = df.reset_index(drop=True)
    
    log_message("Final cleanup completed")
    return df

def transform_data(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Main transformation function - wrapper for Netflix-specific transformations.
    
    Parameters:
    df (pd.DataFrame): Raw data
    
    Returns:
    pd.DataFrame: Transformed data
    """
    return transform_netflix_data(df)