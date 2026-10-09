"""
Utility module for generating physical question paper PDFs in A4 size.
Uses ReportLab to build high-quality, printable exam papers.
Supports 1-column or 2-column layouts, font sizing (compact/normal/large),
and toggles for institute header, candidate box, instructions, and answer key.
"""

import io
import re
import html
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate,
    BaseDocTemplate,
    PageTemplate,
    Frame,
    FrameBreak,
    NextPageTemplate,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas
from PIL import Image as PILImage

from app.config import settings


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print total page count:
    'Page X of Y' on every page, with series title and academic header.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict[str, Any]] = []
        self.series_title: str = ""

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int) -> None:
        self.saveState()
        self.setFont("Times-Roman", 8)
        self.setFillColor(colors.HexColor("#444444"))

        # Footer line
        self.setStrokeColor(colors.HexColor("#cccccc"))
        self.setLineWidth(0.5)
        self.line(12 * mm, 12 * mm, A4[0] - 12 * mm, 12 * mm)

        # Footer Left: Exam title
        if self.series_title:
            title_text = self.series_title[:50] + ("..." if len(self.series_title) > 50 else "")
            self.drawString(12 * mm, 8 * mm, f"{title_text} — Question Paper")

        # Footer Right: Page X of Y
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(A4[0] - 12 * mm, 8 * mm, page_str)

        self.restoreState()


def clean_html_for_reportlab(raw_html: str | None) -> str:
    """
    Converts rich text HTML into ReportLab-compliant XML-like strings.
    ReportLab Paragraph supports: <b>, <i>, <u>, <sub>, <sup>, <font>, <br/>.
    """
    if not raw_html:
        return ""

    text = str(raw_html).replace("\r\n", "\n").replace("\r", "\n")

    # Replace block/break tags with <br/>
    text = re.sub(r"</p\s*>", "<br/>", text, flags=re.I)
    text = re.sub(r"<p[^>]*>", "", text, flags=re.I)
    text = re.sub(r"<br\s*/?>", "<br/>", text, flags=re.I)
    text = re.sub(r"<li[^>]*>", "• ", text, flags=re.I)
    text = re.sub(r"</li\s*>", "<br/>", text, flags=re.I)
    text = re.sub(r"</?(?:ul|ol)[^>]*>", "", text, flags=re.I)

    # Standard formatting tags
    text = re.sub(r"<strong[^>]*>", "<b>", text, flags=re.I)
    text = re.sub(r"</strong\s*>", "</b>", text, flags=re.I)
    text = re.sub(r"<em[^>]*>", "<i>", text, flags=re.I)
    text = re.sub(r"</em\s*>", "</i>", text, flags=re.I)

    # Strip all unsupported tags (e.g. <span>, <div>, <img>, etc.)
    text = re.sub(r"<(?!/?(?:b|i|u|sub|sup|font|br)(?:\s+[^>]*)?/?>)[^>]+>", "", text, flags=re.I)

    # Escape unescaped ampersands
    text = re.sub(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)", "&amp;", text)

    # Collapse multiple consecutive <br/>
    text = re.sub(r"(?:<br/>\s*){3,}", "<br/><br/>", text)

    return text.strip()


def safe_paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    """Creates a Paragraph safely; falls back to stripped plain text if XML parsing fails."""
    cleaned = clean_html_for_reportlab(text)
    try:
        return Paragraph(cleaned, style)
    except Exception:
        # Fallback to fully escaped plain text
        plain = re.sub(r"<[^>]+>", " ", text or "")
        return Paragraph(html.escape(plain.strip()), style)


def get_scaled_image(path_str: str | None, max_w_mm: float, max_h_mm: float) -> RLImage | None:
    """Loads an image from uploads or disk and scales it proportionally."""
    if not path_str:
        return None

    p = Path(path_str)
    if not p.is_file():
        cleaned_path = path_str.replace("uploads/", "").replace("uploads\\", "").lstrip("/\\")
        p = Path(settings.upload_dir) / cleaned_path
    if not p.is_file():
        p = Path("uploads") / path_str.replace("uploads/", "").replace("uploads\\", "").lstrip("/\\")
    if not p.is_file():
        return None

    try:
        with PILImage.open(p) as img:
            w, h = img.size
        if w <= 0 or h <= 0:
            return None

        aspect = h / w
        max_w_pt = max_w_mm * mm
        max_h_pt = max_h_mm * mm

        render_w = min(max_w_pt, w * 0.75)
        render_h = render_w * aspect
        if render_h > max_h_pt:
            render_h = max_h_pt
            render_w = render_h / aspect

        return RLImage(str(p), width=render_w, height=render_h)
    except Exception:
        return None


