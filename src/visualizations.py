"""
Visualization and Analysis Module for Netflix Data Engineering Project

This module creates comprehensive visualizations and analysis reports
for the Netflix dataset after ETL processing.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

from config import OUTPUT_DIR, FIGURE_SIZE, DPI, COLOR_PALETTE
from utils import log_message, handle_error, log_success

# Set style for matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette(COLOR_PALETTE)

class NetflixAnalyzer:
    """
    Comprehensive analyzer for Netflix data with visualization capabilities.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the analyzer with Netflix data.
        
        Parameters:
        df (pd.DataFrame): Cleaned Netflix data
        """
        self.df = df.copy()
        self.output_dir = OUTPUT_DIR
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def create_content_type_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Create analysis of content types (Movies vs TV Shows)."""
        fig, axes = plt.subplots(2, 2, figsize=FIGURE_SIZE)
        fig.suptitle('Netflix Content Type Analysis', fontsize=16, fontweight='bold')
        
        # Content type distribution
        type_counts = self.df['type'].value_counts()
        axes[0, 0].pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%', startangle=90)
        axes[0, 0].set_title('Content Type Distribution')
        
        # Content type by year added
        if 'date_added_year' in self.df.columns:
            yearly_content = self.df.groupby(['date_added_year', 'type']).size().unstack(fill_value=0)
            yearly_content.plot(kind='bar', ax=axes[0, 1], stacked=True)
            axes[0, 1].set_title('Content Added by Year and Type')
            axes[0, 1].set_xlabel('Year Added')
            axes[0, 1].set_ylabel('Number of Titles')
            axes[0, 1].legend(title='Type')
            axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Duration analysis for movies
        if 'duration_value' in self.df.columns:
            movies = self.df[self.df['type'] == 'Movie']['duration_value'].dropna()
            if not movies.empty:
                axes[1, 0].hist(movies, bins=30, alpha=0.7, edgecolor='black')
                axes[1, 0].set_title('Movie Duration Distribution')
                axes[1, 0].set_xlabel('Duration (minutes)')
                axes[1, 0].set_ylabel('Frequency')
                axes[1, 0].axvline(movies.mean(), color='red', linestyle='--', 
                                 label=f'Mean: {movies.mean():.1f} min')
                axes[1, 0].legend()
        
        # TV Show seasons analysis
        if 'duration_value' in self.df.columns:
            tv_shows = self.df[self.df['type'] == 'TV Show']['duration_value'].dropna()
            if not tv_shows.empty:
                season_counts = tv_shows.value_counts().sort_index()
                axes[1, 1].bar(season_counts.index, season_counts.values)
                axes[1, 1].set_title('TV Show Seasons Distribution')
                axes[1, 1].set_xlabel('Number of Seasons')
                axes[1, 1].set_ylabel('Number of Shows')
        
        plt.tight_layout()
        
        # Generate statistics
        stats = {
            'total_content': len(self.df),
            'movies': len(self.df[self.df['type'] == 'Movie']),
            'tv_shows': len(self.df[self.df['type'] == 'TV Show']),
            'movie_percentage': (len(self.df[self.df['type'] == 'Movie']) / len(self.df)) * 100,
            'avg_movie_duration': self.df[self.df['type'] == 'Movie']['duration_value'].mean() if 'duration_value' in self.df.columns else None
        }
        
        return fig, stats
    
    def create_temporal_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Create temporal analysis of Netflix content."""
        fig, axes = plt.subplots(2, 2, figsize=FIGURE_SIZE)
        fig.suptitle('Netflix Temporal Analysis', fontsize=16, fontweight='bold')
        
        # Content added over time
        if 'date_added_year' in self.df.columns:
            yearly_additions = self.df['date_added_year'].value_counts().sort_index()
            axes[0, 0].plot(yearly_additions.index, yearly_additions.values, marker='o')
            axes[0, 0].set_title('Content Added to Netflix by Year')
            axes[0, 0].set_xlabel('Year')
            axes[0, 0].set_ylabel('Number of Titles Added')
            axes[0, 0].grid(True, alpha=0.3)
        
        # Release year distribution
        if 'release_year' in self.df.columns:
            release_years = self.df['release_year'].dropna()
            axes[0, 1].hist(release_years, bins=50, alpha=0.7, edgecolor='black')
            axes[0, 1].set_title('Content Release Year Distribution')
            axes[0, 1].set_xlabel('Release Year')
            axes[0, 1].set_ylabel('Frequency')
            axes[0, 1].axvline(release_years.mean(), color='red', linestyle='--',
                             label=f'Mean: {release_years.mean():.0f}')
            axes[0, 1].legend()
        
        # Content age when added
        if 'content_age_when_added' in self.df.columns:
            content_age = self.df['content_age_when_added'].dropna()
            content_age = content_age[content_age >= 0]  # Filter out negative values
            if not content_age.empty:
                axes[1, 0].hist(content_age, bins=30, alpha=0.7, edgecolor='black')
                axes[1, 0].set_title('Content Age When Added to Netflix')
                axes[1, 0].set_xlabel('Age (years)')
                axes[1, 0].set_ylabel('Frequency')
                axes[1, 0].axvline(content_age.mean(), color='red', linestyle='--',
                                 label=f'Mean: {content_age.mean():.1f} years')
                axes[1, 0].legend()
        
        # Decade analysis
        if 'decade' in self.df.columns:
            decade_counts = self.df['decade'].value_counts().sort_index()
            axes[1, 1].bar(decade_counts.index, decade_counts.values)
            axes[1, 1].set_title('Content by Decade')
            axes[1, 1].set_xlabel('Decade')
            axes[1, 1].set_ylabel('Number of Titles')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Generate statistics
        stats = {
            'earliest_release': self.df['release_year'].min() if 'release_year' in self.df.columns else None,
            'latest_release': self.df['release_year'].max() if 'release_year' in self.df.columns else None,
            'first_added': self.df['date_added'].min() if 'date_added' in self.df.columns else None,
            'last_added': self.df['date_added'].max() if 'date_added' in self.df.columns else None,
            'avg_content_age': self.df['content_age_when_added'].mean() if 'content_age_when_added' in self.df.columns else None
        }
        
        return fig, stats
    
    def create_geographic_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Create geographic analysis of Netflix content."""
        fig, axes = plt.subplots(2, 2, figsize=FIGURE_SIZE)
        fig.suptitle('Netflix Geographic Analysis', fontsize=16, fontweight='bold')
        
        # Top countries by content count
        if 'primary_country' in self.df.columns:
            top_countries = self.df['primary_country'].value_counts().head(15)
            axes[0, 0].barh(range(len(top_countries)), top_countries.values)
            axes[0, 0].set_yticks(range(len(top_countries)))
            axes[0, 0].set_yticklabels(top_countries.index)
            axes[0, 0].set_title('Top 15 Countries by Content Count')
            axes[0, 0].set_xlabel('Number of Titles')
        
        # International vs domestic content
        if 'is_international' in self.df.columns:
            intl_counts = self.df['is_international'].value_counts()
            labels = ['Single Country', 'Multiple Countries']
            axes[0, 1].pie(intl_counts.values, labels=labels, autopct='%1.1f%%', startangle=90)
            axes[0, 1].set_title('International Co-productions')
        
        # Content type by top countries
        if 'primary_country' in self.df.columns and 'type' in self.df.columns:
            top_5_countries = self.df['primary_country'].value_counts().head(5).index
            country_type = self.df[self.df['primary_country'].isin(top_5_countries)].groupby(['primary_country', 'type']).size().unstack(fill_value=0)
            country_type.plot(kind='bar', ax=axes[1, 0], stacked=True)
            axes[1, 0].set_title('Content Type by Top 5 Countries')
            axes[1, 0].set_xlabel('Country')
            axes[1, 0].set_ylabel('Number of Titles')
            axes[1, 0].legend(title='Type')
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Country diversity over time
        if 'date_added_year' in self.df.columns and 'primary_country' in self.df.columns:
            yearly_countries = self.df.groupby('date_added_year')['primary_country'].nunique()
            axes[1, 1].plot(yearly_countries.index, yearly_countries.values, marker='o')
            axes[1, 1].set_title('Country Diversity Over Time')
            axes[1, 1].set_xlabel('Year Added')
            axes[1, 1].set_ylabel('Number of Unique Countries')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Generate statistics
        stats = {
            'total_countries': self.df['primary_country'].nunique() if 'primary_country' in self.df.columns else None,
            'top_country': self.df['primary_country'].mode().iloc[0] if 'primary_country' in self.df.columns and not self.df['primary_country'].mode().empty else None,
            'international_percentage': (self.df['is_international'].sum() / len(self.df)) * 100 if 'is_international' in self.df.columns else None
        }
        
        return fig, stats
    
    def create_genre_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Create genre analysis of Netflix content."""
        fig, axes = plt.subplots(2, 2, figsize=FIGURE_SIZE)
        fig.suptitle('Netflix Genre Analysis', fontsize=16, fontweight='bold')
        
        # Top genres
        if 'primary_genre' in self.df.columns:
            top_genres = self.df['primary_genre'].value_counts().head(15)
            axes[0, 0].barh(range(len(top_genres)), top_genres.values)
            axes[0, 0].set_yticks(range(len(top_genres)))
            axes[0, 0].set_yticklabels(top_genres.index)
            axes[0, 0].set_title('Top 15 Primary Genres')
            axes[0, 0].set_xlabel('Number of Titles')
        
        # Genre diversity
        if 'genre_diversity' in self.df.columns:
            diversity_counts = self.df['genre_diversity'].value_counts().sort_index()
            axes[0, 1].bar(diversity_counts.index, diversity_counts.values)
            axes[0, 1].set_title('Genre Diversity Distribution')
            axes[0, 1].set_xlabel('Number of Genres per Title')
            axes[0, 1].set_ylabel('Number of Titles')
        
        # Genre by content type
        if 'primary_genre' in self.df.columns and 'type' in self.df.columns:
            top_genres_list = self.df['primary_genre'].value_counts().head(10).index
            genre_type = self.df[self.df['primary_genre'].isin(top_genres_list)].groupby(['primary_genre', 'type']).size().unstack(fill_value=0)
            genre_type.plot(kind='bar', ax=axes[1, 0], stacked=True)
            axes[1, 0].set_title('Content Type by Top 10 Genres')
            axes[1, 0].set_xlabel('Genre')
            axes[1, 0].set_ylabel('Number of Titles')
            axes[1, 0].legend(title='Type')
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Rating category distribution
        if 'rating_category' in self.df.columns:
            rating_counts = self.df['rating_category'].value_counts()
            axes[1, 1].pie(rating_counts.values, labels=rating_counts.index, autopct='%1.1f%%', startangle=90)
            axes[1, 1].set_title('Content by Rating Category')
        
        plt.tight_layout()
        
        # Generate statistics
        stats = {
            'total_unique_genres': self.df['primary_genre'].nunique() if 'primary_genre' in self.df.columns else None,
            'most_popular_genre': self.df['primary_genre'].mode().iloc[0] if 'primary_genre' in self.df.columns and not self.df['primary_genre'].mode().empty else None,
            'avg_genres_per_title': self.df['genre_diversity'].mean() if 'genre_diversity' in self.df.columns else None
        }
        
        return fig, stats

def create_netflix_dashboard(df: pd.DataFrame) -> Optional[Path]:
    """
    Create a comprehensive dashboard with all Netflix analyses.
    
    Parameters:
    df (pd.DataFrame): Cleaned Netflix data
    
    Returns:
    Path: Path to saved dashboard or None if error
    """
    try:
        log_message("Creating Netflix analysis dashboard")
        
        analyzer = NetflixAnalyzer(df)
        
        # Create all analyses
        content_fig, content_stats = analyzer.create_content_type_analysis()
        temporal_fig, temporal_stats = analyzer.create_temporal_analysis()
        geographic_fig, geographic_stats = analyzer.create_geographic_analysis()
        genre_fig, genre_stats = analyzer.create_genre_analysis()
        
        # Save individual figures
        timestamp = analyzer.timestamp
        
        content_path = OUTPUT_DIR / f"netflix_content_analysis_{timestamp}.png"
        content_fig.savefig(content_path, dpi=DPI, bbox_inches='tight')
        plt.close(content_fig)
        
        temporal_path = OUTPUT_DIR / f"netflix_temporal_analysis_{timestamp}.png"
        temporal_fig.savefig(temporal_path, dpi=DPI, bbox_inches='tight')
        plt.close(temporal_fig)
        
        geographic_path = OUTPUT_DIR / f"netflix_geographic_analysis_{timestamp}.png"
        geographic_fig.savefig(geographic_path, dpi=DPI, bbox_inches='tight')
        plt.close(geographic_fig)
        
        genre_path = OUTPUT_DIR / f"netflix_genre_analysis_{timestamp}.png"
        genre_fig.savefig(genre_path, dpi=DPI, bbox_inches='tight')
        plt.close(genre_fig)
        
        log_success(f"Dashboard visualizations saved:")
        log_message(f"  - Content analysis: {content_path}")
        log_message(f"  - Temporal analysis: {temporal_path}")
        log_message(f"  - Geographic analysis: {geographic_path}")
        log_message(f"  - Genre analysis: {genre_path}")
        
        return content_path.parent
        
    except Exception as e:
        handle_error(f"Error creating dashboard: {e}")
        return None

def generate_analysis_report(df: pd.DataFrame) -> Optional[Path]:
    """
    Generate a comprehensive text report of Netflix data analysis.
    
    Parameters:
    df (pd.DataFrame): Cleaned Netflix data
    
    Returns:
    Path: Path to saved report or None if error
    """
    try:
        log_message("Generating Netflix analysis report")
        
        analyzer = NetflixAnalyzer(df)
        timestamp = analyzer.timestamp
        
        # Generate all statistics
        _, content_stats = analyzer.create_content_type_analysis()
        _, temporal_stats = analyzer.create_temporal_analysis()
        _, geographic_stats = analyzer.create_geographic_analysis()
        _, genre_stats = analyzer.create_genre_analysis()
        
        # Create comprehensive report
        report_content = f"""
