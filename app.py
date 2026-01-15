"""
Lisbon Road Accidents Dashboard
================================
A Streamlit application for visualizing and analyzing road accident data in Lisbon.

Requirements:
    pip install streamlit pandas geopandas folium plotly streamlit-folium

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import plotly.express as px
from shapely.geometry import Point
from streamlit_folium import st_folium

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Lisbon Road Accidents Dashboard",
    page_icon="🚗",
    layout="wide"
)

# ============================================
# LOAD AND PROCESS DATA
# ============================================
@st.cache_data
def load_data():
    """Load and preprocess the road accidents data."""
    df = pd.read_csv("data/Road_Accidents_Lisbon.csv")
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.month_name()
    
    # Create severity column based on casualties
    def categorize_severity(row):
        if row['fatalities_30d'] > 0:
            return 'Fatal'
        elif row['injuries_serious'] > 0:
            return 'Serious'
        elif row['injuries_light'] > 0:
            return 'Light'
        else:
            return 'Property Damage Only'
    
    df['severity'] = df.apply(categorize_severity, axis=1)
    df['total_casualties'] = df['injuries_light'] + df['injuries_serious'] + df['fatalities_30d']
    
    # Create time period categories
    def categorize_time_period(hour):
        if 6 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 18:
            return 'Afternoon'
        elif 18 <= hour < 22:
            return 'Evening'
        else:
            return 'Night'
    
    df['time_period'] = df['hour'].apply(categorize_time_period)
    
    return df

# Load data
df = load_data()

# ============================================
# SIDEBAR FILTERS
# ============================================
st.sidebar.title("🔍 Filters")
st.sidebar.markdown("Use the filters below to explore the data")

# Date filter
st.sidebar.subheader("📅 Date Range")
date_range = st.sidebar.date_input(
    "Select dates",
    value=(df['date'].min(), df['date'].max()),
    min_value=df['date'].min(),
    max_value=df['date'].max()
)

# Severity filter
st.sidebar.subheader("🏥 Severity")
severity_options = st.sidebar.multiselect(
    "Select severity levels",
    options=df['severity'].unique(),
    default=df['severity'].unique()
)

# Weather filter
st.sidebar.subheader("🌤️ Weather")
weather_options = st.sidebar.multiselect(
    "Select weather conditions",
    options=df['weather'].unique(),
    default=df['weather'].unique()
)

# Road type filter
st.sidebar.subheader("🛣️ Road Type")
road_type_options = st.sidebar.multiselect(
    "Select road types",
    options=df['road_type'].unique(),
    default=df['road_type'].unique()
)

# Parish filter
st.sidebar.subheader("📍 Parish")
parish_options = st.sidebar.multiselect(
    "Select parishes",
    options=sorted(df['parish'].unique()),
    default=sorted(df['parish'].unique())
)

# Time period filter
st.sidebar.subheader("⏰ Time Period")
time_period_options = st.sidebar.multiselect(
    "Select time periods",
    options=['Morning', 'Afternoon', 'Evening', 'Night'],
    default=['Morning', 'Afternoon', 'Evening', 'Night']
)

# Apply filters
if len(date_range) == 2:
    mask = (
        (df['date'].dt.date >= date_range[0]) &
        (df['date'].dt.date <= date_range[1]) &
        (df['severity'].isin(severity_options)) &
        (df['weather'].isin(weather_options)) &
        (df['road_type'].isin(road_type_options)) &
        (df['parish'].isin(parish_options)) &
        (df['time_period'].isin(time_period_options))
    )
    filtered_df = df[mask]
else:
    filtered_df = df

# ============================================
# MAIN CONTENT
# ============================================
st.title("🚗 Lisbon Road Accidents Dashboard")
st.markdown("""
This dashboard provides an interactive analysis of road accidents in Lisbon (2023).
Use the sidebar filters to explore the data.
""")

# ============================================
# KEY METRICS
# ============================================
st.markdown("### 📊 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Total Accidents",
        value=len(filtered_df),
        delta=f"{len(filtered_df)/len(df)*100:.1f}% of total" if len(df) > 0 else None
    )

with col2:
    st.metric(
        label="Total Casualties",
        value=filtered_df['total_casualties'].sum()
    )

with col3:
    st.metric(
        label="Fatal Accidents",
        value=len(filtered_df[filtered_df['severity'] == 'Fatal'])
    )

with col4:
    st.metric(
        label="Serious Injuries",
        value=filtered_df['injuries_serious'].sum()
    )

with col5:
    st.metric(
        label="Parishes Affected",
        value=filtered_df['parish'].nunique()
    )

st.markdown("---")

# ============================================
# MAP SECTION
# ============================================
st.markdown("### 📍 Accident Locations Map")

if len(filtered_df) > 0:
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(
        filtered_df,
        geometry=[Point(xy) for xy in zip(filtered_df['longitude'], filtered_df['latitude'])],
        crs="EPSG:4326"
    )
    
    # Calculate map center
    center = [gdf['latitude'].mean(), gdf['longitude'].mean()]
    
    # Map tile options
    tile_option = st.selectbox(
        "Select map style",
        options=['CartoDB Positron', 'CartoDB dark_matter', 'OpenStreetMap'],
        index=0
    )
    
    # Create map
    m = folium.Map(location=center, zoom_start=12, tiles=tile_option)
    
    # Color mapping for severity
    severity_colors = {
        'Property Damage Only': 'green',
        'Light': 'orange',
        'Serious': 'red',
        'Fatal': 'darkred'
    }
    
    # Add markers for each accident
    for _, row in gdf.iterrows():
        color = severity_colors.get(row['severity'], 'blue')
        
        popup_html = f"""
        <div style="width: 200px;">
            <h4>Accident Details</h4>
            <b>ID:</b> {row['id']}<br>
            <b>Date:</b> {row['date'].strftime('%Y-%m-%d')}<br>
            <b>Time:</b> {row['hour']}:00<br>
            <b>Parish:</b> {row['parish']}<br>
            <b>Road Type:</b> {row['road_type']}<br>
            <b>Accident Type:</b> {row['accident_type']}<br>
            <b>Weather:</b> {row['weather']}<br>
            <b>Severity:</b> {row['severity']}<br>
            <b>Casualties:</b> {row['total_casualties']}
        </div>
        """
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; 
                background-color: white; padding: 10px; border: 2px solid grey; 
                border-radius: 5px; font-size: 14px;">
        <p style="margin: 0 0 5px 0;"><strong>Severity Legend</strong></p>
        <p style="margin: 2px 0;"><span style="color: green;">●</span> Property Damage Only</p>
        <p style="margin: 2px 0;"><span style="color: orange;">●</span> Light Injuries</p>
        <p style="margin: 2px 0;"><span style="color: red;">●</span> Serious Injuries</p>
        <p style="margin: 2px 0;"><span style="color: darkred;">●</span> Fatal</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Display map
    st_folium(m, width=None, height=500)
else:
    st.warning("No data available for the selected filters.")

st.markdown("---")

# ============================================
# CHARTS SECTION
# ============================================
st.markdown("### 📈 Statistical Analysis")

if len(filtered_df) > 0:
    # First row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Accidents by Severity")
        fig_severity = px.pie(
            filtered_df,
            names='severity',
            color='severity',
            color_discrete_map={
                'Property Damage Only': '#2ecc71',
                'Light': '#f1c40f',
                'Serious': '#e74c3c',
                'Fatal': '#9b59b6'
            },
            hole=0.4
        )
        fig_severity.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_severity, use_container_width=True)
    
    with col2:
        st.markdown("#### Accidents by Weather Condition")
        weather_counts = filtered_df['weather'].value_counts().reset_index()
        weather_counts.columns = ['weather', 'count']
        fig_weather = px.bar(
            weather_counts,
            x='weather',
            y='count',
            color='count',
            color_continuous_scale='Viridis'
        )
        fig_weather.update_layout(
            xaxis_title="Weather",
            yaxis_title="Number of Accidents",
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_weather, use_container_width=True)
    
    # Second row of charts
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### Accidents by Road Type")
        road_counts = filtered_df['road_type'].value_counts().reset_index()
        road_counts.columns = ['road_type', 'count']
        fig_road = px.bar(
            road_counts,
            x='road_type',
            y='count',
            color='road_type',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_road.update_layout(
            xaxis_title="Road Type",
            yaxis_title="Number of Accidents",
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_road, use_container_width=True)
    
    with col4:
        st.markdown("#### Accidents by Accident Type")
        type_counts = filtered_df['accident_type'].value_counts().reset_index()
        type_counts.columns = ['accident_type', 'count']
        fig_type = px.bar(
            type_counts,
            x='accident_type',
            y='count',
            color='count',
            color_continuous_scale='Reds'
        )
        fig_type.update_layout(
            xaxis_title="Accident Type",
            yaxis_title="Number of Accidents",
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_type, use_container_width=True)
    
    # Hourly distribution
    st.markdown("#### ⏰ Hourly Distribution of Accidents")
    hourly_data = filtered_df.groupby('hour').size().reset_index(name='count')
    fig_hourly = px.line(
        hourly_data,
        x='hour',
        y='count',
        markers=True
    )
    fig_hourly.add_bar(x=hourly_data['hour'], y=hourly_data['count'], opacity=0.3)
    fig_hourly.update_layout(
        xaxis=dict(tickmode='linear', tick0=0, dtick=2),
        xaxis_title="Hour of Day",
        yaxis_title="Number of Accidents",
        showlegend=False
    )
    st.plotly_chart(fig_hourly, use_container_width=True)
    
    # Monthly trend
    st.markdown("#### 📅 Monthly Accident Trend")
    monthly_data = filtered_df.groupby('month_name').size().reset_index(name='count')
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_data['month_name'] = pd.Categorical(
        monthly_data['month_name'], 
        categories=month_order, 
        ordered=True
    )
    monthly_data = monthly_data.sort_values('month_name')
    
    fig_monthly = px.bar(
        monthly_data,
        x='month_name',
        y='count',
        color='count',
        color_continuous_scale='Blues'
    )
    fig_monthly.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Accidents",
        showlegend=False
    )
    st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Day of week analysis
    st.markdown("#### 📅 Accidents by Day of Week")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_data = filtered_df['day_of_week'].value_counts().reindex(day_order).reset_index()
    day_data.columns = ['day_of_week', 'count']
    
    fig_day = px.bar(
        day_data,
        x='day_of_week',
        y='count',
        color='count',
        color_continuous_scale='Oranges'
    )
    fig_day.update_layout(
        xaxis_title="Day of Week",
        yaxis_title="Number of Accidents",
        showlegend=False
    )
    st.plotly_chart(fig_day, use_container_width=True)
    
    # Top parishes
    st.markdown("#### 📍 Top 10 Parishes by Number of Accidents")
    parish_data = filtered_df['parish'].value_counts().head(10).reset_index()
    parish_data.columns = ['parish', 'count']
    
    fig_parish = px.bar(
        parish_data,
        x='count',
        y='parish',
        orientation='h',
        color='count',
        color_continuous_scale='Greens'
    )
    fig_parish.update_layout(
        xaxis_title="Number of Accidents",
        yaxis_title="Parish",
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig_parish, use_container_width=True)

st.markdown("---")

# ============================================
# DATA TABLE SECTION
# ============================================
st.markdown("### 📋 Detailed Data Table")

# Column selection
columns_to_show = st.multiselect(
    "Select columns to display",
    options=filtered_df.columns.tolist(),
    default=['id', 'date', 'hour', 'parish', 'accident_type', 'severity', 'weather', 
             'road_type', 'total_casualties', 'num_vehicles']
)

if columns_to_show:
    st.dataframe(
        filtered_df[columns_to_show],
        use_container_width=True,
        height=400
    )

# ============================================
# DOWNLOAD SECTION
# ============================================
st.markdown("### 📥 Download Data")
col1, col2 = st.columns(2)

with col1:
    # Download filtered data as CSV
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=csv,
        file_name="lisbon_accidents_filtered.csv",
        mime="text/csv"
    )

with col2:
    # Download full data as CSV
    csv_full = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Dataset (CSV)",
        data=csv_full,
        file_name="lisbon_accidents_full.csv",
        mime="text/csv"
    )

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
    <p><strong>Important Notice:</strong> Use of this data is restricted for educational purposes within this course only.</p>
    <p>Dashboard created for the Python Data Analysis Workshop</p>
</div>
""", unsafe_allow_html=True)
