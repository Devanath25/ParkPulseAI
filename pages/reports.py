"""
Reports Module Page
Generate and export reports
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_processor import DataProcessor
from modules.hotspot_intelligence import HotspotIntelligence
from modules.congestion_risk import CongestionRiskEngine
from modules.enforcement_planner import EnforcementPlanner
from modules.report_generator import ReportGenerator


def show_reports():
    """Display reports module page"""
    
    st.set_page_config(
        page_title="ParkPulse AI - Reports Module",
        page_icon="📄",
        layout="wide"
    )
    
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 2rem;
        }
        .report-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #ddd;
            margin: 1rem 0;
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
        risk_engine = CongestionRiskEngine(processor)
        enforcement_planner = EnforcementPlanner(processor, hotspot_intel, risk_engine)
        report_gen = ReportGenerator(processor, hotspot_intel, risk_engine, enforcement_planner)
        
        return processor, hotspot_intel, risk_engine, enforcement_planner, report_gen
    
    @st.cache_data
    def get_summary_report(_report_gen):
        return _report_gen.generate_summary_report()
    
    @st.cache_data
    def get_hotspot_report(_report_gen, _top_n):
        return _report_gen.generate_hotspot_report(_top_n)
    
    @st.cache_data
    def get_enforcement_report(_report_gen):
        return _report_gen.generate_enforcement_report()
    
    @st.cache_data
    def get_station_report(_report_gen, _station_name):
        return _report_gen.generate_police_station_report(_station_name)
    
    processor, hotspot_intel, risk_engine, enforcement_planner, report_gen = initialize_modules()
    
    st.markdown('<h1 class="main-header">📄 Reports Module</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Report type selection
    report_type = st.sidebar.selectbox(
        "Select Report Type",
        ["Executive Summary", "Hotspot Report", "Enforcement Report", "Police Station Report", "Comprehensive Report"]
    )
    
    if report_type == "Executive Summary":
        st.subheader("📋 Executive Summary Report")
        
        summary = get_summary_report(report_gen)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Violations", f"{summary['key_metrics']['total_violations']:,}")
            st.metric("Police Stations", summary['key_metrics']['police_stations_covered'])
        
        with col2:
            st.metric("Vehicle Types", summary['key_metrics']['vehicle_types_tracked'])
            st.metric("Violation Types", summary['key_metrics']['violation_types_detected'])
        
        with col3:
            st.metric("Unique Locations", f"{summary['key_metrics']['unique_locations']:,}")
            st.metric("Data Period", summary['period'])
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Top Vehicle Types**")
            for vehicle, count in list(summary['top_vehicle_types'].items())[:5]:
                st.write(f"- {vehicle}: {count:,}")
        
        with col2:
            st.write("**Top Violation Types**")
            for violation, count in list(summary['top_violation_types'].items())[:5]:
                st.write(f"- {violation}: {count:,}")
        
        st.markdown("---")
        
        # Export option
        if st.button("Export Executive Summary as CSV"):
            summary_df = pd.DataFrame([summary])
            csv = report_gen.export_to_csv(summary_df, 'executive_summary.csv')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"executive_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    elif report_type == "Hotspot Report":
        st.subheader("🔥 Hotspot Analysis Report")
        
        top_n = st.slider("Number of Top Hotspots", 10, 50, 20, 5)
        hotspot_report = get_hotspot_report(report_gen, top_n)
        
        st.write(f"**Report Generated:** {hotspot_report['generated_at']}")
        
        # Display hotspots
        for hotspot in hotspot_report['top_hotspots']:
            st.markdown(f"""
            <div class="report-card">
                <h3>#{hotspot['rank']} {hotspot['location']}</h3>
                <p><strong>Police Station:</strong> {hotspot['police_station']}</p>
                <p><strong>Violations:</strong> {hotspot['violation_count']:,}</p>
                <p><strong>Severity Score:</strong> {hotspot['severity_score']}</p>
                <p><strong>Risk Category:</strong> {hotspot['risk_category']}</p>
                <p><strong>Common Violation:</strong> {hotspot['common_violation']}</p>
                <p><strong>Common Vehicle:</strong> {hotspot['common_vehicle']}</p>
                <p><strong>Coordinates:</strong> ({hotspot['coordinates']['latitude']:.4f}, {hotspot['coordinates']['longitude']:.4f})</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Export option
        if st.button("Export Hotspot Report as CSV"):
            hotspot_df = pd.DataFrame(hotspot_report['top_hotspots'])
            csv = report_gen.export_to_csv(hotspot_df, 'hotspot_report.csv')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"hotspot_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    elif report_type == "Enforcement Report":
        st.subheader("👮 Enforcement Recommendations Report")
        
        enforcement_report = get_enforcement_report(report_gen)
        
        # ROI Analysis
        roi = enforcement_report['roi_analysis']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Officers", roi['total_officers'])
        with col2:
            st.metric("Total Cost", f"₹{roi['total_cost']:,.0f}")
        with col3:
            st.metric("Expected Reduction", f"{roi['expected_violations_prevented']:.0f}")
        with col4:
            st.metric("ROI", f"{roi['roi_percentage']:.1f}%")
        
        st.markdown("---")
        
        # Recommendations
        st.write("**Top Enforcement Recommendations**")
        
        for rec in enforcement_report['recommendations'][:15]:
            priority_color = {
                'Critical': '🔴',
                'High': '🟠',
                'Medium': '🟡',
                'Low': '🟢'
            }.get(rec['priority_level'], '⚪')
            
            st.markdown(f"""
            <div class="report-card">
                <h3>{priority_color} #{rec['rank']} {rec['location']}</h3>
                <p><strong>Police Station:</strong> {rec['police_station']}</p>
                <p><strong>Priority:</strong> {rec['priority_level']} | <strong>Officers:</strong> {rec['officers_recommended']}</p>
                <p><strong>Expected Reduction:</strong> {rec['expected_reduction']} violations</p>
                <p><strong>Patrol Schedule:</strong> {rec['patrol_schedule']}</p>
                <p><strong>Towing:</strong> {rec['towing_recommendation']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Export option
        if st.button("Export Enforcement Report as CSV"):
            enforcement_df = pd.DataFrame(enforcement_report['recommendations'])
            csv = report_gen.export_to_csv(enforcement_df, 'enforcement_report.csv')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"enforcement_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    elif report_type == "Police Station Report":
        st.subheader("🚔 Police Station Report")
        
        station_name = st.selectbox(
            "Select Police Station",
            ["All Stations"] + sorted(processor.processed_data['police_station'].unique().tolist())
        )
        
        if station_name == "All Stations":
            station_report = get_station_report(report_gen, None)
            st.write(f"**Total Stations:** {len(station_report)}")
        else:
            station_report = get_station_report(report_gen, station_name)
            st.write(f"**Station:** {station_name}")
        
        st.dataframe(station_report, width='stretch')
        
        # Export option
        if st.button("Export Police Station Report as CSV"):
            csv = report_gen.export_to_csv(station_report, 'police_station_report.csv')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"police_station_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    elif report_type == "Comprehensive Report":
        st.subheader("📊 Comprehensive Report")
        
        @st.cache_data
        def get_comprehensive_report(_report_gen):
            return _report_gen.generate_comprehensive_report()
        
        comprehensive = get_comprehensive_report(report_gen)
        
        # Summary section
        st.write("### Executive Summary")
        summary = comprehensive['summary']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Violations", f"{summary['key_metrics']['total_violations']:,}")
        with col2:
            st.metric("Police Stations", summary['key_metrics']['police_stations_covered'])
        with col3:
            st.metric("Unique Locations", f"{summary['key_metrics']['unique_locations']:,}")
        
        # Hotspots section
        st.write("### Top Hotspots")
        for hotspot in comprehensive['hotspots']['top_hotspots'][:5]:
            st.write(f"**#{hotspot['rank']} {hotspot['location']}** - {hotspot['violation_count']:,} violations ({hotspot['risk_category']})")
        
        # Enforcement section
        st.write("### Enforcement ROI")
        roi = comprehensive['enforcement']['roi_analysis']
        st.write(f"**ROI:** {roi['roi_percentage']:.1f}% | **Total Savings:** ₹{roi['total_savings']:,.0f}")
        
        # Export comprehensive report
        st.markdown("---")
        st.write("### Export Comprehensive Report")
        
        export_format = st.selectbox("Export Format", ["CSV", "Excel"])
        
        if export_format == "CSV":
            if st.button("Export All Reports as CSV"):
                # Create multiple CSVs
                summary_df = pd.DataFrame([comprehensive['summary']])
                hotspot_df = pd.DataFrame(comprehensive['hotspots']['top_hotspots'])
                enforcement_df = pd.DataFrame(comprehensive['enforcement']['recommendations'])
                station_df = pd.DataFrame(comprehensive['police_stations'])
                
                st.info("Download each section separately below:")
                
                col1, col2 = st.columns(2)
                with col1:
                    csv1 = report_gen.export_to_csv(summary_df, 'summary.csv')
                    st.download_button("Download Summary", csv1, 'summary.csv', 'text/csv')
                with col2:
                    csv2 = report_gen.export_to_csv(hotspot_df, 'hotspots.csv')
                    st.download_button("Download Hotspots", csv2, 'hotspots.csv', 'text/csv')
        
        else:
            if st.button("Export All Reports as Excel"):
                data_dict = {
                    'Summary': pd.DataFrame([comprehensive['summary']]),
                    'Hotspots': pd.DataFrame(comprehensive['hotspots']['top_hotspots']),
                    'Enforcement': pd.DataFrame(comprehensive['enforcement']['recommendations']),
                    'Police Stations': pd.DataFrame(comprehensive['police_stations'])
                }
                excel_data = report_gen.export_to_excel(data_dict, 'comprehensive_report.xlsx')
                st.download_button(
                    label="Download Excel",
                    data=excel_data,
                    file_name=f"comprehensive_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    st.markdown("---")
    st.markdown("**Report Features:**")
    st.markdown("- Real-time data aggregation")
    st.markdown("- Multiple export formats (CSV, Excel)")
    st.markdown("- Customizable report parameters")
    st.markdown("- Executive-ready formatting")
    st.markdown("- Timestamped reports for tracking")


if __name__ == "__main__":
    show_reports()
