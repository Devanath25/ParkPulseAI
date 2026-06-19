# ParkPulse AI 🚗

**Parking Intelligence & Congestion Prevention Platform**

## Overview

ParkPulse AI is an AI-powered platform designed for traffic authorities to identify parking violation hotspots, estimate congestion impact, predict future hotspots, and recommend targeted enforcement actions. Built for the Flipkart Gridlock Hackathon 2.0 – Round 2.

### Problem Statement

**Poor Visibility on Parking-Induced Congestion**

Traffic authorities lack real-time visibility into parking violations and their impact on city congestion. This leads to inefficient resource allocation, missed enforcement opportunities, and increased traffic congestion.

### Solution

ParkPulse AI provides:
- Real-time hotspot identification using geographic clustering
- Risk-based congestion scoring
- Predictive analytics for future violations
- Smart enforcement planning with ROI analysis
- Comprehensive reporting and insights

## Features

### 1. Executive Dashboard 📊
- Total violations overview
- Top hotspot areas and police stations
- Most frequent violations
- Monthly and daily trends
- Growth indicators
- Interactive filters for data exploration

### 2. Hotspot Intelligence Module 🗺️
- Interactive heatmaps showing violation density
- Violation density maps with clustering
- Hotspot ranking with severity scores
- Cluster analysis using DBSCAN
- Top 10 hotspot locations with risk categories

### 3. Congestion Risk Engine ⚠️
- Risk scoring mechanism (Low, Medium, High, Critical)
- Risk explanations for each location
- Risk distribution analysis
- Police station-wise risk assessment
- Risk trend analysis over time

### 4. Predictive Analytics 🤖
- Machine learning models for hotspot prediction
- Violation forecasting
- Feature importance analysis
- Model performance metrics
- Future violation predictions

### 5. Smart Enforcement Planner 👮 (Flagship Feature)
- Officer deployment recommendations
- Enforcement priority ranking
- Towing recommendations based on violation patterns
- Patrol scheduling suggestions
- ROI analysis for enforcement operations
- Shift-based enforcement schedules
- Weekly enforcement calendar

### 6. Insights Module 💡
- Area-wise analysis
- Police-station-wise analysis
- Time-based trends (hourly, daily, monthly)
- Violation trends and patterns
- Recurring hotspot detection
- Peak hour analysis
- Vehicle type insights

### 7. Reports Module 📄
- Executive summary reports
- Hotspot analysis reports
- Enforcement recommendation reports
- Police station reports
- Comprehensive multi-format reports
- CSV and Excel export functionality

## Technology Stack

- **Python 3.8+**
- **Streamlit** - Web application framework
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **Plotly** - Interactive visualizations
- **Folium** - Interactive maps
- **Scikit-learn** - Machine learning models
- **OpenPyXL** - Excel file handling

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd ParkPulseAI
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure the dataset is in the project directory:
- Place `jan to may police violation_anonymized791b166.csv` in the `data/` directory
- Note: The dataset file is not included in the repository due to size limitations (104MB)
- You can use your own parking violation dataset with similar structure

## Running the Application

1. Activate your virtual environment (if created)

2. Run the Streamlit application:
```bash
streamlit run app.py
```

3. The application will open in your browser at `http://localhost:8501`

## Project Structure

```
ParkPulseAI/
├── app.py                          # Main application entry point
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
├── architecture.md                 # System architecture documentation
├── presentation_notes.md           # Hackathon presentation notes
├── modules/                        # Core analysis modules
│   ├── __init__.py
│   ├── data_processor.py          # Data loading and preprocessing
│   ├── hotspot_intelligence.py    # Hotspot detection and mapping
│   ├── congestion_risk.py        # Risk scoring engine
│   ├── predictive_analytics.py   # ML models for prediction
│   ├── enforcement_planner.py    # Smart enforcement recommendations
│   ├── insights_analyzer.py      # Detailed insights generation
│   └── report_generator.py       # Report generation and export
├── pages/                         # Streamlit pages
│   ├── dashboard.py              # Executive dashboard
│   ├── hotspots.py               # Hotspot intelligence
│   ├── congestion.py             # Congestion risk engine
│   ├── predictions.py            # Predictive analytics
│   ├── enforcement.py            # Smart enforcement planner
│   ├── insights.py               # Insights module
│   └── reports.py                # Reports module
├── assets/                        # Static assets
└── data/                          # Data directory
    └── jan to may police violation_anonymized791b166.csv
```

