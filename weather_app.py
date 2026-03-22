import os
from dotenv import load_dotenv
load_dotenv()
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
    page_title="WeatherPro — Premium Weather Analytics",
    page_icon="⛅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Premium CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Root variables ─────────────────────────────────────────── */
:root {
    --bg-primary: #0f1117;
    --bg-card: rgba(255,255,255,0.04);
    --bg-card-hover: rgba(255,255,255,0.07);
    --border-subtle: rgba(255,255,255,0.06);
    --text-primary: #f0f2f6;
    --text-secondary: rgba(240,242,246,0.55);
    --accent: #6C63FF;
    --accent-glow: rgba(108,99,255,0.35);
    --gradient-warm: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
    --gradient-cool: linear-gradient(135deg, #6C63FF 0%, #48C6EF 100%);
    --gradient-green: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    --gradient-purple: linear-gradient(135deg, #7F00FF 0%, #E100FF 100%);
    --radius: 16px;
    --radius-sm: 10px;
    --shadow-card: 0 4px 24px rgba(0,0,0,0.25);
    --shadow-glow: 0 0 40px var(--accent-glow);
    --font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ── Global resets ──────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: var(--font) !important;
}
.main .block-container {
    max-width: 1200px;
    padding: 2rem 2rem 4rem 2rem;
}
#MainMenu, footer, header, [data-testid="stHeader"] { display: none !important; }

/* ── Streamlit element overrides ────────────────────────────── */
.stTextInput > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: var(--font) !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}
.stTextInput label, .stSelectbox label { display: none !important; }

.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
}

div.stButton > button {
    background: var(--gradient-cool) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 1.5rem !important;
    letter-spacing: 0.3px;
    transition: transform 0.15s, box-shadow 0.2s;
}
div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-glow) !important;
}

/* ── Plotly chart backgrounds ───────────────────────────────── */
[data-testid="stPlotlyChart"] {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius);
    padding: 0.5rem;
}

/* ── Divider ────────────────────────────────────────────────── */
hr { border-color: var(--border-subtle) !important; }

