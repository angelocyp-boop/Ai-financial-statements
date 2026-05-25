"""Word document report generator using python-docx."""
from __future__ import annotations
import os
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.engagement import Engagement
from app.models.statement import FinancialStatement
from app.models.disclosure import DisclosureNote
from app.config import settings


def _fmt(amount: Decimal | None) -> str:
    if amount is None:
        return "-"
    return f"{amount:,.0f}"


def generate_word_report(eng_id: int, db: Session) -> str:
    try:
        from docx import Document
        from docx.shared import Pt, Cm, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT
    except ImportError:
        raise RuntimeError("python-docx not installed")

    eng = db.query(Engagement).filter(Engagement.id == eng_id).first()
    if not eng:
        raise ValueError("Engagement not found")

    doc = Document()

    # Styles
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(10)

    # Cover page
    title = doc.add_heading('', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(eng.client.name if eng.client else 'Company')
    run.font.size = Pt(22)
    run.font.bold = True

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.add_run(f'Financial Statements\nFor the year ended {eng.period_end.strftime("%d %B %Y")}').font.size = Pt(14)

    std_para = doc.add_paragraph()
    std_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    std_para.add_run(f'Prepared in accordance with {eng.reporting_standard.value}').font.size = Pt(11)

    doc.add_page_break()

    # Financial Statements
    stmts = db.query(FinancialStatement).filter(FinancialStatement.engagement_id == eng_id).all()
    stmt_titles = {"SFP": "Statement of Financial Position", "PL": "Statement of Profit or Loss",
                   "CASH_FLOW": "Statement of Cash Flows", "EQUITY": "Statement of Changes in Equity"}

    for stmt in stmts:
        doc.add_heading(stmt_titles.get(stmt.statement_type.value, stmt.statement_type.value), 1)
        doc.add_paragraph(f'As at {eng.period_end.strftime("%d %B %Y")}' if stmt.statement_type.value == "SFP"
                          else f'For the year ended {eng.period_end.strftime("%d %B %Y")}')

        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        hdr = table.rows[0].cells
        hdr[0].text = 'Description'
        hdr[1].text = f'{eng.year}\n{eng.currency}'
        hdr[2].text = f'{eng.comparative_year or ""}\n{eng.currency}'

        for line in stmt.lines:
            row = table.add_row().cells
            indent = '    ' * line.indent_level
            row[0].text = indent + line.label
            row[1].text = _fmt(line.current_amount)
            row[2].text = _fmt(line.comparative_amount)
            if line.is_bold or line.is_total or line.is_header:
                for cell in row:
                    for para in cell.paragraphs:
                        for run in para.runs:
                            run.bold = True

        doc.add_page_break()

    # Disclosure Notes
    notes = db.query(DisclosureNote).filter(DisclosureNote.engagement_id == eng_id).order_by(DisclosureNote.order).all()
    if notes:
        doc.add_heading('Notes to the Financial Statements', 1)
        for note in notes:
            doc.add_heading(f'{note.note_number}. {note.title}', 2)
            if note.content:
                # Strip HTML tags for Word
                import re
                clean = re.sub(r'<[^>]+>', '', note.content)
                doc.add_paragraph(clean)
            doc.add_paragraph('')

    # Save
    os.makedirs(settings.EXPORT_DIR, exist_ok=True)
    filename = f"financial_statements_{eng_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.docx"
    file_path = os.path.join(settings.EXPORT_DIR, filename)
    doc.save(file_path)
    return file_path


def generate_pdf_report(eng_id: int, db: Session) -> str:
    """Generate PDF by converting the Word document via ReportLab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    except ImportError:
        raise RuntimeError("reportlab not installed")

    eng = db.query(Engagement).filter(Engagement.id == eng_id).first()
    if not eng:
        raise ValueError("Engagement not found")

    os.makedirs(settings.EXPORT_DIR, exist_ok=True)
    filename = f"financial_statements_{eng_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join(settings.EXPORT_DIR, filename)

    doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(eng.client.name if eng.client else 'Company', styles['Title']))
    story.append(Paragraph(f'Financial Statements for the year ended {eng.period_end.strftime("%d %B %Y")}', styles['Heading2']))
    story.append(Paragraph(f'Prepared in accordance with {eng.reporting_standard.value}', styles['Normal']))
    story.append(Spacer(1, 1*cm))

    stmts = db.query(FinancialStatement).filter(FinancialStatement.engagement_id == eng_id).all()
    stmt_titles = {"SFP": "Statement of Financial Position", "PL": "Statement of Profit or Loss"}

    for stmt in stmts:
        story.append(Paragraph(stmt_titles.get(stmt.statement_type.value, stmt.statement_type.value), styles['Heading1']))
        data = [["Description", f"{eng.year}\n({eng.currency})", f"{eng.comparative_year or ''}\n({eng.currency})"]]
        for line in stmt.lines:
            indent = '   ' * line.indent_level
            data.append([indent + line.label, _fmt(line.current_amount), _fmt(line.comparative_amount)])

        t = Table(data, colWidths=[10*cm, 3*cm, 3*cm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3a5c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('LEFTPADDING', (0, 0), (0, -1), 6),
        ]))
        story.append(t)
        story.append(PageBreak())

    doc.build(story)
    return file_path
