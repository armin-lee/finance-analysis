"""
Script 2: Exploratory Data Analysis & Visualizations
======================================================
Input  : data/cleaned/personal_finance_clean.csv
Output : assets/ (semua chart PNG)
         data/output/eda_summary.csv

Yang dilakukan:
- Monthly income vs expense trend
- Spending by category (pie + bar)
- Monthly cashflow (savings)
- Top spending categories over time
- Day of week spending pattern
- Outlier visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings
warnings.filterwarnings("ignore")

# ── CONFIG ────────────────────────────────────────────────────────────────────
INPUT_PATH  = "../data/cleaned/personal_finance_clean.csv"
ASSETS_DIR  = "../assets"
OUTPUT_DIR  = "../data/output"
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Style
plt.rcParams.update({
    "figure.facecolor": "#FAFAFA",
    "axes.facecolor":   "#FAFAFA",
    "axes.grid":        True,
    "grid.alpha":       0.3,
    "font.family":      "DejaVu Sans",
    "axes.spines.top":  False,
    "axes.spines.right":False,
})
COLORS = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#3B1F2B",
          "#44BBA4", "#E94F37", "#393E41", "#F5A623", "#7B68EE"]
# ─────────────────────────────────────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    df = pd.read_csv(INPUT_PATH, parse_dates=["date"])
    return df


def chart1_monthly_trend(df):
    """Monthly Income vs Expense trend line chart."""
    monthly = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0).reset_index()
    monthly["month_dt"] = pd.to_datetime(monthly["month"])
    monthly = monthly.sort_values("month_dt")

    if "Income" not in monthly.columns:
        monthly["Income"] = 0
    if "Expense" not in monthly.columns:
        monthly["Expense"] = 0

    monthly["Savings"] = monthly["Income"] - monthly["Expense"]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(monthly["month_dt"], monthly["Income"],  marker="o", color="#2E86AB", linewidth=2.5, label="Income",  markersize=5)
    ax.plot(monthly["month_dt"], monthly["Expense"], marker="s", color="#C73E1D", linewidth=2.5, label="Expense", markersize=5)
    ax.fill_between(monthly["month_dt"],
                    monthly["Income"], monthly["Expense"],
                    where=monthly["Income"] >= monthly["Expense"],
                    alpha=0.1, color="#2E86AB", label="Surplus")
    ax.fill_between(monthly["month_dt"],
                    monthly["Income"], monthly["Expense"],
                    where=monthly["Income"] < monthly["Expense"],
                    alpha=0.1, color="#C73E1D", label="Deficit")

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_title("Monthly Income vs Expense (2023–2024)", fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("")
    ax.set_ylabel("Amount (USD)")
    ax.legend(framealpha=0.9)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    path = f"{ASSETS_DIR}/01_monthly_trend.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Saved: {path}")
    return monthly


def chart2_spending_by_category(df):
    """Spending breakdown by category — pie + bar side by side."""
    expenses = df[df["type"] == "Expense"]
    by_cat = expenses.groupby("category")["amount"].sum().sort_values(ascending=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Pie chart
    wedges, texts, autotexts = ax1.pie(
        by_cat.values,
        labels=by_cat.index,
        autopct="%1.1f%%",
        colors=COLORS[:len(by_cat)],
        startangle=140,
        pctdistance=0.85,
    )
    for t in autotexts:
        t.set_fontsize(9)
    ax1.set_title("Spending Distribution\nby Category", fontsize=14, fontweight="bold")

    # Bar chart
    bars = ax2.barh(by_cat.index[::-1], by_cat.values[::-1], color=COLORS[:len(by_cat)][::-1])
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax2.set_title("Total Spending by Category", fontsize=14, fontweight="bold")
    ax2.set_xlabel("Total Amount (USD)")

    for bar, val in zip(bars, by_cat.values[::-1]):
        ax2.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
                 f"${val:,.0f}", va="center", fontsize=9)

    plt.suptitle("Expense Analysis by Category (2023–2024)", fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()
    path = f"{ASSETS_DIR}/02_spending_by_category.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Saved: {path}")


def chart3_monthly_cashflow(df):
    """Monthly cashflow (savings) bar chart."""
    monthly = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0).reset_index()
    monthly["month_dt"] = pd.to_datetime(monthly["month"])
    monthly = monthly.sort_values("month_dt")

    if "Income" not in monthly.columns: monthly["Income"] = 0
    if "Expense" not in monthly.columns: monthly["Expense"] = 0

    monthly["Cashflow"] = monthly["Income"] - monthly["Expense"]
    colors = ["#2E86AB" if x >= 0 else "#C73E1D" for x in monthly["Cashflow"]]

    fig, ax = plt.subplots(figsize=(14, 6))
    bars = ax.bar(monthly["month_dt"], monthly["Cashflow"], color=colors, width=20, alpha=0.85)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_title("Monthly Cashflow (Income - Expense)", fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("")
    ax.set_ylabel("Cashflow (USD)")

    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor="#2E86AB", label="Surplus (saving)"),
                       Patch(facecolor="#C73E1D", label="Deficit (overspend)")]
    ax.legend(handles=legend_elements)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    path = f"{ASSETS_DIR}/03_monthly_cashflow.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Saved: {path}")


def chart4_category_trend(df):
    """Top 5 category spending trend over months."""
    expenses = df[df["type"] == "Expense"]
    top5_cats = expenses.groupby("category")["amount"].sum().nlargest(5).index.tolist()

    monthly_cat = expenses[expenses["category"].isin(top5_cats)]\
        .groupby(["month", "category"])["amount"].sum().reset_index()
    monthly_cat["month_dt"] = pd.to_datetime(monthly_cat["month"])
    monthly_cat = monthly_cat.sort_values("month_dt")

    fig, ax = plt.subplots(figsize=(14, 6))
    for i, cat in enumerate(top5_cats):
        data = monthly_cat[monthly_cat["category"] == cat]
        ax.plot(data["month_dt"], data["amount"], marker="o", linewidth=2,
                label=cat, color=COLORS[i], markersize=4)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_title("Top 5 Category Spending Trend", fontsize=16, fontweight="bold", pad=15)
    ax.set_ylabel("Monthly Spending (USD)")
    ax.legend(framealpha=0.9)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    path = f"{ASSETS_DIR}/04_category_trend.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Saved: {path}")


def chart5_day_of_week(df):
    """Average spending by day of week."""
    expenses = df[df["type"] == "Expense"]
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    by_day = expenses.groupby("day_of_week")["amount"].mean().reindex(day_order)

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(by_day.index, by_day.values,
                  color=["#C73E1D" if d in ["Saturday", "Sunday"] else "#2E86AB" for d in by_day.index],
                  alpha=0.85)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_title("Average Transaction Amount by Day of Week", fontsize=14, fontweight="bold")
    ax.set_ylabel("Average Amount (USD)")

    for bar, val in zip(bars, by_day.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f"${val:.0f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    path = f"{ASSETS_DIR}/05_day_of_week.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Saved: {path}")


def generate_eda_summary(df, monthly):
    """Generate EDA summary CSV."""
    expenses = df[df["type"] == "Expense"]
    income   = df[df["type"] == "Income"]

    summary = {
        "total_income":          round(income["amount"].sum(), 2),
        "total_expense":         round(expenses["amount"].sum(), 2),
        "total_savings":         round(income["amount"].sum() - expenses["amount"].sum(), 2),
        "savings_rate_pct":      round((income["amount"].sum() - expenses["amount"].sum()) / income["amount"].sum() * 100, 1),
        "avg_monthly_income":    round(income.groupby("month")["amount"].sum().mean(), 2),
        "avg_monthly_expense":   round(expenses.groupby("month")["amount"].sum().mean(), 2),
        "top_category":          expenses.groupby("category")["amount"].sum().idxmax(),
        "top_category_amount":   round(expenses.groupby("category")["amount"].sum().max(), 2),
        "total_transactions":    len(df),
        "date_range":            f"{df['date'].min().date()} to {df['date'].max().date()}",
        "outliers_flagged":      int(df["is_outlier"].sum()),
    }

    summary_df = pd.DataFrame(list(summary.items()), columns=["metric", "value"])
    path = f"{OUTPUT_DIR}/eda_summary.csv"
    summary_df.to_csv(path, index=False)
    print(f"  ✓ Saved: {path}")

    print(f"\n  📊 KEY METRICS:")
    for k, v in summary.items():
        print(f"     {k:<30} : {v}")

    return summary


def main():
    print(f"\nLoading cleaned data...")
    df = load_data()
    print(f"  ✓ {len(df):,} rows loaded\n")

    print("[1/5] Monthly Income vs Expense trend...")
    monthly = chart1_monthly_trend(df)

    print("[2/5] Spending by category...")
    chart2_spending_by_category(df)

    print("[3/5] Monthly cashflow...")
    chart3_monthly_cashflow(df)

    print("[4/5] Category trend over time...")
    chart4_category_trend(df)

    print("[5/5] Day of week pattern...")
    chart5_day_of_week(df)

    print("\nGenerating EDA summary...")
    generate_eda_summary(df, monthly)

    print(f"\n✅ All charts saved to: {ASSETS_DIR}/")
    print(f"✅ Summary saved to: {OUTPUT_DIR}/eda_summary.csv")


if __name__ == "__main__":
    main()
