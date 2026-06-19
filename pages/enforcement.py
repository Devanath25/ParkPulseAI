"""
Smart Enforcement Planner Page
Flagship feature: Officer deployment and enforcement recommendations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_processor import DataProcessor
from modules.hotspot_intelligence import HotspotIntelligence
from modules.congestion_risk import CongestionRiskEngine
from modules.enforcement_planner import EnforcementPlanner


def show_enforcement():
    """Display smart enforcement planner page"""
    
    st.set_page_config(
        page_title="ParkPulse AI - Smart Enforcement Planner",
        page_icon="👮",
        layout="wide"
    )
    
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #27ae60;
            text-align: center;
            margin-bottom: 2rem;
        }
        .priority-critical {
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
        }
        .priority-high {
            background: linear-gradient(135deg, #f39c12 0%, #d68910 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
        }
        .priority-medium {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
        }
        .priority-low {
            background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    @st.cache_resource
    def initialize_modules():
        processor = DataProcessor()
        processor.load_data()
        processor.clean_data()
        
        hotspot_intel = HotspotIntelligence(processor)
        risk_engine = CongestionRiskEngine(processor)
        enforcement_planner = EnforcementPlanner(processor, hotspot_intel, risk_engine)
        
        return processor, hotspot_intel, risk_engine, enforcement_planner
    
    @st.cache_data
    def get_enforcement_plan(_enforcement_planner, _num_officers, _shift_hours):
        return _enforcement_planner.generate_enforcement_plan(num_officers=_num_officers, shift_hours=_shift_hours)
    
    processor, hotspot_intel, risk_engine, enforcement_planner = initialize_modules()
    
    st.markdown('<h1 class="main-header">👮 Smart Enforcement Planner</h1>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🚀 Flagship Feature: AI-Powered Enforcement Optimization")
    st.markdown("This module generates intelligent recommendations for officer deployment, patrol scheduling, and towing operations based on real-time violation patterns and predicted congestion risk.")
    
    st.markdown("---")
    
    # Sidebar controls
    st.sidebar.header("Enforcement Parameters")
    
    num_officers = st.sidebar.slider("Total Officers Available", 10, 200, 50, 5)
    shift_hours = st.sidebar.slider("Shift Duration (Hours)", 4, 12, 8, 1)
    officer_cost = st.sidebar.number_input("Cost per Officer per Hour (₹)", 100, 2000, 500, 50)
    
    # Generate enforcement plan
    with st.spinner("Generating optimal enforcement plan..."):
        enforcement_plan = get_enforcement_plan(enforcement_planner, num_officers, shift_hours)
    
    # ROI Analysis
    st.subheader("💰 ROI Analysis")
    
    roi = enforcement_planner.calculate_roi(officer_cost_per_hour=officer_cost)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Officers", roi['total_officers'])
    
    with col2:
        st.metric("Total Cost", f"₹{roi['total_cost']:,.0f}")
    
    with col3:
        st.metric("Expected Violations Prevented", f"{roi['expected_violations_prevented']:.0f}")
    
    with col4:
        st.metric("ROI", f"{roi['roi_percentage']:.1f}%", delta=f"₹{roi['total_savings']:,.0f} savings")
    
    st.markdown("---")
    
    # Deployment recommendations
    st.subheader("📍 Top Deployment Recommendations")
    
    recommendations = enforcement_planner.get_deployment_recommendations(top_n=20)
    
    for idx, row in recommendations.iterrows():
        priority_class = f"priority-{row['priority_level'].lower()}"
        
        st.markdown(f"""
        <div class="{priority_class}">
            <h3>#{row['rank']} {row['location']}</h3>
            <p><strong>Police Station:</strong> {row['police_station']}</p>
            <p><strong>Priority:</strong> {row['priority_level']} | <strong>Officers:</strong> {row['officers_recommended']}</p>
            <p><strong>Expected Reduction:</strong> {row['expected_reduction']} violations</p>
            <p><strong>Patrol Schedule:</strong> {row['patrol_schedule']}</p>
            <p><strong>Towing:</strong> {row['towing_recommendation']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Priority distribution
    st.subheader("📊 Priority Distribution")
    
    priority_dist = enforcement_plan['priority_level'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_prio = px.pie(
            values=priority_dist.values,
            names=priority_dist.index,
            title='Priority Level Distribution',
            hole=0.4,
            color_discrete_map={
                'Critical': '#e74c3c',
                'High': '#f39c12',
                'Medium': '#3498db',
                'Low': '#95a5a6'
            }
        )
        fig_prio.update_layout(height=400)
        st.plotly_chart(fig_prio, use_container_width=True)
    
    with col2:
        fig_bar = px.bar(
            x=priority_dist.index,
            y=priority_dist.values,
            title='Priority Level Counts',
            color=priority_dist.index,
            color_discrete_map={
                'Critical': '#e74c3c',
                'High': '#f39c12',
                'Medium': '#3498db',
                'Low': '#95a5a6'
            }
        )
        fig_bar.update_layout(
            xaxis_title='Priority Level',
            yaxis_title='Number of Locations',
            height=400
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # Shift schedules
    st.subheader("⏰ Shift-Based Enforcement Schedules")
    
    shift_type = st.selectbox("Select Shift", ["Morning (6AM-2PM)", "Afternoon (2PM-10PM)", "Night (10PM-6AM)"])
    
    shift_map = {
        "Morning (6AM-2PM)": "morning",
        "Afternoon (2PM-10PM)": "afternoon",
        "Night (10PM-6AM)": "night"
    }
    
    shift_schedule = enforcement_planner.get_shift_schedule(shift_type=shift_map[shift_type])
    
    display_cols = ['representative_location', 'police_station', 'priority_level', 
                   'officers_recommended', 'shift_violations']
    display_data = shift_schedule[display_cols].copy()
    display_data.columns = ['Location', 'Police Station', 'Priority', 'Officers', 'Shift Violations']
    
    st.dataframe(display_data.head(15), use_container_width=True)
    
    st.markdown("---")
    
    # Weekly calendar
    st.subheader("📅 Weekly Enforcement Calendar")
    
    weekly_calendar = enforcement_planner.get_weekly_enforcement_calendar()
    
    selected_day = st.selectbox("Select Day", list(weekly_calendar.keys()))
    
    day_schedule = weekly_calendar[selected_day]
    
    display_cols = ['representative_location', 'police_station', 'priority_level', 
                   'officers_recommended', 'day_violations']
    display_data = day_schedule[display_cols].copy()
    display_data.columns = ['Location', 'Police Station', 'Priority', 'Officers', 'Day Violations']
    
    st.dataframe(display_data.head(10), use_container_width=True)
    
    st.markdown("---")
    
    # Intervention impact
    st.subheader("🎯 Intervention Impact Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_impact = px.scatter(
            enforcement_plan.head(50),
            x='violation_count',
            y='intervention_impact_normalized',
            color='priority_level',
            title='Violation Count vs Intervention Impact',
            color_discrete_map={
                'Critical': '#e74c3c',
                'High': '#f39c12',
                'Medium': '#3498db',
                'Low': '#95a5a6'
            },
            opacity=0.7
        )
        fig_impact.update_layout(
            xaxis_title='Current Violations',
            yaxis_title='Intervention Impact Score',
            height=400
        )
        st.plotly_chart(fig_impact, use_container_width=True)
    
    with col2:
        fig_reduction = px.scatter(
            enforcement_plan.head(50),
            x='officers_recommended',
            y='expected_reduction',
            color='priority_level',
            title='Officers vs Expected Reduction',
            color_discrete_map={
                'Critical': '#e74c3c',
                'High': '#f39c12',
                'Medium': '#3498db',
                'Low': '#95a5a6'
            },
            opacity=0.7
        )
        fig_reduction.update_layout(
            xaxis_title='Officers Recommended',
            yaxis_title='Expected Violation Reduction',
            height=400
        )
        st.plotly_chart(fig_reduction, use_container_width=True)
    
    st.markdown("---")
    
    # Complete ranking
    st.subheader("📋 Complete Enforcement Priority Ranking")
    
    ranking = enforcement_planner.get_enforcement_priority_ranking()
    
    display_cols = ['rank', 'representative_location', 'police_station', 'priority_level',
                   'officers_recommended', 'intervention_impact_normalized', 'expected_reduction']
    display_data = ranking[display_cols].copy()
    display_data.columns = ['Rank', 'Location', 'Police Station', 'Priority',
                           'Officers', 'Impact Score', 'Expected Reduction']
    
    st.dataframe(display_data.head(50), use_container_width=True, height=400)
    
    st.markdown("---")
    st.markdown("**Enforcement Methodology:**")
    st.markdown("- **Intervention Impact Score**: Weighted combination of violation count, severity, risk score, and frequency")
    st.markdown("- **Officer Allocation**: Proportional to impact score with minimum allocation for critical/high priority locations")
    st.markdown("- **Patrol Scheduling**: Based on peak violation hours at each location")
    st.markdown("- **Towing Recommendations**: Based on repeat offenders and violation severity")
    st.markdown("- **ROI Calculation**: Considers officer costs vs. expected congestion cost savings")


if __name__ == "__main__":
    show_enforcement()
