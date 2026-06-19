"""
Smart Enforcement Planner Module
Flagship feature: Generates officer deployment recommendations and enforcement priorities
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .shared_data import get_location_column


class EnforcementPlanner:
    """Generate smart enforcement recommendations"""
    
    def __init__(self, data_processor, hotspot_intelligence, congestion_risk):
        self.data_processor = data_processor
        self.hotspot_intelligence = hotspot_intelligence
        self.congestion_risk = congestion_risk
        self.enforcement_plan = None
        
    def generate_enforcement_plan(self, num_officers=50, shift_hours=8):
        """Generate simple enforcement plan for demo mode with performance protection"""
        import time
        start_time = time.time()
        
        # Get hotspot data (already limited to top 20)
        hotspots = self.hotspot_intelligence.identify_hotspots()
        
        # Limit to top 20 for demo mode
        if len(hotspots) > 20:
            hotspots = hotspots.head(20)
        
        # Simple enforcement plan from hotspot counts
        enforcement_data = hotspots.copy()
        
        # Simple intervention impact
        enforcement_data['intervention_impact'] = enforcement_data['violation_count']
        
        # Normalize impact score
        max_impact = enforcement_data['intervention_impact'].max()
        enforcement_data['intervention_impact_normalized'] = (
            enforcement_data['intervention_impact'] / max_impact * 100
        )
        
        # Assign priority levels
        enforcement_data['priority_level'] = pd.cut(
            enforcement_data['intervention_impact_normalized'],
            bins=[0, 25, 50, 75, 100],
            labels=['Low', 'Medium', 'High', 'Critical']
        )
        
        # Simple officer allocation
        enforcement_data['officers_recommended'] = 1
        
        # Simple patrol schedule
        enforcement_data['patrol_schedule'] = "8:00 AM - 4:00 PM"
        
        # Simple towing recommendation
        enforcement_data['towing_recommendation'] = "Standard towing"
        
        # Simple expected reduction
        enforcement_data['expected_reduction'] = (
            enforcement_data['violation_count'] * 0.3
        )
        
        # Add risk score
        enforcement_data['risk_score'] = enforcement_data['severity_score']
        enforcement_data['risk_category'] = enforcement_data['risk_category']
        enforcement_data['violation_frequency'] = enforcement_data['violation_count']
        
        # Sort by priority
        enforcement_data = enforcement_data.sort_values(
            'intervention_impact_normalized', ascending=False
        )
        
        elapsed_time = time.time() - start_time
        print(f"Enforcement plan generated in {elapsed_time:.2f} seconds")
        
        self.enforcement_plan = enforcement_data
        return enforcement_data
    
    def _calculate_officer_allocation(self, data, total_officers):
        """Calculate optimal officer allocation"""
        # Allocate based on impact score
        total_impact = data['intervention_impact_normalized'].sum()
        
        if total_impact == 0:
            return np.zeros(len(data))
        
        # Minimum 1 officer for critical/high priority locations
        min_officers = (data['priority_level'].isin(['Critical', 'High'])).astype(int)
        
        # Remaining officers based on impact
        remaining_officers = total_officers - min_officers.sum()
        if remaining_officers < 0:
            remaining_officers = 0
        
        # Proportional allocation
        proportional = (data['intervention_impact_normalized'] / total_impact * remaining_officers).round()
        
        return (min_officers + proportional).astype(int)
    
    def _generate_patrol_schedule(self, row, shift_hours):
        """Generate patrol schedule for a location"""
        # Get peak hours from data
        df = self.data_processor.get_geographic_data()
        location_col = get_location_column(df)
        location_data = df[df['location_key'] == row['location_key']]
        
        if len(location_data) == 0:
            return "Standard patrol: 9 AM - 5 PM"
        
        # Find peak violation hours
        hour_counts = location_data['hour'].value_counts()
        if len(hour_counts) > 0:
            peak_hour = hour_counts.idxmax()
            start_hour = max(0, peak_hour - 2)
            end_hour = min(24, peak_hour + 3)
            return f"Peak patrol: {start_hour}:00 - {end_hour}:00"
        
        return "Standard patrol: 9 AM - 5 PM"
    
    def _generate_towing_recommendation(self, row):
        """Generate towing recommendation based on violation patterns"""
        df = self.data_processor.get_geographic_data()
        location_col = get_location_column(df)
        location_data = df[df['location_key'] == row['location_key']]
        
        if len(location_data) == 0:
            return "No towing required"
        
        # Check for repeat violations
        vehicle_counts = location_data['vehicle_number'].value_counts()
        repeat_offenders = (vehicle_counts > 1).sum()
        
        # Check for severe violations
        severe_violations = location_data['primary_violation'].isin([
            'PARKING IN A MAIN ROAD',
            'DOUBLE PARKING',
            'PARKING NEAR BUSTOP/SCHOOL/HOSPITAL ETC'
        ]).sum()
        
        if repeat_offenders > 5 and severe_violations > 3:
            return "High priority towing - deploy tow truck immediately"
        elif repeat_offenders > 3 or severe_violations > 2:
            return "Medium priority towing - schedule tow truck"
        elif repeat_offenders > 1:
            return "Low priority towing - monitor for repeat offenders"
        else:
            return "No towing required at this time"
    
    def get_deployment_recommendations(self, top_n=20):
        """Get top deployment recommendations"""
        if self.enforcement_plan is None:
            self.generate_enforcement_plan()
        
        top_locations = self.enforcement_plan.head(top_n)
        
        recommendations = []
        for idx, row in top_locations.iterrows():
            rec = {
                'rank': idx + 1,
                'location': row['representative_location'],
                'police_station': row['police_station'],
                'priority_level': row['priority_level'],
                'officers_recommended': int(row['officers_recommended']),
                'expected_reduction': round(row['expected_reduction'], 1),
                'patrol_schedule': row['patrol_schedule'],
                'towing_recommendation': row['towing_recommendation'],
                'current_violations': int(row['violation_count']),
                'risk_category': row['risk_category']
            }
            recommendations.append(rec)
        
        return pd.DataFrame(recommendations)
    
    def get_enforcement_priority_ranking(self):
        """Get complete priority ranking for enforcement"""
        if self.enforcement_plan is None:
            self.generate_enforcement_plan()
        
        ranking = self.enforcement_plan.copy()
        ranking['rank'] = range(1, len(ranking) + 1)
        
        return ranking[['rank', 'location', 'representative_location', 'police_station',
                       'priority_level', 'officers_recommended', 'intervention_impact_normalized',
                       'expected_reduction', 'patrol_schedule', 'towing_recommendation']]
    
    def get_shift_schedule(self, shift_type='morning'):
        """Generate shift-based enforcement schedule"""
        if self.enforcement_plan is None:
            self.generate_enforcement_plan()
        
        # Define shift hours
        shifts = {
            'morning': (6, 14),
            'afternoon': (14, 22),
            'night': (22, 6)
        }
        
        start_hour, end_hour = shifts.get(shift_type, (6, 14))
        
        # Get data for this shift
        df = self.data_processor.get_geographic_data()
        shift_data = df[df['hour'].between(start_hour, end_hour) if start_hour < end_hour else True]
        
        # Aggregate by location
        shift_hotspots = shift_data.groupby('location_key').size().reset_index(name='shift_violations')
        
        # Merge with enforcement plan
        shift_schedule = self.enforcement_plan.merge(
            shift_hotspots, on='location', how='left'
        ).fillna(0)
        
        # Calculate shift-specific priority
        shift_schedule['shift_priority'] = (
            shift_schedule['shift_violations'] * 0.6 +
            shift_schedule['intervention_impact_normalized'] * 0.4
        )
        
        shift_schedule = shift_schedule.sort_values('shift_priority', ascending=False)
        
        return shift_schedule.head(20)
    
    def calculate_roi(self, officer_cost_per_hour=500):
        """Calculate ROI of enforcement deployment"""
        if self.enforcement_plan is None:
            self.generate_enforcement_plan()
        
        # Total officers
        total_officers = self.enforcement_plan['officers_recommended'].sum()
        
        # Total cost (assuming 8-hour shift)
        total_cost = total_officers * officer_cost_per_hour * 8
        
        # Expected violations prevented
        total_reduction = self.enforcement_plan['expected_reduction'].sum()
        
        # Assume each prevented violation saves 2000 in congestion costs
        savings_per_violation = 2000
        total_savings = total_reduction * savings_per_violation
        
        # ROI
        roi = ((total_savings - total_cost) / total_cost) * 100 if total_cost > 0 else 0
        
        return {
            'total_officers': int(total_officers),
            'total_cost': total_cost,
            'expected_violations_prevented': round(total_reduction, 1),
            'total_savings': total_savings,
            'roi_percentage': round(roi, 2),
            'cost_per_violation_prevented': round(total_cost / total_reduction, 2) if total_reduction > 0 else 0
        }
    
    def get_weekly_enforcement_calendar(self):
        """Generate weekly enforcement calendar"""
        if self.enforcement_plan is None:
            self.generate_enforcement_plan()
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        calendar = {}
        
        df = self.data_processor.get_geographic_data()
        df['day_name'] = df['created_datetime'].dt.day_name()
        
        for day in days:
            day_data = df[df['day_name'] == day]
            day_hotspots = day_data.groupby('location_key').size().reset_index(name='day_violations')
            
            day_schedule = self.enforcement_plan.merge(
                day_hotspots, on='location', how='left'
            ).fillna(0)
            
            day_schedule = day_schedule.sort_values('day_violations', ascending=False)
            calendar[day] = day_schedule.head(10)
        
        return calendar
