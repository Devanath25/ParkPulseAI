"""
Insights Analyzer Module
Provides detailed analysis across different dimensions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .shared_data import get_location_column


class InsightsAnalyzer:
    """Generate insights across multiple dimensions"""
    
    def __init__(self, data_processor):
        self.data_processor = data_processor
        
    def area_wise_analysis(self):
        """Analyze violations by area/location for demo mode"""
        df = self.data_processor.get_geographic_data()
        
        # Sample only 1000 rows for demo mode
        if len(df) > 1000:
            df = df.sample(n=1000, random_state=42)
        
        # Get location column dynamically
        location_col = get_location_column(df)
        
        # Aggregate by location
        area_stats = df.groupby('location_key').agg({
            'latitude': 'first',
            'longitude': 'first',
            'location': 'first',
            'police_station': 'first',
            'id': 'count',
            'vehicle_type': lambda x: x.mode().iloc[0] if len(x) > 0 else None,
            'primary_violation': lambda x: x.mode().iloc[0] if len(x) > 0 else None,
            'created_datetime': ['min', 'max']
        }).reset_index()
        
        area_stats.columns = ['location_key', 'latitude', 'longitude', 'location',
                            'police_station', 'violation_count', 'common_vehicle',
                            'common_violation', 'first_violation', 'last_violation']
        
        # Calculate time span
        area_stats['days_active'] = (
            area_stats['last_violation'] - area_stats['first_violation']
        ).dt.total_seconds() / 86400
        
        # Calculate frequency
        area_stats['violations_per_day'] = np.where(
            area_stats['days_active'] > 0,
            area_stats['violation_count'] / area_stats['days_active'],
            area_stats['violation_count']
        )
        
        area_stats = area_stats.sort_values('violation_count', ascending=False)
        
        return area_stats
    
    def police_station_analysis(self):
        """Analyze violations by police station"""
        df = self.data_processor.get_geographic_data()
        
        # Get location column dynamically
        location_col = get_location_column(df)
        
        station_stats = df.groupby('police_station').agg({
            'id': 'count',
            'vehicle_type': lambda x: x.nunique(),
            'primary_violation': lambda x: x.nunique(),
            'location_key': lambda x: x.nunique(),
            'created_datetime': ['min', 'max'],
            'validation_status': lambda x: (x == 'approved').sum()
        }).reset_index()
        
        station_stats.columns = ['police_station', 'total_violations', 'unique_vehicle_types',
                                'unique_violation_types', 'unique_locations', 'first_violation',
                                'last_violation', 'approved_violations']
        
        # Calculate approval rate
        station_stats['approval_rate'] = (
            station_stats['approved_violations'] / station_stats['total_violations'] * 100
        ).round(2)
        
        # Calculate days active
        station_stats['days_active'] = (
            station_stats['last_violation'] - station_stats['first_violation']
        ).dt.total_seconds() / 86400
        
        # Calculate daily average
        station_stats['avg_violations_per_day'] = np.where(
            station_stats['days_active'] > 0,
            station_stats['total_violations'] / station_stats['days_active'],
            station_stats['total_violations']
        ).round(2)
        
        station_stats = station_stats.sort_values('total_violations', ascending=False)
        
        return station_stats
    
    def time_based_trends(self):
        """Analyze time-based violation patterns"""
        df = self.data_processor.get_geographic_data()
        
        # Hourly patterns
        hourly_stats = df.groupby('hour').size().reset_index(name='violations')
        
        # Daily patterns
        daily_stats = df.groupby('day_of_week').size().reset_index(name='violations')
        daily_stats['day_name'] = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                                   'Friday', 'Saturday', 'Sunday']
        
        # Monthly patterns
        monthly_stats = df.groupby('month').size().reset_index(name='violations')
        month_names = {11: 'November', 12: 'December', 1: 'January', 2: 'February', 
                      3: 'March', 4: 'April'}
        monthly_stats['month_name'] = monthly_stats['month'].map(month_names)
        
        # Weekend vs weekday
        weekend_stats = df.groupby('is_weekend').size().reset_index(name='violations')
        weekend_stats['period'] = weekend_stats['is_weekend'].map({True: 'Weekend', False: 'Weekday'})
        
        return {
            'hourly': hourly_stats,
            'daily': daily_stats,
            'monthly': monthly_stats,
            'weekend_vs_weekday': weekend_stats
        }
    
    def violation_trends(self):
        """Analyze violation type trends"""
        df = self.data_processor.get_geographic_data()
        
        # Overall violation type distribution
        violation_dist = df['primary_violation'].value_counts().reset_index()
        violation_dist.columns = ['violation_type', 'count']
        violation_dist['percentage'] = (violation_dist['count'] / violation_dist['count'].sum() * 100).round(2)
        
        # Violation type by vehicle type
        violation_by_vehicle = pd.crosstab(
            df['primary_violation'], 
            df['vehicle_type'],
            normalize='columns'
        ) * 100
        
        # Violation type trends over time
        df['date'] = df['created_datetime'].dt.date
        violation_time_trend = df.groupby(['date', 'primary_violation']).size().unstack(fill_value=0)
        
        # Most severe violations (by offence code)
        df['offence_code_numeric'] = df['primary_offence_code'].apply(
            lambda x: int(x) if pd.notna(x) and str(x).isdigit() else 0
        )
        severe_violations = df[df['offence_code_numeric'] > 100].groupby('primary_violation').size().reset_index(name='count')
        severe_violations = severe_violations.sort_values('count', ascending=False)
        
        return {
            'distribution': violation_dist,
            'by_vehicle_type': violation_by_vehicle,
            'time_trend': violation_time_trend,
            'severe_violations': severe_violations
        }
    
    def recurring_hotspot_detection(self):
        """Detect recurring hotspots over time"""
        df = self.data_processor.get_geographic_data()
        
        # Get location column dynamically
        location_col = get_location_column(df)
        
        df['week'] = df['created_datetime'].dt.isocalendar().week
        
        # Get weekly counts per location
        weekly_location_counts = df.groupby(['location_key', 'week']).size().reset_index(name='weekly_violations')
        
        # Calculate consistency (how many weeks had violations)
        location_weeks = weekly_location_counts.groupby('location_key').agg({
            'week': 'count',
            'weekly_violations': ['sum', 'mean', 'std']
        }).reset_index()
        
        location_weeks.columns = ['location_key', 'weeks_with_violations', 'total_violations',
                                 'avg_weekly_violations', 'std_weekly_violations']
        
        # Calculate recurrence score
        location_weeks['recurrence_score'] = (
            location_weeks['weeks_with_violations'] * 0.5 +
            location_weeks['avg_weekly_violations'] * 0.3 +
            (location_weeks['std_weekly_violations'].fillna(0) * -0.2)  # Lower std = more consistent
        )
        
        # Merge with location details
        location_details = df.groupby('location_key').agg({
            'latitude': 'first',
            'longitude': 'first',
            'location': 'first',
            'police_station': 'first'
        }).reset_index()
        
        recurring_hotspots = location_weeks.merge(location_details, on='location_key')
        recurring_hotspots = recurring_hotspots.sort_values('recurrence_score', ascending=False)
        
        return recurring_hotspots
    
    def peak_hour_analysis(self):
        """Analyze peak violation hours by location"""
        df = self.data_processor.get_geographic_data()
        
        # Get location column dynamically
        location_col = get_location_column(df)
        
        # Get peak hour for each location
        location_peak_hours = df.groupby(['location_key', 'hour']).size().reset_index(name='hourly_violations')
        peak_hours = location_peak_hours.loc[
            location_peak_hours.groupby('location_key')['hourly_violations'].idxmax()
        ]
        
        # Merge with location details
        location_details = df.groupby('location_key').agg({
            'latitude': 'first',
            'longitude': 'first',
            'location': 'first',
            'police_station': 'first',
            'id': 'count'
        }).reset_index()
        
        peak_hours = peak_hours.merge(location_details, on='location_key')
        peak_hours.columns = ['location_key', 'peak_hour', 'peak_hour_violations',
                            'latitude', 'longitude', 'location', 'police_station', 'total_violations']
        
        peak_hours = peak_hours.sort_values('peak_hour_violations', ascending=False)
        
        return peak_hours
    
    def vehicle_type_insights(self):
        """Generate insights about vehicle types"""
        df = self.data_processor.get_geographic_data()
        
        # Get location column dynamically
        location_col = get_location_column(df)
        
        # Vehicle type distribution
        vehicle_dist = df['vehicle_type'].value_counts().reset_index()
        vehicle_dist.columns = ['vehicle_type', 'count']
        vehicle_dist['percentage'] = (vehicle_dist['count'] / vehicle_dist['count'].sum() * 100).round(2)
        
        # Vehicle type by police station
        vehicle_by_station = pd.crosstab(df['police_station'], df['vehicle_type'])
        
        # Vehicle type by violation type
        vehicle_by_violation = pd.crosstab(df['primary_violation'], df['vehicle_type'])
        
        # Top vehicle types at hotspots
        location_counts = df.groupby('location_key').size().reset_index(name='location_count')
        top_locations = location_counts.nlargest(50, 'location_count')['location_key']
        hotspot_vehicles = df[df['location_key'].isin(top_locations)].groupby('vehicle_type').size().reset_index(name='count')
        hotspot_vehicles = hotspot_vehicles.sort_values('count', ascending=False)
        
        return {
            'distribution': vehicle_dist,
            'by_police_station': vehicle_by_station,
            'by_violation_type': vehicle_by_violation,
            'at_hotspots': hotspot_vehicles
        }
    
    def comparative_analysis(self, metric='violation_count'):
        """Compare different areas/stations"""
        df = self.data_processor.get_geographic_data()
        
        if metric == 'violation_count':
            comparison = df.groupby('police_station').size().reset_index(name='value')
        elif metric == 'approval_rate':
            approved = df[df['validation_status'] == 'approved'].groupby('police_station').size().reset_index(name='approved')
            total = df.groupby('police_station').size().reset_index(name='total')
            comparison = approved.merge(total, on='police_station')
            comparison['value'] = (comparison['approved'] / comparison['total'] * 100).round(2)
        else:
            comparison = df.groupby('police_station').size().reset_index(name='value')
        
        comparison = comparison.sort_values('value', ascending=False)
        
        return comparison
