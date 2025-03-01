import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import folium

def create_forecast_chart(forecast_data, chart_type, units):
    """Create forecast visualization charts with enhanced styling"""
    df = pd.DataFrame(forecast_data)

    # Common layout settings
    layout = dict(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, l=0, r=0, b=0),
        font=dict(family="Arial, sans-serif"),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            tickformat='%H:%M\n%d %b'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)'
        )
    )

    if chart_type == 'temperature':
        temp_unit = "°C" if units == "metric" else "°F"
        fig = px.line(
            df,
            x='datetime',
            y='temp',
            title=f'Temperature Forecast ({temp_unit})',
            labels={'temp': f'Temperature ({temp_unit})', 'datetime': 'Date & Time'}
        )
        fig.update_traces(
            line_color='#FF9F1C',
            line_width=3,
            mode='lines+markers',
            marker=dict(size=6, color='#FF9F1C')
        )

    elif chart_type == 'precipitation':
        fig = px.bar(
            df,
            x='datetime',
            y='precipitation',
            title='Precipitation Probability',
            labels={'precipitation': 'Probability (%)', 'datetime': 'Date & Time'}
        )
        fig.update_traces(
            marker_color='#2EC4B6',
            marker_line_width=0,
            opacity=0.7
        )

    fig.update_layout(**layout)

    return fig

def create_wind_rose(forecast_data):
    """Create enhanced wind rose chart"""
    df = pd.DataFrame(forecast_data)

    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        r=df['wind_speed'],
        theta=df['wind_deg'],
        name='Wind Speed',
        marker_color='#011627',
        opacity=0.7
    ))

    fig.update_layout(
        title=dict(
            text='Wind Direction and Speed',
            font=dict(family="Arial, sans-serif", size=20)
        ),
        polar=dict(
            radialaxis=dict(
                showticklabels=True,
                ticks='',
                gridcolor='rgba(0,0,0,0.1)'
            ),
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                gridcolor='rgba(0,0,0,0.1)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig

def create_weather_map(coordinates):
    """Create an enhanced interactive weather map"""
    m = folium.Map(
        location=[coordinates['lat'], coordinates['lon']],
        zoom_start=10,
        tiles='CartoDB positron'  # Using a cleaner map style
    )

    # Add a styled marker for the location
    folium.CircleMarker(
        location=[coordinates['lat'], coordinates['lon']],
        radius=8,
        popup='Selected Location',
        color='#0066cc',
        fill=True,
        fillColor='#0066cc',
        fillOpacity=0.7
    ).add_to(m)

    return m