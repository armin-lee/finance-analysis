"""
Generate realistic personal finance dataset.
Mirip dengan dataset Kaggle Personal Finance.
"""
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# Config
START_DATE = datetime(2023, 1, 1)
END_DATE   = datetime(2024, 12, 31)
N_ROWS     = 1500

CATEGORIES = {
    "Housing":      {"weight": 0.15, "min": 500,  "max": 2500},
    "Food":         {"weight": 0.20, "min": 5,    "max": 300},
    "Transport":    {"weight": 0.12, "min": 10,   "max": 500},
    "Healthcare":   {"weight": 0.06, "min": 20,   "max": 800},
    "Shopping":     {"weight": 0.12, "min": 10,   "max": 600},
    "Entertainment":{"weight": 0.08, "min": 5,    "max": 200},
    "Utilities":    {"weight": 0.08, "min": 30,   "max": 300},
    "Education":    {"weight": 0.05, "min": 50,   "max": 1000},
    "Travel":       {"weight": 0.07, "min": 100,  "max": 3000},
    "Other":        {"weight": 0.07, "min": 5,    "max": 500},
}

INCOME_SOURCES = ["Salary", "Freelance", "Investment", "Bonus", "Other Income"]

PAYMENT_METHODS = ["Credit Card", "Debit Card", "Cash", "Bank Transfer", "Digital Wallet"]

DESCRIPTIONS = {
    "Housing":       ["Monthly Rent", "Mortgage Payment", "Home Insurance", "Property Tax", "Maintenance"],
    "Food":          ["Grocery Store", "Restaurant", "Coffee Shop", "Food Delivery", "Supermarket"],
    "Transport":     ["Gas Station", "Uber/Grab", "Public Transit", "Car Insurance", "Parking"],
    "Healthcare":    ["Doctor Visit", "Pharmacy", "Dental", "Health Insurance", "Lab Tests"],
    "Shopping":      ["Online Shopping", "Clothing Store", "Electronics", "Home Goods", "Amazon"],
    "Entertainment": ["Netflix", "Spotify", "Cinema", "Games", "Gym Membership"],
    "Utilities":     ["Electricity Bill", "Water Bill", "Internet", "Phone Bill", "Gas Bill"],
    "Education":     ["Online Course", "Books", "Tuition", "Training", "Workshop"],
    "Travel":        ["Flight Ticket", "Hotel", "Airbnb", "Travel Insurance", "Tour Package"],
    "Other":         ["Miscellaneous", "ATM Withdrawal", "Bank Fee", "Subscription", "Donation"],
}

def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

# Generate expenses
rows = []
categories = list(CATEGORIES.keys())
weights = [CATEGORIES[c]["weight"] for c in categories]

for _ in range(N_ROWS):
    cat = random.choices(categories, weights=weights)[0]
    cfg = CATEGORIES[cat]
    amount = round(random.uniform(cfg["min"], cfg["max"]), 2)

    # Tambah noise — beberapa transaksi memiliki anomali
    if random.random() < 0.02:  # 2% outlier
        amount = amount * random.uniform(3, 8)

    date = random_date(START_DATE, END_DATE)

    rows.append({
        "date":           date.strftime("%Y-%m-%d"),
        "month":          date.strftime("%Y-%m"),
        "year":           date.year,
        "quarter":        f"Q{(date.month - 1) // 3 + 1}",
        "category":       cat,
        "description":    random.choice(DESCRIPTIONS[cat]),
        "amount":         amount,
        "type":           "Expense",
        "payment_method": random.choice(PAYMENT_METHODS),
        "notes":          "",
    })

# Generate income
for month_offset in range(24):
    date = START_DATE + timedelta(days=month_offset * 30)
    # Salary setiap bulan
    rows.append({
        "date":           date.strftime("%Y-%m-%d"),
        "month":          date.strftime("%Y-%m"),
        "year":           date.year,
        "quarter":        f"Q{(date.month - 1) // 3 + 1}",
        "category":       "Income",
        "description":    "Monthly Salary",
        "amount":         random.uniform(4500, 5500),
        "type":           "Income",
        "payment_method": "Bank Transfer",
        "notes":          "",
    })
    # Freelance income kadang-kadang
    if random.random() < 0.4:
        rows.append({
            "date":           (date + timedelta(days=random.randint(1, 28))).strftime("%Y-%m-%d"),
            "month":          date.strftime("%Y-%m"),
            "year":           date.year,
            "quarter":        f"Q{(date.month - 1) // 3 + 1}",
            "category":       "Income",
            "description":    "Freelance Payment",
            "amount":         round(random.uniform(200, 1500), 2),
            "type":           "Income",
            "payment_method": "Bank Transfer",
            "notes":          "",
        })

df = pd.DataFrame(rows)
df = df.sort_values("date").reset_index(drop=True)

# Tambah beberapa missing values dan dirty data untuk simulasi cleaning
dirty_idx = random.sample(range(len(df)), 30)
for i in dirty_idx:
    col = random.choice(["description", "payment_method", "notes"])
    df.at[i, col] = ""

# Tambah beberapa duplicate rows
dup_idx = random.sample(range(len(df)), 10)
df = pd.concat([df, df.iloc[dup_idx]], ignore_index=True)

# Shuffle sedikit
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

output_path = "../data/raw/personal_finance_raw.csv"
df.to_csv(output_path, index=False)

print(f"✅ Dataset generated: {len(df)} rows")
print(f"   Date range: {df['date'].min()} → {df['date'].max()}")
print(f"   Categories: {df['category'].nunique()}")
print(f"   Missing values: {df.isnull().sum().sum()}")
print(f"   Duplicates: ~10 baris (sengaja untuk simulasi cleaning)")
print(f"   Saved to: {output_path}")