/* ── Tabs ───────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--bg-card);
    border-radius: var(--radius-sm);
    padding: 4px;
    border: 1px solid var(--border-subtle);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: var(--text-secondary) !important;
    font-family: var(--font) !important;
    font-weight: 500;
    padding: 0.5rem 1.25rem;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #fff !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }
.stTabs [data-baseweb="tab-border"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Helper: metric card HTML ─────────────────────────────────────────────────
def metric_card(icon, value, label, gradient="var(--bg-card)", span=1):
    return f"""
    <div style="
        background: {gradient};
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius);
        padding: 1.5rem 1.75rem;
        box-shadow: var(--shadow-card);
        grid-column: span {span};
        transition: transform 0.2s;
    " onmouseover="this.style.transform='translateY(-3px)'"
       onmouseout="this.style.transform='translateY(0)'">
        <div style="font-size:1.6rem; margin-bottom:0.5rem;">{icon}</div>
        <div style="font-family:var(--font); font-size:1.85rem; font-weight:700; color:var(--text-primary); line-height:1.1;">{value}</div>
        <div style="font-family:var(--font); font-size:0.78rem; color:var(--text-secondary); text-transform:uppercase; letter-spacing:1.2px; margin-top:0.4rem; font-weight:500;">{label}</div>
    </div>"""


# ── Initialize API ───────────────────────────────────────────────────────────
api = WeatherAPI()

# ── Brand header ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:1.5rem 0 0.5rem 0;">
    <div style="font-family:var(--font); font-size:0.85rem; font-weight:600; letter-spacing:3px; text-transform:uppercase; color:var(--accent); margin-bottom:0.4rem;">WeatherPro</div>
    <div style="font-family:var(--font); font-size:2.4rem; font-weight:800; color:var(--text-primary); line-height:1.15;">Weather Analytics</div>
    <div style="font-family:var(--font); font-size:1rem; color:var(--text-secondary); margin-top:0.3rem;">Real-time forecasts &amp; meteorological insights</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Search bar ───────────────────────────────────────────────────────────────
s1, s2, s3 = st.columns([3, 1.2, 1])
with s1:
    location = st.text_input("Location", "London", placeholder="Search city or coordinates…", label_visibility="collapsed")
with s2:
    units = st.selectbox("Units", ["Celsius", "Fahrenheit"], label_visibility="collapsed")
with s3:
    search_button = st.button("Search  🔍", use_container_width=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── Fetch & render ───────────────────────────────────────────────────────────
try:
    current_weather = api.get_current_weather(location, units)
    forecast_data = api.get_forecast(location, units)

    temp_unit = "°C" if units == "Celsius" else "°F"
    speed_unit = "km/h" if units == "Celsius" else "mph"
    weather_icon = WEATHER_ICONS.get(current_weather.get('icon', '01d'), '🌤️')

    # ── Location pill ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center; margin:0.75rem 0 1.5rem 0;">
        <span style="
            display:inline-block;
            background: var(--bg-card);
            border:1px solid var(--border-subtle);
            border-radius:50px;
            padding:0.45rem 1.4rem;
            font-family:var(--font);
            font-size:0.85rem;
            font-weight:500;
            color:var(--text-secondary);
            letter-spacing:0.5px;
        ">📍 {location.title()} &nbsp;·&nbsp; {datetime.now().strftime('%A, %B %d')}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Hero: current weather ────────────────────────────────────────────────
    st.markdown(f"""
    <div style="
        background: var(--gradient-cool);
        border-radius: var(--radius);
        padding: 2.5rem 3rem;
        box-shadow: var(--shadow-glow);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1.5rem;
    ">
        <div>
            <div style="font-family:var(--font); font-size:4.5rem; font-weight:900; color:#fff; line-height:1;">{current_weather['temp']}{temp_unit}</div>
            <div style="font-family:var(--font); font-size:1.05rem; color:rgba(255,255,255,0.7); margin-top:0.4rem;">Feels like {current_weather['feels_like']}{temp_unit}</div>
            <div style="
                display:inline-block;
                margin-top:0.75rem;
                background:rgba(255,255,255,0.18);
                border-radius:50px;
                padding:0.35rem 1rem;
                font-family:var(--font);
                font-size:0.85rem;
                font-weight:500;
                color:#fff;
                backdrop-filter:blur(4px);
            ">{current_weather['description']}</div>
        </div>
        <div style="font-size:5.5rem; line-height:1; opacity:0.85;">{weather_icon}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Metric cards grid ────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="
        display:grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    ">
        {metric_card("💧", f"{current_weather['humidity']}%", "Humidity")}
        {metric_card("💨", f"{current_weather['wind_speed']} {speed_unit}", "Wind Speed")}
        {metric_card("🌡️", f"{current_weather['pressure']} hPa", "Pressure")}
        {metric_card("🧭", f"{current_weather['wind_deg']}°", "Wind Direction")}
    </div>
    """, unsafe_allow_html=True)

    # ── Section divider helper ───────────────────────────────────────────────
    def section_heading(title):
        st.markdown(f"""
        <div style="font-family:var(--font); font-size:1.25rem; font-weight:700; color:var(--text-primary); margin:2rem 0 1rem 0;">{title}</div>
        """, unsafe_allow_html=True)

    # ── Forecast tabs ────────────────────────────────────────────────────────
    section_heading("📊  Forecast")
    tab_temp, tab_precip, tab_wind = st.tabs(["🌡️ Temperature", "🌧️ Precipitation", "🧭 Wind"])

    with tab_temp:
        st.plotly_chart(create_forecast_chart(forecast_data, 'temperature', units), use_container_width=True)
    with tab_precip:
        st.plotly_chart(create_forecast_chart(forecast_data, 'precipitation', units), use_container_width=True)
    with tab_wind:
        st.plotly_chart(create_wind_rose(forecast_data), use_container_width=True)

    # ── Map ──────────────────────────────────────────────────────────────────
    section_heading("🗺️  Weather Map")
    weather_map = create_weather_map(current_weather['coord'])
    st.components.v1.html(weather_map._repr_html_(), height=480)

    # ── Footer ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding:3rem 0 1rem 0;">
        <div style="font-family:var(--font); font-size:0.75rem; color:var(--text-secondary); letter-spacing:0.5px;">
            © 2026 WeatherPro &nbsp;·&nbsp; Powered by WeatherAPI
        </div>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.markdown(f"""
    <div style="
        background: var(--bg-card);
        border: 1px solid rgba(255,107,107,0.3);
        border-radius: var(--radius);
        padding: 3rem 2rem;
        text-align: center;
        margin-top: 3rem;
    ">
        <div style="font-size:2.5rem; margin-bottom:1rem;">⚠️</div>
        <div style="font-family:var(--font); font-size:1.2rem; font-weight:600; color:#FF6B6B; margin-bottom:0.5rem;">Weather Data Unavailable</div>
        <div style="font-family:var(--font); font-size:0.9rem; color:var(--text-secondary);">{str(e)}</div>
        <div style="font-family:var(--font); font-size:0.85rem; color:var(--text-secondary); margin-top:0.75rem;">Check your API key or try a different location.</div>
    </div>
    """, unsafe_allow_html=True)
