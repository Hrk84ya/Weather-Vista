import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from utils.weather_api import WeatherAPI
from utils.visualizations import (
    create_forecast_chart, create_wind_rose, create_weather_map,
    create_comparison_chart, create_daily_detail_chart,
)
from assets.weather_icons import WEATHER_ICONS

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WeatherPro — Premium Weather Analytics",
    page_icon="⛅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Premium CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
:root {
    --bg-primary: #0f1117;
    --bg-card: rgba(255,255,255,0.04);
    --border-subtle: rgba(255,255,255,0.06);
    --text-primary: #f0f2f6;
    --text-secondary: rgba(240,242,246,0.55);
    --accent: #6C63FF;
    --accent-glow: rgba(108,99,255,0.35);
    --gradient-cool: linear-gradient(135deg, #6C63FF 0%, #48C6EF 100%);
    --gradient-green: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    --radius: 16px;
    --radius-sm: 10px;
    --shadow-card: 0 4px 24px rgba(0,0,0,0.25);
    --shadow-glow: 0 0 40px var(--accent-glow);
    --font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: var(--font) !important;
}
.main .block-container { max-width: 1200px; padding: 2rem 2rem 4rem 2rem; }
#MainMenu, footer, header, [data-testid="stHeader"] { display: none !important; }

/* Inputs */
.stTextInput > div > div > input {
    background: var(--bg-card) !important; border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important; color: var(--text-primary) !important;
    font-family: var(--font) !important; font-size: 1rem !important; padding: 0.75rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important; box-shadow: 0 0 0 3px var(--accent-glow) !important;
}
.stTextInput label, .stSelectbox label { display: none !important; }
.stSelectbox > div > div {
    background: var(--bg-card) !important; border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important; color: var(--text-primary) !important;
}
div.stButton > button {
    background: var(--gradient-cool) !important; color: #fff !important; border: none !important;
    border-radius: var(--radius-sm) !important; font-family: var(--font) !important;
    font-weight: 600 !important; font-size: 0.95rem !important; padding: 0.7rem 1.5rem !important;
    transition: transform 0.15s, box-shadow 0.2s;
}
div.stButton > button:hover { transform: translateY(-1px); box-shadow: var(--shadow-glow) !important; }

/* Charts */
[data-testid="stPlotlyChart"] {
    background: var(--bg-card); border: 1px solid var(--border-subtle);
    border-radius: var(--radius); padding: 0.5rem;
}
hr { border-color: var(--border-subtle) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0; background: var(--bg-card); border-radius: var(--radius-sm);
    padding: 4px; border: 1px solid var(--border-subtle);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; color: var(--text-secondary) !important;
    font-family: var(--font) !important; font-weight: 500; padding: 0.5rem 1.25rem;
}
.stTabs [aria-selected="true"] { background: var(--accent) !important; color: #fff !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* Expander */
.streamlit-expanderHeader {
    background: var(--bg-card) !important; border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important; color: var(--text-primary) !important;
    font-family: var(--font) !important; font-weight: 600 !important;
}
.streamlit-expanderContent {
    background: var(--bg-card) !important; border: 1px solid var(--border-subtle) !important;
    border-top: none !important; border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
}

/* Toggle */
.stCheckbox label span { color: var(--text-secondary) !important; font-family: var(--font) !important; }

/* Slider */
[data-testid="stSlider"] label { color: var(--text-secondary) !important; font-family: var(--font) !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────
def metric_card(icon, value, label, gradient="var(--bg-card)"):
    return f"""
    <div style="background:{gradient}; border:1px solid var(--border-subtle); border-radius:var(--radius);
        padding:1.5rem 1.75rem; box-shadow:var(--shadow-card); transition:transform 0.2s;"
        onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="font-size:1.6rem; margin-bottom:0.5rem;">{icon}</div>
        <div style="font-family:var(--font); font-size:1.85rem; font-weight:700; color:var(--text-primary); line-height:1.1;">{value}</div>
        <div style="font-family:var(--font); font-size:0.78rem; color:var(--text-secondary); text-transform:uppercase;
            letter-spacing:1.2px; margin-top:0.4rem; font-weight:500;">{label}</div>
    </div>"""

def section_heading(title):
    st.markdown(f'<div style="font-family:var(--font); font-size:1.25rem; font-weight:700; color:var(--text-primary); margin:2rem 0 1rem 0;">{title}</div>', unsafe_allow_html=True)

# ── Session state defaults ───────────────────────────────────────────────────
if "compare_cities" not in st.session_state:
    st.session_state.compare_cities = []
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

api = WeatherAPI()

# ── Brand header ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:1.5rem 0 0.5rem 0;">
    <div style="font-family:var(--font); font-size:0.85rem; font-weight:600; letter-spacing:3px; text-transform:uppercase; color:var(--accent); margin-bottom:0.4rem;">WeatherPro</div>
    <div style="font-family:var(--font); font-size:2.4rem; font-weight:800; color:var(--text-primary); line-height:1.15;">Weather Analytics</div>
    <div style="font-family:var(--font); font-size:1rem; color:var(--text-secondary); margin-top:0.3rem;">Real-time forecasts &amp; meteorological insights</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Search bar ───────────────────────────────────────────────────────────────
s1, s2, s3, s4 = st.columns([3, 1, 1, 1])
with s1:
    location = st.text_input("Location", "London", placeholder="Search city or coordinates…", label_visibility="collapsed")
with s2:
    units = st.selectbox("Units", ["Celsius", "Fahrenheit"], label_visibility="collapsed")
with s3:
    st.button("Search  🔍", use_container_width=True)
with s4:
    auto_refresh = st.checkbox("⟳ Auto-refresh", value=st.session_state.auto_refresh, key="auto_refresh_cb")
    st.session_state.auto_refresh = auto_refresh

# Auto-refresh every 5 minutes
if st.session_state.auto_refresh:
    st.markdown('<div style="font-family:var(--font); font-size:0.75rem; color:var(--text-secondary); text-align:right; margin-top:-0.5rem;">Refreshes every 5 min</div>', unsafe_allow_html=True)
    import time
    st.empty()
    # Use st.rerun with a timer placeholder
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = time.time()
    if time.time() - st.session_state.last_refresh > 300:
        st.session_state.last_refresh = time.time()
        st.rerun()

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)


# ── Multi-city comparison bar ────────────────────────────────────────────────
with st.expander("🏙️  Compare multiple cities", expanded=False):
    cc1, cc2 = st.columns([3, 1])
    with cc1:
        new_city = st.text_input("Add city", "", placeholder="Type a city name…", key="add_city_input", label_visibility="collapsed")
    with cc2:
        add_clicked = st.button("➕ Add", use_container_width=True, key="add_city_btn")

    if add_clicked and new_city.strip():
        city_clean = new_city.strip().title()
        if city_clean not in st.session_state.compare_cities and len(st.session_state.compare_cities) < 5:
            st.session_state.compare_cities.append(city_clean)
            st.rerun()

    if st.session_state.compare_cities:
        pills_html = ""
        for city in st.session_state.compare_cities:
            pills_html += f'<span style="display:inline-block; background:var(--bg-card); border:1px solid var(--border-subtle); border-radius:50px; padding:0.3rem 1rem; margin:0.25rem 0.3rem; font-family:var(--font); font-size:0.82rem; color:var(--text-primary);">{city}</span>'
        st.markdown(f'<div style="margin:0.5rem 0;">{pills_html}</div>', unsafe_allow_html=True)

        if st.button("🗑️ Clear all cities", key="clear_cities"):
            st.session_state.compare_cities = []
            st.rerun()

# ── Fetch primary data ───────────────────────────────────────────────────────
try:
    current_weather = api.get_current_weather(location, units)
    forecast_result = api.get_forecast(location, units)
    hourly_data = forecast_result["hourly"]
    daily_data = forecast_result["daily"]

    temp_unit = "°C" if units == "Celsius" else "°F"
    speed_unit = "km/h" if units == "Celsius" else "mph"
    weather_icon = WEATHER_ICONS.get(current_weather.get('icon', '01d'), '🌤️')

    # ── Location pill ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center; margin:0.75rem 0 1.5rem 0;">
        <span style="display:inline-block; background:var(--bg-card); border:1px solid var(--border-subtle);
            border-radius:50px; padding:0.45rem 1.4rem; font-family:var(--font); font-size:0.85rem;
            font-weight:500; color:var(--text-secondary); letter-spacing:0.5px;">
            📍 {current_weather['location_name']}, {current_weather['country']}
            &nbsp;·&nbsp; {datetime.now().strftime('%A, %B %d')}
            &nbsp;·&nbsp; Local: {current_weather.get('localtime', '')}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Hero card ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:var(--gradient-cool); border-radius:var(--radius); padding:2.5rem 3rem;
        box-shadow:var(--shadow-glow); display:flex; align-items:center; justify-content:space-between;
        flex-wrap:wrap; gap:1rem; margin-bottom:1.5rem;">
        <div>
            <div style="font-family:var(--font); font-size:4.5rem; font-weight:900; color:#fff; line-height:1;">{current_weather['temp']}{temp_unit}</div>
            <div style="font-family:var(--font); font-size:1.05rem; color:rgba(255,255,255,0.7); margin-top:0.4rem;">Feels like {current_weather['feels_like']}{temp_unit}</div>
            <div style="display:inline-block; margin-top:0.75rem; background:rgba(255,255,255,0.18);
                border-radius:50px; padding:0.35rem 1rem; font-family:var(--font); font-size:0.85rem;
                font-weight:500; color:#fff; backdrop-filter:blur(4px);">{current_weather['description']}</div>
        </div>
        <div style="font-size:5.5rem; line-height:1; opacity:0.85;">{weather_icon}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Metric cards ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(160px, 1fr)); gap:1rem; margin-bottom:2rem;">
        {metric_card("💧", f"{current_weather['humidity']}%", "Humidity")}
        {metric_card("💨", f"{current_weather['wind_speed']} {speed_unit}", "Wind Speed")}
        {metric_card("🌡️", f"{current_weather['pressure']} hPa", "Pressure")}
        {metric_card("🧭", f"{current_weather['wind_deg']}°", "Wind Dir")}
        {metric_card("☀️", f"{current_weather['uv']}", "UV Index")}
        {metric_card("☁️", f"{current_weather['cloud']}%", "Cloud Cover")}
    </div>
    """, unsafe_allow_html=True)


    # ── Daily forecast cards (expandable) ────────────────────────────────────
    section_heading("📅  5-Day Outlook")
    for day in daily_data:
        day_icon = WEATHER_ICONS.get(day.get('icon', '01d'), '🌤️')
        day_date = datetime.strptime(day['date'], '%Y-%m-%d')
        day_label = day_date.strftime('%A, %b %d')
        header = f"{day_icon}  {day_label}  —  {day['min_temp']:.0f}° / {day['max_temp']:.0f}°  ·  {day['condition']}"

        with st.expander(header, expanded=False):
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("🌡️ Avg Temp", f"{day['avg_temp']:.1f}{temp_unit}")
            d2.metric("💧 Humidity", f"{day['avg_humidity']}%")
            d3.metric("💨 Max Wind", f"{day['max_wind']} {speed_unit}")
            d4.metric("🌧️ Rain", f"{day['chance_of_rain']}%")

            d5, d6, d7, d8 = st.columns(4)
            precip_label = "mm" if units == "Celsius" else "in"
            d5.metric("🌧️ Precip", f"{day['total_precip']} {precip_label}")
            d6.metric("☀️ UV", f"{day['uv']}")
            d7.metric("🌅 Sunrise", day['sunrise'])
            d8.metric("🌇 Sunset", day['sunset'])

            # Hourly detail chart for this day
            st.plotly_chart(
                create_daily_detail_chart(hourly_data, day['date'], units),
                use_container_width=True, key=f"detail_{day['date']}"
            )

    # ── Interactive forecast charts ──────────────────────────────────────────
    section_heading("📊  Forecast Explorer")
    tab_temp, tab_precip, tab_scatter, tab_wind = st.tabs([
        "🌡️ Temperature", "🌧️ Precipitation", "🔬 Temp vs Humidity", "🧭 Wind"
    ])
    with tab_temp:
        st.plotly_chart(create_forecast_chart(hourly_data, 'temperature', units), use_container_width=True)
    with tab_precip:
        st.plotly_chart(create_forecast_chart(hourly_data, 'precipitation', units), use_container_width=True)
    with tab_scatter:
        st.plotly_chart(create_forecast_chart(hourly_data, 'humidity_temp', units), use_container_width=True)
    with tab_wind:
        st.plotly_chart(create_wind_rose(hourly_data), use_container_width=True)

    # ── Multi-city comparison ────────────────────────────────────────────────
    if st.session_state.compare_cities:
        section_heading("🏙️  City Comparison")
        city_data_map = {location.title(): hourly_data}
        extra_markers = []

        for city in st.session_state.compare_cities:
            try:
                cw = api.get_current_weather(city, units)
                cf = api.get_forecast(city, units)
                city_data_map[city] = cf["hourly"]
                extra_markers.append({
                    "name": city, "lat": cw["coord"]["lat"], "lon": cw["coord"]["lon"],
                    "temp": f"{cw['temp']}{temp_unit}", "description": cw["description"],
                })
            except Exception:
                st.warning(f"Could not fetch data for {city}")

        if len(city_data_map) > 1:
            compare_metric = st.selectbox(
                "Compare metric", ["temp", "humidity", "wind_speed", "precipitation"],
                format_func=lambda x: {"temp": "🌡️ Temperature", "humidity": "💧 Humidity",
                                       "wind_speed": "💨 Wind Speed", "precipitation": "🌧️ Rain Chance"}[x],
                label_visibility="collapsed",
            )
            st.plotly_chart(create_comparison_chart(city_data_map, compare_metric, units), use_container_width=True)

            # Map with all cities
            section_heading("🗺️  Cities on Map")
            weather_map = create_weather_map(current_weather['coord'], extra_markers)
            st.components.v1.html(weather_map._repr_html_(), height=480)
        else:
            section_heading("🗺️  Weather Map")
            weather_map = create_weather_map(current_weather['coord'])
            st.components.v1.html(weather_map._repr_html_(), height=480)
    else:
        # ── Map (single city) ────────────────────────────────────────────────
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
    <div style="background:var(--bg-card); border:1px solid rgba(255,107,107,0.3); border-radius:var(--radius);
        padding:3rem 2rem; text-align:center; margin-top:3rem;">
        <div style="font-size:2.5rem; margin-bottom:1rem;">⚠️</div>
        <div style="font-family:var(--font); font-size:1.2rem; font-weight:600; color:#FF6B6B; margin-bottom:0.5rem;">Weather Data Unavailable</div>
        <div style="font-family:var(--font); font-size:0.9rem; color:var(--text-secondary);">{str(e)}</div>
        <div style="font-family:var(--font); font-size:0.85rem; color:var(--text-secondary); margin-top:0.75rem;">Check your API key or try a different location.</div>
    </div>
    """, unsafe_allow_html=True)