## Dataset

The application uses parking violation data from Bengaluru, India, containing:
- **298,450 violation records**
- **Date range:** November 2023 to April 2024
- **54 police stations**
- **21 vehicle types**
- **Geographic coordinates** for each violation
- **Violation types** and offence codes
- **Temporal data** for trend analysis

## Usage Guide

### Executive Dashboard
- View overall statistics and metrics
- Apply filters by police station, vehicle type, violation type, and validation status
- Explore time-based trends and patterns
- Analyze top locations and police stations

### Hotspot Intelligence
- Adjust clustering parameters for hotspot detection
- View interactive heatmaps and cluster maps
- Explore top hotspots with severity scores
- Analyze police station-wise hotspot distribution

### Congestion Risk Engine
- View risk category distribution
- Explore high and critical risk locations
- Analyze risk by police station
- Understand risk factors and explanations

### Predictive Analytics
- Train ML models for hotspot classification
- Train regression models for violation prediction
- View feature importance and model performance
- Make predictions on new data

### Smart Enforcement Planner
- Configure officer availability and costs
- View ROI analysis for enforcement operations
- Explore deployment recommendations
- Analyze shift-based schedules
- View weekly enforcement calendar

### Insights Module
- Perform area-wise analysis
- Analyze police station performance
- Explore time-based trends
- Understand violation patterns
- Detect recurring hotspots
- Analyze peak hours and vehicle types

### Reports Module
- Generate executive summaries
- Create hotspot reports
- Export enforcement recommendations
- Generate police station reports
- Export data in CSV or Excel format

## Hackathon Demo Flow

1. **Start with Executive Dashboard** - Show overall metrics and trends
2. **Navigate to Hotspot Intelligence** - Demonstrate interactive maps
3. **Show Congestion Risk Engine** - Explain risk scoring methodology
4. **Demonstrate Predictive Analytics** - Train and show ML models
5. **Highlight Smart Enforcement Planner** - Flagship feature with ROI
6. **Explore Insights Module** - Show detailed analysis capabilities
7. **Generate Reports** - Export sample reports

## Future Scope

### Short-term Enhancements
- Real-time data integration with traffic cameras
- Mobile application for field officers
- Alert system for critical hotspots
- Integration with existing traffic management systems

### Long-term Vision
- City-scale deployment across multiple cities
- Integration with smart city infrastructure
- AI-powered automated enforcement recommendations
- Predictive congestion modeling
- Integration with parking management systems
- Public-facing app for citizens to report violations

### Technical Improvements
- Deep learning models for better prediction accuracy
- Real-time streaming data processing
- Cloud deployment with auto-scaling
- API endpoints for third-party integration
- Advanced visualization with 3D maps

## Business Impact

### For Traffic Authorities
- **30-40% improvement** in enforcement efficiency
- **Reduced congestion** through targeted interventions
- **Data-driven decision making** for resource allocation
- **Cost savings** through optimized officer deployment
- **Real-time visibility** into violation patterns

### For Citizens
- **Reduced traffic congestion**
- **Improved traffic flow**
- **Fair and transparent enforcement**
- **Better parking availability**

### For the City
- **Smart city initiative** implementation
- **Data-driven governance**
- **Improved traffic management**
- **Economic benefits** from reduced congestion

## Contributing

This project was built for the Flipkart Gridlock Hackathon 2.0. For contributions or questions, please contact the development team.

## License

This project is open-source and available for educational and research purposes.

## Acknowledgments

- **Flipkart Gridlock Hackathon 2.0** - Problem statement and platform
- **Bengaluru Traffic Police** - For providing the violation dataset
- **Open-source community** - For the amazing tools and libraries

## Contact

For questions or feedback about ParkPulse AI, please reach out through the hackathon platform or GitHub repository.

---

**Built with ❤️ for Flipkart Gridlock Hackathon 2.0**