# Netflix Data Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Dataset Overview
- Total Content: {len(df):,} titles
- Data Quality: {df.isnull().sum().sum():,} missing values across all columns
- Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB

## Content Type Analysis
- Total Movies: {content_stats['movies']:,} ({content_stats['movie_percentage']:.1f}%)
- Total TV Shows: {content_stats['tv_shows']:,} ({100-content_stats['movie_percentage']:.1f}%)
- Average Movie Duration: {content_stats['avg_movie_duration']:.1f} minutes (if available)

## Temporal Analysis
- Content Release Years: {temporal_stats['earliest_release']} - {temporal_stats['latest_release']}
- Netflix Addition Period: {temporal_stats['first_added']} - {temporal_stats['last_added']}
- Average Content Age When Added: {temporal_stats['avg_content_age']:.1f} years (if available)

## Geographic Analysis
- Total Countries Represented: {geographic_stats['total_countries']}
- Top Content Producer: {geographic_stats['top_country']}
- International Co-productions: {geographic_stats['international_percentage']:.1f}% (if available)

## Genre Analysis
- Unique Primary Genres: {genre_stats['total_unique_genres']}
- Most Popular Genre: {genre_stats['most_popular_genre']}
- Average Genres per Title: {genre_stats['avg_genres_per_title']:.1f} (if available)

