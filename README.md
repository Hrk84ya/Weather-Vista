# ⛅ WeatherPro

Premium weather analytics dashboard built with Python and Streamlit. Dark-themed UI with interactive charts, multi-city comparison, and real-time forecasting.

## Features

- Real-time current weather with detailed metrics (temp, humidity, wind, pressure, UV, cloud cover)
- 5-day forecast with expandable daily cards showing hourly breakdowns
- Interactive Plotly charts with range sliders and dual-axis overlays
- Temperature vs Humidity scatter analysis (color-coded by wind speed)
- Multi-city comparison — add up to 5 cities and compare any metric side by side
- Dark-themed Folium map with all compared cities plotted
- Auto-refresh toggle (5-minute interval)

## Tech Stack

- **Streamlit** — app framework and UI
- **Plotly** — interactive charts (temperature, precipitation, wind rose, scatter)
- **Folium** — interactive maps with dark/light tile layers
- **WeatherAPI** — weather data provider
- **Pandas** — data wrangling

## Setup

1. Clone the repo:
   ```bash
   git clone <repo-url>
   cd Weather-Vista
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your [WeatherAPI](https://www.weatherapi.com/) key:
   ```
   WEATHERAPI_KEY=your_api_key_here
   ```

4. Run the app:
   ```bash
   streamlit run weather_app.py
   ```

## Project Structure

```
├── weather_app.py            # Main Streamlit app
├── utils/
│   ├── weather_api.py        # WeatherAPI client
│   └── visualizations.py     # Plotly charts & Folium map
├── assets/
│   └── weather_icons.py      # Emoji icon mapping
├── requirements.txt
└── .env                      # API key (not committed)
```

## License

See [LICENSE](LICENSE) for details.
