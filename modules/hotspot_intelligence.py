"""
Hotspot Intelligence Module
Analyzes parking violation hotspots and generates geographic visualizations
"""

import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
import folium
from folium.plugins import HeatMap, MarkerCluster
from .shared_data import get_location_column


class HotspotIntelligence:
    """Identify and analyze parking violation hotspots"""
    
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.hotspot_data = None
        
    def identify_hotspots(self):
        """Identify hotspots using aggregated location data for demo mode"""
        df = self.data_processor.get_geographic_data()
        
        # Aggregate by location to get hotspot counts
        location_stats = df.groupby('location_key').agg({
            'latitude': 'first',
            'longitude': 'first',
            'location': 'first',
            'police_station': 'first',
            'id': 'count',
            'primary_violation': lambda x: x.mode().iloc[0] if len(x) > 0 else None,
            'vehicle_type': lambda x: x.mode().iloc[0] if len(x) > 0 else None
        }).reset_index()
        
        location_stats.columns = ['location_key', 'latitude', 'longitude', 'location',
                                'police_station', 'violation_count', 'common_violation', 'common_vehicle']
        
        # Use top 20 locations only for demo mode
        hotspot_stats = location_stats.nlargest(20, 'violation_count')
        
        # Calculate severity score
        max_count = hotspot_stats['violation_count'].max()
        hotspot_stats['severity_score'] = (hotspot_stats['violation_count'] / max_count) * 100
        
        # Assign risk categories
        hotspot_stats['risk_category'] = pd.cut(
            hotspot_stats['severity_score'],
            bins=[0, 25, 50, 75, 100],
            labels=['Low', 'Medium', 'High', 'Critical']
        )
        
        # Add mean coordinates for mapping
        hotspot_stats['mean_latitude'] = hotspot_stats['latitude']
        hotspot_stats['mean_longitude'] = hotspot_stats['longitude']
        hotspot_stats['representative_location'] = hotspot_stats['location']
        
        self.hotspot_data = hotspot_stats
        
        return hotspot_stats
    
    def get_top_hotspots(self, n=10):
        """Get top N hotspots by violation count"""
        if self.hotspot_data is None:
            self.identify_hotspots()
        
        return self.hotspot_data.head(n)
    
    def calculate_density(self, radius_km=0.5):
        """Calculate violation density around each location"""
        df = self.data_processor.get_geographic_data()
        
        coords = df[['latitude', 'longitude']].values
        distances = cdist(coords, coords, metric='euclidean')
        
        # Convert to approximate km (1 degree ≈ 111 km)
        distances_km = distances * 111
        
        # Count violations within radius
        density = (distances_km < radius_km).sum(axis=1)
        df['density_score'] = density
        
        return df
    
    def create_heatmap(self, df=None):
        """Create a folium heatmap"""
        if df is None:
            df = self.data_processor.get_geographic_data()
        
        # Calculate center point
        center_lat = df['latitude'].mean()
        center_lon = df['longitude'].mean()
        
        # Create map
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
        
        # Prepare heat data
        heat_data = [[row['latitude'], row['longitude']] for idx, row in df.iterrows()]
        
        # Add heatmap layer
        HeatMap(heat_data, radius=15, blur=25, max_zoom=13).add_to(m)
        
        return m
    
    def create_hotspot_map(self, top_n=20):
        """Create an interactive map with hotspot markers"""
        if self.hotspot_data is None:
            self.identify_hotspots()
        
        top_hotspots = self.hotspot_data.head(top_n)
        
        # Calculate center point
        center_lat = top_hotspots['mean_latitude'].mean()
        center_lon = top_hotspots['mean_longitude'].mean()
        
        # Create map
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
        
        # Color mapping for risk categories
        risk_colors = {
            'Low': 'green',
            'Medium': 'orange',
            'High': 'red',
            'Critical': 'darkred'
        }
        
        # Add markers for each hotspot
        for idx, row in top_hotspots.iterrows():
            risk_color = risk_colors.get(row['risk_category'], 'blue')
            
            popup_content = f"""
            <b>Hotspot #{idx + 1}</b><br>
            Violations: {row['violation_count']}<br>
            Severity Score: {row['severity_score']:.1f}<br>
            Risk Category: {row['risk_category']}<br>
            Police Station: {row['police_station']}<br>
            Common Violation: {row['common_violation']}<br>
            Common Vehicle: {row['common_vehicle']}
            """
            
            folium.CircleMarker(
                location=[row['mean_latitude'], row['mean_longitude']],
                radius=max(5, min(30, row['violation_count'] / 10)),
                popup=folium.Popup(popup_content, max_width=300),
                color=risk_color,
                fill=True,
                fillColor=risk_color,
                fillOpacity=0.6,
                weight=2
            ).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 150px; height: 120px; 
                    background-color: white; z-index:9999; font-size:14px;
                    border:2px solid grey; border-radius:5px; padding: 10px">
        <p><b>Risk Legend</b></p>
        <p><i class="fa fa-circle" style="color:green"></i> Low</p>
        <p><i class="fa fa-circle" style="color:orange"></i> Medium</p>
        <p><i class="fa fa-circle" style="color:red"></i> High</p>
        <p><i class="fa fa-circle" style="color:darkred"></i> Critical</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    def get_hotspot_ranking(self):
        """Get ranked list of hotspots with detailed metrics"""
        if self.hotspot_data is None:
            self.identify_hotspots()
        
        ranking = self.hotspot_data.copy()
        ranking['rank'] = range(1, len(ranking) + 1)
        
        # Add additional metrics
        ranking['percentile'] = (ranking['rank'] / len(ranking)) * 100
        
        return ranking[['rank', 'violation_count', 'severity_score', 'risk_category',
                       'percentile', 'police_station', 'representative_location',
                       'common_violation', 'common_vehicle']]
    
    def get_police_station_hotspots(self):
        """Get hotspot analysis by police station"""
        if self.hotspot_data is None:
            self.identify_hotspots()
        
        station_stats = self.hotspot_data.groupby('police_station').agg({
            'violation_count': ['sum', 'count', 'mean', 'max'],
            'severity_score': 'mean'
        }).reset_index()
        
        station_stats.columns = ['police_station', 'total_violations', 'num_hotspots',
                                'avg_violations_per_hotspot', 'max_violations_in_hotspot',
                                'avg_severity_score']
        
        station_stats = station_stats.sort_values('total_violations', ascending=False)
        
        return station_stats
