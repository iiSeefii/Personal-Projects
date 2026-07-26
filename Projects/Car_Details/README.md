# 🚗 Used Car Market — Instrument Cluster

A dark-themed, dashboard-style Streamlit app for exploring a used-car listings dataset (India). Built with Streamlit + Plotly Express, styled to look like a car instrument cluster (gauges, panels, amber/teal palette).

## Features

- **Filter console** — filter listings by Brand, Fuel type, Transmission, and Owner count, with a one-click reset.
- **Instrument cluster (KPI gauges)** — fleet size in view, average price, average kilometers driven, average car age.
- **Brand lineup** — bubble chart of average asking price per top 15 brands (bubble size = number of listings).
- **Fuel mix** — horizontal bar chart of listings by fuel type.
- **Model year trend** — median price by manufacture year.
- **Top cities** — top 10 cities by number of listings.
- **Geographic spread** — interactive map (bubble size = listings, color = avg. price) plus a matching data table.
- **Gearbox / Ownership / Price band** — manual vs automatic split, ownership history distribution, and price-band histogram.
- **Showroom floor** — table of the top 10 most expensive listings currently in view.
- **Dataset download** — button to download the original Excel file.

## Requirements

```bash
pip install streamlit plotly pandas numpy openpyxl
```

## Project files

| File | Purpose |
|---|---|
| `Dashboard.py` | Main Streamlit app |
| `location_coords.py` | Dictionary mapping city/location names to `(lat, lon)` coordinates, used for the map |
| `car_details_fixed.xlsx` | Dataset (2,059 used-car listings). Place it in the same folder as `Dashboard.py` |

If `car_details_fixed.xlsx` isn't found next to the script, the app will show a file-uploader so you can upload it manually at runtime.

## Expected dataset columns

The loader expects these columns in the Excel file:

`Brand`, `Model`, `Price`, `Year`, `Kilometers Driven`, `Fuel Type`, `Transmission`, `Location`, `Owner`, `Seller Type`, `Drivetrain`, `Seating Capacity`

## Run it

```bash
streamlit run Dashboard.py
```

The app opens in your browser at `http://localhost:8501`.

## Notes

- Built for exploratory analysis only — not a valuation tool.
- Dark theme uses the **Chakra Petch** and **Inter** Google Fonts (loaded via CDN, requires internet access on first load).
