# Interactive-Vehicle-Registration-Growth-Dashboard-for-Investor-Insights
An interactive web dashboard for analyzing and visualizing vehicle registration trends across manufacturers and categories in India. Calculates key growth metrics — Year-over-Year (YoY) and Quarter-over-Quarter (QoQ) — with powerful filtering and comparison features for investor insights.

---

## 📦 Setup Instructions

### 1. Clone Repository

git clone <your_repo_url>
cd <your_repo_name>

text

### 2. Create Virtual Environment (Recommended)
python -m venv venv

Activate virtual environment
Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

text

### 3. Install Dependencies
pip install -r requirements.txt

text

### 4. Prepare Raw Data
- Place raw Excel files in:
raw_data/maker/<year>/<file>.xlsx

text
**Example Structure:**
raw_data/
└── maker/
├── 2021/
│ ├── two_reportTable.xlsx
│ ├── three_reportTable.xlsx
│ └── four_reportTable.xlsx
├── 2022/
│ └── ...


### 5. Process Data
Run the processing script to generate `master_Data.csv`:
python process.py

text

### 6. Run the Dashboard
streamlit run app.py
Open http://localhost:8501 in your web browser.

---

## 📊 Data Assumptions
- **Data Source**: Official Vahan portal (or equivalent Excel exports)
- **File Naming**: Filenames must include `two`, `three`, or `four` for category detection.
- **One File per Category per Year** in `raw_data/maker/<year>/`
- **Header Format**: Actual headers start at 5th row (index 4 in pandas).
- **Variable Month Columns**: Supports years with fewer than 12 months of data.
- **Numeric Values**: All registration values converted to numeric (commas and text cleaned).
- Includes **ALL_MAKERS** totals per category for aggregated analysis.

---

## 🚀 Feature Roadmap
1. **Export Options** — Download filtered views as CSV/Excel.
2. **KPI Cards** — Highlight top and bottom performers.
3. **Regional Maps** — Add state/region-level visualization.
4. **Enhanced Charts** — Area charts, scatter plots, trend overlays.
5. **Auto-Updates** — Monthly ingestion from APIs.
6. **Forecasting** — Predictive models for upcoming quarters.

---

## 📂 Repository Structure
├── README.md # Documentation (this file)
├── requirements.txt # Python dependencies
├── process.py # Data processing script
├── app.py # Streamlit dashboard app
├── master_Data.csv # Processed dataset (optional, can be generated)
├── raw_data.zip/ # Folder containing all raw Excel files
│ └── maker/
│ ├── 2021/
│ ├── 2022/
│ └── ...

---

## 🛠 Tech Stack
- **Python** — Core programming language
- **pandas** — Data processing and aggregation  
- **openpyxl** — Excel file reading  
- **Streamlit** — Interactive dashboard framework  
- **Plotly** — Interactive data visualization  
- **Pathlib** — File path handling

---

## 🙌 Author
Siddhartha — Data Analyst and AI Engineer
