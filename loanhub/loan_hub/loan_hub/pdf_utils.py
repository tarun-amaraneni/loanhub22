from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER


# ============================================================
# GLOBAL STYLES
# ============================================================

title_style = ParagraphStyle(
    name="TitleStyle",
    fontSize=18,
    leading=22,
    spaceAfter=12,
    alignment=TA_CENTER,
    fontName="Helvetica-Bold"
)

section_style = ParagraphStyle(
    name="SectionStyle",
    fontSize=13,
    spaceBefore=18,
    spaceAfter=8,
    textColor=colors.HexColor("#1F4E79"),
    fontName="Helvetica-Bold"
)

normal_style = ParagraphStyle(
    name="NormalStyle",
    fontSize=10,
    leading=14
)


# ============================================================
# SAFE TABLE STYLING (NO INDEX ERRORS)
# ============================================================

def styled_table(table, row_count):
    style = [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E5AAC")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]

    # Zebra rows dynamically (prevents crash)
    for i in range(1, row_count):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), colors.whitesmoke))

    table.setStyle(TableStyle(style))


# ============================================================
# USER FULL REPORT (ALL LOANS + REPAYMENTS)
# ============================================================

def build_user_pdf(response, gen_no, loan_blocks):

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=25
    )

    elements = []

    # ---------------- HEADER ----------------
    elements.append(Paragraph("LOAN ACCOUNT STATEMENT", title_style))
    elements.append(Paragraph(f"<b>GEN NO:</b> {gen_no}", normal_style))
    elements.append(Spacer(1, 15))

    grand_total = 0

    # ============================================================
    # LOOP BLOCKS (IMPORTANT CHANGE)
    # ============================================================

    for block in loan_blocks:
        loan = block["loan"]
        repayments = block["repayments"]

        elements.append(Paragraph(f"Loan Code: {loan.code}", section_style))

        # -------- Loan Summary --------
        info = [
            ["Name", loan.name],
            ["Loan Type", loan.type_of_loan],
            ["Sanction Amount", f"{loan.amount:,.2f}"],
            ["Interest", f"{loan.interest:,.2f}"],
            ["Current Balance", f"{loan.balance:,.2f}"],
            ["Status", loan.loan_status],
            ["Date", str(loan.date)],
        ]

        info_table = Table(info, colWidths=[150, 330])
        info_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
        ]))

        elements.append(info_table)
        elements.append(Spacer(1, 12))

        # -------- Repayment Table --------
        elements.append(Paragraph("Repayment History", normal_style))
        elements.append(Spacer(1, 6))

        data = [["Date", "Total Paid", "Principal", "Interest"]]

        total_paid = 0

        for r in repayments:
            total_paid += float(r.total_payment or 0)

            data.append([
                str(r.created_at.date()),
                f"{r.total_payment:,.2f}",
                f"{r.paid_to_principal:,.2f}",
                f"{r.paid_to_interest:,.2f}",
            ])

        # If no repayments — avoid crash
        if len(data) == 1:
            data.append(["-", "No repayments yet", "-", "-"])

        repay_table = Table(data, colWidths=[100, 120, 120, 120])
        styled_table(repay_table, len(data))

        elements.append(repay_table)
        elements.append(Spacer(1, 6))

        elements.append(
            Paragraph(f"<b>Total Repaid:</b> {total_paid:,.2f}", normal_style)
        )

        grand_total += total_paid

        elements.append(Spacer(1, 25))

    # -------- GRAND TOTAL --------
    elements.append(Paragraph("<b>Overall Amount Repaid</b>", section_style))
    elements.append(
        Paragraph(f"<b>{grand_total:,.2f}</b>", normal_style)
    )

    doc.build(elements)

# ============================================================
# SINGLE LOAN REPORT  (UPDATED — ACCEPTS REPAYMENTS)
# ============================================================

def build_single_loan_pdf(response, loan, repayments):

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=25
    )

    elements = []

    # -------- Title --------
    elements.append(Paragraph("LOAN DETAIL REPORT", title_style))
    elements.append(Spacer(1, 20))

    # -------- Loan Information --------
    info = [
        ["Loan Code", loan.code],
        ["GEN NO", loan.gen_no],
        ["Name", loan.name],
        ["Type", loan.type_of_loan],
        ["Sanction Amount", f"{loan.amount:,.2f}"],
        ["Interest", f"{loan.interest:,.2f}"],
        ["Current Balance", f"{loan.balance:,.2f}"],
        ["Status", loan.loan_status],
        ["Date", str(loan.date)],
    ]

    table = Table(info, colWidths=[150, 330])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # -------- Repayments --------
    elements.append(Paragraph("Repayment History", section_style))
    elements.append(Spacer(1, 6))

    data = [["Date", "Total Paid", "Principal", "Interest"]]

    total_paid = 0

    for r in repayments:
        total_paid += float(r.total_payment or 0)

        data.append([
            str(r.created_at.date()),
            f"{r.total_payment:,.2f}",
            f"{r.paid_to_principal:,.2f}",
            f"{r.paid_to_interest:,.2f}",
        ])

    # If no repayments — avoid crash
    if len(data) == 1:
        data.append(["-", "No repayments yet", "-", "-"])

    repay_table = Table(data, colWidths=[100, 120, 120, 120])
    styled_table(repay_table, len(data))

    elements.append(repay_table)
    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(f"<b>Total Repaid :</b> {total_paid:,.2f}", normal_style)
    )

    doc.build(elements)