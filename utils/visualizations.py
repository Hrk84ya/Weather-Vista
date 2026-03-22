import plotly.graph_objects as go
import pandas as pd
import folium

# ── Shared theme ─────────────────────────────────────────────────────────────
_C = {
    'accent': '#6C63FF', 'cyan': '#48C6EF', 'green': '#38ef7d',
    'orange': '#FF8E53', 'red': '#FF6B6B', 'purple': '#E100FF',
    'text': '#f0f2f6', 'dim': 'rgba(240,242,246,0.45)',
    'grid': 'rgba(255,255,255,0.04)', 'bg': 'rgba(0,0,0,0)',
}

_AXIS = dict(
    showgrid=True, gridcolor=_C['grid'], gridwidth=1, zeroline=False,
    tickfont=dict(size=10, color=_C['dim']),
    title_font=dict(size=11, color=_C['dim']),
)

_HOVER = dict(
    bgcolor='rgba(15,17,23,0.92)', bordercolor='rgba(255,255,255,0.08)',
    font=dict(family="Inter, sans-serif", color=_C['text'], size=13),
)

_BASE = dict(
    plot_bgcolor=_C['bg'], paper_bgcolor=_C['bg'],
    font=dict(family="Inter, -apple-system, sans-serif", size=12, color=_C['text']),
    margin=dict(t=50, l=50, r=30, b=50),
    hovermode='x unified', hoverlabel=_HOVER,
    xaxis=_AXIS.copy(), yaxis=_AXIS.copy(),
)

def _layout(**overrides):
    """Merge _BASE with overrides so duplicate keys don't cause errors."""
    merged = dict(_BASE)
    merged.update(overrides)
    return merged


# ── Temperature chart with range selector + feels-like overlay ───────────────
def create_forecast_chart(hourly_data, chart_type, units):
    df = pd.DataFrame(hourly_data)

    if chart_type == 'temperature':
        temp_unit = "°C" if units == "Celsius" else "°F"
        fig = go.Figure()

        # Feels-like band
        fig.add_trace(go.Scatter(
            x=df['datetime'], y=df['feels_like'],
            mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip',
        ))
        fig.add_trace(go.Scatter(
            x=df['datetime'], y=df['temp'],
            fill='tonexty', mode='none',
            fillcolor='rgba(108,99,255,0.08)',
            showlegend=False, hoverinfo='skip',
        ))

        # Actual temp
        fig.add_trace(go.Scatter(
            x=df['datetime'], y=df['temp'],
            mode='lines+markers', name='Temperature',
            line=dict(color=_C['accent'], width=2.5, shape='spline'),
            marker=dict(size=4, color=_C['accent'], line=dict(width=1.5, color='#0f1117')),
            hovertemplate='<b>%{x|%a %d, %H:%M}</b><br>Temp: %{y:.1f}' + temp_unit + '<extra></extra>',
        ))
        # Feels-like line
        fig.add_trace(go.Scatter(
            x=df['datetime'], y=df['feels_like'],
            mode='lines', name='Feels like',
            line=dict(color=_C['cyan'], width=1.5, dash='dot', shape='spline'),
            hovertemplate='Feels: %{y:.1f}' + temp_unit + '<extra></extra>',
        ))

        fig.update_layout(**_layout(
            title=dict(text=f'Temperature ({temp_unit})', font=dict(size=15, color=_C['text']), x=0),
            xaxis_tickformat='%H:%M<br>%d %b',
            yaxis_title=temp_unit,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                        font=dict(size=11, color=_C['dim'])),
            xaxis_rangeslider=dict(visible=True, bgcolor='rgba(255,255,255,0.02)',
                                   bordercolor='rgba(255,255,255,0.06)', borderwidth=1, thickness=0.06),
        ))

    elif chart_type == 'precipitation':
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['datetime'], y=df['precipitation'], name='Rain %',
            marker=dict(
                color=df['precipitation'],
                colorscale=[[0, _C['cyan']], [0.5, _C['accent']], [1, _C['red']]],
                line=dict(width=0), opacity=0.85, cornerradius=4,
            ),
            hovertemplate='<b>%{x|%a %d, %H:%M}</b><br>%{y}%<extra></extra>',
        ))
        # Humidity overlay
        fig.add_trace(go.Scatter(
            x=df['datetime'], y=df['humidity'],
            mode='lines', name='Humidity %',
            line=dict(color=_C['cyan'], width=1.5, shape='spline'),
            yaxis='y2',
            hovertemplate='Humidity: %{y}%<extra></extra>',
        ))
        fig.update_layout(**_layout(
            title=dict(text='Precipitation & Humidity', font=dict(size=15, color=_C['text']), x=0),
            xaxis_tickformat='%H:%M<br>%d %b',
            yaxis_title='Rain %', bargap=0.3,
            yaxis2=dict(title='Humidity %', overlaying='y', side='right',
                        showgrid=False, tickfont=dict(size=10, color=_C['dim']),
                        title_font=dict(size=11, color=_C['dim'])),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                        font=dict(size=11, color=_C['dim'])),
            xaxis_rangeslider=dict(visible=True, bgcolor='rgba(255,255,255,0.02)',
                                   bordercolor='rgba(255,255,255,0.06)', borderwidth=1, thickness=0.06),
        ))

    elif chart_type == 'humidity_temp':
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['temp'], y=df['humidity'],
            mode='markers', name='Hourly',
            marker=dict(
                size=8, color=df['wind_speed'],
                colorscale=[[0, _C['cyan']], [0.5, _C['accent']], [1, _C['purple']]],
                showscale=True, opacity=0.8,
                colorbar=dict(title='Wind', tickfont=dict(size=9, color=_C['dim']),
                              titlefont=dict(size=10, color=_C['dim']), len=0.6),
                line=dict(width=0.5, color='rgba(255,255,255,0.15)'),
            ),
            text=df['datetime'].dt.strftime('%a %H:%M'),
            hovertemplate='<b>%{text}</b><br>Temp: %{x:.1f}<br>Humidity: %{y}%<br><extra></extra>',
        ))
        temp_unit = "°C" if units == "Celsius" else "°F"
        fig.update_layout(**_layout(
            title=dict(text='Temperature vs Humidity', font=dict(size=15, color=_C['text']), x=0),
            xaxis_title=f'Temperature ({temp_unit})', yaxis_title='Humidity (%)',
            hovermode='closest',
        ))

    return fig


