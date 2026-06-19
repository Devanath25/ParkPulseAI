"""
Shared Data Loader
Single cached loader for the entire application
"""

import pandas as pd
import streamlit as st
import os

@st.cache_resource
def load_shared_data():
    """Load and cache the dataset once for all modules"""
    # Try to use full dataset if available, otherwise use sample dataset
    full_data_path = "data/jan to may police violation_anonymized791b166.csv"
    sample_data_path = "data/sample_dataset.csv"
    
    if os.path.exists(full_data_path):
        data_path = full_data_path
    else:
        data_path = sample_data_path
    
    return pd.read_csv(data_path)

def get_location_column(df):
    """Get the location column name dynamically"""
    if "location" in df.columns:
        return "location"
    else:
        return next((col for col in df.columns if "location" in col.lower()), "location")
