import json
import os
import urllib.request
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# -------- CONFIG --------
SCHOOL_NAME = "Springfield High School"
EXAM_TITLE = "Final Examination 2025"
SUBJECT = "Science"
DATE = "August 2025"
DURATION = "3 Hours"
MAX_MARKS = "100"
LOGO_URL = ""  # optional
LOGO_FILE = "school_logo.jpg"
WATERMARK_TEXT = "CONFIDENTIAL"

# Download logo if needed
if LOGO_URL and not os.path.exists(LOGO_FILE):
    try:
        urllib.request.urlretrieve(LOGO_URL, LOGO_FILE)
    except:
        LOGO_FILE = None

# -------- Load Questions --------
with open("questions.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# -------- PDF Setup --------
def header_footer(canvas, doc):
    # Watermark (very light)
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 50)
    canvas.setFillGray(0.92)
    canvas.rotate(30)
    canvas.drawCentredString(A4[0] / 2, A4[1] / 3, WATERMARK_TEXT)
    canvas.restoreState()

    # Header line
    canvas.setStrokeColor(colors.HexColor("#003366"))
    canvas.setLineWidth(1)
    canvas.line(50, A4[1] - 65, A4[0] - 50, A4[1] - 65)

    # Header text
    canvas.setFont("Helvetica-Bold", 13)
    canvas.drawString(50, A4[1] - 50, f"{SCHOOL_NAME} - {EXAM_TITLE}")

    canvas.setFont("Helvetica", 10)
    canvas.drawString(50, A4[1] - 62,
                      f"Subject: {SUBJECT} | Duration: {DURATION} | Max Marks: {MAX_MARKS}")

    # Footer
    canvas.setStrokeColor(colors.HexColor("#003366"))
    canvas.line(50, 50, A4[0] - 50, 50)
    page_num = canvas.getPageNumber()
    canvas.setFont("Helvetica", 9)
    canvas.drawCentredString(A4[0] / 2.0, 38, f"Page {page_num}")

doc = SimpleDocTemplate(
    "question_paper_with_answers.pdf",
    pagesize=A4,
    rightMargin=50, leftMargin=50,
    topMargin=80, bottomMargin=65
)

# -------- Styles --------
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitlePage', fontSize=28, leading=34, alignment=1,
                          textColor=colors.HexColor("#003366"), fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name='SchoolName', fontSize=22, leading=28, alignment=1,
                          fontName="Helvetica-Bold", textColor=colors.HexColor("#222222")))
styles.add(ParagraphStyle(name='SectionHeading', fontSize=14, leading=18, spaceAfter=8,
                          textColor=colors.white, backColor=colors.HexColor("#003366"),
                          alignment=0, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name='Question', fontSize=12, leading=15,
                          fontName="Times-Roman", spaceAfter=4))
styles.add(ParagraphStyle(name='MarksRight', fontSize=10, alignment=2,
                          textColor=colors.HexColor("#666666")))
styles.add(ParagraphStyle(name='Option', fontSize=11, leftIndent=14, spaceAfter=2,
                          fontName="Times-Roman"))
styles.add(ParagraphStyle(name='Instruction', fontSize=11, leading=15,
                          textColor=colors.black, leftIndent=6))
styles.add(ParagraphStyle(name='Answer', fontSize=11, leading=14,
                          textColor=colors.green, leftIndent=12, fontName="Helvetica-Oblique"))

elements = []

# -------- Title Page --------
elements.append(Spacer(1, 1.0 * inch))
if LOGO_FILE and os.path.exists(LOGO_FILE):
    img = Image(LOGO_FILE, width=1.6 * inch, height=1.6 * inch)
    img.hAlign = 'CENTER'
    elements.append(img)
    elements.append(Spacer(1, 0.3 * inch))

elements.append(Paragraph(SCHOOL_NAME, styles['SchoolName']))
elements.append(Spacer(1, 0.15 * inch))
elements.append(Paragraph(EXAM_TITLE, styles['TitlePage']))
elements.append(Spacer(1, 0.3 * inch))

# Exam details table
details = [
    ["Subject:", SUBJECT],
    ["Date:", DATE],
    ["Duration:", DURATION],
    ["Maximum Marks:", MAX_MARKS]
]
details_table = Table(details, colWidths=[120, doc.width - 120])
details_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 11),
    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
]))
elements.append(details_table)
elements.append(Spacer(1, 0.4 * inch))

# Instructions block
instruction_text = (
    "<b>Instructions:</b><br/>"
    "1. Answer all questions.<br/>"
    "2. Marks are indicated against each question.<br/>"
    "3. Write neatly and clearly.<br/>"
    "4. Read each question carefully before answering."
)
instruction_table = Table([[Paragraph(instruction_text, styles['Instruction'])]], colWidths=[doc.width])
instruction_table.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#003366")),
    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#E6F0FF")),
    ('INNERPADDING', (0, 0), (-1, -1), 8),
]))
elements.append(instruction_table)
elements.append(PageBreak())

# -------- Question Helpers --------
q_number = 1

def add_section(title):
    elements.append(Spacer(1, 0.2 * inch))
    section_table = Table([[Paragraph(title, styles['SectionHeading'])]], colWidths=[doc.width])
    section_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5)
    ]))
    elements.append(section_table)
    elements.append(Spacer(1, 0.15 * inch))