# ── Wind rose ────────────────────────────────────────────────────────────────
def create_wind_rose(hourly_data):
    df = pd.DataFrame(hourly_data)
    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        r=df['wind_speed'], theta=df['wind_deg'],
        marker=dict(
            color=df['wind_speed'],
            colorscale=[[0, _C['cyan']], [0.5, _C['accent']], [1, _C['purple']]],
            line=dict(width=0), opacity=0.8,
            colorbar=dict(title=dict(text="Speed", font=dict(size=11, color=_C['dim'])),
                          tickfont=dict(size=10, color=_C['dim']), bgcolor=_C['bg'], borderwidth=0, len=0.6),
        ),
        hovertemplate='<b>%{theta}°</b><br>Speed: %{r:.1f}<extra></extra>',
    ))
    fig.update_layout(
        paper_bgcolor=_C['bg'], plot_bgcolor=_C['bg'],
        font=dict(family="Inter, sans-serif", color=_C['text']),
        title=dict(text='Wind Direction & Speed', font=dict(size=15, color=_C['text']), x=0),
        margin=dict(t=50, l=40, r=40, b=40), showlegend=False,
        polar=dict(
            bgcolor=_C['bg'],
            radialaxis=dict(showticklabels=True, gridcolor='rgba(255,255,255,0.06)',
                            tickfont=dict(size=9, color=_C['dim'])),
            angularaxis=dict(direction="clockwise", rotation=90,
                             gridcolor='rgba(255,255,255,0.06)',
                             tickfont=dict(size=10, color=_C['dim'])),
        ),
    )
    return fig


# ── Multi-city comparison chart ──────────────────────────────────────────────
def create_comparison_chart(city_data_map, metric, units):
    """city_data_map: {city_name: hourly_list}"""
    palette = [_C['accent'], _C['cyan'], _C['green'], _C['orange'], _C['red'], _C['purple']]
    temp_unit = "°C" if units == "Celsius" else "°F"
    fig = go.Figure()

    for i, (city, hourly) in enumerate(city_data_map.items()):
        df = pd.DataFrame(hourly)
        color = palette[i % len(palette)]
        y_col = metric
        fig.add_trace(go.Scatter(
            x=df['datetime'], y=df[y_col],
            mode='lines', name=city.title(),
            line=dict(color=color, width=2, shape='spline'),
            hovertemplate=f'<b>{city.title()}</b><br>' + '%{x|%a %H:%M}<br>%{y:.1f}<extra></extra>',
        ))

    labels = {'temp': f'Temperature ({temp_unit})', 'humidity': 'Humidity (%)',
              'wind_speed': 'Wind Speed', 'precipitation': 'Rain Chance (%)'}
    fig.update_layout(**_layout(
        title=dict(text=f'City Comparison — {labels.get(metric, metric)}',
                   font=dict(size=15, color=_C['text']), x=0),
        xaxis_tickformat='%H:%M<br>%d %b',
        yaxis_title=labels.get(metric, metric),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                    font=dict(size=11, color=_C['dim'])),
        xaxis_rangeslider=dict(visible=True, bgcolor='rgba(255,255,255,0.02)',
                               bordercolor='rgba(255,255,255,0.06)', borderwidth=1, thickness=0.06),
    ))
    return fig


