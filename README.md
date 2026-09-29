# DataSense AI

**AI-Powered Data Analyzer - Runs Completely Offline, No API Required**

![DataSense AI](https://img.shields.io/badge/Version-1.0.0-blue)
![Platform-Windows](https://img.shields.io/badge/Platform-Windows-green)
![License-MIT](https://img.shields.io/badge/License-MIT-yellow)

## Overview

DataSense AI is a powerful desktop application that provides AI-powered data analysis without relying on any external APIs. All analysis is performed locally using state-of-the-art machine learning libraries.

## Features

### 🤖 AI-Powered Analysis
- **Auto-Analysis**: One-click comprehensive data analysis
- **Pattern Detection**: Identify trends, cycles, and anomalies
- **Clustering**: K-means clustering for grouping data
- **Classification**: Decision tree for categorical prediction
- **Regression**: Linear regression for predictions
- **Outlier Detection**: Statistical outlier identification

### 📊 Visualization
- Line Charts
- Bar Charts
- Scatter Plots
- Histograms
- Pie Charts
- Box Plots

### 📈 Statistics
- Descriptive Statistics (mean, median, std, quartiles)
- Correlation Analysis
- Distribution Analysis
- Hypothesis Testing

### 💾 Data Support
- **Import**: CSV, Excel (.xlsx), JSON, TSV
- **Export**: CSV, Excel, PNG (charts)

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows 10/11

### Setup

1. **Install Python** (if not already installed)
   - Download from [python.org](https://www.python.org/downloads/)
   - Ensure to check "Add Python to PATH"

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   python run.py
   ```

## Quick Start

### Flask Web App

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask backend**
   ```bash
   python web_app.py
   ```

3. **Open the browser**
   Visit `http://127.0.0.1:5000`

4. **Upload data**
   Upload a CSV or Excel file to see:
   - NaN / blank value counts
   - Numeric zero counts
   - Zero-like text values such as `0` and `0.0`
   - Per-column data quality
   - Numeric statistics
   - Duplicate rows
   - Strong correlations
   - First 10 preview rows

5. **Use chatbot instructions**
   Add an instruction before analyzing, or upload once and use the chatbot box below the results:
   - `show only NaN columns`
   - `show zeros only`
   - `show top 5 rows`
   - `show only correlations`
   - `show numeric stats`
   - `summary only`

### Desktop App

1. **Launch the app**: Run `python run.py`
2. **Import Data**: Click "📂 Import" or use File → Import Data
3. **Select a file**: Choose CSV, Excel, or JSON file
4. **Run AI Analysis**: Click "🤖 AI Analyze" button
5. **View Results**: Switch between tabs to explore insights, charts, and statistics

## Project Structure

```
DataSense AI/
├── run.py                 # Application entry point
├── main.py                # Main application setup
├── SPEC.md                # Detailed specification
├── requirements.txt       # Python dependencies
├── ui/
│   └── main_window.py    # Main UI window
├── core/
│   ├── data_manager.py   # Data loading & manipulation
│   ├── ml_engine.py      # Local ML algorithms
│   ├── visualization_engine.py  # Chart creation
│   ├── statistics_engine.py     # Statistical analysis
│   └── insight_generator.py     # Natural language insights
└── assets/
    └── (icon files)
```

## Technical Stack

| Component | Technology |
|-----------|------------|
| GUI Framework | PyQt6 |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Statistics | SciPy |
| Visualization | Matplotlib |

**All dependencies are local packages - NO external AI APIs required**

## System Requirements

- **OS**: Windows 10 or higher
- **RAM**: 4 GB minimum (8 GB recommended)
- **Storage**: 500 MB for installation
- **Display**: 1280x800 or higher resolution

## Troubleshooting

### Import Errors
If you encounter import errors, ensure all dependencies are installed:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Display Issues
The application uses QtAgg backend for matplotlib. If charts don't display:
```bash
pip install PyQt6
```

### Memory Issues
For large datasets (>100MB), the app may show memory warnings. Consider:
- Sampling the data before import
- Closing other applications
- Using 64-bit Python

## License

MIT License - See LICENSE file for details.

## Credits

Built with:
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI
- [Pandas](https://pandas.pydata.org/) - Data analysis
- [Scikit-learn](https://scikit-learn.org/) - Machine learning
- [Matplotlib](https://matplotlib.org/) - Visualization

---

**Note**: This application runs entirely offline with no external API dependencies. All AI/ML operations are performed locally on your machine.


## Deploying to Vercel

- Entry point is configured in `pyproject.toml` (`web_app:app`).
- `requirements.txt` contains web-only dependencies; desktop packages are in `requirements-desktop.txt`.
- Set an environment variable `SECRET_KEY` (any long random string) in Vercel project settings.
- Note: on Vercel, user accounts are stored in `/tmp` and are not persistent. Use a real database for production.
