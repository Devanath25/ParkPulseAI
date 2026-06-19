"""
Executive Dashboard Page
Main dashboard showing key metrics and trends
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add modules to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_processor import DataProcessor
from modules.hotspot_intelligence import HotspotIntelligence
from modules.congestion_risk import CongestionRiskEngine
from modules.insights_analyzer import InsightsAnalyzer


def show_dashboard():
    """Display the executive dashboard"""
    
    # Page config
    st.set_page_config(
        page_title="ParkPulse AI - Executive Dashboard",
        page_icon="🚗",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            margin: 0.5rem;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
        }
        .metric-label {
            font-size: 1rem;
            opacity: 0.9;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize data processor
    @st.cache_resource
    def initialize_data():
        processor = DataProcessor()
        processor.load_data()
        processor.clean_data()
        return processor
    
    @st.cache_data
    def get_filtered_data(_processor, _filters):
        filtered = _processor.filter_data(_filters) if _filters else _processor.processed_data
        # Sample only 1000 rows for demo mode
        if len(filtered) > 1000:
            filtered = filtered.sample(n=1000, random_state=42)
        return filtered
    
    processor = initialize_data()
    
    # Header
    st.markdown('<h1 class="main-header">🚗 ParkPulse AI Executive Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Summary statistics
    stats = processor.get_summary_stats()
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Violations",
            value=f"{stats['total_violations']:,}",
            delta="All Time"
        )
    
    with col2:
        st.metric(
            label="Police Stations",
            value=stats['police_stations'],
            delta="Active"
        )
    
    with col3:
        st.metric(
            label="Vehicle Types",
            value=stats['vehicle_types'],
            delta="Tracked"
        )
    
    with col4:
        st.metric(
            label="Unique Locations",
            value=f"{stats['unique_locations']:,}",
            delta="Hotspots"
        )
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        police_stations = ['All'] + sorted(processor.processed_data['police_station'].unique().tolist())
        selected_station = st.selectbox("Police Station", police_stations)
    
    with col2:
        vehicle_types = ['All'] + sorted(processor.processed_data['vehicle_type'].unique().tolist())
        selected_vehicle = st.selectbox("Vehicle Type", vehicle_types)
    
    with col3:
        violation_types = ['All'] + sorted(processor.processed_data['primary_violation'].dropna().unique().tolist())
        selected_violation = st.selectbox("Violation Type", violation_types)
    
    with col4:
        validation_statuses = ['All'] + sorted(processor.processed_data['validation_status'].dropna().unique().tolist())
        selected_status = st.selectbox("Validation Status", validation_statuses)
    
    # Apply filters
    filters = {}
    if selected_station != 'All':
        filters['police_station'] = [selected_station]
    if selected_vehicle != 'All':
        filters['vehicle_type'] = [selected_vehicle]
    if selected_violation != 'All':
        filters['violation_type'] = [selected_violation]
    if selected_status != 'All':
        filters['validation_status'] = [selected_status]
    
    filtered_data = get_filtered_data(processor, filters)
    
    # Time series charts
    st.subheader("📈 Violation Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly trend
        monthly_data = filtered_data.groupby('month').size().reset_index(name='count')
        month_names = {11: 'Nov', 12: 'Dec', 1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr'}
        monthly_data['month_name'] = monthly_data['month'].map(month_names)
        
        fig_monthly = px.line(
            monthly_data,
            x='month_name',
            y='count',
            title='Monthly Violation Trend',
            markers=True,
            line_shape='spline'
        )
        fig_monthly.update_layout(
            xaxis_title='Month',
            yaxis_title='Number of Violations',
            height=300
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with col2:
        # Daily trend (last 30 days)
        filtered_data['date'] = pd.to_datetime(filtered_data['created_datetime'], errors="coerce", format="mixed").dt.date
        daily_data = filtered_data.groupby('date').size().reset_index(name='count')
        daily_data = daily_data.sort_values('date').tail(30)
        
        fig_daily = px.line(
            daily_data,
            x='date',
            y='count',
            title='Daily Violation Trend (Last 30 Days)',
            markers=True
        )
        fig_daily.update_layout(
            xaxis_title='Date',
            yaxis_title='Number of Violations',
            height=300
        )
        st.plotly_chart(fig_daily, use_container_width=True)
    
    # Top charts
    st.subheader("🏆 Top Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 police stations
        station_counts = filtered_data['police_station'].value_counts().head(10)
        fig_stations = px.bar(
            x=station_counts.values,
            y=station_counts.index,
            orientation='h',
            title='Top 10 Police Stations by Violations',
            color=station_counts.values,
            color_continuous_scale='Blues'
        )
        fig_stations.update_layout(
            xaxis_title='Number of Violations',
            yaxis_title='Police Station',
            height=400
        )
        st.plotly_chart(fig_stations, use_container_width=True)
    
    with col2:
        # Top 10 locations
        location_counts = filtered_data['location'].value_counts().head(10)
        fig_locations = px.bar(
            x=location_counts.values,
            y=location_counts.index,
            orientation='h',
            title='Top 10 Hotspot Locations',
            color=location_counts.values,
            color_continuous_scale='Reds'
        )
        fig_locations.update_layout(
            xaxis_title='Number of Violations',
            yaxis_title='Location',
            height=400
        )
        st.plotly_chart(fig_locations, use_container_width=True)
    
    # Violation and vehicle type analysis
    st.subheader("📊 Violation & Vehicle Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Violation type distribution
        violation_dist = filtered_data['primary_violation'].value_counts().head(10)
        fig_violations = px.pie(
            values=violation_dist.values,
            names=violation_dist.index,
            title='Top 10 Violation Types',
            hole=0.4
        )
        fig_violations.update_layout(height=400)
        st.plotly_chart(fig_violations, use_container_width=True)
    
    with col2:
        # Vehicle type distribution
        vehicle_dist = filtered_data['vehicle_type'].value_counts().head(10)
        fig_vehicles = px.pie(
            values=vehicle_dist.values,
            names=vehicle_dist.index,
            title='Top 10 Vehicle Types',
            hole=0.4
        )
        fig_vehicles.update_layout(height=400)
        st.plotly_chart(fig_vehicles, use_container_width=True)
    
    # Time-based patterns
    st.subheader("⏰ Time-Based Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly pattern
        hourly_data = filtered_data.groupby('hour').size().reset_index(name='count')
        fig_hourly = px.line(
            hourly_data,
            x='hour',
            y='count',
            title='Hourly Violation Pattern',
            markers=True
        )
        fig_hourly.update_layout(
            xaxis_title='Hour of Day',
            yaxis_title='Number of Violations',
            height=300
        )
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    with col2:
        # Day of week pattern
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_pattern = filtered_data.groupby('day_of_week').size().reset_index(name='count')
        daily_pattern['day_name'] = daily_pattern['day_of_week'].apply(lambda x: day_names[x])
        
        fig_daily_pattern = px.bar(
            daily_pattern,
            x='day_name',
            y='count',
            title='Day of Week Pattern',
            color='count',
            color_continuous_scale='Viridis'
        )
        fig_daily_pattern.update_layout(
            xaxis_title='Day of Week',
            yaxis_title='Number of Violations',
            height=300
        )
        st.plotly_chart(fig_daily_pattern, use_container_width=True)
    
    # Growth indicators
    st.subheader("📈 Growth Indicators")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Calculate week-over-week growth
        filtered_data['week'] = pd.to_datetime(filtered_data['created_datetime'], errors="coerce", format="mixed").dt.isocalendar().week
        weekly_counts = filtered_data.groupby('week').size()
        if len(weekly_counts) > 1:
            growth = ((weekly_counts.iloc[-1] - weekly_counts.iloc[-2]) / weekly_counts.iloc[-2] * 100)
            st.metric(
                "Week-over-Week Growth",
                f"{growth:.1f}%",
                delta=f"{'↑' if growth > 0 else '↓'} {abs(growth):.1f}%"
            )
    
    with col2:
        # Calculate month-over-month growth
        monthly_counts = filtered_data.groupby('month').size()
        if len(monthly_counts) > 1:
            growth = ((monthly_counts.iloc[-1] - monthly_counts.iloc[-2]) / monthly_counts.iloc[-2] * 100)
            st.metric(
                "Month-over-Month Growth",
                f"{growth:.1f}%",
                delta=f"{'↑' if growth > 0 else '↓'} {abs(growth):.1f}%"
            )
    
    with col3:
        # Average daily violations
        date_range = (pd.to_datetime(filtered_data['created_datetime'], errors="coerce", format="mixed").max() - 
                     pd.to_datetime(filtered_data['created_datetime'], errors="coerce", format="mixed").min()).days
        if date_range > 0:
            avg_daily = len(filtered_data) / date_range
            st.metric(
                "Avg Daily Violations",
                f"{avg_daily:.1f}",
                delta="Per Day"
            )
    
    st.markdown("---")
    st.markdown(f"**Data Period:** {stats['date_range']['start'].strftime('%Y-%m-%d')} to {stats['date_range']['end'].strftime('%Y-%m-%d')}")
    st.markdown(f"**Total Records Displayed:** {len(filtered_data):,}")


if __name__ == "__main__":
    show_dashboard()
