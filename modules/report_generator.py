"""
Report Generator Module
Generates summary reports and export functionality
"""

import pandas as pd
import numpy as np
from datetime import datetime
import io
from .shared_data import get_location_column


class ReportGenerator:
    """Generate various reports for stakeholders"""
    
    def __init__(self, data_processor, hotspot_intelligence, congestion_risk, enforcement_planner):
        self.data_processor = data_processor
        self.hotspot_intelligence = hotspot_intelligence
        self.congestion_risk = congestion_risk
        self.enforcement_planner = enforcement_planner
        
    def generate_summary_report(self):
        """Generate executive summary report"""
        stats = self.data_processor.get_summary_stats()
        
        summary = {
            'report_title': 'ParkPulse AI - Executive Summary',
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'period': f"{stats['date_range']['start'].strftime('%Y-%m-%d')} to {stats['date_range']['end'].strftime('%Y-%m-%d')}",
            'key_metrics': {
                'total_violations': stats['total_violations'],
                'police_stations_covered': stats['police_stations'],
                'vehicle_types_tracked': stats['vehicle_types'],
                'violation_types_detected': stats['violation_types'],
                'unique_locations': stats['unique_locations']
            },
            'validation_status': stats['validation_status'],
            'top_vehicle_types': dict(list(stats['vehicle_type_distribution'].items())[:5]),
            'top_violation_types': dict(list(stats['violation_type_distribution'].items())[:5])
        }
        
        return summary
    
    def generate_hotspot_report(self, top_n=20):
        """Generate detailed hotspot report"""
        hotspots = self.hotspot_intelligence.get_top_hotspots(top_n)
        
        report = {
            'report_title': 'ParkPulse AI - Hotspot Analysis Report',
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'top_hotspots': []
        }
        
        for idx, row in hotspots.iterrows():
            hotspot_info = {
                'rank': idx + 1,
                'location': row['representative_location'],
                'police_station': row['police_station'],
                'violation_count': int(row['violation_count']),
                'severity_score': round(row['severity_score'], 2),
                'risk_category': row['risk_category'],
                'common_violation': row['common_violation'],
                'common_vehicle': row['common_vehicle'],
                'coordinates': {
                    'latitude': row['mean_latitude'],
                    'longitude': row['mean_longitude']
                }
            }
            report['top_hotspots'].append(hotspot_info)
        
        return report
    
    def generate_enforcement_report(self):
        """Generate enforcement recommendations report"""
        recommendations = self.enforcement_planner.get_deployment_recommendations()
        roi = self.enforcement_planner.calculate_roi()
        
        report = {
            'report_title': 'ParkPulse AI - Enforcement Recommendations Report',
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'roi_analysis': roi,
            'recommendations': []
        }
        
        for idx, row in recommendations.iterrows():
            rec_info = {
                'rank': int(row['rank']),
                'location': row['location'],
                'police_station': row['police_station'],
                'priority_level': row['priority_level'],
                'officers_recommended': int(row['officers_recommended']),
                'expected_reduction': round(row['expected_reduction'], 1),
                'patrol_schedule': row['patrol_schedule'],
                'towing_recommendation': row['towing_recommendation'],
                'current_violations': int(row['current_violations']),
                'risk_category': row['risk_category']
            }
            report['recommendations'].append(rec_info)
        
        return report
    
    def generate_police_station_report(self, station_name=None):
        """Generate report for specific police station or all stations"""
        df = self.data_processor.processed_data
        location_col = get_location_column(df)
        
        station_stats = df.groupby('police_station').agg({
            'id': 'count',
            'vehicle_type': lambda x: x.nunique(),
            'primary_violation': lambda x: x.nunique(),
            'location_key': lambda x: x.nunique()
        }).reset_index()
        
        station_stats.columns = ['police_station', 'total_violations', 'unique_vehicle_types',
                                'unique_violation_types', 'unique_locations']
        
        if station_name:
            station_stats = station_stats[station_stats['police_station'] == station_name]
        
        station_stats = station_stats.sort_values('total_violations', ascending=False)
        
        return station_stats
    
    def export_to_csv(self, data, filename):
        """Export data to CSV format"""
        if isinstance(data, pd.DataFrame):
            csv_buffer = io.StringIO()
            data.to_csv(csv_buffer, index=False)
            return csv_buffer.getvalue()
        elif isinstance(data, dict):
            df = pd.DataFrame(data)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            return csv_buffer.getvalue()
        return None
    
    def export_to_excel(self, data_dict, filename):
        """Export multiple dataframes to Excel"""
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            for sheet_name, data in data_dict.items():
                if isinstance(data, pd.DataFrame):
                    data.to_excel(writer, sheet_name=sheet_name, index=False)
                elif isinstance(data, dict):
                    pd.DataFrame(data).to_excel(writer, sheet_name=sheet_name, index=False)
        return buffer.getvalue()
    
    def generate_comprehensive_report(self):
        """Generate comprehensive report with all modules"""
        report = {
            'summary': self.generate_summary_report(),
            'hotspots': self.generate_hotspot_report(10),
            'enforcement': self.generate_enforcement_report(),
            'police_stations': self.generate_police_station_report().head(10).to_dict('records')
        }
        
        return report
    
    def format_report_as_text(self, report):
        """Format report as readable text"""
        text_lines = []
        
        if 'summary' in report:
            summary = report['summary']
            text_lines.append("=" * 60)
            text_lines.append(summary['report_title'])
            text_lines.append("=" * 60)
            text_lines.append(f"Generated: {summary['generated_at']}")
            text_lines.append(f"Period: {summary['period']}")
            text_lines.append("")
            text_lines.append("KEY METRICS:")
            for metric, value in summary['key_metrics'].items():
                text_lines.append(f"  - {metric.replace('_', ' ').title()}: {value:,}")
            text_lines.append("")
        
        if 'hotspots' in report:
            text_lines.append("-" * 60)
            text_lines.append("TOP HOTSPOTS")
            text_lines.append("-" * 60)
            for hotspot in report['hotspots']['top_hotspots'][:10]:
                text_lines.append(f"\n#{hotspot['rank']} {hotspot['location']}")
                text_lines.append(f"  Police Station: {hotspot['police_station']}")
                text_lines.append(f"  Violations: {hotspot['violation_count']:,}")
                text_lines.append(f"  Risk: {hotspot['risk_category']} (Score: {hotspot['severity_score']})")
        
        if 'enforcement' in report:
            text_lines.append("\n" + "-" * 60)
            text_lines.append("ENFORCEMENT RECOMMENDATIONS")
            text_lines.append("-" * 60)
            text_lines.append(f"\nROI Analysis:")
            roi = report['enforcement']['roi_analysis']
            text_lines.append(f"  Total Officers: {roi['total_officers']}")
            text_lines.append(f"  Total Cost: ₹{roi['total_cost']:,.2f}")
            text_lines.append(f"  Expected Violations Prevented: {roi['expected_violations_prevented']}")
            text_lines.append(f"  Total Savings: ₹{roi['total_savings']:,.2f}")
            text_lines.append(f"  ROI: {roi['roi_percentage']:.2f}%")
        
        return "\n".join(text_lines)
