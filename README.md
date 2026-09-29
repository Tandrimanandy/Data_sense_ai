<div align="center">

<h1>DataSense AI</h1>

<p><strong>AI-powered data analysis — fully offline, no external APIs required.</strong></p>

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.5%2B-41CD52?style=flat&logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E?style=flat&logo=scikitlearn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D4?style=flat&logo=windows&logoColor=white)](https://microsoft.com/windows)

</div>

---

## Overview

DataSense AI is a dual-interface data analysis platform — available as both a **desktop application** (PyQt6) and a **web application** (Flask) — that brings machine learning-powered insights to your data entirely on-device. No cloud services, no API keys, no internet connection required.

It is built for data analysts, researchers, business professionals, and students who need reliable, reproducible analysis with complete data privacy.

---

## Features

### 🤖 AI Analysis Engine (Local ML)
- **Auto-Analysis** — one-click comprehensive pipeline across all numeric features
- **Pattern Detection** — identifies trends, cycles, and structural anomalies
- **Clustering** — K-Means segmentation with silhouette scoring
- **Regression** — linear and decision-tree regression with R², MAE, and RMSE metrics
- **Classification** — Random Forest and Decision Tree classifiers with full report output
- **Outlier Detection** — statistical identification via Z-score and IQR methods
- **Correlation Analysis** — pairwise correlation matrix with threshold-based flagging
- **Natural Language Insights** — auto-generated plain-English summaries of results

### 📊 Visualization
- Line, Bar, Scatter, Histogram, Pie, and Box Plot charts
- Interactive zoom, pan, and hover tooltips
- Multi-series comparisons across variables
- One-click export to PNG

### 📈 Statistical Analysis
- Descriptive statistics (mean, median, std, quartiles, skewness, kurtosis)
- Distribution analysis
- Hypothesis testing (t-test, chi-square)
- Confidence intervals

### 💾 Data I/O
| Direction | Formats |
|-----------|---------|
| Import | CSV, Excel (`.xlsx`), JSON, TSV |
| Export | CSV, Excel, PNG (charts), PDF (report) |

### 🌐 Web Interface (Flask)
- User authentication (signup / login) with hashed passwords
- Upload and analyze files directly in-browser
- Inline chatbot for natural-language result filtering
- Data quality report: NaN counts, zero-value detection, duplicate rows, column stats
- Preview the first 10 rows alongside analysis results

---

## Architecture

```
DataSense AI/
├── run.py                        # Desktop app entry point
├── main.py                       # Application bootstrap
├── web_app.py                    # Flask web backend
├── requirements.txt
├── SPEC.md                       # Full product specification
│
├── core/
│   ├── data_manager.py           # Data loading, cleaning, transformation
│   ├── ml_engine.py              # Local ML algorithms (sklearn + scipy)
│   ├── visualization_engine.py   # Chart generation (matplotlib / seaborn)
│   ├── statistics_engine.py      # Statistical computations (numpy / scipy)
│   ├── insight_generator.py      # Natural language insight generation
│   └── web_analysis.py           # Web-specific analysis & chatbot routing
│
├── ui/
│   └── main_window.py            # PyQt6 desktop UI
│
└── templates/
    ├── index.html                # Web app dashboard
    ├── login.html                # Auth — login page
    └── signup.html               # Auth — signup page
```

**Data flow:**

```
UI Layer (PyQt6 / Flask)
        │
        ▼
  DataManager  ──►  MLEngine (scikit-learn)
        │                   │
        ▼                   ▼
   IO Handler         StatisticsEngine (NumPy / SciPy)
        │                   │
        └──────────┬─────────┘
                   ▼
        VisualizationEngine (Matplotlib)
                   │
                   ▼
          InsightGenerator (NL summaries)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Desktop GUI | PyQt6 |
| Web Backend | Flask + Werkzeug |
| Data Processing | Pandas, NumPy |
| Machine Learning | scikit-learn |
| Statistics | SciPy |
| Visualization | Matplotlib, Seaborn |
| Excel I/O | OpenPyXL |

> All dependencies are standard Python packages. **No external AI APIs are used at any point.**

---

## Getting Started

### Prerequisites

- Python **3.8** or higher
- Windows **10 / 11** (desktop app); any OS for the web app
- `pip`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Tandrimanandy/datasense-ai.git
cd datasense-ai

# 2. (Recommended) Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

---

### Running the Desktop App

```bash
python run.py
```

**Workflow:**
1. Click **📂 Import** or use *File → Import Data* to load a CSV, Excel, or JSON file.
2. Explore the data in the sortable, filterable table view.
3. Click **🤖 AI Analyze** to run the full local ML pipeline.
4. Switch between the **Insights**, **Charts**, and **Statistics** tabs to explore results.
5. Export charts or full reports via *File → Export*.

---

### Running the Web App

```bash
python web_app.py
```

Then open your browser and navigate to:

```
http://127.0.0.1:5000
```

**Workflow:**
1. Sign up for a local account (credentials are stored on-device only).
2. Upload a CSV or Excel file on the dashboard.
3. Review the auto-generated data quality report and summary statistics.
4. Use the chatbot input to filter or drill into specific results:

| Command | Effect |
|---------|--------|
| `show only NaN columns` | Highlights columns with missing values |
| `show zeros only` | Surfaces zero and zero-like values |
| `show top 5 rows` | Returns the first 5 preview rows |
| `show only correlations` | Filters to the correlation section |
| `show numeric stats` | Displays descriptive statistics only |
| `summary only` | Returns the high-level insight summary |

---

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | Windows 10 | Windows 11 |
| RAM | 4 GB | 8 GB |
| Storage | 500 MB | 1 GB |
| Display | 1280 × 800 | 1920 × 1080 |
| Python | 3.8 | 3.11+ |

---

## Troubleshooting

**Missing dependencies after install**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Charts not rendering in the desktop app**
PyQt6's QtAgg backend must be available. Reinstall if necessary:
```bash
pip install --force-reinstall PyQt6
```

**Memory warnings with large files (> 100 MB)**
- Consider sampling the dataset before import.
- Close other memory-intensive applications.
- Ensure you are using 64-bit Python (`python -c "import platform; print(platform.architecture())"`).

**Web app authentication issues**
User credentials are stored in `users.json` in the project root. If the file is corrupted, delete it and re-register.

---

## Roadmap

- [ ] Cross-platform desktop support (macOS, Linux)
- [ ] Additional chart types (heatmaps, violin plots, treemaps)
- [ ] Time-series specific analysis module
- [ ] PDF report export from the web interface
- [ ] Plugin architecture for custom analysis modules
- [ ] Dark mode for the desktop UI

---

## Contributing

Contributions are welcome. To get started:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request.

Please follow [PEP 8](https://pep8.org/) style conventions and include docstrings for all new functions and classes.

---

## License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for full terms.

---

## Acknowledgements

DataSense AI is built on top of outstanding open-source projects:

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) — cross-platform GUI toolkit
- [Flask](https://flask.palletsprojects.com/) — lightweight web framework
- [Pandas](https://pandas.pydata.org/) — data manipulation and analysis
- [scikit-learn](https://scikit-learn.org/) — machine learning algorithms
- [Matplotlib](https://matplotlib.org/) & [Seaborn](https://seaborn.pydata.org/) — data visualization
- [SciPy](https://scipy.org/) — scientific computing and statistics

---

<div align="center">
<sub>Built with ❤️ — fully offline, fully private, fully yours.</sub>
</div>
