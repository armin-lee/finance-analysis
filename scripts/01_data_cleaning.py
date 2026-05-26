"""
Script 1: Data Cleaning
========================
Input  : data/raw/personal_finance_raw.csv
Output : data/cleaned/personal_finance_clean.csv

Yang dilakukan:
- Cek & handle missing values
- Hapus duplicate rows
- Fix tipe data (date, amount)
- Validasi nilai amount (tidak boleh negatif/nol)
- Tambah kolom turunan (month_name, week)
- Log semua perubahan
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

# ── CONFIG ────────────────────────────────────────────────────────────────────
INPUT_PATH  = "../data/raw/personal_finance_raw.csv"
OUTPUT_PATH = "../data/cleaned/personal_finance_clean.csv"
LOG_PATH    = "../data/cleaned/cleaning_log.txt"
# ─────────────────────────────────────────────────────────────────────────────

def log(msg: str, logs: list):
    print(msg)
    logs.append(msg)

def clean_data(df: pd.DataFrame, logs: list) -> pd.DataFrame:

    log(f"\n{'='*50}", logs)
    log(f"  DATA CLEANING REPORT", logs)
    log(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", logs)
    log(f"{'='*50}", logs)

    # ── Step 1: Overview awal ─────────────────────────────────────────────────
    log(f"\n[1/7] Dataset Overview (Before Cleaning)", logs)
    log(f"  Rows        : {len(df):,}", logs)
    log(f"  Columns     : {df.shape[1]}", logs)
    log(f"  Memory      : {df.memory_usage(deep=True).sum() / 1024:.1f} KB", logs)
    log(f"  Date range  : {df['date'].min()} → {df['date'].max()}", logs)

    original_rows = len(df)

    # ── Step 2: Fix tipe data ─────────────────────────────────────────────────
    log(f"\n[2/7] Fixing Data Types", logs)
    df["date"]   = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["year"]   = df["year"].astype(int, errors="ignore")
    log(f"  ✓ date   → datetime", logs)
    log(f"  ✓ amount → float", logs)
    log(f"  ✓ year   → int", logs)

    # ── Step 3: Handle missing values ────────────────────────────────────────
    log(f"\n[3/7] Handling Missing Values", logs)
    missing_before = df.isnull().sum()
    total_missing = missing_before.sum()

    if total_missing > 0:
        log(f"  Missing values found:", logs)
        for col, count in missing_before[missing_before > 0].items():
            log(f"    {col}: {count} missing", logs)

    # Fill missing values (pandas 2.x syntax)
    df["description"]    = df["description"].fillna("Unknown")
    df["payment_method"] = df["payment_method"].fillna("Unknown")
    df["notes"]          = df["notes"].fillna("").astype(str)

    # Drop rows dengan amount atau date missing (tidak bisa dianalisis)
    rows_before = len(df)
    df.dropna(subset=["date", "amount"], inplace=True)
    dropped_missing = rows_before - len(df)

    log(f"  ✓ Filled: description, payment_method, notes → 'Unknown'/''", logs)
    log(f"  ✓ Dropped {dropped_missing} rows dengan date/amount kosong", logs)

    # ── Step 4: Hapus duplicate ───────────────────────────────────────────────
    log(f"\n[4/7] Removing Duplicates", logs)
    rows_before = len(df)
    df.drop_duplicates(inplace=True)
    duplicates_removed = rows_before - len(df)
    log(f"  ✓ Removed {duplicates_removed} duplicate rows", logs)

    # ── Step 5: Validasi amount ───────────────────────────────────────────────
    log(f"\n[5/7] Validating Amount Values", logs)
    invalid_amount = df[df["amount"] <= 0]
    log(f"  Amount ≤ 0: {len(invalid_amount)} rows", logs)
    df = df[df["amount"] > 0]
    log(f"  ✓ Removed {len(invalid_amount)} rows dengan amount tidak valid", logs)

    # Flag outliers (amount > 3x std dari category)
    df["is_outlier"] = False
    for cat in df["category"].unique():
        mask = df["category"] == cat
        cat_data = df.loc[mask, "amount"]
        mean, std = cat_data.mean(), cat_data.std()
        outlier_mask = mask & (df["amount"] > mean + 3 * std)
        df.loc[outlier_mask, "is_outlier"] = True

    outlier_count = df["is_outlier"].sum()
    log(f"  ✓ Flagged {outlier_count} outliers (amount > mean + 3*std per category)", logs)

    # ── Step 6: Tambah kolom turunan ─────────────────────────────────────────
    log(f"\n[6/7] Adding Derived Columns", logs)
    df["month"]      = df["date"].dt.to_period("M").astype(str)
    df["month_name"] = df["date"].dt.strftime("%B %Y")
    df["year"]       = df["date"].dt.year
    df["quarter"]    = df["date"].dt.quarter.map({1:"Q1", 2:"Q2", 3:"Q3", 4:"Q4"})
    df["week"]       = df["date"].dt.isocalendar().week.astype(int)
    df["day_of_week"]= df["date"].dt.day_name()
    df["amount_usd"] = df["amount"].round(2)  # normalized

    log(f"  ✓ Added: month_name, week, day_of_week, amount_usd", logs)

    # ── Step 7: Sort & reset index ────────────────────────────────────────────
    log(f"\n[7/7] Finalizing", logs)
    df.sort_values("date", inplace=True)
    df.reset_index(drop=True, inplace=True)

    rows_removed = original_rows - len(df)
    log(f"\n{'='*50}", logs)
    log(f"  CLEANING SUMMARY", logs)
    log(f"{'='*50}", logs)
    log(f"  Rows before  : {original_rows:,}", logs)
    log(f"  Rows after   : {len(df):,}", logs)
    log(f"  Rows removed : {rows_removed:,} ({rows_removed/original_rows*100:.1f}%)", logs)
    log(f"  Duplicates   : {duplicates_removed}", logs)
    log(f"  Outliers flagged: {outlier_count}", logs)
    log(f"  Status       : ✅ CLEAN", logs)

    return df


def main():
    print(f"\nLoading: {INPUT_PATH}")
    df = pd.read_csv(INPUT_PATH)

    logs = []
    df_clean = clean_data(df, logs)

    # Save cleaned data
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df_clean.to_csv(OUTPUT_PATH, index=False)
    print(f"\n✅ Saved: {OUTPUT_PATH}")

    # Save log
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(logs))
    print(f"✅ Log saved: {LOG_PATH}")


if __name__ == "__main__":
    main()
