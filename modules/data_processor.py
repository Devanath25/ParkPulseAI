"""
Data Processor Module
Handles data loading, cleaning, and preprocessing
"""

import pandas as pd
import numpy as np
from datetime import datetime
import ast
import os
from .shared_data import load_shared_data, get_location_column


class DataProcessor:
    """Process and clean parking violation data"""
    
    def __init__(self, data_path="data/jan to may police violation_anonymized791b166.csv"):
        self.data_path = data_path
        self.raw_data = None
        self.processed_data = None
        
    def load_data(self):
        """Load the raw dataset using shared loader"""
        self.raw_data = load_shared_data()
        return self.raw_data
    
    def clean_data(self):
        """Clean and preprocess the data"""
        if self.raw_data is None:
            self.load_data()
        
        df = self.raw_data.copy()
        
        # Convert datetime columns
        df['created_datetime'] = pd.to_datetime(df['created_datetime'], errors="coerce", format="mixed")
        df['modified_datetime'] = pd.to_datetime(df['modified_datetime'], errors="coerce", format="mixed")
        if 'validation_timestamp' in df.columns:
            df['validation_timestamp'] = pd.to_datetime(df['validation_timestamp'], errors="coerce", format="mixed")
        
        # Extract temporal features
        df['date'] = df['created_datetime'].dt.date
        df['hour'] = df['created_datetime'].dt.hour
        df['day_of_week'] = df['created_datetime'].dt.dayofweek
        df['month'] = df['created_datetime'].dt.month
        df['year'] = df['created_datetime'].dt.year
        df['is_weekend'] = df['day_of_week'].isin([5, 6])
        
        # Parse violation_type and offence_code from string lists
        df['violation_type_list'] = df['violation_type'].apply(self._parse_list)
        df['offence_code_list'] = df['offence_code'].apply(self._parse_list)
        
        # Get primary violation type and offence code
        df['primary_violation'] = df['violation_type_list'].apply(lambda x: x[0] if x else None)
        df['primary_offence_code'] = df['offence_code_list'].apply(lambda x: x[0] if x else None)
        
        # Clean location data
        df['location'] = df['location'].fillna('Unknown')
        
        # Handle missing police stations
        df['police_station'] = df['police_station'].fillna('Unknown')
        
        # Clean validation status
        df['validation_status'] = df['validation_status'].fillna('pending')
        
        # Create location identifier for clustering
        location_col = get_location_column(df)
        df['location_key'] = df['latitude'].round(4).astype(str) + '_' + df['longitude'].round(4).astype(str)
        
        self.processed_data = df
        return df
    
    def _parse_list(self, x):
        """Parse string representation of list"""
        if pd.isna(x) or x == 'NULL':
            return []
        try:
            return ast.literal_eval(x)
        except:
            return []
    
    def get_summary_stats(self):
        """Get summary statistics of the dataset"""
        if self.processed_data is None:
            self.clean_data()
        
        df = self.processed_data
        
        stats = {
            'total_violations': len(df),
            'date_range': {
                'start': df['created_datetime'].min(),
                'end': df['created_datetime'].max()
            },
            'police_stations': df['police_station'].nunique(),
            'vehicle_types': df['vehicle_type'].nunique(),
            'violation_types': df['primary_violation'].nunique(),
            'unique_locations': df['location_key'].nunique(),
            'validation_status': df['validation_status'].value_counts().to_dict(),
            'vehicle_type_distribution': df['vehicle_type'].value_counts().to_dict(),
            'violation_type_distribution': df['primary_violation'].value_counts().to_dict()
        }
        
        return stats
    
    def get_time_series_data(self, freq='D'):
        """Get time series aggregated data"""
        if self.processed_data is None:
            self.clean_data()
        
        df = self.processed_data.copy()
        df.set_index('created_datetime', inplace=True)
        
        if freq == 'D':
            return df.resample('D').size()
        elif freq == 'W':
            return df.resample('W').size()
        elif freq == 'M':
            return df.resample('M').size()
        elif freq == 'H':
            return df.resample('H').size()
        
        return df.resample('D').size()
    
    def filter_data(self, filters):
        """Filter data based on criteria"""
        if self.processed_data is None:
            self.clean_data()
        
        df = self.processed_data.copy()
        
        if 'police_station' in filters and filters['police_station']:
            df = df[df['police_station'].isin(filters['police_station'])]
        
        if 'vehicle_type' in filters and filters['vehicle_type']:
            df = df[df['vehicle_type'].isin(filters['vehicle_type'])]
        
        if 'violation_type' in filters and filters['violation_type']:
            df = df[df['primary_violation'].isin(filters['violation_type'])]
        
        if 'date_range' in filters and filters['date_range']:
            start_date, end_date = filters['date_range']
            df = df[(df['created_datetime'] >= start_date) & (df['created_datetime'] <= end_date)]
        
        if 'validation_status' in filters and filters['validation_status']:
            df = df[df['validation_status'].isin(filters['validation_status'])]
        
        return df
    
    def get_geographic_data(self):
        """Get data with geographic coordinates for demo mode"""
        if self.processed_data is None:
            self.clean_data()
        
        df = self.processed_data.copy()
        # Remove records with invalid coordinates
        df = df[(df['latitude'].between(12.8, 13.2)) & (df['longitude'].between(77.4, 77.8))]
        
        # Sample only 1000 rows for demo mode
        if len(df) > 1000:
            df = df.sample(n=1000, random_state=42)
        
        return df
    
    def get_hotspot_data(self):
        """Get data aggregated by location for hotspot analysis"""
        if self.processed_data is None:
            self.clean_data()
        
        df = self.processed_data.copy()
        
        # Aggregate by location_key
        hotspot_data = df.groupby('location_key').agg({
            'latitude': 'first',
            'longitude': 'first',
            'location': 'first',
            'police_station': 'first',
            'junction_name': 'first',
            'id': 'count',
            'vehicle_type': lambda x: x.mode().iloc[0] if len(x) > 0 else None,
            'primary_violation': lambda x: x.mode().iloc[0] if len(x) > 0 else None
        }).reset_index()
        
        hotspot_data.columns = ['location_key', 'latitude', 'longitude', 'location', 
                               'police_station', 'junction_name', 'violation_count',
                               'common_vehicle_type', 'common_violation']
        
        hotspot_data = hotspot_data.sort_values('violation_count', ascending=False)
        
        return hotspot_data