def add_mcq(qs):
    global q_number
    bg_toggle = True
    for q in qs:
        bg_color = colors.HexColor("#F9F9F9") if bg_toggle else colors.white
        marks_text = f"({q.get('marks', '')} marks)" if q.get('marks') else ""
        
        question_table = Table([
            [Paragraph(f"{q_number}. {q['question']}", styles['Question']),
             Paragraph(marks_text, styles['MarksRight'])]
        ], colWidths=[doc.width - 50, 50])
        question_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        block = [question_table]

        labels = ["A", "B", "C", "D", "E", "F"]
        opts = [f"({labels[i]}) {o}" for i, o in enumerate(q['options'].values())]
        col_count = 2 if len(opts) <= 4 else 3
        option_rows = [opts[i:i+col_count] for i in range(0, len(opts), col_count)]
        opt_table = Table(
            [[Paragraph(opt, styles['Option']) for opt in row] for row in option_rows],
            colWidths=[doc.width / col_count - 10] * col_count
        )
        opt_table.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 18),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
        ]))
        block.append(opt_table)

        ans_text = ""
        if "answers" in q:
            ans_text = ", ".join(f"{k}: {v}" for k, v in q["answers"].items())
        elif "correct_options" in q:
            ans_text = ", ".join(q["correct_options"])
        elif "correct_option" in q:
            ans_text = q["correct_option"]

        block.append(Paragraph(f"Answer: {ans_text}", styles['Answer']))

        # Add explanation if provided
        if q.get("explanation"):
            exp_table = Table([[Paragraph(f"<b>Explanation:</b><br/>{q['explanation']}", styles['Instruction'])]],
                            colWidths=[doc.width])
            exp_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#003366")),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#E6F0FF")),
                ('INNERPADDING', (0, 0), (-1, -1), 6),
            ]))
            block.append(Spacer(1, 0.05 * inch))
            block.append(exp_table)

        block.append(Spacer(1, 0.12 * inch))
        elements.append(KeepTogether(block))
        bg_toggle = not bg_toggle
        q_number += 1


def add_written(qs, lines=2):
    global q_number
    bg_toggle = True
    for q in qs:
        bg_color = colors.HexColor("#F9F9F9") if bg_toggle else colors.white
        marks_text = f"({q.get('marks', '')} marks)" if q.get('marks') else ""
        
        # Question row
        question_table = Table([
            [Paragraph(f"{q_number}. {q['question']}", styles['Question']),
             Paragraph(marks_text, styles['MarksRight'])]
        ], colWidths=[doc.width - 50, 50])
        question_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        block = [question_table]

        # Answer lines for student copy
        for _ in range(lines):
            block.append(Spacer(1, 0.25 * inch))
            block.append(Table([[""]], colWidths=[doc.width],
                               style=TableStyle([
                                   ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.HexColor("#AAAAAA")),
                                   ('LINESTYLE', (0, 0), (-1, -1), 'dotted')
                               ])))

        # Answer text (teacher copy)
        ans = q.get("answer")
        if isinstance(ans, list):
            ans = ", ".join(str(a) for a in ans)
        block.append(Spacer(1, 0.1 * inch))
        block.append(Paragraph(f"Answer: {ans}", styles['Answer']))

        # Key Points block
        if q.get("key_points"):
            key_points_text = "<br/>".join([f"• {kp}" for kp in q["key_points"]])
            kp_table = Table([[Paragraph(f"<b>Key Points:</b><br/>{key_points_text}", styles['Instruction'])]],
                             colWidths=[doc.width])
            kp_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#003366")),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#E6F0FF")),
                ('INNERPADDING', (0, 0), (-1, -1), 6),
            ]))
            block.append(Spacer(1, 0.05 * inch))
            block.append(kp_table)

        # Explanation block
        if q.get("explanation"):
            exp_table = Table([[Paragraph(f"<b>Explanation:</b><br/>{q['explanation']}", styles['Instruction'])]],
                              colWidths=[doc.width])
            exp_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#003366")),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#E6F0FF")),
                ('INNERPADDING', (0, 0), (-1, -1), 6),
            ]))
            block.append(Spacer(1, 0.05 * inch))
            block.append(exp_table)

        block.append(Spacer(1, 0.15 * inch))
        elements.append(KeepTogether(block))
        bg_toggle = not bg_toggle
        q_number += 1




# -------- Build Sections --------
if "single_correct_mcq" in data:
    add_section("Single Correct Multiple Choice Questions")
    add_mcq(data["single_correct_mcq"])
if "multiple_correct_mcq" in data:
    add_section("Multiple Correct Multiple Choice Questions")
    add_mcq(data["multiple_correct_mcq"])
if "answer_in_one_sentence" in data:
    add_section("Answer in One Sentence")
    add_written(data["answer_in_one_sentence"], lines=1)
if "fill_in_the_blanks" in data:
    add_section("Fill in the Blanks")
    add_written(data["fill_in_the_blanks"], lines=1)
if "answer_in_brief" in data:
    add_section("Answer in Brief")
    add_written(data["answer_in_brief"], lines=3)
if "answer_in_detail" in data:
    add_section("Answer in Detail")
    add_written(data["answer_in_detail"], lines=6)

# -------- Generate PDF --------
doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
print("✅ Teacher’s Copy generated: question_paper.pdf")
