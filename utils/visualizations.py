import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import folium

# ── Shared theme ─────────────────────────────────────────────────────────────
_COLORS = {
    'accent': '#6C63FF',
    'cyan': '#48C6EF',
    'green': '#38ef7d',
    'orange': '#FF8E53',
    'red': '#FF6B6B',
    'text': '#f0f2f6',
    'text_dim': 'rgba(240,242,246,0.45)',
    'grid': 'rgba(255,255,255,0.04)',
    'bg': 'rgba(0,0,0,0)',
}

_LAYOUT_BASE = dict(
    plot_bgcolor=_COLORS['bg'],
    paper_bgcolor=_COLORS['bg'],
    font=dict(family="Inter, -apple-system, sans-serif", size=12, color=_COLORS['text']),
    margin=dict(t=50, l=50, r=30, b=50),
    hovermode='x unified',
    hoverlabel=dict(
        bgcolor='rgba(15,17,23,0.92)',
        bordercolor='rgba(255,255,255,0.08)',
        font=dict(family="Inter, sans-serif", color=_COLORS['text'], size=13),
    ),
    xaxis=dict(
        showgrid=True, gridcolor=_COLORS['grid'], gridwidth=1,
        zeroline=False,
        tickfont=dict(size=10, color=_COLORS['text_dim']),
        title_font=dict(size=11, color=_COLORS['text_dim']),
    ),
    yaxis=dict(
        showgrid=True, gridcolor=_COLORS['grid'], gridwidth=1,
        zeroline=False,
        tickfont=dict(size=10, color=_COLORS['text_dim']),
        title_font=dict(size=11, color=_COLORS['text_dim']),
    ),
)


def create_forecast_chart(forecast_data, chart_type, units):
    """Create premium forecast charts with dark theme."""
    df = pd.DataFrame(forecast_data)

    if chart_type == 'temperature':
        temp_unit = "°C" if units == "Celsius" else "°F"
        fig = go.Figure()

        # Gradient area fill
        fig.add_trace(go.Scatter(
            x=df['datetime'], y=df['temp'],
            fill='tozeroy',
            mode='none',
            fillcolor='rgba(108,99,255,0.10)',
            showlegend=False,
            hoverinfo='skip',
        ))
        # Main line
        fig.add_trace(go.Scatter(
            x=df['datetime'], y=df['temp'],
            mode='lines+markers',
            line=dict(color=_COLORS['accent'], width=2.5, shape='spline'),
            marker=dict(size=4, color=_COLORS['accent'], line=dict(width=1.5, color='#0f1117')),
            name='Temperature',
            hovertemplate='<b>%{x|%a %d, %H:%M}</b><br>%{y:.1f}' + temp_unit + '<extra></extra>',
        ))

        fig.update_layout(
            **_LAYOUT_BASE,
            title=dict(text=f'Temperature ({temp_unit})', font=dict(size=15, color=_COLORS['text']), x=0, xanchor='left'),
            xaxis_tickformat='%H:%M<br>%d %b',
            yaxis_title=temp_unit,
        )

    elif chart_type == 'precipitation':
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['datetime'], y=df['precipitation'],
            marker=dict(
                color=df['precipitation'],
                colorscale=[[0, _COLORS['cyan']], [0.5, _COLORS['accent']], [1, _COLORS['red']]],
                line=dict(width=0),
                opacity=0.85,
                cornerradius=4,
            ),
            hovertemplate='<b>%{x|%a %d, %H:%M}</b><br>%{y}%<extra></extra>',
            name='Precipitation',
        ))
        fig.update_layout(
            **_LAYOUT_BASE,
            title=dict(text='Precipitation Probability (%)', font=dict(size=15, color=_COLORS['text']), x=0, xanchor='left'),
            xaxis_tickformat='%H:%M<br>%d %b',
            yaxis_title='%',
            bargap=0.3,
        )

    return fig


def create_wind_rose(forecast_data):
    """Create premium wind rose with dark theme."""
    df = pd.DataFrame(forecast_data)

    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        r=df['wind_speed'],
        theta=df['wind_deg'],
        marker=dict(
            color=df['wind_speed'],
            colorscale=[[0, _COLORS['cyan']], [0.5, _COLORS['accent']], [1, '#E100FF']],
            line=dict(width=0),
            opacity=0.8,
            colorbar=dict(
                title=dict(text="Speed", font=dict(size=11, color=_COLORS['text_dim'])),
                tickfont=dict(size=10, color=_COLORS['text_dim']),
                bgcolor=_COLORS['bg'],
                borderwidth=0,
                len=0.6,
            ),
        ),
        hovertemplate='<b>%{theta}°</b><br>Speed: %{r:.1f}<extra></extra>',
    ))

    fig.update_layout(
        paper_bgcolor=_COLORS['bg'],
        plot_bgcolor=_COLORS['bg'],
        font=dict(family="Inter, sans-serif", color=_COLORS['text']),
        title=dict(text='Wind Direction & Speed', font=dict(size=15, color=_COLORS['text']), x=0, xanchor='left'),
        margin=dict(t=50, l=40, r=40, b=40),
        showlegend=False,
        polar=dict(
            bgcolor=_COLORS['bg'],
            radialaxis=dict(
                showticklabels=True, gridcolor='rgba(255,255,255,0.06)',
                tickfont=dict(size=9, color=_COLORS['text_dim']),
            ),
            angularaxis=dict(
                direction="clockwise", rotation=90,
                gridcolor='rgba(255,255,255,0.06)',
                tickfont=dict(size=10, color=_COLORS['text_dim']),
            ),
        ),
    )
    return fig


def create_weather_map(coordinates):
    """Create a dark-themed interactive weather map."""
    m = folium.Map(
        location=[coordinates['lat'], coordinates['lon']],
        zoom_start=11,
        tiles=None,
    )

    # Dark tile layer
    folium.TileLayer(
        'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        attr='© OpenStreetMap contributors © CARTO',
        name='Dark',
        overlay=False,
        control=True,
    ).add_to(m)

    # Light option
    folium.TileLayer(
        'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        attr='© OpenStreetMap contributors © CARTO',
        name='Light',
        overlay=False,
        control=True,
    ).add_to(m)

    # Pulsing marker
    folium.CircleMarker(
        location=[coordinates['lat'], coordinates['lon']],
        radius=10,
        popup=folium.Popup('📍 Selected Location', parse_html=True),
        color='#6C63FF',
        weight=2,
        fill=True,
        fillColor='#6C63FF',
        fillOpacity=0.7,
    ).add_to(m)

    # Outer glow ring
    folium.CircleMarker(
        location=[coordinates['lat'], coordinates['lon']],
        radius=22,
        color='#6C63FF',
        weight=1,
        fill=True,
        fillColor='#6C63FF',
        fillOpacity=0.12,
    ).add_to(m)

    folium.LayerControl().add_to(m)
    return m
