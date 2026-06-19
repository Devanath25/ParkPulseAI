# ParkPulse AI - System Architecture

## Overview

ParkPulse AI is a modular, data-driven platform designed to analyze parking violations, identify congestion hotspots, and provide intelligent enforcement recommendations. The architecture follows a layered approach with clear separation of concerns.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                            │
│                    (Streamlit Web App)                            │
├─────────────────────────────────────────────────────────────────┤
│  Dashboard  │  Hotspots  │  Congestion  │  Predictions  │       │
│  Insights   │  Reports   │  Enforcement │  Navigation   │       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Business Logic Layer                          │
│                        (Modules)                                  │
├─────────────────────────────────────────────────────────────────┤
│  DataProcessor  │  HotspotIntelligence  │  CongestionRiskEngine  │
│  PredictiveAnalytics │  EnforcementPlanner │  InsightsAnalyzer   │
│  ReportGenerator                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Data Processing Layer                         │
│                   (Pandas, NumPy, Scikit-learn)                  │
├─────────────────────────────────────────────────────────────────┤
│  Data Cleaning  │  Feature Engineering  │  ML Model Training    │
│  Clustering     │  Risk Scoring         │  Prediction           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Data Storage Layer                           │
│                      (CSV Files)                                  │
├─────────────────────────────────────────────────────────────────┤
│  Parking Violation Dataset (298,450 records)                     │
│  Geographic Coordinates, Temporal Data, Categorical Features     │
└─────────────────────────────────────────────────────────────────┘
```

## Module Explanations

### 1. Data Processor Module
**Purpose:** Data loading, cleaning, and preprocessing

**Responsibilities:**
- Load raw parking violation data from CSV
- Clean and preprocess data
- Handle missing values
- Parse complex data structures (violation types, offence codes)
- Extract temporal features (hour, day, month, weekend)
- Create location identifiers for clustering
- Apply data filters
- Generate summary statistics

**Key Functions:**
- `load_data()` - Load raw dataset
- `clean_data()` - Clean and preprocess
- `get_summary_stats()` - Generate statistics
- `get_time_series_data()` - Aggregate by time periods
- `filter_data()` - Apply filters
- `get_geographic_data()` - Extract geographic data
- `get_hotspot_data()` - Aggregate for hotspot analysis

### 2. Hotspot Intelligence Module
**Purpose:** Identify and analyze parking violation hotspots

**Responsibilities:**
- Perform geographic clustering using DBSCAN
- Calculate hotspot severity scores
- Generate interactive maps (heatmaps, cluster maps)
- Rank hotspots by violation count and severity
- Analyze hotspot distribution by police station
- Calculate violation density

**Key Functions:**
- `identify_hotspots()` - DBSCAN clustering
- `get_top_hotspots()` - Get top N hotspots
- `calculate_density()` - Calculate violation density
- `create_heatmap()` - Generate folium heatmap
- `create_hotspot_map()` - Generate interactive hotspot map
- `create_cluster_map()` - Generate clustered marker map
- `get_hotspot_ranking()` - Get ranked hotspots
- `get_police_station_hotspots()` - Station-wise analysis

### 3. Congestion Risk Engine Module
**Purpose:** Calculate congestion risk scores and categorize locations

**Responsibilities:**
- Calculate comprehensive risk scores
- Assign risk categories (Low, Medium, High, Critical)
- Generate risk explanations
- Analyze risk distribution
- Perform risk analysis by police station
- Analyze risk trends over time
- Predict risk changes

**Risk Scoring Formula:**
```
Risk Score = (Normalized Count × 0.30) + 
             (Normalized Frequency × 0.25) +
             (Normalized Peak Hour × 0.15) +
             (Normalized Diversity × 0.10) +
             (Recency Score × 0.10) +
             (Junction Factor × 10)
```

**Key Functions:**
- `calculate_risk_score()` - Calculate risk scores
- `get_risk_distribution()` - Get risk category distribution
- `get_high_risk_locations()` - Filter high-risk locations
- `get_risk_by_police_station()` - Station-wise risk analysis
- `get_risk_trends()` - Analyze risk trends
- `predict_risk_change()` - Predict future risk changes

### 4. Predictive Analytics Module
**Purpose:** Train ML models for prediction tasks

**Responsibilities:**
- Prepare features for ML models
- Train classification model (hotspot prediction)
- Train regression model (violation prediction)
- Calculate feature importance
- Evaluate model performance
- Make predictions on new data
- Save/load trained models

**Models Used:**
- **Random Forest Classifier** - Predict if location will become hotspot
- **Random Forest Regressor** - Predict number of violations

**Key Functions:**
- `prepare_features()` - Feature engineering
- `train_hotspot_classifier()` - Train classification model
- `train_violation_regressor()` - Train regression model
- `predict_hotspot_probability()` - Predict hotspot probability
- `predict_future_violations()` - Predict future violations
- `get_feature_importance()` - Get feature importance
- `save_models()` / `load_models()` - Model persistence

### 5. Enforcement Planner Module (Flagship Feature)
**Purpose:** Generate intelligent enforcement recommendations

**Responsibilities:**
- Calculate intervention impact scores
- Assign priority levels to locations
- Calculate optimal officer allocation
- Generate patrol schedules
- Provide towing recommendations
- Calculate ROI for enforcement operations
- Generate shift-based schedules
- Create weekly enforcement calendar

**Intervention Impact Formula:**
```
Impact Score = (Violation Count × 0.40) + 
               (Severity Score × 0.30) +
               (Risk Score × 0.20) +
               (Violation Frequency × 0.10)
