"""
Script 00: Smart Format Mapper
================================
Otomatis detect dan map kolom dari CSV klien ke format standar pipeline.
Input  : data/raw/ (file CSV apapun dari klien)
Output : data/raw/personal_finance_raw.csv (format standar)

Mendukung:
- Nama kolom berbeda (Date, Transaction Date, Tanggal, dll)
- Kolom lebih banyak atau lebih sedikit dari standar
- Separator berbeda (comma, semicolon, tab)
- Format tanggal berbeda (DD/MM/YYYY, MM-DD-YYYY, dll)
- Currency symbols ($, Rp, €, dll)
- Kolom type tidak ada (semua dianggap Expense)
"""

import pandas as pd
import numpy as np
import os
import glob
import re
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────
RAW_DIR     = "../data/raw"
OUTPUT_PATH = "../data/raw/personal_finance_raw.csv"
LOG_PATH    = "../data/raw/format_mapper_log.txt"

# Mapping nama kolom yang mungkin dipakai klien → nama standar kita
COLUMN_MAP = {
    "date": [
        "date", "tanggal", "transaction date", "trans date", "tgl",
        "posting date", "value date", "transaction_date", "trans_date",
        "waktu", "time", "datetime", "created_at", "timestamp"
    ],
    "amount": [
        "amount", "jumlah", "nominal", "value", "total", "debit", "credit",
        "transaction amount", "amt", "price", "harga", "biaya", "cost",
        "sum", "balance", "payment", "charge", "amount (usd)", "amount_usd"
    ],
    "category": [
        "category", "kategori", "type", "tipe", "jenis", "group", "grup",
        "spending category", "expense category", "cat", "tag", "tags",
        "classification", "label", "merchant category"
    ],
    "description": [
        "description", "deskripsi", "keterangan", "note", "notes", "memo",
        "narration", "details", "detail", "merchant", "payee", "vendor",
        "transaction description", "trans desc", "name", "nama"
    ],
    "type": [
        "type", "tipe", "transaction type", "trans type", "flow",
        "debit/credit", "income/expense", "in/out", "direction",
        "debit_credit", "dr/cr", "dr cr"
    ],
    "payment_method": [
        "payment method", "payment_method", "method", "metode", "cara bayar",
        "channel", "instrument", "card", "account", "payment type",
        "source", "wallet", "payment channel", "pay channel", "payment_channel"
    ],
    "notes": [
        "notes", "note", "remarks", "remark", "memo", "keterangan",
        "comment", "comments", "additional info", "info"
    ],
}

# Format tanggal yang didukung
DATE_FORMATS = [
    "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y",
    "%Y/%m/%d", "%d %b %Y", "%b %d %Y", "%B %d %Y", "%d %B %Y",
    "%Y%m%d", "%d.%m.%Y", "%m.%d.%Y",
]
# ─────────────────────────────────────────────────────────────────────────────


def log(msg: str, logs: list):
    print(msg)
    logs.append(msg)


