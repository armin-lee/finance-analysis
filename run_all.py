"""
run_all.py — Full pipeline runner
===================================
Usage:
    python run_all.py              # Run all steps
    python run_all.py --skip-gen   # Skip dataset generation (use existing data)
"""

import subprocess
import sys
import os
import time
import argparse

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR  = os.path.join(PROJECT_ROOT, "scripts")


def check_requirements():
    required = ["pandas", "numpy", "matplotlib", "seaborn", "openpyxl"]
    missing = [pkg for pkg in required if not __import_safe(pkg)]
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"   Run: pip install -r requirements.txt\n")
        sys.exit(1)


def __import_safe(pkg):
    try:
        __import__(pkg)
        return True
    except ImportError:
        return False


def check_input_data(skip_gen: bool) -> bool:
    raw_path = os.path.join(PROJECT_ROOT, "data", "raw", "personal_finance_raw.csv")
    if not os.path.exists(raw_path):
        if skip_gen:
            print(f"\n❌ Data not found: {raw_path}")
            print(f"   Remove --skip-gen to auto-generate, or place your CSV there.\n")
            sys.exit(1)
        return False
    return True


def run_script(script_name: str, label: str, step: int, total: int):
    print(f"\n[{step}/{total}] {label}")
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    print(f"       Running: scripts/{script_name}")
    start = time.time()

    result = subprocess.run(
        [sys.executable, script_path],
        cwd=SCRIPTS_DIR,
    )
    elapsed = time.time() - start

    if result.returncode != 0:
        print(f"\n❌ Failed at step {step}: {script_name}")
        sys.exit(1)

    print(f"       ✓ Done in {elapsed:.1f}s")
    return elapsed


def main():
    parser = argparse.ArgumentParser(description="Finance Analysis Pipeline")
    parser.add_argument("--skip-gen", action="store_true",
                        help="Skip dataset generation")
    args = parser.parse_args()

    print("\n" + "=" * 55)
    print("  📊 FINANCE ANALYSIS — FULL PIPELINE")
    print("=" * 55)
    print(f"  Python : {sys.version.split()[0]}")
    print(f"  Root   : {PROJECT_ROOT}")

    # Pre-flight
    print("\n⚙️  Pre-flight checks...")
    check_requirements()
    print("  ✓ All dependencies installed")

    data_exists = check_input_data(args.skip_gen)

    # Ensure dirs exist
    for d in ["data/raw", "data/cleaned", "data/output", "assets", "reports"]:
        os.makedirs(os.path.join(PROJECT_ROOT, d), exist_ok=True)

    # Build pipeline
    scripts = []
    if not args.skip_gen and not data_exists:
        scripts.append(("generate_dataset.py", "Generate sample dataset"))

    scripts += [
        ("01_data_cleaning.py",    "Data cleaning & validation"),
        ("02_eda_visualization.py", "EDA & chart generation"),
        ("03_report_generator.py",  "HTML report generation"),
    ]

    total = len(scripts)
    print(f"\n🚀 Running {total} steps...\n" + "-" * 55)
    start_all = time.time()

    for i, (script, label) in enumerate(scripts, 1):
        run_script(script, label, i, total)

    report_path = os.path.join(PROJECT_ROOT, "reports", "finance_analysis_report.html")
    print("\n" + "=" * 55)
    print("  ✅ PIPELINE COMPLETE")
    print("=" * 55)
    print(f"  Total time   : {time.time() - start_all:.1f}s")
    print(f"  Report       : reports/finance_analysis_report.html")
    print(f"  Charts       : assets/ (5 PNG files)")
    print(f"  Cleaned data : data/cleaned/personal_finance_clean.csv")
    print(f"  Summary      : data/output/eda_summary.csv")
    print(f"\n  💡 Open in browser: {report_path}")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
