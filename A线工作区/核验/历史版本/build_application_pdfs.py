"""Render the two reviewed English sources; leave all original project files unchanged."""
import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = ROOT / "材料"
OUT = MATERIALS / "对外PDF"
OUT.mkdir(exist_ok=True)

STYLES = {
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=20, leading=24, spaceAfter=7),
    "project_title": ParagraphStyle("project_title", fontName="Helvetica-Bold", fontSize=17, leading=21, spaceAfter=6),
    "heading": ParagraphStyle("heading", fontName="Helvetica-Bold", fontSize=10.8, leading=14, spaceBefore=11, spaceAfter=5, textColor=colors.HexColor("#175449"), keepWithNext=True),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10, leading=13.4, spaceAfter=5),
    "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=10, leading=13.4, spaceAfter=4, leftIndent=10, firstLineIndent=-9),
    "caption": ParagraphStyle("caption", fontName="Helvetica", fontSize=8.2, leading=10.5, textColor=colors.HexColor("#444444"), spaceAfter=4),
}


def inline(text):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escape(text))


def fitted_image(path, width, height):
    original_w, original_h = ImageReader(str(path)).getSize()
    scale = min(width / original_w, height / original_h)
    return Image(str(path), width=original_w * scale, height=original_h * scale)


def project_figures():
    structure = Path(r"E:\360MoveData\Users\zzj\OneDrive\桌面\毕业设计\结题\终稿\_ppt_assets_resistive_film\fig6_2_final_3d_model.png")
    curve = Path(r"F:\biyesheji\最终结果ohmic_sheet_12x12_multitemplate_topology_ga\best_s11_ohmic_sheet_12x12.png")
    table = Table([
        [fitted_image(structure, 238, 137), fitted_image(curve, 238, 137)],
        [Paragraph("Thesis CST geometry view (original project image).", STYLES["caption"]),
         Paragraph("Archived co-polar reflection curve, not measured absorptance.", STYLES["caption"])],
    ], colWidths=[249, 249])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#CCCCCC"))
    canvas.line(48, 35, A4[0] - 48, 35)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawString(48, 24, f"Zijing Zhou | {doc.asset_version} | 26 September 2026")
    canvas.drawRightString(A4[0] - 48, 24, str(doc.page))
    canvas.restoreState()


def render(source_name, output_name, project=False, version="v1.0"):
    if (OUT / output_name).exists():
        raise FileExistsError(f"Preserve the existing PDF; choose a new version: {output_name}")
    doc = SimpleDocTemplate(str(OUT / output_name), pagesize=A4, leftMargin=48, rightMargin=48,
                            topMargin=39, bottomMargin=46, title=output_name.removesuffix(".pdf"), author="Zijing Zhou")
    doc.asset_version = version
    content = []
    for raw in (MATERIALS / source_name).read_text(encoding="utf-8").splitlines():
        text = raw.strip()
        if not text:
            continue
        if text.startswith("# "):
            content.append(Paragraph(inline(text[2:]), STYLES["project_title" if project else "title"]))
        elif text.startswith("## "):
            if project and text == "## Archived Simulation Result":
                content.extend([Spacer(1, 4), project_figures()])
            content.append(Paragraph(inline(text[3:]), STYLES["heading"]))
        elif text.startswith("- "):
            content.append(Paragraph("&#8226; " + inline(text[2:]), STYLES["bullet"]))
        else:
            content.append(Paragraph(inline(text), STYLES["body"]))
    doc.build(content, onFirstPage=footer, onLaterPages=footer)
    print(OUT / output_name)


if __name__ == "__main__":
    render("Academic_CV_v1.1_READY.md", "Zijing_Zhou_CV_v1.1.pdf", version="v1.1")
