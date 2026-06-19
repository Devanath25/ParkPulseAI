"""
Congestion Risk Engine Page
Risk scoring and congestion analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_processor import DataProcessor
from modules.congestion_risk import CongestionRiskEngine


def show_congestion():
    """Display congestion risk engine page"""
    
    st.set_page_config(
        page_title="ParkPulse AI - Congestion Risk Engine",
        page_icon="⚠️",
        layout="wide"
    )
    
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #f39c12;
            text-align: center;
            margin-bottom: 2rem;
        }
        .risk-critical {
            background-color: #ffebee;
            padding: 1rem;
            border-radius: 5px;
            border-left: 5px solid #f44336;
        }
        .risk-high {
            background-color: #fff3e0;
            padding: 1rem;
            border-radius: 5px;
            border-left: 5px solid #ff9800;
        }
        .risk-medium {
            background-color: #e8f5e9;
            padding: 1rem;
            border-radius: 5px;
            border-left: 5px solid #4caf50;
        }
        .risk-low {
            background-color: #e3f2fd;
            padding: 1rem;
            border-radius: 5px;
            border-left: 5px solid #2196f3;
        }
        </style>
    """, unsafe_allow_html=True)
    
    @st.cache_resource
    def initialize_modules():
        processor = DataProcessor()
        processor.load_data()
        processor.clean_data()
        
        risk_engine = CongestionRiskEngine(processor)
        return processor, risk_engine
    
    @st.cache_data
    def get_risk_scores(_risk_engine):
        return _risk_engine.calculate_risk_score()
    
    processor, risk_engine = initialize_modules()
    
    st.markdown('<h1 class="main-header">⚠️ Congestion Risk Engine</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Calculate risk scores
    risk_scores = get_risk_scores(risk_engine)
    
    # Risk distribution metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        critical_count = len(risk_scores[risk_scores['risk_category'] == 'Critical'])
        st.metric("Critical Risk", critical_count, delta="Immediate Action")
    
    with col2:
        high_count = len(risk_scores[risk_scores['risk_category'] == 'High'])
        st.metric("High Risk", high_count, delta="Priority")
    
    with col3:
        medium_count = len(risk_scores[risk_scores['risk_category'] == 'Medium'])
        st.metric("Medium Risk", medium_count)
    
    with col4:
        low_count = len(risk_scores[risk_scores['risk_category'] == 'Low'])
        st.metric("Low Risk", low_count)
    
    st.markdown("---")
    
    # Risk distribution chart
    st.subheader("📊 Risk Category Distribution")
    
    risk_dist = risk_scores['risk_category'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = px.pie(
            values=risk_dist.values,
            names=risk_dist.index,
            title='Risk Category Distribution',
            hole=0.4,
            color_discrete_map={
                'Critical': '#f44336',
                'High': '#ff9800',
                'Medium': '#4caf50',
                'Low': '#2196f3'
            }
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        fig_bar = px.bar(
            x=risk_dist.index,
            y=risk_dist.values,
            title='Risk Category Counts',
            color=risk_dist.index,
            color_discrete_map={
                'Critical': '#f44336',
                'High': '#ff9800',
                'Medium': '#4caf50',
                'Low': '#2196f3'
            }
        )
        fig_bar.update_layout(
            xaxis_title='Risk Category',
            yaxis_title='Number of Locations',
            height=400
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # High risk locations
    st.subheader("🚨 High & Critical Risk Locations")
    
    high_risk = risk_engine.get_high_risk_locations(threshold='High')
    
    display_cols = ['location', 'violation_count', 'risk_score', 'risk_category', 
                   'violation_frequency', 'risk_explanation']
    display_data = high_risk[display_cols].copy()
    display_data.columns = ['Location', 'Violations', 'Risk Score', 'Risk Category', 
                           'Frequency (per day)', 'Explanation']
    
    st.dataframe(display_data.head(20), use_container_width=True, height=400)
    
    st.markdown("---")
    
    # Risk by police station
    st.subheader("🚔 Risk Analysis by Police Station")
    
    station_risk = risk_engine.get_risk_by_police_station()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_station = px.bar(
            station_risk.head(15),
            x='avg_risk_score',
            y='police_station',
            orientation='h',
            title='Average Risk Score by Police Station',
            color='avg_risk_score',
            color_continuous_scale='Reds'
        )
        fig_station.update_layout(
            xaxis_title='Average Risk Score',
            yaxis_title='Police Station',
            height=500
        )
        st.plotly_chart(fig_station, use_container_width=True)
    
    with col2:
        st.dataframe(station_risk.head(10), use_container_width=True)
    
    st.markdown("---")
    
    # Risk score distribution
    st.subheader("📈 Risk Score Distribution")
    
    fig_hist = px.histogram(
        risk_scores,
        x='risk_score',
        nbins=50,
        title='Risk Score Distribution',
        color='risk_category',
        color_discrete_map={
            'Critical': '#f44336',
            'High': '#ff9800',
            'Medium': '#4caf50',
            'Low': '#2196f3'
        }
    )
    fig_hist.update_layout(
        xaxis_title='Risk Score',
        yaxis_title='Number of Locations',
        height=400
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    
    st.markdown("---")
    
    # Risk factors analysis
    st.subheader("🔍 Risk Factors Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Violation Count Impact**")
        sample_size = min(1000, len(risk_scores))
        fig_count = px.scatter(
            risk_scores.sample(sample_size),
            x='violation_count',
            y='risk_score',
            title='Violation Count vs Risk Score',
            color='risk_category',
            opacity=0.6
        )
        fig_count.update_layout(height=300)
        st.plotly_chart(fig_count, use_container_width=True)
    
    with col2:
        st.write("**Frequency Impact**")
        sample_size = min(1000, len(risk_scores))
        fig_freq = px.scatter(
            risk_scores.sample(sample_size),
            x='violation_frequency',
            y='risk_score',
            title='Frequency vs Risk Score',
            color='risk_category',
            opacity=0.6
        )
        fig_freq.update_layout(height=300)
        st.plotly_chart(fig_freq, use_container_width=True)
    
    with col3:
        st.write("**Peak Hour Impact**")
        sample_size = min(1000, len(risk_scores))
        fig_peak = px.scatter(
            risk_scores.sample(sample_size),
            x='peak_hour_concentration',
            y='risk_score',
            title='Peak Hour vs Risk Score',
            color='risk_category',
            opacity=0.6
        )
        fig_peak.update_layout(height=300)
        st.plotly_chart(fig_peak, use_container_width=True)
    
    st.markdown("---")
    
    # Risk explanations
    st.subheader("📝 Sample Risk Explanations")
    
    sample_size = min(5, len(risk_scores))
    sample_locations = risk_scores.sample(sample_size)
    
    for idx, row in sample_locations.iterrows():
        risk_class = f"risk-{row['risk_category'].lower()}"
        st.markdown(f"""
        <div class="{risk_class}">
            <strong>Location:</strong> {row['location']}<br>
            <strong>Risk Category:</strong> {row['risk_category']} (Score: {row['risk_score']:.1f})<br>
            <strong>Explanation:</strong> {row['risk_explanation']}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**Risk Scoring Methodology:**")
    st.markdown("- **Violation Count (30%)**: Total number of violations at location")
    st.markdown("- **Violation Frequency (25%)**: Violations per day")
    st.markdown("- **Peak Hour Concentration (15%)**: Maximum violations in a single hour")
    st.markdown("- **Vehicle Diversity (10%)**: Number of different vehicle types")
    st.markdown("- **Recency Score (10%)**: How recent the violations were")
    st.markdown("- **Junction Factor (10%)**: Bonus if location is at a junction")


if __name__ == "__main__":
    show_congestion()
