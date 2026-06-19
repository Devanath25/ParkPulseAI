"""
Insights Module Page
Detailed analysis across different dimensions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_processor import DataProcessor
from modules.insights_analyzer import InsightsAnalyzer


def show_insights():
    """Display insights analyzer page"""
    
    st.set_page_config(
        page_title="ParkPulse AI - Insights Module",
        page_icon="💡",
        layout="wide"
    )
    
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #3498db;
            text-align: center;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    @st.cache_resource
    def initialize_modules():
        data_path = "data/jan to may police violation_anonymized791b166.csv"
        processor = DataProcessor(data_path)
        processor.load_data()
        processor.clean_data()
        
        insights = InsightsAnalyzer(processor)
        return processor, insights
    
    @st.cache_data
    def get_area_analysis(_insights):
        return _insights.area_wise_analysis()
    
    @st.cache_data
    def get_station_analysis(_insights):
        return _insights.police_station_analysis()
    
    @st.cache_data
    def get_time_trends(_insights):
        return _insights.time_based_trends()
    
    @st.cache_data
    def get_violation_trends(_insights):
        return _insights.violation_trends()
    
    @st.cache_data
    def get_recurring_hotspots(_insights):
        return _insights.recurring_hotspot_detection()
    
    @st.cache_data
    def get_peak_hours(_insights):
        return _insights.peak_hour_analysis()
    
    @st.cache_data
    def get_vehicle_insights(_insights):
        return _insights.vehicle_type_insights()
    
    processor, insights = initialize_modules()
    
    st.markdown('<h1 class="main-header">💡 Insights Module</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Analysis type selection
    analysis_type = st.sidebar.selectbox(
        "Select Analysis Type",
        ["Area-wise Analysis", "Police Station Analysis", "Time-based Trends", 
         "Violation Trends", "Recurring Hotspots", "Peak Hour Analysis", "Vehicle Type Insights"]
    )
    
    if analysis_type == "Area-wise Analysis":
        st.subheader("📍 Area-wise Analysis")
        
        area_analysis = get_area_analysis(insights)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Top 20 Areas by Violation Count")
            display_cols = ['location', 'violation_count', 'violations_per_day', 
                           'police_station', 'common_violation']
            display_data = area_analysis[display_cols].head(20).copy()
            display_data.columns = ['Location', 'Violations', 'Violations/Day', 
                                   'Police Station', 'Common Violation']
            st.dataframe(display_data, use_container_width=True, height=400)
        
        with col2:
            fig_area = px.scatter(
                area_analysis.head(50),
                x='longitude',
                y='latitude',
                size='violation_count',
                color='violations_per_day',
                title='Geographic Distribution of Violations',
                hover_data=['location'],
                color_continuous_scale='Viridis'
            )
            fig_area.update_layout(
                xaxis_title='Longitude',
                yaxis_title='Latitude',
                height=500
            )
            st.plotly_chart(fig_area, use_container_width=True)
    
    elif analysis_type == "Police Station Analysis":
        st.subheader("🚔 Police Station Analysis")
        
        station_analysis = get_station_analysis(insights)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_station = px.bar(
                station_analysis.head(15),
                x='total_violations',
                y='police_station',
                orientation='h',
                title='Top 15 Police Stations by Violations',
                color='total_violations',
                color_continuous_scale='Blues'
            )
            fig_station.update_layout(
                xaxis_title='Total Violations',
                yaxis_title='Police Station',
                height=500
            )
            st.plotly_chart(fig_station, use_container_width=True)
        
        with col2:
            st.dataframe(station_analysis.head(15), use_container_width=True)
        
        st.markdown("---")
        
        # Approval rate analysis
        fig_approval = px.scatter(
            station_analysis,
            x='total_violations',
            y='approval_rate',
            size='unique_locations',
            hover_data=['police_station'],
            title='Violations vs Approval Rate',
            color='approval_rate',
            color_continuous_scale='RdYlGn'
        )
        fig_approval.update_layout(
            xaxis_title='Total Violations',
            yaxis_title='Approval Rate (%)',
            height=400
        )
        st.plotly_chart(fig_approval, use_container_width=True)
    
    elif analysis_type == "Time-based Trends":
        st.subheader("⏰ Time-based Trends")
        
        time_trends = get_time_trends(insights)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hourly = px.line(
                time_trends['hourly'],
                x='hour',
                y='violations',
                title='Hourly Violation Pattern',
                markers=True,
                line_shape='spline'
            )
            fig_hourly.update_layout(
                xaxis_title='Hour of Day',
                yaxis_title='Number of Violations',
                height=300
            )
            st.plotly_chart(fig_hourly, use_container_width=True)
        
        with col2:
            fig_daily = px.bar(
                time_trends['daily'],
                x='day_name',
                y='violations',
                title='Day of Week Pattern',
                color='violations',
                color_continuous_scale='Blues'
            )
            fig_daily.update_layout(
                xaxis_title='Day of Week',
                yaxis_title='Number of Violations',
                height=300
            )
            st.plotly_chart(fig_daily, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_monthly = px.line(
                time_trends['monthly'],
                x='month_name',
                y='violations',
                title='Monthly Trend',
                markers=True
            )
            fig_monthly.update_layout(
                xaxis_title='Month',
                yaxis_title='Number of Violations',
                height=300
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        with col2:
            fig_weekend = px.bar(
                time_trends['weekend_vs_weekday'],
                x='period',
                y='violations',
                title='Weekend vs Weekday',
                color='period',
                color_discrete_map={'Weekend': '#e74c3c', 'Weekday': '#3498db'}
            )
            fig_weekend.update_layout(
                xaxis_title='Period',
                yaxis_title='Number of Violations',
                height=300
            )
            st.plotly_chart(fig_weekend, use_container_width=True)
    
    elif analysis_type == "Violation Trends":
        st.subheader("📊 Violation Trends")
        
        violation_trends = get_violation_trends(insights)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Violation Type Distribution")
            st.dataframe(violation_trends['distribution'], use_container_width=True)
            
            fig_violation = px.pie(
                violation_trends['distribution'].head(10),
                values='count',
                names='violation_type',
                title='Top 10 Violation Types',
                hole=0.4
            )
            fig_violation.update_layout(height=400)
            st.plotly_chart(fig_violation, use_container_width=True)
        
        with col2:
            st.write("Severe Violations")
            st.dataframe(violation_trends['severe_violations'].head(10), use_container_width=True)
            
            fig_severe = px.bar(
                violation_trends['severe_violations'].head(10),
                x='count',
                y='primary_violation',
                orientation='h',
                title='Severe Violations',
                color='count',
                color_continuous_scale='Reds'
            )
            fig_severe.update_layout(
                xaxis_title='Count',
                yaxis_title='Violation Type',
                height=400
            )
            st.plotly_chart(fig_severe, use_container_width=True)
    
    elif analysis_type == "Recurring Hotspots":
        st.subheader("🔄 Recurring Hotspot Detection")
        
        recurring = get_recurring_hotspots(insights)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Top 20 Recurring Hotspots")
            display_cols = ['location', 'weeks_with_violations', 'total_violations',
                           'avg_weekly_violations', 'recurrence_score', 'police_station']
            display_data = recurring[display_cols].head(20).copy()
            display_data.columns = ['Location', 'Weeks Active', 'Total Violations',
                                   'Avg Weekly', 'Recurrence Score', 'Police Station']
            st.dataframe(display_data, use_container_width=True, height=400)
        
        with col2:
            fig_recur = px.scatter(
                recurring.head(50),
                x='weeks_with_violations',
                y='avg_weekly_violations',
                size='total_violations',
                color='recurrence_score',
                title='Recurring Hotspots Analysis',
                hover_data=['location'],
                color_continuous_scale='Plasma'
            )
            fig_recur.update_layout(
                xaxis_title='Weeks with Violations',
                yaxis_title='Avg Weekly Violations',
                height=500
            )
            st.plotly_chart(fig_recur, use_container_width=True)
    
    elif analysis_type == "Peak Hour Analysis":
        st.subheader("🕐 Peak Hour Analysis")
        
        peak_hours = get_peak_hours(insights)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Top 20 Locations by Peak Hour Violations")
            display_cols = ['location', 'peak_hour', 'peak_hour_violations',
                           'total_violations', 'police_station']
            display_data = peak_hours[display_cols].head(20).copy()
            display_data.columns = ['Location', 'Peak Hour', 'Peak Violations',
                                   'Total Violations', 'Police Station']
            st.dataframe(display_data, use_container_width=True, height=400)
        
        with col2:
            fig_peak = px.scatter(
                peak_hours.head(50),
                x='peak_hour',
                y='peak_hour_violations',
                size='total_violations',
                color='police_station',
                title='Peak Hour Distribution',
                hover_data=['location'],
                opacity=0.7
            )
            fig_peak.update_layout(
                xaxis_title='Peak Hour',
                yaxis_title='Peak Hour Violations',
                height=500
            )
            st.plotly_chart(fig_peak, use_container_width=True)
        
        # Peak hour distribution
        fig_peak_dist = px.histogram(
            peak_hours,
            x='peak_hour',
            nbins=24,
            title='Distribution of Peak Hours Across Locations',
            color_discrete_sequence=['#3498db']
        )
        fig_peak_dist.update_layout(
            xaxis_title='Hour of Day',
            yaxis_title='Number of Locations',
            height=300
        )
        st.plotly_chart(fig_peak_dist, use_container_width=True)
    
    elif analysis_type == "Vehicle Type Insights":
        st.subheader("🚗 Vehicle Type Insights")
        
        vehicle_insights = get_vehicle_insights(insights)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Vehicle Type Distribution")
            st.dataframe(vehicle_insights['distribution'], use_container_width=True)
            
            fig_vehicle = px.pie(
                vehicle_insights['distribution'].head(10),
                values='count',
                names='vehicle_type',
                title='Top 10 Vehicle Types',
                hole=0.4
            )
            fig_vehicle.update_layout(height=400)
            st.plotly_chart(fig_vehicle, use_container_width=True)
        
        with col2:
            st.write("Vehicles at Hotspots")
            st.dataframe(vehicle_insights['at_hotspots'], use_container_width=True)
            
            fig_hotspot_vehicles = px.bar(
                vehicle_insights['at_hotspots'].head(10),
                x='count',
                y='vehicle_type',
                orientation='h',
                title='Vehicle Types at Hotspots',
                color='count',
                color_continuous_scale='Blues'
            )
            fig_hotspot_vehicles.update_layout(
                xaxis_title='Count',
                yaxis_title='Vehicle Type',
                height=400
            )
            st.plotly_chart(fig_hotspot_vehicles, use_container_width=True)
    
    st.markdown("---")
    st.markdown("**Insights Generated From:**")
    st.markdown("- Geographic clustering analysis")
    st.markdown("- Temporal pattern recognition")
    st.markdown("- Cross-dimensional correlation")
    st.markdown("- Statistical trend analysis")


if __name__ == "__main__":
    show_insights()
