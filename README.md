# 📊 Personal Finance Data Analysis

> An end-to-end data analysis pipeline for personal finance data — from raw CSV to a professional HTML report with charts, insights, and monthly summaries.

---

## 🔍 Overview

This project demonstrates a complete data analyst workflow:

1. **Data Cleaning** — handle missing values, duplicates, outliers, and type fixes
2. **Exploratory Data Analysis** — trends, category breakdowns, cashflow analysis
3. **Visualization** — 5 professional charts (PNG)
4. **Client Report** — self-contained HTML report with embedded charts and tables

**Use case:** A freelance data analyst receives a client's raw finance CSV and delivers a clean dataset + professional report as the final deliverable.

---

## 📁 Project Structure

```
finance_analysis/
│
├── scripts/
│   ├── generate_dataset.py       # Generate sample dataset (for demo/testing)
│   ├── 01_data_cleaning.py       # Clean & validate raw data
│   ├── 02_eda_visualization.py   # EDA & chart generation
│   └── 03_report_generator.py   # HTML report generator
│
├── data/
│   ├── raw/                      # Raw input data (not committed to Git)
│   ├── cleaned/                  # Cleaned output + cleaning log
│   └── output/                   # EDA summary CSV
│
├── assets/                       # Generated charts (PNG)
├── reports/                      # Final HTML report for client
│
├── run_all.py                    # Run full pipeline in one command
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

---

## ⚙️ Setup

### Prerequisites
- Python 3.9 or higher
- pip

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/finance-analysis.git
cd finance-analysis
```

### 2. Create virtual environment
```bash
python -m venv venv
```

### 3. Activate virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

### Option A — Run full pipeline (recommended)
```bash
python run_all.py
```

This runs all scripts in order and generates the complete output.

### Option B — Run scripts individually
```bash
# Step 1: Generate sample data (skip if you have your own CSV)
python scripts/generate_dataset.py

# Step 2: Clean the data
python scripts/01_data_cleaning.py

# Step 3: Generate charts
python scripts/02_eda_visualization.py

# Step 4: Generate HTML report
python scripts/03_report_generator.py
```

---

## 📥 Using Your Own Data

Replace the sample dataset with your own CSV file:

1. Place your CSV in `data/raw/` and name it `personal_finance_raw.csv`
2. Ensure your CSV has these columns:

| Column | Type | Example |
|--------|------|---------|
| `date` | Date (YYYY-MM-DD) | 2024-03-15 |
| `category` | String | Food |
| `description` | String | Grocery Store |
| `amount` | Float | 45.50 |
| `type` | String | Expense / Income |
| `payment_method` | String | Credit Card |
| `notes` | String | *(optional)* |

3. Run `python run_all.py`

---

## 📊 Sample Output

### Key Metrics
| Metric | Value |
|--------|-------|
| Analysis Period | 2023–2024 (24 months) |
| Total Transactions | ~1,500 |
| Charts Generated | 5 |
| Report Format | HTML (print to PDF) |

### Charts Included
| # | Chart | Description |
|---|-------|-------------|
| 1 | Monthly Trend | Income vs Expense line chart |
| 2 | Category Breakdown | Pie + bar chart by category |
| 3 | Monthly Cashflow | Surplus/deficit bar chart |
| 4 | Category Trend | Top 5 categories over time |
| 5 | Day of Week | Average spending by weekday |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.9+ | Core language |
| pandas | Data manipulation & cleaning |
| matplotlib | Chart generation |
| seaborn | Enhanced visualizations |
| openpyxl | Excel file support |

---

## 📋 Data Cleaning Steps

The cleaning script (`01_data_cleaning.py`) performs:

- ✅ Fix data types (date → datetime, amount → float)
- ✅ Fill missing values (description, payment_method → "Unknown")
- ✅ Remove duplicate rows
- ✅ Validate amount values (remove ≤ 0)
- ✅ Flag statistical outliers (> mean + 3×std per category)
- ✅ Add derived columns (month_name, week, day_of_week)
- ✅ Generate cleaning log with full audit trail

---

## ⚠️ Known Limitations

- Report is HTML-based — to get PDF, use browser's Print → Save as PDF
- Dataset generator uses synthetic data for demo purposes only
- Google Trends and external APIs are not used in this pipeline

---

## 📄 License

MIT License — free to use and modify for personal or commercial projects.

---

## 👤 Author

Built as a portfolio project for freelance data analytics services.
For inquiries, reach out via [Fiverr](https://www.fiverr.com) or [LinkedIn].
