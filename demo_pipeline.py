#!/usr/bin/env python3
"""
Demo script to showcase the Netflix ETL pipeline without requiring PostgreSQL setup.
This script demonstrates the Extract and Transform phases and generates sample outputs.
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def demo_extract_transform():
    """Demonstrate the Extract and Transform phases of the pipeline."""
    
    print("=" * 80)
    print("NETFLIX DATA ENGINEERING PIPELINE - DEMONSTRATION")
    print("=" * 80)
    
    try:
        # Import modules
        from extract import extract_netflix_data
        from transform import transform_netflix_data
        from utils import log_message, log_success, get_data_quality_report
        from visualizations import create_netflix_dashboard, generate_analysis_report, create_sql_queries_examples
        
        print("\n[STEP 1] EXTRACTING NETFLIX DATA")
        print("-" * 50)
        
        # Extract data
        raw_data = extract_netflix_data()
        
        if raw_data is None:
            print("[ERROR] Failed to extract data. Please ensure netflix_titles.csv is in the parent directory.")
            return False
        
        print(f"[SUCCESS] Successfully extracted {len(raw_data)} Netflix titles")
        print(f"[INFO] Data shape: {raw_data.shape}")
        print(f"[INFO] Columns: {list(raw_data.columns)}")
        
        print("\n[STEP 2] TRANSFORMING DATA")
        print("-" * 50)
        
        # Transform data
        transformed_data = transform_netflix_data(raw_data)
        
        if transformed_data is None:
            print("[ERROR] Failed to transform data")
            return False
        
        print(f"[SUCCESS] Successfully transformed data")
        print(f"[INFO] Final shape: {transformed_data.shape}")
        
        # Show transformation summary
        original_rows = len(raw_data)
        final_rows = len(transformed_data)
        rows_removed = original_rows - final_rows
        
        print(f"   - Original rows: {len(raw_data):,}")
        print(f"   - Final rows: {len(transformed_data):,}")
        print(f"   - Rows removed: {len(raw_data) - len(transformed_data):,} ({((len(raw_data) - len(transformed_data)) / len(raw_data) * 100):.1f}%)")
        
        quality_report = get_data_quality_report(transformed_data)
        print(f"\n[INFO] Relatório de Qualidade dos Dados:")
        print(f"   - Total de linhas: {quality_report['total_linhas']:,}")
        print(f"   - Total de colunas: {quality_report['total_colunas']}")
        print(f"   - Linhas duplicadas: {quality_report['linhas_duplicadas']}")
        print(f"   - Uso de memória: {quality_report['uso_de_memoria'] / 1024**2:.2f} MB")
        
        print("\n[STEP 3] GENERATING SAMPLE INSIGHTS")
        print("-" * 50)
        
        # Show some basic insights
        if 'type' in transformed_data.columns:
            type_counts = transformed_data['type'].value_counts()
            print(f"[ANALYSIS] Content Distribution:")
            for content_type, count in type_counts.items():
                percentage = (count / len(transformed_data)) * 100
                print(f"   - {content_type}: {count:,} ({percentage:.1f}%)")
        
        if 'primary_country' in transformed_data.columns:
            top_countries = transformed_data['primary_country'].value_counts().head(5)
            print(f"[ANALYSIS] Top 5 Countries:")
            for country, count in top_countries.items():
                print(f"   - {country}: {count:,} titles")
        
        if 'primary_genre' in transformed_data.columns:
            top_genres = transformed_data['primary_genre'].value_counts().head(5)
            print(f"[ANALYSIS] Top 5 Genres:")
            for genre, count in top_genres.items():
                print(f"   - {genre}: {count:,} titles")
        
        print("\n[STEP 4] CREATING VISUALIZATIONS AND REPORTS")
        print("-" * 50)
        
        # Create visualizations (this will save files to output directory)
        dashboard_path = create_netflix_dashboard(transformed_data)
        if dashboard_path:
            print(f"[SUCCESS] Dashboard visualizations created in: {dashboard_path}")
        
        # Generate analysis report
        report_path = generate_analysis_report(transformed_data)
        if report_path:
            print(f"[SUCCESS] Analysis report created: {report_path}")
        
        # Create SQL queries examples
        sql_path = create_sql_queries_examples()
        print(f"[SUCCESS] SQL queries examples created: {sql_path}")
        
        print("\n[SUCCESS] DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("[INFO] Check the 'output' directory for:")
        print("   - Visualization dashboards (PNG files)")
        print("   - Analysis report (Markdown file)")
        print("   - SQL query examples")
        print("   - Data quality reports (JSON files)")
        print("\n[INFO] To run the complete pipeline with PostgreSQL:")
        print("   1. Set up PostgreSQL database")
        print("   2. Configure .env file with database credentials")
        print("   3. Run: python src/pipeline.py")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = demo_extract_transform()
    sys.exit(0 if success else 1)
