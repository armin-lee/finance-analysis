"""
Script 2: EDA & Visualizations
================================
Principles:
- One chart, one message
- Storytelling titles
- Strategic color: highlight + gray
- Proper whitespace & padding
- No chartjunk
- Direct labeling
- Clear typography hierarchy
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
import os
import warnings
warnings.filterwarnings("ignore")

# ── CONFIG ────────────────────────────────────────────────────────────────────
INPUT_PATH = "../data/cleaned/personal_finance_clean.csv"
ASSETS_DIR = "../assets"
OUTPUT_DIR = "../data/output"
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── BRAND PALETTE ─────────────────────────────────────────────────────────────
BLUE       = "#2E86AB"
RED        = "#E63946"
GRAY       = "#C4CDD6"
DARK_GRAY  = "#4A5568"
MID_GRAY   = "#718096"
LIGHT_BG   = "#F8F9FA"
WHITE      = "#FFFFFF"

# ── TYPOGRAPHY ────────────────────────────────────────────────────────────────
TITLE_SIZE    = 15
SUBTITLE_SIZE = 10
LABEL_SIZE    = 10
TICK_SIZE     = 9
ANNOT_SIZE    = 9

plt.rcParams.update({
    "figure.facecolor":   WHITE,
    "axes.facecolor":     WHITE,
    "axes.grid":          True,
    "grid.color":         "#EDEDF0",
    "grid.linewidth":     0.6,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.spines.left":   False,
    "axes.spines.bottom": True,
    "axes.edgecolor":     "#D1D5DB",
    "font.family":        "DejaVu Sans",
    "text.color":         DARK_GRAY,
    "axes.labelcolor":    MID_GRAY,
    "xtick.color":        MID_GRAY,
    "ytick.color":        MID_GRAY,
    "xtick.labelsize":    TICK_SIZE,
    "ytick.labelsize":    TICK_SIZE,
    "axes.labelsize":     LABEL_SIZE,
})

# ── HELPERS ───────────────────────────────────────────────────────────────────
def save(fig, name):
    path = f"{ASSETS_DIR}/{name}"
    fig.savefig(path, dpi=150, bbox_inches="tight",
                facecolor=WHITE, pad_inches=0.3)
    plt.close(fig)
    print(f"  ✓ {path}")


def styled_title(ax, title, subtitle, pad=18):
    """Title + subtitle dengan hierarchy yang jelas dan whitespace yang cukup."""
    ax.set_title(title, fontsize=TITLE_SIZE, fontweight="bold",
                 loc="left", pad=pad, color=DARK_GRAY)
    # Subtitle sebagai text annotation di bawah title, bukan ax.text
    ax.annotate(subtitle,
                xy=(0, 1), xycoords="axes fraction",
                xytext=(0, pad + 6), textcoords=("axes fraction", "points"),
                fontsize=SUBTITLE_SIZE, color=MID_GRAY,
                va="bottom", ha="left")


def fmt_currency(x, _):
    if abs(x) >= 1000:
        return f"${x/1000:.0f}K"
    return f"${x:.0f}"


# ── CHART 1: INCOME VS EXPENSE ────────────────────────────────────────────────
def chart1_income_vs_expense(df):
    monthly = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0).reset_index()
    monthly["month_dt"] = pd.to_datetime(monthly["month"])
    monthly = monthly.sort_values("month_dt").reset_index(drop=True)
    if "Income"  not in monthly.columns: monthly["Income"]  = 0
    if "Expense" not in monthly.columns: monthly["Expense"] = 0

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.subplots_adjust(left=0.08, right=0.88, top=0.78, bottom=0.18)

    # Shaded gap area
    ax.fill_between(monthly["month_dt"], monthly["Income"], monthly["Expense"],
                    where=monthly["Expense"] >= monthly["Income"],
                    alpha=0.07, color=RED)
    ax.fill_between(monthly["month_dt"], monthly["Income"], monthly["Expense"],
                    where=monthly["Income"] > monthly["Expense"],
                    alpha=0.07, color=BLUE)

    # Lines
    ax.plot(monthly["month_dt"], monthly["Expense"],
            color=RED, linewidth=2.5, zorder=3, solid_capstyle="round")
    ax.plot(monthly["month_dt"], monthly["Income"],
            color=BLUE, linewidth=2.5, zorder=3, solid_capstyle="round")

    # Direct end-of-line labels — pushed to right with padding
    for val, color, label in [
        (monthly["Expense"].iloc[-1], RED,  "Expense"),
        (monthly["Income"].iloc[-1],  BLUE, "Income"),
    ]:
        ax.annotate(label,
                    xy=(monthly["month_dt"].iloc[-1], val),
                    xytext=(12, 0), textcoords="offset points",
                    color=color, fontweight="bold", fontsize=LABEL_SIZE,
                    va="center", annotation_clip=False)

    # Annotate worst gap — with enough offset to not overlap line
    monthly["gap"] = monthly["Expense"] - monthly["Income"]
    worst = monthly.loc[monthly["gap"].idxmax()]
    mid_y = (worst["Expense"] + worst["Income"]) / 2
    ax.annotate(f"Largest gap\n${worst['gap']:,.0f}",
                xy=(worst["month_dt"], mid_y),
                xytext=(30, 0), textcoords="offset points",
                ha="left", va="center",
                color=RED, fontsize=ANNOT_SIZE, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=RED,
                                lw=1.2, connectionstyle="arc3,rad=-0.2"),
                bbox=dict(boxstyle="round,pad=0.3", fc=WHITE, ec=RED,
                          lw=0.8, alpha=0.9))

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_currency))
    ax.tick_params(bottom=True, left=False)
    ax.yaxis.set_ticks_position("none")
    ax.set_xlabel("")
    plt.xticks(rotation=35, ha="right")

    fig.suptitle("Expenses Consistently Exceed Income",
                  x=0.08, y=0.97, ha="left",
                  fontsize=TITLE_SIZE, fontweight="bold", color=DARK_GRAY)
    fig.text(0.08, 0.91, "Monthly income vs. expense  •  2023–2024",
             ha="left", fontsize=SUBTITLE_SIZE, color=MID_GRAY)

    save(fig, "01_monthly_trend.png")


# ── CHART 2: SPENDING BY CATEGORY ─────────────────────────────────────────────
def chart2_spending_by_category(df):
    expenses = df[df["type"] == "Expense"]
    by_cat   = expenses.groupby("category")["amount"].sum().sort_values()
    total    = by_cat.sum()
    top_cat  = by_cat.idxmax()
    pct_top  = by_cat[top_cat] / total * 100

    colors_bar = [BLUE if c == top_cat else GRAY for c in by_cat.index]

    fig, ax = plt.subplots(figsize=(11, 6.5))
    fig.subplots_adjust(left=0.18, right=0.78, top=0.88, bottom=0.1)

    bars = ax.barh(by_cat.index, by_cat.values,
                   color=colors_bar, height=0.6, zorder=2)

    # Labels: inside if wide enough, outside if small
    threshold = by_cat.max() * 0.22
    for bar, val, cat in zip(bars, by_cat.values, by_cat.index):
        pct   = val / total * 100
        label = f"${val/1000:.0f}K  ({pct:.0f}%)"
        if val >= threshold:
            ax.text(bar.get_width() * 0.97,
                    bar.get_y() + bar.get_height() / 2,
                    label, va="center", ha="right",
                    color=WHITE if cat == top_cat else DARK_GRAY,
                    fontsize=LABEL_SIZE, fontweight="bold")
        else:
            ax.text(bar.get_width() + total * 0.002,
                    bar.get_y() + bar.get_height() / 2,
                    label, va="center", ha="left",
                    color=DARK_GRAY, fontsize=LABEL_SIZE - 1)

    ax.set_xlim(0, by_cat.max() * 1.45)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_currency))
    ax.tick_params(bottom=True, left=False)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("")  # tidak perlu label x

    fig.suptitle(f"Housing Dominates — {pct_top:.0f}% of All Spending",
                  x=0.18, y=0.98, ha="left",
                  fontsize=TITLE_SIZE, fontweight="bold", color=DARK_GRAY)
    fig.text(0.18, 0.93, "Total expenses by category  •  2023–2024",
             ha="left", fontsize=SUBTITLE_SIZE, color=MID_GRAY)

    save(fig, "02_spending_by_category.png")


# ── CHART 3: MONTHLY CASHFLOW ─────────────────────────────────────────────────
def chart3_monthly_cashflow(df):
    monthly = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0).reset_index()
    monthly["month_dt"] = pd.to_datetime(monthly["month"])
    monthly = monthly.sort_values("month_dt").reset_index(drop=True)
    if "Income"  not in monthly.columns: monthly["Income"]  = 0
    if "Expense" not in monthly.columns: monthly["Expense"] = 0
    monthly["cashflow"] = monthly["Income"] - monthly["Expense"]

    surplus_n = (monthly["cashflow"] > 0).sum()
    total_n   = len(monthly)
    colors_bar = [BLUE if v >= 0 else RED for v in monthly["cashflow"]]

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.subplots_adjust(left=0.08, right=0.88, top=0.78, bottom=0.22)

    ax.bar(monthly["month_dt"], monthly["cashflow"],
           color=colors_bar, width=20, alpha=0.85, zorder=2)
    ax.axhline(0, color=DARK_GRAY, linewidth=1.0, zorder=3)

    # Annotate worst month — di samping kanan bar, hindari overlap axis
    worst = monthly.loc[monthly["cashflow"].idxmin()]
    ax.annotate(f"Worst: ${worst['cashflow']:,.0f}",
                xy=(worst["month_dt"], worst["cashflow"]),
                xytext=(40, 0), textcoords="offset points",
                ha="left", va="center",
                color=RED, fontsize=ANNOT_SIZE, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2,
                                connectionstyle="arc3,rad=0.2"),
                bbox=dict(boxstyle="round,pad=0.3", fc=WHITE,
                          ec=RED, lw=0.8, alpha=0.95),
                annotation_clip=False)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_currency))
    ax.tick_params(bottom=True, left=False)
    ax.yaxis.set_ticks_position("none")
    plt.xticks(rotation=35, ha="right")

    surplus_p = mpatches.Patch(color=BLUE, alpha=0.85,
                               label=f"Surplus — {surplus_n} months")
    deficit_p = mpatches.Patch(color=RED,  alpha=0.85,
                               label=f"Deficit — {total_n - surplus_n} months")
    ax.legend(handles=[surplus_p, deficit_p], loc="upper right",
              framealpha=0.95, fontsize=LABEL_SIZE,
              edgecolor="#E2E8F0", borderpad=0.8)

    fig.suptitle(f"Only {surplus_n} of {total_n} Months Had Positive Cashflow",
                  x=0.08, y=0.97, ha="left",
                  fontsize=TITLE_SIZE, fontweight="bold", color=DARK_GRAY)
    fig.text(0.08, 0.91, "Monthly cashflow = Income − Expense  •  2023–2024",
             ha="left", fontsize=SUBTITLE_SIZE, color=MID_GRAY)

    save(fig, "03_monthly_cashflow.png")


# ── CHART 4: CATEGORY TREND ───────────────────────────────────────────────────
def chart4_category_trend(df):
    expenses  = df[df["type"] == "Expense"]
    top5      = expenses.groupby("category")["amount"].sum().nlargest(5).index.tolist()
    monthly_c = (expenses[expenses["category"].isin(top5)]
                 .groupby(["month", "category"])["amount"].sum()
                 .reset_index())
    monthly_c["month_dt"] = pd.to_datetime(monthly_c["month"])
    monthly_c = monthly_c.sort_values("month_dt")

    # Focus on most volatile category
    volatility = monthly_c.groupby("category")["amount"].std()
    focus_cat  = volatility.idxmax()

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.subplots_adjust(left=0.08, right=0.86, top=0.78, bottom=0.18)

    # Kumpulkan end values untuk stagger label
    end_values = {}
    for cat in top5:
        data = monthly_c[monthly_c["category"] == cat]
        end_values[cat] = data.iloc[-1]["amount"]

    # Sort by end value untuk assign stagger offset
    sorted_cats = sorted(end_values.items(), key=lambda x: x[1])
    label_offsets = {}
    prev_y = None
    MIN_GAP = 500  # minimum gap antar label dalam unit data

    for cat, val in sorted_cats:
        if prev_y is not None and abs(val - prev_y) < MIN_GAP:
            label_offsets[cat] = prev_y + MIN_GAP
        else:
            label_offsets[cat] = val
        prev_y = label_offsets[cat]

    for cat in top5:
        data = monthly_c[monthly_c["category"] == cat]
        last = data.iloc[-1]
        label_y = label_offsets[cat]

        if cat == focus_cat:
            ax.plot(data["month_dt"], data["amount"],
                    color=BLUE, linewidth=2.5, zorder=4,
                    solid_capstyle="round")
            # Leader line dari data ke label jika ada offset
            if abs(label_y - last["amount"]) > 100:
                ax.plot([last["month_dt"], last["month_dt"]],
                        [last["amount"], label_y],
                        color=BLUE, linewidth=0.8, alpha=0.5,
                        clip_on=False)
            ax.annotate(cat,
                        xy=(last["month_dt"], label_y),
                        xytext=(10, 0), textcoords="offset points",
                        color=BLUE, fontweight="bold",
                        fontsize=LABEL_SIZE, va="center",
                        annotation_clip=False)
            # Spike annotation
            spike = data.loc[data["amount"].idxmax()]
            ax.annotate(f"Spike\n${spike['amount']:,.0f}",
                        xy=(spike["month_dt"], spike["amount"]),
                        xytext=(0, 28), textcoords="offset points",
                        ha="center", color=BLUE,
                        fontsize=ANNOT_SIZE, fontweight="bold",
                        arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.2),
                        bbox=dict(boxstyle="round,pad=0.3", fc=WHITE,
                                  ec=BLUE, lw=0.8, alpha=0.9))
        else:
            ax.plot(data["month_dt"], data["amount"],
                    color=GRAY, linewidth=1.0, zorder=2, alpha=0.8)
            if abs(label_y - last["amount"]) > 100:
                ax.plot([last["month_dt"], last["month_dt"]],
                        [last["amount"], label_y],
                        color=GRAY, linewidth=0.8, alpha=0.5,
                        clip_on=False)
            ax.annotate(cat,
                        xy=(last["month_dt"], label_y),
                        xytext=(10, 0), textcoords="offset points",
                        color=MID_GRAY, fontsize=TICK_SIZE, va="center",
                        annotation_clip=False)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_currency))
    ax.tick_params(bottom=True, left=False)
    ax.yaxis.set_ticks_position("none")
    plt.xticks(rotation=35, ha="right")

    fig.suptitle(f"{focus_cat} Is the Most Volatile Spending Category",
                  x=0.08, y=0.97, ha="left",
                  fontsize=TITLE_SIZE, fontweight="bold", color=DARK_GRAY)
    fig.text(0.08, 0.91, f"Top 5 categories  •  {focus_cat} highlighted  •  2023–2024",
             ha="left", fontsize=SUBTITLE_SIZE, color=MID_GRAY)

    save(fig, "04_category_trend.png")


# ── CHART 5: DAY OF WEEK ──────────────────────────────────────────────────────
def chart5_day_of_week(df):
    expenses  = df[df["type"] == "Expense"]
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    by_day    = expenses.groupby("day_of_week")["amount"].mean().reindex(day_order)

    weekend    = ["Saturday", "Sunday"]
    peak_val   = by_day.max()
    peak_day   = by_day.idxmax()
    # Semua hari yang dalam 1% dari peak dianggap tied
    peak_days   = [d for d in by_day.index if by_day[d] >= peak_val * 0.99]
    is_weekend_peak = all(d in weekend for d in peak_days)
    peak_label  = " & ".join(peak_days) if len(peak_days) > 1 else peak_days[0]
    weekday_avg = by_day[[d for d in by_day.index if d not in weekend]].mean()
    weekend_avg = by_day[weekend].mean()
    higher_period = "Weekdays" if weekday_avg >= weekend_avg else "Weekends"

    if weekday_avg >= weekend_avg:
        title_str = f"Spending Tends to Peak Mid-Week — ${weekday_avg:,.0f} Weekday Avg"
    else:
        title_str = f"Weekend Spending Exceeds Weekdays — ${weekend_avg:,.0f} Weekend Avg"

    colors_bar = []
    for d in by_day.index:
        if d in peak_days:
            colors_bar.append(RED if is_weekend_peak else BLUE)
        elif d in weekend:
            colors_bar.append("#F4A261")
        else:
            colors_bar.append(GRAY)

    fig, ax = plt.subplots(figsize=(11, 5.5))
    fig.subplots_adjust(left=0.1, right=0.95, top=0.78, bottom=0.18)

    bars = ax.bar(by_day.index, by_day.values,
                  color=colors_bar, width=0.55, zorder=2)

    # Weekend background shading
    for i, day in enumerate(day_order):
        if day in weekend:
            ax.axvspan(i - 0.45, i + 0.45, alpha=0.06,
                       color=RED, zorder=0)

    # Labels above bars — uniform offset
    y_offset = by_day.max() * 0.025
    for bar, val, day in zip(bars, by_day.values, day_order):
        is_peak = (day in peak_days)
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + y_offset,
                f"${val:.0f}",
                ha="center", va="bottom",
                fontsize=LABEL_SIZE,
                color=BLUE if is_peak and not is_weekend_peak else (RED if is_peak else MID_GRAY),
                fontweight="bold" if is_peak or day in weekend else "normal")

    ax.set_ylim(0, by_day.max() * 1.22)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_currency))
    ax.tick_params(bottom=True, left=False)
    ax.yaxis.set_ticks_position("none")
    ax.grid(axis="x", visible=False)

    peak_color = RED if is_weekend_peak else BLUE
    legend_handles = [
        mpatches.Patch(color=peak_color,   alpha=0.85, label="Peak"),
        mpatches.Patch(color="#F4A261",    alpha=0.85, label="Weekend"),
        mpatches.Patch(color=GRAY,         alpha=0.7,  label="Weekday"),
    ]
    ax.legend(handles=legend_handles,
              loc="upper center",
              bbox_to_anchor=(0.5, 1.13),
              ncol=3,
              frameon=False,              # no border
              fontsize=LABEL_SIZE,
              columnspacing=1.2,
              handlelength=1.2)

    fig.suptitle(title_str,
                  x=0.1, y=0.97, ha="left",
                  fontsize=TITLE_SIZE, fontweight="bold", color=DARK_GRAY)
    fig.text(0.1, 0.91, "Average transaction amount by day of week  •  2023–2024",
             ha="left", fontsize=SUBTITLE_SIZE, color=MID_GRAY)

    save(fig, "05_day_of_week.png")


# ── EDA SUMMARY ───────────────────────────────────────────────────────────────
def generate_eda_summary(df):
    expenses = df[df["type"] == "Expense"]
    income   = df[df["type"] == "Income"]

    summary = {
        "total_income":        round(income["amount"].sum(), 2),
        "total_expense":       round(expenses["amount"].sum(), 2),
        "total_savings":       round(income["amount"].sum() - expenses["amount"].sum(), 2),
        "savings_rate_pct":    round((income["amount"].sum() - expenses["amount"].sum()) / income["amount"].sum() * 100, 1),
        "avg_monthly_income":  round(income.groupby("month")["amount"].sum().mean(), 2),
        "avg_monthly_expense": round(expenses.groupby("month")["amount"].sum().mean(), 2),
        "top_category":        expenses.groupby("category")["amount"].sum().idxmax(),
        "top_category_amount": round(expenses.groupby("category")["amount"].sum().max(), 2),
        "top_category_pct":    round(expenses.groupby("category")["amount"].sum().max() / expenses["amount"].sum() * 100, 1),
        "total_transactions":  len(df),
        "date_range":          f"{df['date'].min()} to {df['date'].max()}",
        "outliers_flagged":    int(df["is_outlier"].sum()),
    }

    pd.DataFrame(list(summary.items()), columns=["metric","value"])\
      .to_csv(f"{OUTPUT_DIR}/eda_summary.csv", index=False)

    print(f"\n  📊 KEY METRICS:")
    for k, v in summary.items():
        print(f"     {k:<30} : {v}")
    return summary


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print(f"\nLoading cleaned data...")
    df = pd.read_csv(INPUT_PATH, parse_dates=["date"])
    print(f"  ✓ {len(df):,} rows loaded\n")

    print("[1/5] Income vs Expense trend...")
    chart1_income_vs_expense(df)

    print("[2/5] Spending by category...")
    chart2_spending_by_category(df)

    print("[3/5] Monthly cashflow...")
    chart3_monthly_cashflow(df)

    print("[4/5] Category trend...")
    chart4_category_trend(df)

    print("[5/5] Day of week pattern...")
    chart5_day_of_week(df)

    print("\nGenerating EDA summary...")
    generate_eda_summary(df)

    print(f"\n✅ All charts saved to: {ASSETS_DIR}/")


if __name__ == "__main__":
    main()