```

**Key Functions:**
- `generate_enforcement_plan()` - Generate comprehensive plan
- `get_deployment_recommendations()` - Get top recommendations
- `get_enforcement_priority_ranking()` - Get complete ranking
- `get_shift_schedule()` - Generate shift-based schedule
- `calculate_roi()` - Calculate ROI analysis
- `get_weekly_enforcement_calendar()` - Weekly calendar

### 6. Insights Analyzer Module
**Purpose:** Provide detailed analysis across multiple dimensions

**Responsibilities:**
- Area-wise violation analysis
- Police station performance analysis
- Time-based trend analysis (hourly, daily, monthly)
- Violation type trend analysis
- Recurring hotspot detection
- Peak hour analysis
- Vehicle type insights
- Comparative analysis

**Key Functions:**
- `area_wise_analysis()` - Analyze by location
- `police_station_analysis()` - Analyze by station
- `time_based_trends()` - Analyze temporal patterns
- `violation_trends()` - Analyze violation patterns
- `recurring_hotspot_detection()` - Detect recurring hotspots
- `peak_hour_analysis()` - Analyze peak hours
- `vehicle_type_insights()` - Vehicle type analysis
- `comparative_analysis()` - Compare areas/stations

### 7. Report Generator Module
**Purpose:** Generate and export reports

**Responsibilities:**
- Generate executive summary reports
- Generate hotspot analysis reports
- Generate enforcement recommendation reports
- Generate police station reports
- Generate comprehensive reports
- Export data to CSV format
- Export data to Excel format
- Format reports as text

**Key Functions:**
- `generate_summary_report()` - Executive summary
- `generate_hotspot_report()` - Hotspot report
- `generate_enforcement_report()` - Enforcement report
- `generate_police_station_report()` - Station report
- `generate_comprehensive_report()` - Comprehensive report
- `export_to_csv()` - CSV export
- `export_to_excel()` - Excel export
- `format_report_as_text()` - Text formatting

## Data Flow

### 1. Data Ingestion
```
CSV File → DataProcessor.load_data() → Raw DataFrame
```

### 2. Data Processing
```
Raw DataFrame → DataProcessor.clean_data() → Processed DataFrame
```

### 3. Analysis Pipeline
```
Processed DataFrame → 
  ├─→ HotspotIntelligence → Hotspot Data
  ├─→ CongestionRiskEngine → Risk Scores
  ├─→ PredictiveAnalytics → ML Predictions
  ├─→ EnforcementPlanner → Enforcement Plan
  ├─→ InsightsAnalyzer → Insights
  └─→ ReportGenerator → Reports
```

### 4. Visualization
```
Analysis Results → Streamlit Pages → Interactive Visualizations
```

## Technology Stack

### Backend
- **Python 3.8+** - Core programming language
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **Scikit-learn** - Machine learning models
- **Folium** - Interactive maps

### Frontend
- **Streamlit** - Web application framework
- **Plotly** - Interactive charts
- **Folium** - Interactive maps

### Data Storage
- **CSV Files** - Raw and processed data

## Performance Considerations

### Caching
- Streamlit caching for expensive operations
- Module-level caching for data processing
- Model persistence to avoid retraining

### Optimization
- Data sampling for large visualizations
- Efficient clustering algorithms
- Batch processing for predictions

### Scalability
- Modular architecture for easy scaling
- Database integration ready
- API endpoints for external integration

## Security Considerations

### Data Privacy
- Anonymized vehicle numbers
- No personal identification information
- Secure data handling practices

### Access Control
- Role-based access (future enhancement)
- Authentication (future enhancement)
- Audit logging (future enhancement)

## Deployment Architecture

### Current Setup
- Local development environment
- Streamlit local server
- File-based data storage

### Production Deployment (Future)
```
┌─────────────────────────────────────────────────────────────────┐
│                     Load Balancer                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Streamlit Server (Multi-instance)            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Application Server                            │
│              (Python, Modules, ML Models)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Database (PostgreSQL)                         │
│              (Violation Data, Models, Cache)                      │
└─────────────────────────────────────────────────────────────────┘
```

## Integration Points

### External Systems (Future)
- Traffic camera feeds
- Parking management systems
- Traffic signal control systems
- Mobile applications for officers
- Citizen reporting apps

### API Endpoints (Future)
- `/api/violations` - Violation data
- `/api/hotspots` - Hotspot data
- `/api/predictions` - ML predictions
- `/api/enforcement` - Enforcement recommendations
- `/api/reports` - Report generation

## Monitoring and Logging

### Current
- Streamlit logs
- Console output
- Error handling

### Future Enhancements
- Application performance monitoring
- User activity tracking
- Error alerting
- Analytics dashboard

## Testing Strategy

### Unit Tests (Future)
- Module function testing
- Data processing validation
- ML model testing

### Integration Tests (Future)
- End-to-end workflow testing
- API testing
- Data pipeline testing

### Performance Tests (Future)
- Load testing
- Stress testing
- Response time monitoring

## Maintenance and Updates

### Regular Tasks
- Data updates
- Model retraining
- Feature enhancements
- Bug fixes

### Version Control
- Git for code management
- Semantic versioning
- Change logs

---

**Architecture Version:** 1.0  
**Last Updated:** June 2026  
**For:** Flipkart Gridlock Hackathon 2.0
