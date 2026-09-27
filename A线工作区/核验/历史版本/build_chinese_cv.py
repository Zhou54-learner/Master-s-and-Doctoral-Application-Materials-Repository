"""Render the Chinese review master without changing historical application PDFs."""
import argparse
import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1] / "材料"
SOURCE = ROOT / "中文学术简历_v0.1_INTERNAL.md"
OUTPUT = ROOT / "校对稿" / "周子靖_中文学术简历_v0.1_INTERNAL.pdf"
FONT_DIR = Path("C:/Windows/Fonts")

pdfmetrics.registerFont(TTFont("CVRegular", str(FONT_DIR / "SourceHanSansCNRegular.ttf")))
pdfmetrics.registerFont(TTFont("CVBold", str(FONT_DIR / "SourceHanSansCNBold.ttf")))
pdfmetrics.registerFontFamily("CVRegular", normal="CVRegular", bold="CVBold")
INK = colors.HexColor("#202827")
MUTED = colors.HexColor("#606A67")
ACCENT = colors.HexColor("#255E52")
WIDTH = A4[0] - 100
BODY = ParagraphStyle("body", fontName="CVRegular", fontSize=9.5, leading=14.5,
                      textColor=INK, spaceAfter=3.5, wordWrap="CJK")
STYLES = {
    "body": BODY,
    "name": ParagraphStyle("name", parent=BODY, fontName="CVBold", fontSize=25, leading=31, spaceAfter=4),
    "contact": ParagraphStyle("contact", parent=BODY, fontSize=9.5, textColor=MUTED, spaceAfter=6),
    "heading": ParagraphStyle("heading", parent=BODY, fontName="CVBold", fontSize=11,
                              leading=16, textColor=ACCENT, spaceBefore=9, spaceAfter=4,
                              keepWithNext=True),
    "date": ParagraphStyle("date", parent=BODY, fontSize=8.8, alignment=2, textColor=MUTED),
    "bullet": ParagraphStyle("bullet", parent=BODY, leftIndent=10, firstLineIndent=-9),
    "doi": ParagraphStyle("doi", parent=BODY, fontSize=8.4, leading=12, textColor=MUTED),
}


def markup(text):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escape(text))


def dated_row(text):
    label, date = text.rsplit(" | ", 1)
    date_width = max(94, pdfmetrics.stringWidth(date, "CVRegular", 8.8) + 10)
    table = Table([[Paragraph(markup(label), BODY), Paragraph(markup(date), STYLES["date"])]],
                  colWidths=[WIDTH - date_width, date_width], hAlign="LEFT")
    table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                              ("LEFTPADDING", (0, 0), (-1, -1), 0),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                              ("TOPPADDING", (0, 0), (-1, -1), 0),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    table.keepWithNext = True
    return table


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D5DEDA"))
    canvas.line(44, 35, A4[0] - 44, 35)
    canvas.setFillColor(MUTED)
    canvas.setFont("CVRegular", 7.5)
    canvas.drawString(44, 22, "内部校对稿 · 未经本人确认，不外发 | v0.1 | 2026-09-26")
    canvas.drawRightString(A4[0] - 44, 22, str(doc.page))
    canvas.restoreState()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-internal", action="store_true",
                        help="Regenerate this unsent INTERNAL preview only; never touches READY PDFs.")
    args = parser.parse_args()
    if OUTPUT.exists() and not args.refresh_internal:
        raise FileExistsError(f"Preserve existing versions: {OUTPUT}")
    OUTPUT.parent.mkdir(exist_ok=True)
    content = []
    for raw in SOURCE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("## 校对说明"):
            break
        if not line:
            continue
        if line.startswith("# "):
            content.append(Paragraph(markup(line[2:]), STYLES["name"]))
        elif line.startswith("## "):
            content.append(Paragraph(markup(line[3:]), STYLES["heading"]))
            content.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D5DEDA"), spaceAfter=5))
        elif line.startswith("Zijing Zhou"):
            content.append(Paragraph(markup(line), STYLES["contact"]))
            content.append(Spacer(1, 2))
        elif " | " in line:
            content.append(dated_row(line))
        elif line.startswith("- "):
            content.append(Paragraph("&#8226; " + markup(line[2:]), STYLES["bullet"]))
        else:
            style = STYLES["doi"] if line.startswith("DOI") else BODY
            content.append(Paragraph(markup(line), style))
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=44, rightMargin=44,
                            topMargin=34, bottomMargin=46, title="周子靖 | 中文学术简历 | 内部校对稿",
                            author="周子靖")
    doc.build(content, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    main()
