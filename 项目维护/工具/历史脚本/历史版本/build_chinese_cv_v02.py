"""Build an editable v0.2 CV from its Chinese Markdown master, locally only."""
import argparse
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_LINE_SPACING, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1] / "材料"
STEM = "周子靖_中文学术简历_v0.2_INTERNAL"
SOURCE = ROOT / f"{STEM}.md"
OUTPUT = ROOT / "校对稿" / f"{STEM}.docx"
FONT = "Source Han Sans CN Regular"
BOLD_FONT = "Source Han Sans CN Bold"


def font(run, size=None, bold=False, color="222222"):
    face = BOLD_FONT if bold else FONT
    run.font.name = face
    run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)
    if size is not None:
        run.font.size = Pt(size)
    fonts = run._element.get_or_add_rPr().rFonts
    for attr in ("eastAsia", "ascii", "hAnsi", "cs"):
        fonts.set(qn(f"w:{attr}"), face)


def add_text(paragraph, text, size=None, color="222222"):
    for part in re.split(r"(\*\*.*?\*\*)", text):
        if not part:
            continue
        bold = part.startswith("**") and part.endswith("**")
        font(paragraph.add_run(part[2:-2] if bold else part), size, bold, color)


def hyperlink(paragraph, label, target, size=9):
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), paragraph.part.relate_to(
        target,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    ))
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    for tag, attrs in (
        ("w:rFonts", {"w:ascii": FONT, "w:hAnsi": FONT, "w:eastAsia": FONT}),
        ("w:color", {"w:val": "555555"}),
        ("w:sz", {"w:val": str(int(size * 2))}),
    ):
        element = OxmlElement(tag)
        for key, val in attrs.items():
            element.set(qn(key), val)
        props.append(element)
    run.append(props)
    text = OxmlElement("w:t")
    text.text = label
    run.append(text)
    link.append(run)
    paragraph._p.append(link)


def paragraph(doc, after=2, before=0, keep_next=False):
    p = doc.add_paragraph()
    fmt = p.paragraph_format
    fmt.space_after = Pt(after)
    fmt.space_before = Pt(before)
    fmt.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    fmt.line_spacing = Pt(15.5)
    fmt.keep_together = True
    fmt.keep_with_next = keep_next
    fmt.widow_control = True
    # Prevent Word's character-grid defaults from changing CJK line spacing.
    props = p._p.get_or_add_pPr()
    grid = OxmlElement("w:snapToGrid")
    grid.set(qn("w:val"), "0")
    props.append(grid)
    hanging_punctuation = OxmlElement("w:overflowPunct")
    hanging_punctuation.set(qn("w:val"), "0")
    props.append(hanging_punctuation)
    return p


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-internal", action="store_true")
    args = parser.parse_args()
    if OUTPUT.exists() and not args.refresh_internal:
        raise FileExistsError(f"Preserve existing versions: {OUTPUT}")

    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Mm(210), Mm(297)
    section.left_margin = section.right_margin = Mm(18)
    section.top_margin, section.bottom_margin = Mm(15), Mm(17)
    section.footer_distance = Mm(8)
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = FONT, Pt(10.5)
    normal._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), FONT)
    doc.core_properties.title = "周子靖 | 中文学术简历 | v0.2 INTERNAL"
    doc.core_properties.author = "周子靖"
    doc.core_properties.subject = "国内本科起点博士申请；中文校对母版"
    doc.core_properties.comments = "Local internal review. Not sent or submitted."

    current_section = None
    new_publication = False
    for raw in SOURCE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            if current_section == "代表论文":
                new_publication = True
            continue
        if line.startswith("# "):
            p = paragraph(doc, after=4)
            p.paragraph_format.line_spacing = Pt(30)
            add_text(p, f"**{line[2:]}**", size=24)
        elif line.startswith("Zijing Zhou"):
            p = paragraph(doc, after=1)
            add_text(p, "Zijing Zhou   |   ", size=10, color="555555")
            email = line.split(" | ", 1)[1]
            hyperlink(p, email, "mailto:" + email, size=10)
        elif line.startswith("## "):
            current_section = line[3:]
            p = paragraph(doc, before=8, after=5, keep_next=True)
            p.paragraph_format.line_spacing = Pt(17)
            add_text(p, f"**{current_section}**", size=11.5)
            borders = OxmlElement("w:pBdr")
            bottom = OxmlElement("w:bottom")
            for key, value in {"val": "single", "sz": "4", "space": "3", "color": "BBBBBB"}.items():
                bottom.set(qn("w:" + key), value)
            borders.append(bottom)
            p._p.get_or_add_pPr().append(borders)
            new_publication = False
        elif " | " in line:
            label, date = line.rsplit(" | ", 1)
            p = paragraph(doc, keep_next=current_section == "科研经历" or label.startswith("**哈尔"))
            p.paragraph_format.tab_stops.add_tab_stop(Mm(174), WD_TAB_ALIGNMENT.RIGHT)
            add_text(p, label)
            add_text(p, "\t" + date, size=9, color="555555")
        elif line.startswith("- "):
            p = paragraph(doc, after=3)
            p.paragraph_format.left_indent = Pt(10.5)
            p.paragraph_format.first_line_indent = Pt(-10.5)
            add_text(p, "• " + line[2:])
        elif line.startswith("DOI："):
            p = paragraph(doc, after=1, keep_next=True)
            p.paragraph_format.line_spacing = Pt(12)
            doi = line[4:]
            add_text(p, "DOI：", size=9, color="555555")
            hyperlink(p, doi, "https://doi.org/" + doi)
        else:
            is_citation = current_section == "代表论文" and not line.startswith("个人贡献")
            p = paragraph(doc, before=5 if is_citation and new_publication else 0,
                          keep_next=is_citation or line.startswith("科研指导"))
            add_text(p, line)
            new_publication = False

    footer = section.footer.paragraphs[0]
    footer.style = doc.styles["Normal"]
    footer.paragraph_format.tab_stops.clear_all()
    footer.paragraph_format.tab_stops.add_tab_stop(Mm(174), WD_TAB_ALIGNMENT.RIGHT)
    add_text(footer, "v0.2 INTERNAL | 2026-09-26\t", size=8, color="777777")
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    page_run = OxmlElement("w:r")
    page_props = OxmlElement("w:rPr")
    page_size = OxmlElement("w:sz")
    page_size.set(qn("w:val"), "16")
    page_props.append(page_size)
    page_run.append(page_props)
    page_text = OxmlElement("w:t")
    page_text.text = "1"
    page_run.append(page_text)
    field.append(page_run)
    footer._p.append(field)
    OUTPUT.parent.mkdir(exist_ok=True)
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
