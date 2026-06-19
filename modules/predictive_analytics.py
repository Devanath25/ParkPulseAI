"""
Predictive Analytics Module
Machine learning models for predicting hotspots and congestion
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, mean_squared_error, r2_score
import joblib
import os
from .shared_data import get_location_column


class PredictiveAnalytics:
    """Train and use ML models for parking violation prediction"""
    
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.classification_model = None
        self.regression_model = None
        self.feature_importance = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
    def prepare_features(self, df=None):
        """Prepare features for ML models"""
        if df is None:
            df = self.data_processor.get_geographic_data()
        
        # Create feature set
        features = pd.DataFrame()
        
        # Temporal features
        features['hour'] = df['hour']
        features['day_of_week'] = df['day_of_week']
        features['month'] = df['month']
        features['is_weekend'] = df['is_weekend'].astype(int)
        
        # Location features
        features['latitude'] = df['latitude']
        features['longitude'] = df['longitude']
        
        # Encode categorical features
        if 'police_station' in df.columns:
            if 'police_station' not in self.label_encoders:
                self.label_encoders['police_station'] = LabelEncoder()
                features['police_station_encoded'] = self.label_encoders['police_station'].fit_transform(
                    df['police_station'].fillna('Unknown')
                )
            else:
                features['police_station_encoded'] = self.label_encoders['police_station'].transform(
                    df['police_station'].fillna('Unknown')
                )
        
        if 'vehicle_type' in df.columns:
            if 'vehicle_type' not in self.label_encoders:
                self.label_encoders['vehicle_type'] = LabelEncoder()
                features['vehicle_type_encoded'] = self.label_encoders['vehicle_type'].fit_transform(
                    df['vehicle_type'].fillna('Unknown')
                )
            else:
                features['vehicle_type_encoded'] = self.label_encoders['vehicle_type'].transform(
                    df['vehicle_type'].fillna('Unknown')
                )
        
        if 'primary_violation' in df.columns:
            if 'primary_violation' not in self.label_encoders:
                self.label_encoders['primary_violation'] = LabelEncoder()
                features['violation_type_encoded'] = self.label_encoders['primary_violation'].fit_transform(
                    df['primary_violation'].fillna('Unknown')
                )
            else:
                features['violation_type_encoded'] = self.label_encoders['primary_violation'].transform(
                    df['primary_violation'].fillna('Unknown')
                )
        
        # Junction feature
        if 'junction_name' in df.columns:
            features['is_junction'] = df['junction_name'].apply(
                lambda x: 1 if x and 'No Junction' not in str(x) else 0
            )
        
        # Validation status
        if 'validation_status' in df.columns:
            features['is_approved'] = (df['validation_status'] == 'approved').astype(int)
        
        return features
    
    def train_hotspot_classifier(self):
        """Train classifier to predict if location will become hotspot for demo mode"""
        df = self.data_processor.get_geographic_data()
        
        # Sample only 1000 rows for demo mode
        if len(df) > 1000:
            df = df.sample(n=1000, random_state=42)
        
        # Get location column dynamically
        location_col = get_location_column(df)
        
        # Aggregate by location to get hotspot labels
        location_counts = df.groupby('location_key').size().reset_index(name='violation_count')
        threshold = location_counts['violation_count'].quantile(0.75)
        location_counts['is_hotspot'] = (location_counts['violation_count'] >= threshold).astype(int)
        
        # Merge back to original data
        df = df.merge(location_counts[['location_key', 'is_hotspot']], on='location_key', how='left')
        
        # Prepare features
        features = self.prepare_features(df)
        
        # Split data
        X = features
        y = df['is_hotspot']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.classification_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        self.classification_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.classification_model.predict(X_test_scaled)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Feature importance
        self.feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.classification_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return {
            'model': self.classification_model,
            'report': report,
            'feature_importance': self.feature_importance,
            'accuracy': report['accuracy']
        }
    
    def train_violation_regressor(self):
        """Train regressor to predict number of violations"""
        df = self.data_processor.get_geographic_data()
        
        # Get location column dynamically
        location_col = get_location_column(df)
        
        # Aggregate by location and time
        df['date'] = df['created_datetime'].dt.date
        location_time_counts = df.groupby(['location_key', 'date']).size().reset_index(name='daily_violations')
        
        # Merge back to get features
        df = df.merge(location_time_counts, on=['location_key', 'date'], how='left')
        
        # Prepare features
        features = self.prepare_features(df)
        
        # Remove duplicates
        features = features.drop_duplicates()
        y = location_time_counts['daily_violations']
        
        # Align
        common_index = features.index.intersection(y.index)
        X = features.loc[common_index]
        y = y.loc[common_index]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.regression_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.regression_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.regression_model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return {
            'model': self.regression_model,
            'mse': mse,
            'r2_score': r2,
            'predictions': y_pred[:10],
            'actual': y_test[:10].values
        }
    
    def predict_hotspot_probability(self, location_data):
        """Predict probability of location becoming hotspot"""
        if self.classification_model is None:
            self.train_hotspot_classifier()
        
        features = self.prepare_features(location_data)
        features_scaled = self.scaler.transform(features)
        
        probabilities = self.classification_model.predict_proba(features_scaled)
        
        # Safe logic to handle different probability shapes
        if probabilities.shape[1] == 2:
            return probabilities[:, 1]
        else:
            return probabilities[:, 0]
    
    def predict_future_violations(self, location_data, days=7):
        """Predict future violations for locations"""
        if self.regression_model is None:
            self.train_violation_regressor()
        
        features = self.prepare_features(location_data)
        features_scaled = self.scaler.transform(features)
        
        predictions = self.regression_model.predict(features_scaled)
        
        # Scale by days
        predictions = predictions * days
        
        return predictions
    
    def get_feature_importance(self):
        """Get feature importance from trained models"""
        if self.feature_importance is None:
            if self.classification_model is not None:
                feature_count = len(self.feature_columns) if hasattr(self, 'feature_columns') else 0
                if feature_count > 0:
                    self.feature_importance = pd.DataFrame({
                        'feature': self.feature_columns,
                        'importance': self.classification_model.feature_importances_
                    }).sort_values('importance', ascending=False)
                else:
                    self.feature_importance = pd.DataFrame({'feature': [], 'importance': []})
        
        return self.feature_importance
    
    def get_model_performance(self):
        """Get performance metrics for all models"""
        performance = {}
        
        feature_count = len(self.feature_columns) if hasattr(self, 'feature_columns') else 0
        
        if self.classification_model is not None:
            performance['classification'] = {
                'model_type': 'Random Forest Classifier',
                'feature_count': feature_count,
                'estimators': self.classification_model.n_estimators
            }
        
        if self.regression_model is not None:
            performance['regression'] = {
                'model_type': 'Random Forest Regressor',
                'feature_count': feature_count,
                'estimators': self.regression_model.n_estimators
            }
        
        return performance
    
    def save_models(self, path='models'):
        """Save trained models to disk"""
        os.makedirs(path, exist_ok=True)
        
        if self.classification_model is not None:
            joblib.dump(self.classification_model, f'{path}/classifier.pkl')
        
        if self.regression_model is not None:
            joblib.dump(self.regression_model, f'{path}/regressor.pkl')
        
        joblib.dump(self.scaler, f'{path}/scaler.pkl')
        joblib.dump(self.label_encoders, f'{path}/encoders.pkl')
    
    def load_models(self, path='models'):
        """Load trained models from disk"""
        if os.path.exists(f'{path}/classifier.pkl'):
            self.classification_model = joblib.load(f'{path}/classifier.pkl')
        
        if os.path.exists(f'{path}/regressor.pkl'):
            self.regression_model = joblib.load(f'{path}/regressor.pkl')
        
        if os.path.exists(f'{path}/scaler.pkl'):
            self.scaler = joblib.load(f'{path}/scaler.pkl')
        
        if os.path.exists(f'{path}/encoders.pkl'):
            self.label_encoders = joblib.load(f'{path}/encoders.pkl')
