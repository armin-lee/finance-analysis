"""
Portfolio PDF Generator
========================
Buat PDF portofolio profesional untuk ditunjukkan ke klien Fiverr.
Isi: cover, overview jasa, sample charts, sample metrics, CTA.
"""

import os
import base64
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, HRFlowable, PageBreak
)
from reportlab.platypus import KeepTogether
from reportlab.lib.utils import ImageReader

# ── CONFIG ────────────────────────────────────────────────────────────────────
ASSETS_DIR  = "../assets"
OUTPUT_PATH = "../reports/portfolio_finance_analysis.pdf"

# Brand colors
BLUE        = colors.HexColor("#2E86AB")
DARK        = colors.HexColor("#2D3748")
GRAY        = colors.HexColor("#718096")
LIGHT_GRAY  = colors.HexColor("#F7FAFC")
RED         = colors.HexColor("#C73E1D")
GREEN       = colors.HexColor("#44BBA4")
WHITE       = colors.white
# ─────────────────────────────────────────────────────────────────────────────

W, H = A4  # 210 x 297 mm

def build_styles():
    base = getSampleStyleSheet()
    styles = {
        "cover_title": ParagraphStyle("cover_title",
            fontSize=28, fontName="Helvetica-Bold",
            textColor=WHITE, alignment=TA_CENTER, spaceAfter=6),
        "cover_sub": ParagraphStyle("cover_sub",
            fontSize=13, fontName="Helvetica",
            textColor=colors.HexColor("#BEE3F8"), alignment=TA_CENTER, spaceAfter=4),
        "cover_tag": ParagraphStyle("cover_tag",
            fontSize=10, fontName="Helvetica",
            textColor=colors.HexColor("#90CDF4"), alignment=TA_CENTER),
        "section_title": ParagraphStyle("section_title",
            fontSize=16, fontName="Helvetica-Bold",
            textColor=BLUE, spaceBefore=14, spaceAfter=8,
            borderPad=4),
        "body": ParagraphStyle("body",
            fontSize=10, fontName="Helvetica",
            textColor=DARK, spaceAfter=6, leading=15),
        "bullet": ParagraphStyle("bullet",
            fontSize=10, fontName="Helvetica",
            textColor=DARK, spaceAfter=4, leftIndent=16, leading=14),
        "caption": ParagraphStyle("caption",
            fontSize=8, fontName="Helvetica",
            textColor=GRAY, alignment=TA_CENTER, spaceAfter=8),
        "metric_label": ParagraphStyle("metric_label",
            fontSize=8, fontName="Helvetica",
            textColor=GRAY, alignment=TA_CENTER),
        "metric_value": ParagraphStyle("metric_value",
            fontSize=18, fontName="Helvetica-Bold",
            textColor=BLUE, alignment=TA_CENTER),
        "footer": ParagraphStyle("footer",
            fontSize=8, fontName="Helvetica",
            textColor=GRAY, alignment=TA_CENTER),
        "cta_title": ParagraphStyle("cta_title",
            fontSize=18, fontName="Helvetica-Bold",
            textColor=WHITE, alignment=TA_CENTER, spaceAfter=8),
        "cta_body": ParagraphStyle("cta_body",
            fontSize=11, fontName="Helvetica",
            textColor=colors.HexColor("#BEE3F8"), alignment=TA_CENTER, spaceAfter=6),
        "tag": ParagraphStyle("tag",
            fontSize=9, fontName="Helvetica-Bold",
            textColor=BLUE, alignment=TA_CENTER),
    }
    return styles


