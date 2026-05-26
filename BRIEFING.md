# BRIEFING: Finance Analysis Portfolio Project

> File ini untuk Claude AI — paste di awal sesi baru untuk langsung dapat konteks penuh project ini.

---

## Tujuan Project

Portfolio project #1 untuk jasa freelance data analytics di Fiverr.
Mendemonstrasikan kemampuan end-to-end: format mapping → cleaning → EDA → visualisasi → laporan HTML.

**Audiens ganda:**
- **Recruiter/developer** → lihat via GitHub (code + README)
- **Klien Fiverr** → lihat via portfolio PDF + screenshot hasil

---

## Struktur File

```
finance_analysis/
├── run_all.py                        ← entry point pipeline
├── requirements.txt
├── .gitignore
├── README.md                         ← untuk GitHub (recruiter)
├── BRIEFING.md                       ← file ini
│
├── scripts/
│   ├── 00_format_mapper.py           ← auto-detect & map CSV klien
│   ├── 01_data_cleaning.py           ← cleaning, validasi, audit log
│   ├── 02_eda_visualization.py       ← 5 charts dengan viz principles
│   ├── 03_report_generator.py        ← HTML report untuk klien
│   ├── generate_dataset.py           ← buat sample data synthetic
│   └── generate_portfolio_pdf.py     ← buat PDF portofolio Fiverr
│
├── sample/                           ← di-commit ke GitHub (preview)
│   ├── sample_data.csv               ← 50 rows demo data
│   └── *.png                         ← 5 charts (embed di README)
│
├── data/
│   ├── raw/                          ← input (NOT committed)
│   ├── cleaned/                      ← output cleaning (NOT committed)
│   └── output/                       ← EDA summary CSV (NOT committed)
│
├── assets/                           ← generated charts (NOT committed)
└── reports/                          ← HTML + PDF report (NOT committed)
```

---

## Cara Pakai Pipeline

### Demo dengan sample data:
```bash
python run_all.py
```

### Dengan data klien (format apapun):
```bash
# Taruh CSV klien di data/raw/ (nama bebas)
python run_all.py --client-data
```

### Skip generate, langsung analisis:
```bash
python run_all.py --skip-gen
```

### Generate portfolio PDF (untuk Fiverr):
```bash
python scripts/generate_portfolio_pdf.py
# Output: reports/portfolio_finance_analysis.pdf
```

---

## Detail Setiap Script

### `00_format_mapper.py`
Auto-detect dan map CSV format klien ke format standar pipeline.

**Yang didukung:**
- Separator: comma, semicolon, tab (auto-detect)
- 13 format tanggal (YYYY-MM-DD, DD/MM/YYYY, dll)
- Currency symbols ($, Rp, €, £) — auto-strip
- Format angka: 1,000.50 (US) dan 1.000,50 (EU)
- Kolom hilang → fallback default (category="Other", type inferred dari amount sign)
- Extra kolom → diabaikan

**Output:** `data/raw/personal_finance_raw.csv` (format standar)
**Log:** `data/raw/format_mapper_log.txt`

---

### `01_data_cleaning.py`
**Input:** `data/raw/personal_finance_raw.csv`
**Output:** `data/cleaned/personal_finance_clean.csv` + `cleaning_log.txt`

Steps (7):
1. Dataset overview
2. Fix data types (date → datetime, amount → float)
3. Handle missing values (fillna, bukan drop)
4. Remove duplicates
5. Validate amount (drop ≤ 0)
6. Flag outliers (amount > mean + 3×std per category)
7. Add derived columns: month_name, week, day_of_week, amount_usd

**Note:** Pandas 2.x — gunakan `df["col"] = df["col"].fillna(val)`, bukan `inplace=True`

---

### `02_eda_visualization.py`
**Input:** `data/cleaned/personal_finance_clean.csv`
**Output:** `assets/*.png` (5 charts) + `data/output/eda_summary.csv`

**Data Visualization Principles yang diterapkan:**
- One chart, one message
- Storytelling titles (data-adaptive, bukan hardcoded)
- Strategic color: 1–2 warna highlight + abu-abu untuk konteks
- Direct labeling — legend minimal
- Annotation dengan bbox (tidak overlap data)
- Proper whitespace: `fig.subplots_adjust` + `pad_inches=0.3`
- Title via `fig.suptitle`, subtitle via `fig.text` (tidak overlap)
- Legend: `frameon=False`, horizontal `ncol=3` di bawah subtitle

**5 Charts:**

| # | File | Message | Highlight color |
|---|------|---------|-----------------|
| 1 | `01_monthly_trend.png` | "Expenses Consistently Exceed Income" | RED=expense, BLUE=income |
| 2 | `02_spending_by_category.png` | "Housing Dominates — 45% of All Spending" | BLUE=top category, GRAY=rest |
| 3 | `03_monthly_cashflow.png` | "Only X of 24 Months Had Positive Cashflow" | BLUE=surplus, RED=deficit |
| 4 | `04_category_trend.png` | "Travel Is the Most Volatile Category" | BLUE=focus, GRAY=context |
| 5 | `05_day_of_week.png` | Pattern-based title (weekday vs weekend) | BLUE/RED=peak, ORANGE=weekend, GRAY=weekday |

**Brand palette:**
```python
BLUE      = "#2E86AB"   # primary, income, positive, focus
RED       = "#E63946"   # alert, expense, negative, deficit
GRAY      = "#C4CDD6"   # context, supporting
ORANGE    = "#F4A261"   # weekend (chart 5 only)
DARK_GRAY = "#4A5568"   # text
MID_GRAY  = "#718096"   # subtitle, axis labels
```

