# 🚨 DC Crime Incidents Dashboard

An interactive Streamlit dashboard for exploring crime incident data in Washington, D.C. — filter by date, shift, offense type, method, district, and neighborhood cluster, and uncover patterns across time and geography.

🔗 **Live Demo:** [https://personal-projects-ghugelonfqersrahdxeha6.streamlit.app]
📦 **Repository:** [https://github.com/iiSeefii/Personal-Projects/tree/main/Projects/Crime_Death_Incidents]

---

## ✨ Features

- **Dynamic filtering** — date range, shift, offense type, method, district, and neighborhood cluster, all from a single sidebar
- **KPI summary row** — total incidents, armed crime rate, median reporting gap, most common offense, and most affected district
- **Time trends** — monthly incident volume and offense type distribution
- **Timing patterns** — crimes by shift, and a day-of-week × hour heatmap
- **Geographic view** — interactive incident map plus a per-district breakdown
- **Neighborhood analysis** — top 10 clusters by incident count, and crime method by offense type
- **Duration & reporting gap analysis** — histogram of incident duration and boxplot of reporting delay by offense
- **Auto-generated quick insights** — peak hour/day, weapon involvement rate, slowest-to-report offense
- **Raw data explorer** — expandable table of the filtered dataset with CSV export

## 🛠️ Tech Stack

- **Streamlit** — dashboard framework and UI
- **Pandas / NumPy** — data processing, feature engineering, duration parsing
- **Plotly Express** — all charts (line, pie, bar, heatmap, scatter map, histogram, box)
- **Openpyxl** — reading the Excel dataset

## 📊 Dataset

The dashboard reads from `crime_data_cleaned.xlsx`, a cleaned version of Washington, D.C.'s public crime incident data. Preparation (done separately, outside this script) included:

- Reverse geocoding to enrich neighborhood/location data
- Feature engineering for incident duration and reporting gap
- Datetime parsing and cleanup
- Export to Excel format

Key columns used: `START_DATE`, `REPORT_DAT`, `SHIFT`, `OFFENSE`, `METHOD`, `DISTRICT`, `NEIGHBORHOOD_CLUSTER`, `LATITUDE`, `LONGITUDE`, `INCIDENT_DURATION`, `REPORTING_GAP`.

> **Note:** The dataset file isn't included in this repo (data files are usually excluded from version control). Place `crime_data_cleaned.xlsx` in the same directory as `Dashboard.py` before running.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd <your-repo-folder>

# (Optional) create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the app

```bash
cd 'Projects/Crime_Death_Incidents'
streamlit run Dashboard.py
```

The app will open automatically in your browser at `http://localhost:8501`.

## 📁 Project Structure

```
.
├── Dashboard.py              # Main Streamlit app
├── requirements.txt          # Python dependencies
├── crime_data_cleaned.xlsx   # Dataset (not included — see Dataset section)
└── README.md
```

## 💡 Key Insights Surfaced

The dashboard automatically highlights:
- Peak incident hour and most frequent day of the week
- Percentage of incidents involving a weapon (firearm or knife)
- The offense type with the longest median reporting delay


## 👤 Author

Built by **Seif**
[GitHub](https://github.com/iiSeefii) · [LinkedIn](https://www.linkedin.com/in/seif-muhammad1112/) · [Email](https://mail.google.com/mail/u/0/?fs=1&to=iiseefii17@gmail.com&tf=cm)