def cover_page(styles) -> list:
    """Halaman cover dengan background biru."""
    elements = []

    # Background biru via table
    cover_data = [[Paragraph("", styles["body"])]]
    cover_table = Table(cover_data, colWidths=[W - 40*mm], rowHeights=[60*mm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLUE),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [BLUE]),
    ]))

    # Header box
    header_content = [
        [Paragraph("📊", ParagraphStyle("icon", fontSize=32, alignment=TA_CENTER, spaceAfter=4))],
        [Paragraph("Personal Finance", styles["cover_title"])],
        [Paragraph("Data Analysis Service", styles["cover_title"])],
        [Spacer(1, 4*mm)],
        [Paragraph("Professional data analysis for individuals & small businesses", styles["cover_sub"])],
        [Paragraph("Clean Data  •  Visual Insights  •  Actionable Reports", styles["cover_tag"])],
    ]

    header_table = Table(header_content, colWidths=[W - 40*mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLUE),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))

    elements.append(Spacer(1, 20*mm))
    elements.append(header_table)
    elements.append(Spacer(1, 10*mm))

    # Divider
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#BEE3F8")))
    elements.append(Spacer(1, 8*mm))

    # What you get section
    elements.append(Paragraph("What You Get", ParagraphStyle("wygTitle",
        fontSize=13, fontName="Helvetica-Bold", textColor=DARK,
        alignment=TA_CENTER, spaceAfter=8)))

    deliverables = [
        ["✓  Cleaned & validated dataset",    "✓  5 professional charts (PNG)"],
        ["✓  Monthly cashflow analysis",       "✓  Category spending breakdown"],
        ["✓  Outlier & anomaly detection",     "✓  Full HTML report for client"],
    ]
    del_table = Table(deliverables, colWidths=[(W-40*mm)/2, (W-40*mm)/2])
    del_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("TEXTCOLOR", (0,0), (-1,-1), DARK),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    elements.append(del_table)
    elements.append(Spacer(1, 8*mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=GRAY))
    elements.append(Spacer(1, 6*mm))

    # Sample metrics
    elements.append(Paragraph("Sample Project Metrics", ParagraphStyle("metTitle",
        fontSize=11, fontName="Helvetica-Bold", textColor=DARK,
        alignment=TA_CENTER, spaceAfter=8)))

    metrics = [
        [
            Paragraph("1,536", styles["metric_value"]),
            Paragraph("24", styles["metric_value"]),
            Paragraph("5", styles["metric_value"]),
            Paragraph("100%", styles["metric_value"]),
        ],
        [
            Paragraph("Transactions\nProcessed", styles["metric_label"]),
            Paragraph("Months\nCovered", styles["metric_label"]),
            Paragraph("Charts\nGenerated", styles["metric_label"]),
            Paragraph("Automated\nPipeline", styles["metric_label"]),
        ],
    ]
    metrics_table = Table(metrics, colWidths=[(W-40*mm)/4]*4)
    metrics_table.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LINEBELOW", (0,0), (-1,0), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    elements.append(metrics_table)

    elements.append(PageBreak())
    return elements


def charts_page(styles) -> list:
    """Halaman dengan sample charts."""
    elements = []

    elements.append(Paragraph("Sample Output: Charts & Visualizations", styles["section_title"]))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceAfter=8))
    elements.append(Paragraph(
        "Every analysis includes professional charts that make your financial data easy to understand at a glance.",
        styles["body"]))
    elements.append(Spacer(1, 4*mm))

    chart_files = [
        ("01_monthly_trend.png",         "Chart 1 — Monthly Income vs Expense Trend"),
        ("02_spending_by_category.png",  "Chart 2 — Spending Distribution by Category"),
        ("03_monthly_cashflow.png",      "Chart 3 — Monthly Cashflow (Surplus/Deficit)"),
        ("04_category_trend.png",        "Chart 4 — Top Category Spending Over Time"),
        ("05_day_of_week.png",           "Chart 5 — Average Spending by Day of Week"),
    ]

    for fname, caption in chart_files:
        path = os.path.join(ASSETS_DIR, fname)
        if os.path.exists(path):
            img = Image(path, width=W - 40*mm, height=55*mm, kind="proportional")
            elements.append(img)
            elements.append(Paragraph(caption, styles["caption"]))
            elements.append(Spacer(1, 3*mm))

    elements.append(PageBreak())
    return elements


