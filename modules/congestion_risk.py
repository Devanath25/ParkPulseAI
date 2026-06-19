"""
Congestion Risk Engine Module
Calculates congestion risk scores and categorizes locations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .shared_data import get_location_column


class CongestionRiskEngine:
    """Calculate congestion risk based on violation patterns"""
    
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.risk_scores = None
        
    def calculate_risk_score(self, df=None):
        """Calculate comprehensive risk score for each location"""
        if df is None:
            df = self.data_processor.get_geographic_data()
        
        # Get location column dynamically
        location_col = get_location_column(df)
        
        # Aggregate by location
        location_stats = df.groupby('location_key').agg({
            'latitude': 'first',
            'longitude': 'first',
            'location': 'first',
            'police_station': 'first',
            'junction_name': 'first',
            'id': 'count',
            'primary_violation': lambda x: x.tolist(),
            'vehicle_type': lambda x: x.tolist(),
            'created_datetime': ['min', 'max'],
            'hour': lambda x: x.tolist(),
            'day_of_week': lambda x: x.tolist()
        }).reset_index()
        
        location_stats.columns = ['location_key', 'latitude', 'longitude', 'location',
                                'police_station', 'junction_name', 'violation_count',
                                'violations_list', 'vehicles_list', 'first_violation',
                                'last_violation', 'hours_list', 'days_list']
        
        # Calculate temporal spread
        location_stats['time_span_days'] = (
            location_stats['last_violation'] - location_stats['first_violation']
        ).dt.total_seconds() / 86400
        
        # Calculate violation frequency (violations per day)
        location_stats['violation_frequency'] = np.where(
            location_stats['time_span_days'] > 0,
            location_stats['violation_count'] / location_stats['time_span_days'],
            location_stats['violation_count']
        )
        
        # Calculate peak hour concentration
        location_stats['peak_hour_concentration'] = location_stats['hours_list'].apply(
            lambda x: max([x.count(h) for h in range(24)]) if x else 0
        )
        
        # Calculate vehicle type diversity
        location_stats['vehicle_diversity'] = location_stats['vehicles_list'].apply(
            lambda x: len(set(x)) if x else 0
        )
        
        # Calculate violation type diversity
        location_stats['violation_diversity'] = location_stats['violations_list'].apply(
            lambda x: len(set(x)) if x else 0
        )
        
        # Check if it's a junction (junctions are higher risk)
        location_stats['is_junction'] = location_stats['junction_name'].apply(
            lambda x: 1 if x and 'No Junction' not in str(x) else 0
        )
        
        # Calculate recency score (recent violations are higher risk)
        max_date = df['created_datetime'].max()
        location_stats['recency_score'] = (
            (max_date - location_stats['last_violation']).dt.total_seconds() / 86400
        )
        location_stats['recency_score'] = 100 / (location_stats['recency_score'] + 1)
        
        # Normalize all factors to 0-100 scale
        location_stats['normalized_count'] = self._normalize(location_stats['violation_count'])
        location_stats['normalized_frequency'] = self._normalize(location_stats['violation_frequency'])
        location_stats['normalized_peak'] = self._normalize(location_stats['peak_hour_concentration'])
        location_stats['normalized_diversity'] = self._normalize(location_stats['vehicle_diversity'])
        
        # Calculate weighted risk score
        location_stats['risk_score'] = (
            location_stats['normalized_count'] * 0.30 +
            location_stats['normalized_frequency'] * 0.25 +
            location_stats['normalized_peak'] * 0.15 +
            location_stats['normalized_diversity'] * 0.10 +
            location_stats['recency_score'] * 0.10 +
            location_stats['is_junction'] * 10
        )
        
        # Assign risk categories
        location_stats['risk_category'] = pd.cut(
            location_stats['risk_score'],
            bins=[0, 25, 50, 75, 100],
            labels=['Low', 'Medium', 'High', 'Critical']
        )
        
        # Add risk explanation
        location_stats['risk_explanation'] = location_stats.apply(
            self._generate_risk_explanation, axis=1
        )
        
        self.risk_scores = location_stats
        return location_stats
    
    def _normalize(self, series):
        """Normalize series to 0-100 scale"""
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([50] * len(series), index=series.index)
        return ((series - min_val) / (max_val - min_val)) * 100
    
    def _generate_risk_explanation(self, row):
        """Generate explanation for risk category"""
        explanations = []
        
        if row['risk_score'] >= 75:
            explanations.append("Critical risk due to high violation frequency")
        elif row['risk_score'] >= 50:
            explanations.append("High risk area requiring attention")
        elif row['risk_score'] >= 25:
            explanations.append("Moderate risk with periodic violations")
        else:
            explanations.append("Low risk area with minimal violations")
        
        if row['violation_count'] > 50:
            explanations.append(f"High violation count ({row['violation_count']})")
        
        if row['violation_frequency'] > 1:
            explanations.append(f"High frequency ({row['violation_frequency']:.2f} violations/day)")
        
        if row['is_junction']:
            explanations.append("Located at junction - higher congestion impact")
        
        if row['peak_hour_concentration'] > 10:
            explanations.append("Peak hour concentration detected")
        
        return " | ".join(explanations)
    
    def get_risk_distribution(self):
        """Get distribution of risk categories"""
        if self.risk_scores is None:
            self.calculate_risk_score()
        
        return self.risk_scores['risk_category'].value_counts()
    
    def get_high_risk_locations(self, threshold='High'):
        """Get locations above risk threshold"""
        if self.risk_scores is None:
            self.calculate_risk_score()
        
        if isinstance(threshold, str):
            # Use category
            high_risk = self.risk_scores[
                self.risk_scores['risk_category'].isin(['High', 'Critical'])
            ]
        else:
            # Use numeric threshold
            high_risk = self.risk_scores[self.risk_scores['risk_score'] >= threshold]
        
        return high_risk.sort_values('risk_score', ascending=False)
    
    def get_risk_by_police_station(self):
        """Get risk analysis by police station"""
        if self.risk_scores is None:
            self.calculate_risk_score()
        
        station_risk = self.risk_scores.groupby('police_station').agg({
            'risk_score': ['mean', 'max', 'min'],
            'violation_count': 'sum',
            'risk_category': lambda x: (x == 'Critical').sum()
        }).reset_index()
        
        station_risk.columns = ['police_station', 'avg_risk_score', 'max_risk_score',
                               'min_risk_score', 'total_violations', 'critical_hotspots']
        
        station_risk = station_risk.sort_values('avg_risk_score', ascending=False)
        
        return station_risk
    
    def get_risk_trends(self, window_days=7):
        """Analyze risk trends over time"""
        df = self.data_processor.get_geographic_data()
        
        # Get location column dynamically
        location_col = get_location_column(df)
        
        # Calculate daily risk
        df['date'] = df['created_datetime'].dt.date
        daily_stats = df.groupby(['date', 'location_key']).size().reset_index(name='daily_violations')
        
        # Calculate rolling average
        daily_stats['date'] = pd.to_datetime(daily_stats['date'], errors="coerce", format="mixed")
        daily_stats = daily_stats.sort_values('date')
        
        location_trends = daily_stats.groupby('location_key').apply(
            lambda x: x.set_index('date')['daily_violations'].rolling(
                window=window_days, min_periods=1
            ).mean().iloc[-1] if len(x) > 0 else 0
        ).reset_index(name='trend_score')
        
        return location_trends
    
    def predict_risk_change(self, days_ahead=7):
        """Predict risk change based on historical patterns"""
        df = self.data_processor.get_geographic_data()
        
        # Get location column dynamically
        location_col = get_location_column(df)
        
        # Get recent violations
        recent_date = df['created_datetime'].max() - timedelta(days=30)
        recent_df = df[df['created_datetime'] >= recent_date]
        
        # Calculate weekly patterns
        recent_df['week'] = recent_df['created_datetime'].dt.isocalendar().week
        weekly_counts = recent_df.groupby(['location_key', 'week']).size().reset_index(name='weekly_violations')
        
        # Calculate trend
        trend_data = weekly_counts.groupby('location_key').agg({
            'weekly_violations': ['mean', 'std', 'last']
        }).reset_index()
        
        trend_data.columns = ['location_key', 'avg_weekly', 'std_weekly', 'last_week']
        
        # Predict next week
        trend_data['predicted_next_week'] = trend_data['last_week'] + (
            (trend_data['last_week'] - trend_data['avg_weekly']) * 0.5
        )
        
        trend_data['predicted_risk_change'] = (
            (trend_data['predicted_next_week'] - trend_data['avg_weekly']) / 
            trend_data['avg_weekly'] * 100
        ).fillna(0)
        
        return trend_data