# ── Daily detail chart (single day hourly) ───────────────────────────────────
def create_daily_detail_chart(hourly_data, selected_date, units):
    df = pd.DataFrame(hourly_data)
    df_day = df[df['date'] == selected_date].copy()
    temp_unit = "°C" if units == "Celsius" else "°F"

    fig = go.Figure()
    # Temp area
    fig.add_trace(go.Scatter(
        x=df_day['datetime'], y=df_day['temp'],
        fill='tozeroy', mode='lines+markers', name='Temp',
        fillcolor='rgba(108,99,255,0.12)',
        line=dict(color=_C['accent'], width=2.5, shape='spline'),
        marker=dict(size=6, color=_C['accent'], line=dict(width=1.5, color='#0f1117')),
        hovertemplate='<b>%{x|%H:%M}</b><br>%{y:.1f}' + temp_unit + '<extra></extra>',
    ))
    # Cloud cover
    fig.add_trace(go.Bar(
        x=df_day['datetime'], y=df_day['cloud'], name='Cloud %',
        marker=dict(color='rgba(255,255,255,0.08)', line=dict(width=0)),
        yaxis='y2',
        hovertemplate='Cloud: %{y}%<extra></extra>',
    ))

    fig.update_layout(**_layout(
        title=dict(text=f'Hourly Detail — {selected_date}', font=dict(size=15, color=_C['text']), x=0),
        xaxis_tickformat='%H:%M', yaxis_title=temp_unit,
        yaxis2=dict(title='Cloud %', overlaying='y', side='right', range=[0, 100],
                    showgrid=False, tickfont=dict(size=10, color=_C['dim']),
                    title_font=dict(size=11, color=_C['dim'])),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                    font=dict(size=11, color=_C['dim'])),
        bargap=0.4,
    ))
    return fig


# ── Weather map ──────────────────────────────────────────────────────────────
def create_weather_map(coordinates, extra_cities=None):
    """Dark-themed map. extra_cities: list of {name, lat, lon, temp, description}"""
    m = folium.Map(location=[coordinates['lat'], coordinates['lon']], zoom_start=11, tiles=None)

    folium.TileLayer(
        'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        attr='© OpenStreetMap © CARTO', name='Dark', overlay=False, control=True,
    ).add_to(m)
    folium.TileLayer(
        'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        attr='© OpenStreetMap © CARTO', name='Light', overlay=False, control=True,
    ).add_to(m)

    # Primary marker
    _add_marker(m, coordinates['lat'], coordinates['lon'], '📍 Primary Location', '#6C63FF')

    # Extra city markers
    if extra_cities:
        colors = ['#48C6EF', '#38ef7d', '#FF8E53', '#FF6B6B', '#E100FF']
        for i, city in enumerate(extra_cities):
            label = f"{city['name']}: {city['temp']} — {city['description']}"
            _add_marker(m, city['lat'], city['lon'], label, colors[i % len(colors)])
        # Fit bounds
        lats = [coordinates['lat']] + [c['lat'] for c in extra_cities]
        lons = [coordinates['lon']] + [c['lon'] for c in extra_cities]
        m.fit_bounds([[min(lats) - 1, min(lons) - 1], [max(lats) + 1, max(lons) + 1]])

    folium.LayerControl().add_to(m)
    return m


def _add_marker(m, lat, lon, label, color):
    folium.CircleMarker(
        location=[lat, lon], radius=10,
        popup=folium.Popup(label, parse_html=True),
        color=color, weight=2, fill=True, fillColor=color, fillOpacity=0.7,
    ).add_to(m)
    folium.CircleMarker(
        location=[lat, lon], radius=22,
        color=color, weight=1, fill=True, fillColor=color, fillOpacity=0.12,
    ).add_to(m)