def process_page(styles) -> list:
    """Halaman proses kerja dan deliverables."""
    elements = []

    elements.append(Paragraph("How It Works", styles["section_title"]))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceAfter=8))

    steps = [
        ("1", "You Send Your Data",
         "Upload your CSV or Excel file containing your transactions. Any format accepted."),
        ("2", "Data Cleaning",
         "I validate, fix, and clean your data — handle missing values, duplicates, and outliers."),
        ("3", "Analysis & Visualization",
         "Generate 5 professional charts and compute key financial metrics."),
        ("4", "Report Delivery",
         "You receive a clean dataset, all charts (PNG), and a full HTML report ready to present."),
    ]

    for num, title, desc in steps:
        step_data = [[
            Paragraph(num, ParagraphStyle("stepNum",
                fontSize=18, fontName="Helvetica-Bold",
                textColor=WHITE, alignment=TA_CENTER)),
            Table([[Paragraph(title, ParagraphStyle("stepTitle",
                        fontSize=11, fontName="Helvetica-Bold", textColor=DARK))],
                   [Paragraph(desc, styles["body"])]],
                  colWidths=[W - 40*mm - 20*mm])
        ]]
        step_table = Table(step_data, colWidths=[14*mm, W - 40*mm - 14*mm])
        step_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,-1), BLUE),
            ("ALIGN", (0,0), (0,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING", (1,0), (1,-1), 10),
            ("ROUNDEDCORNERS", [3]),
        ]))
        elements.append(step_table)
        elements.append(Spacer(1, 4*mm))

    elements.append(Spacer(1, 6*mm))
    elements.append(Paragraph("Deliverables Included", styles["section_title"]))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceAfter=8))

    deliverables = [
        ["Deliverable", "Format", "Description"],
        ["Cleaned Dataset", "CSV", "Validated, duplicate-free, ready for further use"],
        ["Cleaning Report", "TXT", "Full audit trail of all changes made"],
        ["5 Charts", "PNG", "High-resolution, ready to present or embed"],
        ["EDA Summary", "CSV", "Key metrics in tabular format"],
        ["Full Report", "HTML", "Self-contained report with all charts and tables"],
    ]
    del_table = Table(deliverables,
        colWidths=[(W-40*mm)*0.3, (W-40*mm)*0.15, (W-40*mm)*0.55])
    del_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), BLUE),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    elements.append(del_table)
    elements.append(PageBreak())
    return elements


def cta_page(styles) -> list:
    """Halaman penutup dengan call to action."""
    elements = []

    elements.append(Spacer(1, 20*mm))

    cta_content = [
        [Paragraph("Ready to Understand Your Finances?", styles["cta_title"])],
        [Spacer(1, 4*mm)],
        [Paragraph("Send me your data and I'll deliver a complete analysis within 24–48 hours.", styles["cta_body"])],
        [Paragraph("No technical knowledge required on your end.", styles["cta_body"])],
        [Spacer(1, 8*mm)],
        [Paragraph("Find me on Fiverr", ParagraphStyle("ctaLink",
            fontSize=14, fontName="Helvetica-Bold",
            textColor=WHITE, alignment=TA_CENTER))],
    ]
    cta_table = Table(cta_content, colWidths=[W - 40*mm])
    cta_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLUE),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 16),
        ("RIGHTPADDING", (0,0), (-1,-1), 16),
        ("ROUNDEDCORNERS", [6]),
    ]))
    elements.append(cta_table)
    elements.append(Spacer(1, 10*mm))

    # Tags
    tags = ["Python", "Pandas", "Data Cleaning", "EDA", "Visualization", "Finance Analytics"]
    tag_data = [[Paragraph(f"  {t}  ", styles["tag"]) for t in tags]]
    tag_table = Table(tag_data, colWidths=[(W-40*mm)/len(tags)]*len(tags))
    tag_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#EBF8FF")),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#BEE3F8")),
    ]))
    elements.append(tag_table)
    elements.append(Spacer(1, 8*mm))

    elements.append(Paragraph(
        "Portfolio sample — data is synthetic and for demonstration purposes only.",
        styles["footer"]))

    return elements


def build_pdf():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=15*mm,
        bottomMargin=15*mm,
        title="Personal Finance Data Analysis — Portfolio",
        author="Data Analysis Service",
    )

    styles = build_styles()

    story = []
    story += cover_page(styles)
    story += charts_page(styles)
    story += process_page(styles)
    story += cta_page(styles)

    doc.build(story)
    size_kb = os.path.getsize(OUTPUT_PATH) / 1024
    print(f"✅ Portfolio PDF saved: {OUTPUT_PATH}")
    print(f"   Pages: 4 | Size: {size_kb:.1f} KB")


if __name__ == "__main__":
    build_pdf()