## Data Quality Summary
"""
        
        # Add data quality details
        for column in df.columns:
            missing_count = df[column].isnull().sum()
            missing_pct = (missing_count / len(df)) * 100
            if missing_count > 0:
                report_content += f"- {column}: {missing_count:,} missing ({missing_pct:.1f}%)\n"
        
        report_content += f"""
## Key Insights
1. Netflix has a {'movie' if content_stats['movies'] > content_stats['tv_shows'] else 'TV show'}-heavy catalog
2. The platform shows {'recent' if temporal_stats['avg_content_age'] and temporal_stats['avg_content_age'] < 5 else 'diverse age'} content preferences
3. Content represents {geographic_stats['total_countries']} countries, showing global diversity
4. {genre_stats['most_popular_genre']} is the most popular genre category

## Technical Notes
- Data processed through comprehensive ETL pipeline
- Missing values handled strategically based on column importance
- Feature engineering applied for enhanced analysis
- All visualizations saved as high-resolution PNG files

---
Report generated by Netflix Data Engineering Pipeline
"""
        
        # Save report
        report_path = OUTPUT_DIR / f"netflix_analysis_report_{timestamp}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        log_success(f"Analysis report saved: {report_path}")
        return report_path
        
    except Exception as e:
        handle_error(f"Error generating analysis report: {e}")
        return None

def create_sql_queries_examples() -> Path:
    """
    Create a file with example SQL queries for the Netflix database.
    
    Returns:
    Path: Path to saved SQL queries file
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    sql_queries = """
-- Netflix Data Analysis - Example SQL Queries
-- Generated by Netflix Data Engineering Pipeline

-- 1. Basic content overview
SELECT 
    type,
    COUNT(*) as content_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM netflix_titles), 2) as percentage
FROM netflix_titles 
GROUP BY type;

-- 2. Top 10 countries by content count
SELECT 
    primary_country,
    COUNT(*) as content_count
FROM netflix_titles 
WHERE primary_country IS NOT NULL
GROUP BY primary_country 
ORDER BY content_count DESC 
LIMIT 10;

-- 3. Content added by year
SELECT 
    date_added_year,
    COUNT(*) as titles_added
FROM netflix_titles 
WHERE date_added_year IS NOT NULL
GROUP BY date_added_year 
ORDER BY date_added_year;

-- 4. Most popular genres
SELECT 
    primary_genre,
    COUNT(*) as title_count
FROM netflix_titles 
WHERE primary_genre IS NOT NULL
GROUP BY primary_genre 
ORDER BY title_count DESC 
LIMIT 15;

-- 5. Average movie duration by decade
SELECT 
    decade,
    AVG(duration_value) as avg_duration_minutes,
    COUNT(*) as movie_count
FROM netflix_titles 
WHERE type = 'Movie' AND decade IS NOT NULL AND duration_value IS NOT NULL
GROUP BY decade 
ORDER BY decade;

-- 6. Content by rating category
SELECT 
    rating_category,
    type,
    COUNT(*) as content_count
FROM netflix_titles 
WHERE rating_category IS NOT NULL
GROUP BY rating_category, type 
ORDER BY rating_category, type;

-- 7. International vs domestic content by year
SELECT 
    date_added_year,
    SUM(CASE WHEN is_international = true THEN 1 ELSE 0 END) as international_content,
    SUM(CASE WHEN is_international = false THEN 1 ELSE 0 END) as domestic_content
FROM netflix_titles 
WHERE date_added_year IS NOT NULL
GROUP BY date_added_year 
ORDER BY date_added_year;

-- 8. Longest and shortest content
SELECT 
    title,
    type,
    duration_value,
    duration_unit,
    release_year
FROM netflix_titles 
WHERE duration_value IS NOT NULL
ORDER BY duration_value DESC 
LIMIT 5;

SELECT 
    title,
    type,
    duration_value,
    duration_unit,
    release_year
FROM netflix_titles 
WHERE duration_value IS NOT NULL AND duration_value > 0
ORDER BY duration_value ASC 
LIMIT 5;

-- 9. Content with most diverse cast/crew
SELECT 
    title,
    type,
    cast_count,
    director_count,
    country_count,
    genre_diversity
FROM netflix_titles 
WHERE cast_count IS NOT NULL
ORDER BY (cast_count + director_count + country_count + genre_diversity) DESC 
LIMIT 10;

-- 10. Recent additions analysis
SELECT 
    title,
    type,
    primary_country,
    primary_genre,
    date_added,
    release_year,
    content_age_when_added
FROM netflix_titles 
WHERE date_added >= '2020-01-01'
ORDER BY date_added DESC 
LIMIT 20;
"""
    
    queries_path = OUTPUT_DIR / f"netflix_sql_queries_{timestamp}.sql"
    with open(queries_path, 'w', encoding='utf-8') as f:
        f.write(sql_queries)
    
    log_success(f"SQL queries examples saved: {queries_path}")
    return queries_path
