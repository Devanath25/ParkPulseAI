"""
Hotspot Intelligence Page
Interactive maps and hotspot analysis
"""

import streamlit as st
import pandas as pd
import folium
from streamlit.components.v1 import html
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_processor import DataProcessor
from modules.hotspot_intelligence import HotspotIntelligence


def show_hotspots():
    """Display hotspot intelligence page"""
    
    st.set_page_config(
        page_title="ParkPulse AI - Hotspot Intelligence",
        page_icon="🗺️",
        layout="wide"
    )
    
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #e74c3c;
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
        
        hotspot_intel = HotspotIntelligence(processor)
        return processor, hotspot_intel
    
    processor, hotspot_intel = initialize_modules()
    
    st.markdown('<h1 class="main-header">🗺️ Hotspot Intelligence Module</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar controls
    st.sidebar.header("Map Controls")
    
    top_n = st.sidebar.slider("Top Hotspots to Display", 10, 100, 20, 5)
    
    # Identify hotspots with caching
    @st.cache_data
    def get_hotspots():
        return hotspot_intel.identify_hotspots()
    
    hotspots = get_hotspots()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Hotspots", len(hotspots))
    
    with col2:
        critical = len(hotspots[hotspots['risk_category'] == 'Critical'])
        st.metric("Critical Hotspots", critical, delta="High Priority")
    
    with col3:
        high = len(hotspots[hotspots['risk_category'] == 'High'])
        st.metric("High Risk Hotspots", high)
    
    with col4:
        avg_severity = hotspots['severity_score'].mean()
        st.metric("Avg Severity Score", f"{avg_severity:.1f}")
    
    st.markdown("---")
    
    # Map tabs
    tab1, tab2 = st.tabs(["🔥 Heatmap", "📍 Hotspot Map"])
    
    with tab1:
        st.subheader("Violation Heatmap")
        
        @st.cache_data
        def create_heatmap_cached():
            return hotspot_intel.create_heatmap()
        
        heatmap = create_heatmap_cached()
        html(heatmap._repr_html_(), height=600)
        
        st.info("🔥 Darker areas indicate higher violation density")
    
    with tab2:
        st.subheader(f"Top {top_n} Hotspots Map")
        
        @st.cache_data
        def create_hotspot_map_cached(_top_n):
            return hotspot_intel.create_hotspot_map(top_n=_top_n)
        
        hotspot_map = create_hotspot_map_cached(top_n)
        html(hotspot_map._repr_html_(), height=600)
        
        st.info("📍 Click on markers to see detailed information about each hotspot")
    
    st.markdown("---")
    
    # Top hotspots table
    st.subheader(f"🏆 Top {top_n} Hotspots Ranking")
    
    @st.cache_data
    def get_top_hotspots_cached(_top_n):
        return hotspot_intel.get_top_hotspots(_top_n)
    
    top_hotspots = get_top_hotspots_cached(top_n)
    
    display_columns = ['violation_count', 'severity_score', 'risk_category', 
                      'police_station', 'common_violation', 'common_vehicle']
    display_data = top_hotspots[display_columns].copy()
    display_data.columns = ['Violations', 'Severity Score', 'Risk Category', 
                           'Police Station', 'Common Violation', 'Common Vehicle']
    
    # Add color coding for risk
    def color_risk(val):
        if val == 'Critical':
            return 'background-color: #ffebee'
        elif val == 'High':
            return 'background-color: #fff3e0'
        elif val == 'Medium':
            return 'background-color: #e8f5e9'
        else:
            return 'background-color: #e3f2fd'
    
    styled_table = display_data.style.applymap(color_risk, subset=['Risk Category'])
    st.dataframe(styled_table, use_container_width=True)
    
    # Police station hotspots
    st.subheader("🚔 Police Station Hotspot Analysis")
    
    @st.cache_data
    def get_station_hotspots_cached():
        return hotspot_intel.get_police_station_hotspots()
    
    station_hotspots = get_station_hotspots_cached()
    st.dataframe(station_hotspots.head(10), use_container_width=True)
    
    # Risk distribution
    st.subheader("📊 Risk Category Distribution")
    
    risk_dist = hotspots['risk_category'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.bar_chart(risk_dist)
    
    with col2:
        st.write(risk_dist)
    
    st.markdown("---")
    st.markdown("**Analysis Summary:**")
    st.markdown(f"- Identified {len(hotspots)} distinct hotspot locations")
    st.markdown(f"- {critical} locations classified as Critical risk requiring immediate attention")
    st.markdown(f"- {high} locations classified as High risk requiring priority enforcement")


if __name__ == "__main__":
    show_hotspots()
