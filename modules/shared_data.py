"""
Shared Data Loader
Single cached loader for the entire application
"""

import pandas as pd
import streamlit as st

@st.cache_resource
def load_shared_data():
    """Load and cache the dataset once for all modules"""
    data_path = "data/jan to may police violation_anonymized791b166.csv"
    return pd.read_csv(data_path)

def get_location_column(df):
    """Get the location column name dynamically"""
    if "location" in df.columns:
        return "location"
    else:
        return next((col for col in df.columns if "location" in col.lower()), "location")