**Known issue — Chart 4 (category trend):**
Label end-of-line di-stagger dengan algoritma MIN_GAP=500. Kalau data klien punya banyak kategori dengan nilai akhir yang sangat berdekatan, mungkin perlu naikkan MIN_GAP.

**Known issue — Chart 5 (day of week):**
Title dan highlight color bersifat data-adaptive:
- Kalau weekday avg ≥ weekend avg → title "Spending Tends to Peak Mid-Week", peak bar = BLUE
- Kalau weekend avg > weekday avg → title "Weekend Spending Exceeds Weekdays", peak bar = RED
- "Peak" di legend = hari/periode dengan spending tertinggi

---

### `03_report_generator.py`
**Input:** cleaned CSV + EDA summary CSV + assets/*.png
**Output:** `reports/finance_analysis_report.html`

HTML self-contained — semua charts di-embed sebagai base64.
Isi: KPI cards, key insights, 5 charts, category table, monthly summary table.
Untuk PDF: buka di browser → Print → Save as PDF.

---

### `generate_dataset.py`
Buat synthetic dataset yang realistis untuk demo.

**Data specs:**
- 1,546 rows (sebelum cleaning) → ~1,538 rows (setelah cleaning)
- Period: 2023-01-01 → 2024-12-31
- Income: salary $8,500–$10,500/bulan + freelance $500–$2,500 (60% bulan)
- Expense: 10 kategori, amount sudah di-calibrate agar income ≈ expense
- ~12 bulan surplus, ~12 bulan deficit (realistis dan interesting)
- 10 duplicate rows (sengaja, untuk demo cleaning)
- Missing values di description, payment_method, notes (sengaja)
- ~21 outliers (sengaja)

**Jangan ubah random seed (42)** kecuali ingin dataset yang berbeda.

---

### `generate_portfolio_pdf.py`
Buat PDF 4 halaman untuk ditunjukkan ke klien Fiverr (bukan untuk GitHub).

Isi:
1. Cover — judul, deliverables, sample metrics
2. Charts — 5 chart dari assets/
3. How It Works — 4 langkah + tabel deliverables
4. CTA — call to action Fiverr + skill tags

**Output:** `reports/portfolio_finance_analysis.pdf`
**Tidak perlu di-commit ke GitHub.**

---

## Dataset Format Standar

Kolom yang dibutuhkan pipeline setelah format mapper:

| Kolom | Type | Keterangan |
|-------|------|------------|
| date | datetime | YYYY-MM-DD |
| month | string | YYYY-MM |
| year | int | 2023/2024 |
| quarter | string | Q1/Q2/Q3/Q4 |
| category | string | Housing, Food, dll |
| description | string | Narasi transaksi |
| amount | float | Positif selalu |
| type | string | "Expense" atau "Income" |
| payment_method | string | Credit Card, Cash, dll |
| notes | string | Optional |

Kolom tambahan yang ditambahkan oleh `01_data_cleaning.py`:
- `month_name` — "January 2024"
- `week` — nomor minggu ISO
- `day_of_week` — "Monday", "Tuesday", dll
- `amount_usd` — sama dengan amount (normalized)
- `is_outlier` — True/False

---

## GitHub Repository

URL: `https://github.com/armin-lee/finance-analysis`
Status: Public
Branch: main

**Yang di-commit:**
- `scripts/` — semua script (termasuk 00_format_mapper.py)
- `sample/` — sample_data.csv + 5 charts PNG
- `run_all.py`, `requirements.txt`, `.gitignore`, `README.md`, `BRIEFING.md`

**Yang TIDAK di-commit (.gitignore):**
- `data/raw/`, `data/cleaned/`, `data/output/`
- `assets/`, `reports/`
- `venv/`

---

## Dependencies

```
pandas>=2.0.0,<4.0.0
numpy>=1.24.0,<3.0.0
matplotlib>=3.7.0,<4.0.0
seaborn>=0.12.0,<1.0.0
openpyxl>=3.1.0,<4.0.0
reportlab>=3.6.0          # untuk generate_portfolio_pdf.py saja
```

Install:
```bash
pip install -r requirements.txt
pip install reportlab      # tambahan untuk PDF
```

---

## Roadmap / Next Steps

### ✅ Selesai
- Pipeline end-to-end (format mapper → cleaning → EDA → report)
- 5 charts dengan data visualization principles
- HTML report self-contained
- Portfolio PDF untuk Fiverr
- GitHub repository (public)
- README dengan embedded charts
- Sample dataset 50 rows

### 🔲 Belum selesai
- Update `sample/` folder di GitHub dengan charts terbaru (setelah redesign)
- Update README dengan charts terbaru
- Push BRIEFING.md ke GitHub
- Project portfolio #2 (Ecommerce)
- Setup Fiverr listing

---

## Instruksi untuk Claude di Sesi Baru

1. Baca file ini sebagai konteks utama project ini
2. Untuk konteks yang lebih luas (roadmap Fiverr, niche research, dll) → baca `PROJECT_CONTEXT.md`
3. Semua penjelasan dalam **Bahasa Indonesia**
4. Jawaban singkat dan to the point
5. Kalau ada issue dengan chart → cek dulu apakah masalah data atau masalah rendering
6. Jangan ubah brand palette kecuali diminta
7. Jangan hardcode nama hari/kategori di title — selalu data-adaptive
8. Pandas 2.x: hindari `inplace=True` pada `fillna` dan operasi serupa
9. Title chart: pakai `fig.suptitle`, subtitle: pakai `fig.text` — JANGAN `ax.set_title` + `ax.annotate` kombinasi (menyebabkan overlap)