def format_duration_str(seconds: int | None) -> str:
    if not seconds or seconds <= 0:
        return "60 Minutes"
    h = seconds // 3600
    m = round((seconds % 3600) / 60)
    if h > 0 and m > 0:
        return f"{h} Hour{'s' if h > 1 else ''} {m} Mins"
    if h > 0:
        return f"{h} Hour{'s' if h > 1 else ''}"
    return f"{m} Minutes"


def generate_question_paper_pdf_bytes(
    test_series: Any,
    series_questions: list[Any],
    organization: Any = None,
    include_answers: bool = False,
    columns: int = 1,
    font_size: str = "normal",
    show_candidate_box: bool = True,
    show_instructions: bool = True,
    show_org_header: bool = True,
) -> bytes:
    """
    Builds and returns a complete, printable physical question paper in A4 PDF bytes.
    Supports 1-column or 2-column layout, font size scaling, and header section toggles.
    """
    buffer = io.BytesIO()

    # Printable page width: A4 is 210mm x 297mm
    # Left & Right margins: 14mm each -> Usable width = 210 - 28 = 182mm
    margin = 14 * mm
    printable_width = A4[0] - (2 * margin)
    usable_h = A4[1] - (2 * margin)

    # Validate columns
    num_columns = 2 if int(columns or 1) == 2 else 1

    # Font scale calculation
    fs_mode = str(font_size or "normal").lower().strip()
    if fs_mode == "compact":
        font_scale = 0.88
    elif fs_mode == "large":
        font_scale = 1.15
    else:
        font_scale = 1.0

    styles = getSampleStyleSheet()

    # Dynamic styles based on font_scale
    org_title_style = ParagraphStyle(
        "OrgTitle",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=max(11.0, 15.0 * font_scale),
        leading=max(14.0, 18.0 * font_scale),
        alignment=TA_CENTER,
        textColor=colors.black,
    )
    series_title_style = ParagraphStyle(
        "SeriesTitle",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=max(10.0, 13.0 * font_scale),
        leading=max(13.0, 16.0 * font_scale),
        alignment=TA_CENTER,
        textColor=colors.black,
    )
    copy_badge_style = ParagraphStyle(
        "CopyBadge",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=max(8.0, 9.0 * font_scale),
        leading=max(10.0, 11.0 * font_scale),
        alignment=TA_CENTER,
        textColor=colors.HexColor("#b30000"),
    )
    meta_style = ParagraphStyle(
        "MetaText",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=max(7.5, 9.0 * font_scale),
        leading=max(9.5, 11.0 * font_scale),
        alignment=TA_CENTER,
        textColor=colors.black,
    )
    candidate_style = ParagraphStyle(
        "CandidateField",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=max(7.5, 8.5 * font_scale),
        leading=max(9.5, 11.0 * font_scale),
        textColor=colors.black,
    )
    inst_header_style = ParagraphStyle(
        "InstHeader",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=max(8.0, 9.0 * font_scale),
        leading=max(10.0, 12.0 * font_scale),
        textColor=colors.black,
    )
    inst_body_style = ParagraphStyle(
        "InstBody",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=max(7.0, 8.0 * font_scale),
        leading=max(9.0, 10.5 * font_scale),
        alignment=TA_LEFT,
        textColor=colors.black,
    )
    q_text_style = ParagraphStyle(
        "QuestionText",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=max(8.0, 9.5 * font_scale),
        leading=max(11.0, 13.0 * font_scale),
        textColor=colors.black,
    )
    q_marks_style = ParagraphStyle(
        "QuestionMarks",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=max(7.0, 8.0 * font_scale),
        leading=max(9.0, 10.0 * font_scale),
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#333333"),
    )
    opt_label_style = ParagraphStyle(
        "OptLabel",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=max(7.5, 9.0 * font_scale),
        leading=max(10.0, 12.0 * font_scale),
        textColor=colors.black,
    )
    opt_text_style = ParagraphStyle(
        "OptText",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=max(7.0, 8.5 * font_scale),
        leading=max(9.5, 11.5 * font_scale),
        textColor=colors.black,
    )
    opt_correct_style = ParagraphStyle(
        "OptCorrectText",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=max(7.0, 8.5 * font_scale),
        leading=max(9.5, 11.5 * font_scale),
        textColor=colors.HexColor("#006622"),
    )
    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=max(7.0, 8.0 * font_scale),
        leading=max(9.0, 10.0 * font_scale),
        alignment=TA_CENTER,
    )
    table_bold_style = ParagraphStyle(
        "TableBold",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=max(7.5, 8.5 * font_scale),
        leading=max(9.0, 10.0 * font_scale),
        alignment=TA_CENTER,
    )

    header_flowables: list[Any] = []

    # ── 1. Organization Logo & Header ──
    if show_org_header:
        if organization and getattr(organization, "logo", None):
            logo_img = get_scaled_image(organization.logo, max_w_mm=45, max_h_mm=16)
            if logo_img:
                logo_img.hAlign = "CENTER"
                header_flowables.append(logo_img)
                header_flowables.append(Spacer(1, 2 * mm))

        if organization and getattr(organization, "name", None):
            header_flowables.append(Paragraph(str(organization.name).upper(), org_title_style))
            header_flowables.append(Spacer(1, 1 * mm))

    series_name = getattr(test_series, "name", "Examination")
    header_flowables.append(Paragraph(series_name.upper(), series_title_style))

    if include_answers:
        header_flowables.append(Spacer(1, 1 * mm))
        header_flowables.append(Paragraph("[ TEACHER EVALUATION COPY — WITH ANSWER KEY ]", copy_badge_style))

    header_flowables.append(Spacer(1, 2.5 * mm))
    header_flowables.append(HRFlowable(width="100%", thickness=1.2, color=colors.black, spaceAfter=2.5 * mm))

    # ── 2. Exam Metadata Table ──
    total_marks = 0
    for sq in series_questions:
        if getattr(sq, "marks", None) is not None:
            try:
                total_marks += float(sq.marks)
            except (ValueError, TypeError):
                total_marks += 1
        elif getattr(sq, "question", None) and getattr(sq.question, "marks", None):
            try:
                total_marks += float(sq.question.marks)
            except (ValueError, TypeError):
                total_marks += 1
        else:
            total_marks += 1

    total_marks_str = str(int(total_marks)) if total_marks.is_integer() else f"{total_marks:.1f}"
    duration_str = format_duration_str(getattr(test_series, "duration_seconds", None))
    total_q_count = len(series_questions)

    meta_col_w = printable_width / 3.0
    meta_table = Table(
        [
            [
                Paragraph(f"<b>Time Allowed:</b> {duration_str}", meta_style),
                Paragraph(f"<b>Maximum Marks:</b> {total_marks_str}", meta_style),
                Paragraph(f"<b>Total Questions:</b> {total_q_count}", meta_style),
            ]
        ],
        colWidths=[meta_col_w, meta_col_w, meta_col_w],
    )
    meta_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.8, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8f8f8")),
                ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    header_flowables.append(meta_table)
    header_flowables.append(Spacer(1, 2.5 * mm))

    # ── 3. Candidate Fill-in Details Box ──
    if show_candidate_box:
        half_w = printable_width / 2.0
        candidate_table = Table(
            [
                [
                    Paragraph("<b>Candidate Name:</b> ___________________________", candidate_style),
                    Paragraph("<b>Roll / Reg. No:</b> _____________________", candidate_style),
                ],
                [
                    Paragraph("<b>Batch / Section:</b> __________________________", candidate_style),
                    Paragraph("<b>Date of Exam:</b> _____________________", candidate_style),
                ],
                [
                    Paragraph("<b>Candidate Signature:</b> ____________________", candidate_style),
                    Paragraph("<b>Invigilator Sign:</b> _____________________", candidate_style),
                ],
            ],
            colWidths=[half_w, half_w],
        )
        candidate_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.8, colors.black),
                    ("TOPPADDING", (0, 0), (-1, -1), 1.5 * mm),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        header_flowables.append(candidate_table)
        header_flowables.append(Spacer(1, 2.5 * mm))

    # ── 4. General Instructions Section ──
    if show_instructions:
        instructions_text = getattr(test_series, "instructions", None)
        if not instructions_text:
            instructions_text = (
                "1. This paper contains objective multiple choice questions. All questions are compulsory.<br/>"
                "2. Each question has four alternative choices (A, B, C, D). Mark the single most correct response.<br/>"
                "3. Do not write anything on the question paper except your details in the designated box.<br/>"
                "4. Electronic gadgets, mobile phones, and calculators are strictly prohibited."
            )

        inst_flowables = [
            Paragraph("<b>GENERAL INSTRUCTIONS:</b>", inst_header_style),
            Spacer(1, 1 * mm),
            safe_paragraph(instructions_text, inst_body_style),
        ]
        inst_table = Table([[inst_flowables]], colWidths=[printable_width])
        inst_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.6, colors.black),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fafafa")),
                    ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
                ]
            )
        )
        header_flowables.append(inst_table)
        header_flowables.append(Spacer(1, 3.5 * mm))

    # Column dimensions for questions
    gutter = 6 * mm
    col_w = (printable_width - gutter) / 2.0 if num_columns == 2 else printable_width
    q_content_width = col_w

    # ── 5. Questions Section Flowables ──
    question_flowables: list[Any] = []
    answer_key_matrix: list[tuple[int, str]] = []

    for idx, sq in enumerate(series_questions):
        q_obj = getattr(sq, "question", sq)
        if not q_obj:
            continue

        q_flowables: list[Any] = []

        q_marks = getattr(sq, "marks", None)
        if q_marks is None:
            q_marks = getattr(q_obj, "marks", 1)
        try:
            q_marks_float = float(q_marks)
            q_marks_str = f"[{int(q_marks_float)}M]" if q_marks_float.is_integer() else f"[{q_marks_float:.1f}M]"
        except Exception:
            q_marks_str = "[1M]"

        q_neg = getattr(sq, "negative_marks", None)
        if q_neg:
            try:
                q_neg_float = float(q_neg)
                if q_neg_float > 0:
                    q_marks_str += f" [-{int(q_neg_float) if q_neg_float.is_integer() else q_neg_float}]"
            except Exception:
                pass

        # Question Statement with Number
        q_text = getattr(q_obj, "question", "")
        q_p = safe_paragraph(f"<b>Q.{idx + 1}.</b> {q_text}", q_text_style)
        marks_p = Paragraph(q_marks_str, q_marks_style)

        marks_col_w = 16 * mm if num_columns == 2 else 24 * mm
        header_table = Table(
            [[q_p, marks_p]],
            colWidths=[q_content_width - marks_col_w, marks_col_w],
        )
        header_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1 * mm),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        q_flowables.append(header_table)

        # Question Diagrams (if any)
        diagram_paths: list[str] = []
        if hasattr(q_obj, "diagrams") and q_obj.diagrams:
            for d in q_obj.diagrams:
                if getattr(d, "path", None):
                    diagram_paths.append(d.path)
        if hasattr(q_obj, "diagram_path") and q_obj.diagram_path:
            if q_obj.diagram_path not in diagram_paths:
                diagram_paths.append(q_obj.diagram_path)

        for d_path in diagram_paths:
            diag_max_w = min(75.0, (q_content_width / mm) - 4.0) if num_columns == 2 else 120.0
            diag_max_h = 38.0 if num_columns == 2 else 45.0
            d_img = get_scaled_image(d_path, max_w_mm=diag_max_w, max_h_mm=diag_max_h)
            if d_img:
                d_img.hAlign = "CENTER"
                q_flowables.append(Spacer(1, 1.5 * mm))
                q_flowables.append(d_img)
                q_flowables.append(Spacer(1, 1.5 * mm))

        # Options
        raw_options = getattr(q_obj, "options", [])
        correct_letter = "-"

        if raw_options:
            q_flowables.append(Spacer(1, 1 * mm))
            option_rows: list[list[Any]] = []

            for opt_idx, opt in enumerate(raw_options):
                opt_letter = chr(65 + opt_idx)  # A, B, C, D
                opt_text = getattr(opt, "ans", getattr(opt, "text", ""))
                is_correct = bool(getattr(opt, "is_correct", False))
                if is_correct:
                    correct_letter = opt_letter

                label_p = Paragraph(f"<b>({opt_letter})</b>", opt_label_style)

                if include_answers and is_correct:
                    content_p = safe_paragraph(f"{opt_text}  <b>[✓ Correct Answer]</b>", opt_correct_style)
                else:
                    content_p = safe_paragraph(opt_text, opt_text_style)

                cell_flowables: list[Any] = [content_p]

                # Option Diagram if any
                opt_diag_path = getattr(opt, "diagram_path", None)
                if opt_diag_path:
                    opt_diag_max_w = min(45.0, (q_content_width / mm) - 12.0) if num_columns == 2 else 50.0
                    opt_diag_max_h = 20.0 if num_columns == 2 else 22.0
                    opt_diag_img = get_scaled_image(opt_diag_path, max_w_mm=opt_diag_max_w, max_h_mm=opt_diag_max_h)
                    if opt_diag_img:
                        cell_flowables.append(opt_diag_img)

                option_rows.append([label_p, cell_flowables])

            opt_label_w = 7 * mm if num_columns == 2 else 10 * mm
            opt_table = Table(
                option_rows,
                colWidths=[opt_label_w, q_content_width - (opt_label_w + 2 * mm)],
            )
            opt_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("TOPPADDING", (0, 0), (-1, -1), 0.8 * mm),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0.8 * mm),
                        ("LEFTPADDING", (0, 0), (-1, -1), 1 * mm),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )
            q_flowables.append(opt_table)

        answer_key_matrix.append((idx + 1, correct_letter))

        q_flowables.append(Spacer(1, 1.5 * mm))
        q_flowables.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#dddddd"), spaceAfter=2.5 * mm))

        # Keep question together on a single page if reasonable size
        question_flowables.append(KeepTogether(q_flowables))

    # ── 6. Answer Key Matrix Table (If include_answers is True) ──
    key_flowables: list[Any] = []
    if include_answers and answer_key_matrix:
        key_flowables.append(Spacer(1, 4 * mm))
        key_flowables.append(Paragraph("<b>COMPLETE ANSWER KEY MATRIX</b>", inst_header_style))
        key_flowables.append(Spacer(1, 2 * mm))

        cols_per_row = 5 if num_columns == 2 else 10
        cell_w = q_content_width / float(cols_per_row)
        table_data: list[list[Any]] = []

        for row_start in range(0, len(answer_key_matrix), cols_per_row):
            chunk = answer_key_matrix[row_start : row_start + cols_per_row]
            header_row: list[Any] = []
            ans_row: list[Any] = []

            for q_num, ans_val in chunk:
                header_row.append(Paragraph(f"Q.{q_num}", table_cell_style))
                ans_row.append(Paragraph(f"<b>{ans_val}</b>", table_bold_style))

            while len(header_row) < cols_per_row:
                header_row.append(Paragraph("-", table_cell_style))
                ans_row.append(Paragraph("-", table_cell_style))

            table_data.append(header_row)
            table_data.append(ans_row)

        ans_table = Table(table_data, colWidths=[cell_w] * cols_per_row)
        ans_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.8, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 1.2 * mm),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2 * mm),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        key_flowables.append(ans_table)

    # ── 7. End of Question Paper & Rough Work ──
    end_flowables = [
        Spacer(1, 4 * mm),
        Paragraph(
            "<b>*** END OF QUESTION PAPER ***</b>",
            ParagraphStyle(
                "EndNotice",
                parent=styles["Normal"],
                fontName="Times-Bold",
                fontSize=max(7.5, 9.0 * font_scale),
                alignment=TA_CENTER,
                textColor=colors.black,
            ),
        ),
        Spacer(1, 5 * mm),
        HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#999999"), dash=(3, 3)),
        Spacer(1, 1.5 * mm),
        Paragraph(
            "SPACE FOR ROUGH WORK",
            ParagraphStyle(
                "RoughWork",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=max(6.5, 7.5 * font_scale),
                alignment=TA_CENTER,
                textColor=colors.HexColor("#888888"),
            ),
        ),
    ]

    # Canvas factory for NumberedCanvas
    def canvas_factory(*args: Any, **kwargs: Any) -> NumberedCanvas:
        c = NumberedCanvas(*args, **kwargs)
        c.series_title = getattr(test_series, "name", "")
        return c

    # ── 8. Assemble Document (1 Column vs 2 Column) ──
    if num_columns == 1:
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=margin,
            rightMargin=margin,
            topMargin=margin,
            bottomMargin=margin,
        )
        story: list[Any] = []
        story.extend(header_flowables)
        story.extend(question_flowables)
        if key_flowables:
            story.append(KeepTogether(key_flowables))
        story.append(KeepTogether(end_flowables))
        doc.build(story, canvasmaker=canvas_factory)

    else:
        # 2-column layout with BaseDocTemplate and PageTemplates
        divider_x = margin + col_w + (gutter / 2.0)

        # Later pages (Page 2+) have full-height 2-column frames
        later_col1 = Frame(
            margin,
            margin,
            col_w,
            usable_h,
            id="later_col1",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        later_col2 = Frame(
            margin + col_w + gutter,
            margin,
            col_w,
            usable_h,
            id="later_col2",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )

        def on_later_page(c: canvas.Canvas, _doc: Any) -> None:
            c.saveState()
            c.setStrokeColor(colors.HexColor("#dddddd"))
            c.setLineWidth(0.5)
            c.line(divider_x, margin, divider_x, margin + usable_h)
            c.restoreState()

        later_template = PageTemplate(id="LaterPages", frames=[later_col1, later_col2], onPage=on_later_page)

        # Measure height of header block to fit on Page 1
        header_h = 0.0
        for it in header_flowables:
            try:
                _, h_val = it.wrap(printable_width, usable_h)
                header_h += h_val
            except Exception:
                pass
        header_h += 3 * mm

        doc = BaseDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=margin,
            rightMargin=margin,
            topMargin=margin,
            bottomMargin=margin,
        )

        if header_flowables and header_h < (usable_h - 40 * mm):
            # Page 1 top frame for header, and bottom 2 columns for starting questions
            p1_col_h = usable_h - header_h - 2 * mm
            top_frame = Frame(
                margin,
                margin + usable_h - header_h,
                printable_width,
                header_h,
                id="top_frame",
                leftPadding=0,
                rightPadding=0,
                topPadding=0,
                bottomPadding=0,
            )
            p1_col1 = Frame(
                margin,
                margin,
                col_w,
                p1_col_h,
                id="p1_col1",
                leftPadding=0,
                rightPadding=0,
                topPadding=0,
                bottomPadding=0,
            )
            p1_col2 = Frame(
                margin + col_w + gutter,
                margin,
                col_w,
                p1_col_h,
                id="p1_col2",
                leftPadding=0,
                rightPadding=0,
                topPadding=0,
                bottomPadding=0,
            )

            def on_p1_page(c: canvas.Canvas, _doc: Any) -> None:
                c.saveState()
                c.setStrokeColor(colors.HexColor("#dddddd"))
                c.setLineWidth(0.5)
                c.line(divider_x, margin, divider_x, margin + p1_col_h)
                c.restoreState()

            p1_template = PageTemplate(id="FirstPage", frames=[top_frame, p1_col1, p1_col2], onPage=on_p1_page)
            doc.addPageTemplates([p1_template, later_template])

            story = [
                NextPageTemplate("LaterPages"),
                *header_flowables,
                FrameBreak(),
                *question_flowables,
            ]
        elif header_flowables:
            # Header is very large: Page 1 holds full-width header, Page 2+ holds 2 columns
            p1_full_frame = Frame(
                margin,
                margin,
                printable_width,
                usable_h,
                id="p1_full_frame",
                leftPadding=0,
                rightPadding=0,
                topPadding=0,
                bottomPadding=0,
            )
            p1_template = PageTemplate(id="FirstPage", frames=[p1_full_frame])
            doc.addPageTemplates([p1_template, later_template])

            story = [
                NextPageTemplate("LaterPages"),
                *header_flowables,
                PageBreak(),
                *question_flowables,
            ]
        else:
            # No header flowables
            doc.addPageTemplates([later_template])
            story = list(question_flowables)

        if key_flowables:
            story.append(KeepTogether(key_flowables))
        story.append(KeepTogether(end_flowables))

        doc.build(story, canvasmaker=canvas_factory)

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
