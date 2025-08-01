"""
Main ETL Pipeline Orchestrator for Netflix Data Engineering Project

This module orchestrates the complete ETL pipeline:
1. Extract Netflix data from CSV
2. Transform and clean the data
3. Load data into PostgreSQL
4. Generate reports and visualizations
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from config import NETFLIX_CSV_PATH, TABLE_NAME, OUTPUT_DIR
from extract import extract_netflix_data
from transform import transform_netflix_data
from load import load_to_postgres, get_table_info
from utils import log_message, handle_error, log_success, get_data_quality_report
from visualizations import create_netflix_dashboard, generate_analysis_report

class NetflixETLPipeline:
    """
    Complete ETL Pipeline for Netflix data processing.
    """
    
    def __init__(self, csv_path: Optional[Path] = None, table_name: str = TABLE_NAME):
        """
        Initialize the ETL pipeline.
        
        Parameters:
        csv_path (Path, optional): Path to Netflix CSV file
        table_name (str): Target database table name
        """
        self.csv_path = csv_path or NETFLIX_CSV_PATH
        self.table_name = table_name
        self.pipeline_start_time = None
        self.pipeline_end_time = None
        self.raw_data = None
        self.transformed_data = None
        self.pipeline_report = {}
    
    def run_full_pipeline(self) -> bool:
        """
        Execute the complete ETL pipeline.
        
        Returns:
        bool: True if pipeline completed successfully, False otherwise
        """
        log_message("=" * 80)
        log_message("STARTING NETFLIX DATA ENGINEERING PIPELINE")
        log_message("=" * 80)
        
        self.pipeline_start_time = datetime.now()
        
        try:
            # Step 1: Extract
            if not self._extract_data():
                return False
            
            # Step 2: Transform
            if not self._transform_data():
                return False
            
            # Step 3: Load
            if not self._load_data():
                return False
            
            # Step 4: Generate reports and visualizations
            if not self._generate_reports():
                return False
            
            # Step 5: Create final pipeline report
            self._create_pipeline_report()
            
            self.pipeline_end_time = datetime.now()
            duration = self.pipeline_end_time - self.pipeline_start_time
            
            log_success("=" * 80)
            log_success(f"PIPELINE COMPLETED SUCCESSFULLY IN {duration}")
            log_success("=" * 80)
            
            return True
            
        except Exception as e:
            handle_error(f"Pipeline failed with unexpected error: {e}")
            return False
    
    def _extract_data(self) -> bool:
        """Extract data from CSV file."""
        log_message("STEP 1: EXTRACTING DATA")
        log_message("-" * 40)
        
        self.raw_data = extract_netflix_data(self.csv_path)
        
        if self.raw_data is None:
            handle_error("Data extraction failed")
            return False
        
        log_success(f"Extraction completed: {len(self.raw_data)} records extracted")
        return True
    
    def _transform_data(self) -> bool:
        """Transform and clean the data."""
        log_message("STEP 2: TRANSFORMING DATA")
        log_message("-" * 40)
        
        self.transformed_data = transform_netflix_data(self.raw_data)
        
        if self.transformed_data is None:
            handle_error("Data transformation failed")
            return False
        
        # Log transformation summary
        original_rows = len(self.raw_data)
        final_rows = len(self.transformed_data)
        rows_removed = original_rows - final_rows
        
        log_success(f"Transformation completed:")
        log_message(f"  - Original rows: {original_rows}")
        log_message(f"  - Final rows: {final_rows}")
        log_message(f"  - Rows removed: {rows_removed} ({(rows_removed/original_rows)*100:.1f}%)")
        
        return True
    
    def _load_data(self) -> bool:
        """Load data into PostgreSQL database."""
        log_message("STEP 3: LOADING DATA")
        log_message("-" * 40)
        
        success = load_to_postgres(self.transformed_data, self.table_name)
        
        if not success:
            handle_error("Data loading failed")
            return False
        
        # Verify the load
        table_info = get_table_info(self.table_name)
        if table_info:
            log_success(f"Data loaded successfully to table '{self.table_name}'")
            log_message(f"  - Rows in database: {table_info['row_count']}")
            log_message(f"  - Columns: {table_info['column_count']}")
        
        return True
    
    def _generate_reports(self) -> bool:
        """Generate visualizations and analysis reports."""
        log_message("STEP 4: GENERATING REPORTS AND VISUALIZATIONS")
        log_message("-" * 40)
        
        try:
            # Create visualizations dashboard
            dashboard_path = create_netflix_dashboard(self.transformed_data)
            if dashboard_path:
                log_success(f"Dashboard created: {dashboard_path}")
            
            # Generate analysis report
            report_path = generate_analysis_report(self.transformed_data)
            if report_path:
                log_success(f"Analysis report created: {report_path}")
            
            return True
            
        except Exception as e:
            handle_error(f"Error generating reports: {e}")
            return False
    
    def _create_pipeline_report(self) -> None:
        """Create comprehensive pipeline execution report."""
        duration = self.pipeline_end_time - self.pipeline_start_time
        
        self.pipeline_report = {
            'pipeline_execution': {
                'start_time': self.pipeline_start_time.isoformat(),
                'end_time': self.pipeline_end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'status': 'SUCCESS'
            },
            'data_summary': {
                'source_file': str(self.csv_path),
                'target_table': self.table_name,
                'raw_data_rows': len(self.raw_data) if self.raw_data is not None else 0,
                'transformed_data_rows': len(self.transformed_data) if self.transformed_data is not None else 0,
                'data_quality': get_data_quality_report(self.transformed_data) if self.transformed_data is not None else {}
            }
        }
        
        # Save pipeline report
        report_file = OUTPUT_DIR / f"pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.pipeline_report, f, indent=2, default=str)
            
            log_success(f"Pipeline report saved: {report_file}")
            
        except Exception as e:
            handle_error(f"Error saving pipeline report: {e}")

def run_netflix_pipeline(csv_path: Optional[Path] = None) -> bool:
    """
    Convenience function to run the complete Netflix ETL pipeline.
    
    Parameters:
    csv_path (Path, optional): Path to Netflix CSV file
    
    Returns:
    bool: True if pipeline completed successfully
    """
    pipeline = NetflixETLPipeline(csv_path)
    return pipeline.run_full_pipeline()

if __name__ == "__main__":
    # Run the pipeline
    success = run_netflix_pipeline()
    
    if success:
        log_success("Netflix ETL Pipeline completed successfully!")
        log_message("Check the output directory for reports and visualizations.")
    else:
        handle_error("Netflix ETL Pipeline failed!")
        log_message("Check the logs for error details.")
