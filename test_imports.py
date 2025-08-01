#!/usr/bin/env python3
"""
Test script to verify all imports are working correctly
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test all module imports"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import pandas as pd
        import numpy as np
        print("[OK] pandas and numpy imported successfully")
        
        # Test database imports
        from sqlalchemy import create_engine
        import psycopg2
        print("[OK] SQLAlchemy and psycopg2 imported successfully")
        
        # Test visualization imports
        import matplotlib.pyplot as plt
        import seaborn as sns
        import plotly.express as px
        print("[OK] Visualization libraries imported successfully")
        
        # Test logging
        from loguru import logger
        print("[OK] Loguru imported successfully")
        
        # Test environment
        from dotenv import load_dotenv
        print("[OK] python-dotenv imported successfully")
        
        # Test our modules
        from config import DATABASE_URL, TABLE_NAME, NETFLIX_CSV_PATH
        print("[OK] Config module imported successfully")
        
        from utils import log_message, handle_error, validate_data
        print("[OK] Utils module imported successfully")
        
        from extract import extract_netflix_data
        print("[OK] Extract module imported successfully")
        
        from transform import transform_netflix_data
        print("[OK] Transform module imported successfully")
        
        from load import load_to_postgres
        print("[OK] Load module imported successfully")
        
        from visualizations import create_netflix_dashboard
        print("[OK] Visualizations module imported successfully")
        
        from pipeline import NetflixETLPipeline
        print("[OK] Pipeline module imported successfully")
        
        print("\nSUCCESS: All imports successful! The pipeline is ready to run.")
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
