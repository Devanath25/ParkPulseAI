"""
Predictive Analytics Page
ML models for predicting hotspots and violations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_processor import DataProcessor
from modules.predictive_analytics import PredictiveAnalytics


def show_predictions():
    """Display predictive analytics page"""
    
    st.set_page_config(
        page_title="ParkPulse AI - Predictive Analytics",
        page_icon="🤖",
        layout="wide"
    )
    
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #9b59b6;
            text-align: center;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    @st.cache_resource
    def initialize_modules():
        processor = DataProcessor()
        processor.load_data()
        processor.clean_data()
        
        predictor = PredictiveAnalytics(processor)
        return processor, predictor
    
    processor, predictor = initialize_modules()
    
    st.markdown('<h1 class="main-header">🤖 Predictive Analytics Module</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Model selection
    st.sidebar.header("Model Controls")
    
    model_type = st.sidebar.radio(
        "Select Model",
        ["Hotspot Classification", "Violation Prediction", "Both Models"]
    )
    
    # Train models
    st.subheader("🎓 Training Machine Learning Models")
    
    with st.spinner("Training models... This may take a moment..."):
        if model_type in ["Hotspot Classification", "Both Models"]:
            classifier_results = predictor.train_hotspot_classifier()
            st.success("✅ Hotspot Classification Model Trained Successfully!")
        
        if model_type in ["Violation Prediction", "Both Models"]:
            regression_results = predictor.train_violation_regressor()
            st.success("✅ Violation Prediction Model Trained Successfully!")
    
    st.markdown("---")
    
    # Model performance
    st.subheader("📊 Model Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if model_type in ["Hotspot Classification", "Both Models"]:
            st.write("**Hotspot Classification Model**")
            st.metric("Accuracy", f"{classifier_results['accuracy']:.2%}")
            st.write("Classification Report:")
            report_df = pd.DataFrame(classifier_results['report']).transpose()
            st.dataframe(report_df, width='stretch')
    
    with col2:
        if model_type in ["Violation Prediction", "Both Models"]:
            st.write("**Violation Prediction Model**")
            st.metric("R² Score", f"{regression_results['r2_score']:.3f}")
            st.metric("MSE", f"{regression_results['mse']:.2f}")
            st.write("Sample Predictions:")
            pred_df = pd.DataFrame({
                'Predicted': regression_results['predictions'],
                'Actual': regression_results['actual']
            })
            st.dataframe(pred_df, width='stretch')
    
    st.markdown("---")
    
    # Feature importance
    st.subheader("🔍 Feature Importance")
    
    if model_type in ["Hotspot Classification", "Both Models"]:
        feature_importance = predictor.get_feature_importance()
        
        fig_importance = px.bar(
            feature_importance,
            x='importance',
            y='feature',
            orientation='h',
            title='Feature Importance for Hotspot Prediction',
            color='importance',
            color_continuous_scale='Purples'
        )
        fig_importance.update_layout(
            xaxis_title='Importance Score',
            yaxis_title='Feature',
            height=400
        )
        st.plotly_chart(fig_importance, use_container_width=True)
        
        st.dataframe(feature_importance, width='stretch')
    
    st.markdown("---")
    
    # Predictions
    st.subheader("🔮 Make Predictions")
    
    # Get sample data for prediction
    df = processor.get_geographic_data().sample(100)
    
    if model_type in ["Hotspot Classification", "Both Models"]:
        st.write("**Hotspot Probability Predictions**")
        
        hotspot_probs = predictor.predict_hotspot_probability(df)
        
        df_with_probs = df.copy()
        df_with_probs['hotspot_probability'] = hotspot_probs
        df_with_probs = df_with_probs.sort_values('hotspot_probability', ascending=False)
        
        display_cols = ['location', 'hotspot_probability', 'police_station', 'primary_violation']
        display_data = df_with_probs[display_cols].copy()
        display_data.columns = ['Location', 'Hotspot Probability', 'Police Station', 'Violation Type']
        
        st.dataframe(display_data.head(20), use_container_width=True)
        
        # Probability distribution
        fig_prob = px.histogram(
            df_with_probs,
            x='hotspot_probability',
            nbins=20,
            title='Hotspot Probability Distribution',
            color_discrete_sequence=['#9b59b6']
        )
        fig_prob.update_layout(
            xaxis_title='Hotspot Probability',
            yaxis_title='Count',
            height=300
        )
        st.plotly_chart(fig_prob, use_container_width=True)
    
    if model_type in ["Violation Prediction", "Both Models"]:
        st.write("**Future Violation Predictions**")
        
        days_ahead = st.slider("Days to Predict", 1, 30, 7)
        
        future_violations = predictor.predict_future_violations(df, days=days_ahead)
        
        df_with_pred = df.copy()
        df_with_pred['predicted_violations'] = future_violations
        df_with_pred = df_with_pred.sort_values('predicted_violations', ascending=False)
        
        display_cols = ['location', 'predicted_violations', 'police_station']
        display_data = df_with_pred[display_cols].copy()
        display_data.columns = ['Location', f'Predicted Violations ({days_ahead} days)', 'Police Station']
        
        st.dataframe(display_data.head(20), use_container_width=True)
        
        # Prediction distribution
        fig_pred = px.histogram(
            df_with_pred,
            x='predicted_violations',
            nbins=20,
            title=f'Predicted Violations Distribution ({days_ahead} days)',
            color_discrete_sequence=['#8e44ad']
        )
        fig_pred.update_layout(
            xaxis_title='Predicted Violations',
            yaxis_title='Count',
            height=300
        )
        st.plotly_chart(fig_pred, use_container_width=True)
    
    st.markdown("---")
    
    # Model details - disabled for demo mode
    # st.subheader("📋 Model Details")
    # 
    # performance = predictor.get_model_performance()
    # 
    # for model_name, details in performance.items():
    #     st.write(f"**{model_name.capitalize()} Model**")
    #     col1, col2, col3 = st.columns(3)
    #     with col1:
    #         st.metric("Type", details['model_type'])
    #     with col2:
    #         st.metric("Features", details['feature_count'])
    #     with col3:
    #         st.metric("Estimators", details['estimators'])
    # 
    # st.markdown("---")
    # st.markdown("**Model Information:**")
    # st.markdown("- **Algorithm**: Random Forest (Ensemble Learning)")
    # st.markdown("- **Training Data**: Historical parking violation records")
    # st.markdown("- **Features Used**: Temporal, geographic, and categorical features")
    # st.markdown("- **Cross-Validation**: 5-fold validation applied")
    # st.markdown("- **Model Persistence**: Models can be saved and loaded for reuse")


if __name__ == "__main__":
    show_predictions()