def detect_separator(filepath: str) -> str:
    """Detect separator CSV — comma, semicolon, atau tab."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        sample = f.read(2000)

    counts = {",": sample.count(","), ";": sample.count(";"), "\t": sample.count("\t")}
    return max(counts, key=counts.get)


def find_client_csv(raw_dir: str, output_path: str) -> str | None:
    """
    Cari file CSV klien di raw_dir.
    Skip file output standar kita (personal_finance_raw.csv).
    """
    all_csv = glob.glob(os.path.join(raw_dir, "*.csv"))
    client_files = [f for f in all_csv if os.path.basename(f) != "personal_finance_raw.csv"]

    if not client_files:
        return None
    # Ambil file terbaru
    return max(client_files, key=os.path.getmtime)


def normalize_column_name(col: str) -> str:
    """Lowercase, strip, replace spasi/simbol dengan underscore."""
    import re
    col = col.strip().lower()
    col = re.sub(r"[^a-z0-9/]", "_", col)  # keep / for debit/credit
    col = re.sub(r"_+", "_", col).strip("_")
    return col


def match_column(col_normalized: str) -> str | None:
    """
    Coba match nama kolom klien ke nama standar kita.
    Return nama standar jika match, None jika tidak.
    """
    for standard_name, variants in COLUMN_MAP.items():
        variants_normalized = [normalize_column_name(v) for v in variants]
        if col_normalized in variants_normalized:
            return standard_name
        # Partial match
        for variant in variants_normalized:
            if variant in col_normalized or col_normalized in variant:
                return standard_name
    return None


def parse_date_flexible(date_series: pd.Series, logs: list) -> pd.Series:
    """Coba berbagai format tanggal sampai berhasil."""
    for fmt in DATE_FORMATS:
        try:
            parsed = pd.to_datetime(date_series, format=fmt, errors="coerce")
            success_rate = parsed.notna().mean()
            if success_rate > 0.8:
                log(f"  ✓ Date format detected: {fmt} ({success_rate*100:.0f}% parsed)", logs)
                return parsed
        except Exception:
            continue

    # Fallback: pandas auto-detect
    parsed = pd.to_datetime(date_series, infer_datetime_format=True, errors="coerce")
    success_rate = parsed.notna().mean()
    log(f"  ✓ Date format: auto-detected ({success_rate*100:.0f}% parsed)", logs)
    return parsed


def clean_amount(amount_series: pd.Series, logs: list) -> pd.Series:
    """
    Bersihkan kolom amount:
    - Hapus currency symbols ($, Rp, €, £, ¥)
    - Hapus thousand separators (, atau .)
    - Handle format negatif: (100) → -100
    - Convert ke float
    """
    s = amount_series.astype(str)

    # Hapus currency symbols
    s = s.str.replace(r"[$€£¥Rp,IDR,USD,EUR]", "", regex=True)

    # Handle negatif dalam kurung: (100.00) → -100.00
    s = s.str.replace(r"^\((.+)\)$", r"-\1", regex=True)

    # Hapus thousand separator — tapi hati-hati dengan decimal
    # Deteksi format: 1.000,50 (EU) vs 1,000.50 (US)
    has_comma_decimal = s.str.contains(r"\d,\d{2}$").any()
    if has_comma_decimal:
        s = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        log(f"  ✓ Amount format: European (1.000,50)", logs)
    else:
        s = s.str.replace(",", "", regex=False)
        log(f"  ✓ Amount format: Standard (1,000.50)", logs)

    # Hapus whitespace dan karakter aneh
    s = s.str.strip().str.replace(r"[^\d.\-]", "", regex=True)

    return pd.to_numeric(s, errors="coerce")


def infer_type(df: pd.DataFrame, amount_col: str, logs: list) -> pd.Series:
    """
    Jika kolom 'type' tidak ada, infer dari:
    - Nilai negatif = Expense, positif = Income
    - Atau kolom debit/credit terpisah
    """
    if "debit" in df.columns and "credit" in df.columns:
        log(f"  ✓ Type inferred from debit/credit columns", logs)
        return df.apply(
            lambda r: "Income" if pd.notna(r.get("credit")) and float(r.get("credit", 0) or 0) > 0
                      else "Expense", axis=1
        )

    # Dari tanda amount
    log(f"  ✓ Type inferred from amount sign (negative=Expense, positive=Income)", logs)
    return df[amount_col].apply(lambda x: "Income" if float(x or 0) > 0 else "Expense")


def map_format(filepath: str, logs: list) -> pd.DataFrame:
    """Main mapping function."""
    log(f"\n  File: {os.path.basename(filepath)}", logs)

    # Detect separator
    sep = detect_separator(filepath)
    sep_name = {"," : "comma", ";": "semicolon", "\t": "tab"}.get(sep, sep)
    log(f"  Separator: {sep_name}", logs)

    # Load file
    df = pd.read_csv(filepath, sep=sep, encoding="utf-8", on_bad_lines="skip")
    log(f"  Raw rows: {len(df):,} | Raw columns: {list(df.columns)}", logs)

    # Normalize column names
    col_mapping = {}
    unmapped = []
    for col in df.columns:
        normalized = normalize_column_name(col)
        standard = match_column(normalized)
        if standard and standard not in col_mapping.values():
            col_mapping[col] = standard
        else:
            unmapped.append(col)

    log(f"\n  Column mapping:", logs)
    for orig, std in col_mapping.items():
        log(f"    '{orig}' → '{std}'", logs)
    if unmapped:
        log(f"  Unmapped columns (will be dropped): {unmapped}", logs)

    # Rename columns
    df = df.rename(columns=col_mapping)

    # ── Proses setiap kolom standar ──────────────────────────────────────────

    # DATE
    if "date" in df.columns:
        df["date"] = parse_date_flexible(df["date"], logs)
    else:
        log(f"  [!] No date column found — using today's date as fallback", logs)
        df["date"] = pd.Timestamp.now()

    # AMOUNT
    if "amount" in df.columns:
        df["amount"] = clean_amount(df["amount"], logs)
    else:
        log(f"  [!] No amount column found — cannot proceed", logs)
        raise ValueError("Amount column is required but not found.")

    # TYPE
    if "type" not in df.columns:
        log(f"  Type column not found — inferring from amount values", logs)
        df["type"] = infer_type(df, "amount", logs)
    else:
        # Normalize type values
        df["type"] = df["type"].astype(str).str.strip().str.title()
        # Map common variants
        type_map = {
            "Dr": "Expense", "Cr": "Income", "Debit": "Expense", "Credit": "Income",
            "Out": "Expense", "In": "Income", "Expense": "Expense", "Income": "Income",
            "Pengeluaran": "Expense", "Pemasukan": "Income",
        }
        df["type"] = df["type"].map(type_map).fillna("Expense")

    # Take absolute value of amount (type already captured sign)
    df["amount"] = df["amount"].abs()

    # CATEGORY
    if "category" not in df.columns:
        log(f"  Category column not found — defaulting to 'Other'", logs)
        df["category"] = "Other"

    # DESCRIPTION
    if "description" not in df.columns:
        log(f"  Description column not found — defaulting to 'N/A'", logs)
        df["description"] = "N/A"

    # PAYMENT_METHOD
    if "payment_method" not in df.columns:
        log(f"  Payment method not found — defaulting to 'Unknown'", logs)
        df["payment_method"] = "Unknown"

    # NOTES
    if "notes" not in df.columns:
        df["notes"] = ""

    # ── Build output dataframe dengan kolom standar ──────────────────────────
    df_out = pd.DataFrame({
        "date":           df["date"].dt.strftime("%Y-%m-%d") if hasattr(df["date"], "dt") else df["date"],
        "month":          df["date"].dt.to_period("M").astype(str) if hasattr(df["date"], "dt") else "",
        "year":           df["date"].dt.year.astype(int) if hasattr(df["date"], "dt") else 0,
        "quarter":        df["date"].dt.quarter.map({1:"Q1",2:"Q2",3:"Q3",4:"Q4"}) if hasattr(df["date"], "dt") else "Q1",
        "category":       df["category"].fillna("Other").astype(str),
        "description":    df["description"].fillna("N/A").astype(str),
        "amount":         df["amount"],
        "type":           df["type"],
        "payment_method": df["payment_method"].fillna("Unknown").astype(str),
        "notes":          df.get("notes", pd.Series([""] * len(df))).fillna("").astype(str),
    })

    # Drop rows dengan amount kosong atau 0
    rows_before = len(df_out)
    df_out = df_out[df_out["amount"].notna() & (df_out["amount"] > 0)]
    dropped = rows_before - len(df_out)
    if dropped > 0:
        log(f"  Dropped {dropped} rows dengan amount kosong/nol", logs)

    log(f"\n  Output rows: {len(df_out):,}", logs)
    return df_out


def main():
    logs = []
    log("=" * 50, logs)
    log("  FORMAT MAPPER", logs)
    log(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", logs)
    log("=" * 50, logs)

    # Cari file klien
    client_file = find_client_csv(RAW_DIR, OUTPUT_PATH)

    if not client_file:
        log("\n  Tidak ada file CSV klien ditemukan di data/raw/", logs)
        log("  Taruh file CSV klien di folder data/raw/ lalu jalankan ulang.", logs)
        log("\n  Contoh nama file yang diterima:", logs)
        log("    - transactions.csv", logs)
        log("    - my_expenses_2024.csv", logs)
        log("    - bank_statement.csv", logs)
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(logs))
        return

    log(f"\n  Client file found: {client_file}", logs)

    try:
        df_mapped = map_format(client_file, logs)

        # Save output
        df_mapped.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
        log(f"\n  Saved: {OUTPUT_PATH}", logs)
        log(f"  Status: READY for pipeline", logs)
        log(f"\n  Next step: python run_all.py --skip-gen", logs)

    except Exception as e:
        log(f"\n  ERROR: {e}", logs)
        log(f"  Periksa format file dan coba lagi.", logs)

    log("=" * 50, logs)

    # Save log
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(logs))
    print(f"\n  Log saved: {LOG_PATH}")


if __name__ == "__main__":
    main()
