"""
ParkPulse AI - Main Application
Parking Intelligence & Congestion Prevention Platform
Flipkart Gridlock Hackathon 2.0 – Round 2
"""

import streamlit as st
import sys
import os

# Configure page
st.set_page_config(
    page_title="ParkPulse AI",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point"""
    
    # Sidebar navigation
    st.sidebar.title("🚗 ParkPulse AI")
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigate to:",
        [
            "📊 Executive Dashboard",
            "🗺️ Hotspot Intelligence",
            "⚠️ Congestion Risk Engine",
            "🤖 Predictive Analytics",
            "👮 Smart Enforcement Planner",
            "💡 Insights Module",
            "📄 Reports"
        ]
    )
    
    st.sidebar.markdown("---")
    
    # About section
    st.sidebar.markdown("### About")
    st.sidebar.markdown("""
    **ParkPulse AI** is an intelligent parking violation analysis platform designed for traffic authorities.
    
    **Hackathon:** Flipkart Gridlock 2.0
    
    **Problem:** Poor Visibility on Parking-Induced Congestion
    """)
    
    # Page routing
    if page == "📊 Executive Dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard()
    
    elif page == "🗺️ Hotspot Intelligence":
        from pages.hotspots import show_hotspots
        show_hotspots()
    
    elif page == "⚠️ Congestion Risk Engine":
        from pages.congestion import show_congestion
        show_congestion()
    
    elif page == "🤖 Predictive Analytics":
        from pages.predictions import show_predictions
        show_predictions()
    
    elif page == "👮 Smart Enforcement Planner":
        from pages.enforcement import show_enforcement
        show_enforcement()
    
    elif page == "💡 Insights Module":
        from pages.insights import show_insights
        show_insights()
    
    elif page == "📄 Reports":
        from pages.reports import show_reports
        show_reports()


if __name__ == "__main__":
    main()
