import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from utils.weather_api import WeatherAPI
from utils.visualizations import create_forecast_chart, create_wind_rose, create_weather_map
from assets.weather_icons import WEATHER_ICONS

# Page config
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌤",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background-color: #f8f9fa;
    }
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #0066cc;
    }
    .metric-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .location-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
        color: #333;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize API
api = WeatherAPI()

# Title and Search
st.title("🌡️ Weather Dashboard")
st.markdown("---")

# Location search
col1, col2 = st.columns([3, 1])
with col1:
    location = st.text_input("Enter location", "London", placeholder="Enter city name...")
with col2:
    units = st.selectbox("Units", ["Celsius", "Fahrenheit"], index=0)

try:
    # Fetch weather data
    current_weather = api.get_current_weather(location, units)
    forecast_data = api.get_forecast(location, units)

    # Location header
    st.markdown(f"<h1 class='location-header'>{location.title()}</h1>", unsafe_allow_html=True)

    # Current weather display
    st.subheader("Current Conditions")
    cols = st.columns(4)

    with cols[0]:
        temp_unit = "°C" if units == "Celsius" else "°F"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{current_weather['temp']}{temp_unit}</div>
                <div class="metric-label">Temperature</div>
                <div>Feels like: {current_weather['feels_like']}{temp_unit}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with cols[1]:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{current_weather['humidity']}%</div>
                <div class="metric-label">Humidity</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with cols[2]:
        speed_unit = "km/h" if units == "Celsius" else "mph"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{current_weather['wind_speed']}</div>
                <div class="metric-label">Wind Speed ({speed_unit})</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with cols[3]:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{current_weather['pressure']}</div>
                <div class="metric-label">Pressure (hPa)</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # Forecast section
    st.subheader("5-Day Forecast")

    # Temperature forecast with improved styling
    temp_chart = create_forecast_chart(forecast_data, 'temperature', units)
    st.plotly_chart(temp_chart, use_container_width=True)

    # Precipitation and Wind Rose in columns
    col1, col2 = st.columns(2)
    with col1:
        precip_chart = create_forecast_chart(forecast_data, 'precipitation', units)
        st.plotly_chart(precip_chart, use_container_width=True)

    with col2:
        wind_rose = create_wind_rose(forecast_data)
        st.plotly_chart(wind_rose, use_container_width=True)

    # Weather map with improved styling
    st.subheader("Weather Map")
    weather_map = create_weather_map(current_weather['coord'])
    st.components.v1.html(weather_map._repr_html_(), height=400)

except Exception as e:
    st.error(f"Error fetching weather data: {str(e)}")