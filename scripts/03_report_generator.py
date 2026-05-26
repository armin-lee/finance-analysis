"""
Script 3: Client Report Generator
===================================
Input  : data/cleaned/, data/output/, assets/
Output : reports/finance_analysis_report.html

Generate laporan HTML profesional yang bisa:
- Dibuka di browser
- Di-print ke PDF
- Dikirim ke klien sebagai deliverable
"""

import pandas as pd
import os
import base64
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────
CLEANED_PATH = "../data/cleaned/personal_finance_clean.csv"
SUMMARY_PATH = "../data/output/eda_summary.csv"
ASSETS_DIR   = "../assets"
REPORT_PATH  = "../reports/finance_analysis_report.html"
os.makedirs("../reports", exist_ok=True)
# ─────────────────────────────────────────────────────────────────────────────

def img_to_base64(path: str) -> str:
    """Convert image to base64 untuk embed di HTML."""
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def load_data():
    df      = pd.read_csv(CLEANED_PATH, parse_dates=["date"])
    summary = pd.read_csv(SUMMARY_PATH).set_index("metric")["value"].to_dict()
    return df, summary


def format_currency(val) -> str:
    try:
        return f"${float(val):,.2f}"
    except:
        return str(val)


def generate_report(df, summary):
    expenses = df[df["type"] == "Expense"]
    income   = df[df["type"] == "Income"]

    # Category breakdown table
    cat_table = expenses.groupby("category")["amount"].agg(["sum", "count", "mean"])\
        .sort_values("sum", ascending=False).reset_index()
    cat_table.columns = ["Category", "Total", "Transactions", "Avg per Transaction"]
    cat_table["% of Total"] = (cat_table["Total"] / cat_table["Total"].sum() * 100).round(1)

    cat_rows = ""
    for _, row in cat_table.iterrows():
        cat_rows += f"""
        <tr>
            <td><span class="badge">{row['Category']}</span></td>
            <td class="amount">{format_currency(row['Total'])}</td>
            <td>{int(row['Transactions'])}</td>
            <td class="amount">{format_currency(row['Avg per Transaction'])}</td>
            <td>
                <div class="bar-wrap">
                    <div class="bar-fill" style="width:{row['% of Total']}%"></div>
                    <span>{row['% of Total']}%</span>
                </div>
            </td>
        </tr>"""

    # Monthly summary table
    monthly = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0).reset_index()
    if "Income" not in monthly.columns: monthly["Income"] = 0
    if "Expense" not in monthly.columns: monthly["Expense"] = 0
    monthly["Cashflow"] = monthly["Income"] - monthly["Expense"]
    monthly["Status"] = monthly["Cashflow"].apply(lambda x: "🟢 Surplus" if x >= 0 else "🔴 Deficit")
    monthly = monthly.sort_values("month", ascending=False).head(12)

    monthly_rows = ""
    for _, row in monthly.iterrows():
        cf_class = "positive" if row["Cashflow"] >= 0 else "negative"
        monthly_rows += f"""
        <tr>
            <td>{row['month']}</td>
            <td class="amount">{format_currency(row.get('Income', 0))}</td>
            <td class="amount">{format_currency(row.get('Expense', 0))}</td>
            <td class="amount {cf_class}">{format_currency(row['Cashflow'])}</td>
            <td>{row['Status']}</td>
        </tr>"""

    # Encode images
    charts = {
        "monthly_trend":    img_to_base64(f"{ASSETS_DIR}/01_monthly_trend.png"),
        "by_category":      img_to_base64(f"{ASSETS_DIR}/02_spending_by_category.png"),
        "cashflow":         img_to_base64(f"{ASSETS_DIR}/03_monthly_cashflow.png"),
        "category_trend":   img_to_base64(f"{ASSETS_DIR}/04_category_trend.png"),
        "day_of_week":      img_to_base64(f"{ASSETS_DIR}/05_day_of_week.png"),
    }

    def img_tag(key):
        b64 = charts.get(key, "")
        if not b64:
            return "<p>Chart not available</p>"
        return f'<img src="data:image/png;base64,{b64}" style="width:100%;border-radius:8px;">'

    # Savings rate color
    savings_rate = float(summary.get("savings_rate_pct", 0))
    sr_color = "#2E86AB" if savings_rate >= 0 else "#C73E1D"
    sr_label = "Surplus" if savings_rate >= 0 else "Deficit"

    # Key insights
    top_cat = summary.get("top_category", "N/A")
    top_cat_amount = format_currency(summary.get("top_category_amount", 0))
    avg_monthly_expense = format_currency(summary.get("avg_monthly_expense", 0))
    outliers = summary.get("outliers_flagged", 0)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Personal Finance Analysis Report</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: #F4F6F9; color: #2D3748; }}

  .header {{ background: linear-gradient(135deg, #2E86AB, #1a5276); color: white; padding: 40px; }}
  .header h1 {{ font-size: 28px; margin-bottom: 6px; }}
  .header p {{ opacity: 0.85; font-size: 14px; }}

  .container {{ max-width: 1100px; margin: 0 auto; padding: 30px 20px; }}

  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 24px 0; }}
  .kpi-card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,.07); border-top: 4px solid #2E86AB; }}
  .kpi-card.red {{ border-top-color: #C73E1D; }}
  .kpi-card.green {{ border-top-color: #44BBA4; }}
  .kpi-card.orange {{ border-top-color: #F18F01; }}
  .kpi-label {{ font-size: 12px; color: #718096; text-transform: uppercase; letter-spacing: .5px; }}
  .kpi-value {{ font-size: 22px; font-weight: 700; margin-top: 6px; }}
  .kpi-sub {{ font-size: 11px; color: #A0AEC0; margin-top: 4px; }}

  .section {{ background: white; border-radius: 10px; padding: 24px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,.07); }}
  .section h2 {{ font-size: 18px; margin-bottom: 16px; color: #2D3748; border-left: 4px solid #2E86AB; padding-left: 12px; }}

  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ background: #F7FAFC; padding: 10px 12px; text-align: left; font-weight: 600; color: #4A5568; border-bottom: 2px solid #E2E8F0; }}
  td {{ padding: 9px 12px; border-bottom: 1px solid #F0F4F8; }}
  tr:hover td {{ background: #F7FAFC; }}
  .amount {{ font-family: monospace; font-weight: 600; }}
  .positive {{ color: #2E86AB; }}
  .negative {{ color: #C73E1D; }}

  .badge {{ background: #EBF8FF; color: #2E86AB; padding: 2px 8px; border-radius: 12px; font-size: 12px; }}

  .bar-wrap {{ display: flex; align-items: center; gap: 8px; }}
  .bar-fill {{ height: 8px; background: #2E86AB; border-radius: 4px; min-width: 2px; }}

  .insight-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }}
  .insight-card {{ background: #F7FAFC; border-radius: 8px; padding: 16px; border-left: 3px solid #2E86AB; }}
  .insight-card h4 {{ font-size: 13px; color: #4A5568; margin-bottom: 6px; }}
  .insight-card p {{ font-size: 14px; font-weight: 600; color: #2D3748; }}

  .footer {{ text-align: center; padding: 24px; color: #A0AEC0; font-size: 12px; }}
  .chart-grid {{ display: grid; grid-template-columns: 1fr; gap: 20px; }}
  .chart-grid.two-col {{ grid-template-columns: 1fr 1fr; }}

  @media print {{
    body {{ background: white; }}
    .section {{ box-shadow: none; border: 1px solid #E2E8F0; page-break-inside: avoid; }}
  }}
</style>
</head>
<body>

<div class="header">
  <h1>📊 Personal Finance Analysis Report</h1>
  <p>Analysis Period: {summary.get('date_range', 'N/A')} &nbsp;|&nbsp; Generated: {datetime.now().strftime('%B %d, %Y')} &nbsp;|&nbsp; Total Transactions: {int(float(summary.get('total_transactions', 0))):,}</p>
</div>

<div class="container">

  <!-- KPI Cards -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">Total Income</div>
      <div class="kpi-value">{format_currency(summary.get('total_income', 0))}</div>
      <div class="kpi-sub">Avg {format_currency(summary.get('avg_monthly_income', 0))}/month</div>
    </div>
    <div class="kpi-card red">
      <div class="kpi-label">Total Expense</div>
      <div class="kpi-value">{format_currency(summary.get('total_expense', 0))}</div>
      <div class="kpi-sub">Avg {avg_monthly_expense}/month</div>
    </div>
    <div class="kpi-card {'green' if savings_rate >= 0 else 'red'}">
      <div class="kpi-label">Net Savings</div>
      <div class="kpi-value" style="color:{sr_color}">{format_currency(summary.get('total_savings', 0))}</div>
      <div class="kpi-sub">{savings_rate:.1f}% savings rate ({sr_label})</div>
    </div>
    <div class="kpi-card orange">
      <div class="kpi-label">Top Expense Category</div>
      <div class="kpi-value" style="font-size:18px">{top_cat}</div>
      <div class="kpi-sub">{top_cat_amount} total</div>
    </div>
  </div>

  <!-- Key Insights -->
  <div class="section">
    <h2>💡 Key Insights</h2>
    <div class="insight-grid">
      <div class="insight-card">
        <h4>Highest Spending Category</h4>
        <p>{top_cat} — {top_cat_amount}</p>
      </div>
      <div class="insight-card">
        <h4>Average Monthly Expense</h4>
        <p>{avg_monthly_expense}</p>
      </div>
      <div class="insight-card">
        <h4>Anomalies Detected</h4>
        <p>{outliers} transactions flagged as outliers</p>
      </div>
      <div class="insight-card">
        <h4>Financial Status</h4>
        <p style="color:{sr_color}">{sr_label} — {abs(savings_rate):.1f}% {"saved" if savings_rate >= 0 else "over budget"}</p>
      </div>
    </div>
  </div>

  <!-- Charts -->
  <div class="section">
    <h2>📈 Monthly Income vs Expense</h2>
    {img_tag("monthly_trend")}
  </div>

  <div class="section">
    <h2>💰 Monthly Cashflow</h2>
    {img_tag("cashflow")}
  </div>

  <div class="section">
    <h2>🏷️ Spending by Category</h2>
    {img_tag("by_category")}
  </div>

  <div class="section">
    <h2>📅 Category Spending Trend</h2>
    {img_tag("category_trend")}
  </div>

  <div class="section">
    <h2>📆 Spending by Day of Week</h2>
    {img_tag("day_of_week")}
  </div>

  <!-- Category Table -->
  <div class="section">
    <h2>🗂️ Expense Breakdown by Category</h2>
    <table>
      <thead>
        <tr>
          <th>Category</th>
          <th>Total Spent</th>
          <th>Transactions</th>
          <th>Avg per Transaction</th>
          <th>% of Total</th>
        </tr>
      </thead>
      <tbody>{cat_rows}</tbody>
    </table>
  </div>

  <!-- Monthly Table -->
  <div class="section">
    <h2>📅 Monthly Summary (Last 12 Months)</h2>
    <table>
      <thead>
        <tr>
          <th>Month</th>
          <th>Income</th>
          <th>Expense</th>
          <th>Cashflow</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>{monthly_rows}</tbody>
    </table>
  </div>

</div>

<div class="footer">
  <p>Report generated by Finance Data Analysis Tool &nbsp;|&nbsp; {datetime.now().strftime('%Y-%m-%d %H:%M')} &nbsp;|&nbsp; Confidential</p>
</div>

</body>
</html>"""

    return html


def main():
    print("\nLoading data...")
    df, summary = load_data()

    print("Generating HTML report...")
    html = generate_report(df, summary)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    file_size = os.path.getsize(REPORT_PATH) / 1024
    print(f"\n✅ Report saved: {REPORT_PATH}")
    print(f"   File size: {file_size:.1f} KB")
    print(f"   Open di browser untuk preview")


if __name__ == "__main__":
    main()
