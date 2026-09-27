"""Render the current Chinese candidate using the existing Word CV layout."""
import argparse
from copy import deepcopy
from pathlib import Path
import re

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parents[1] / "材料"
INTERNAL = "周子靖_中文学术简历_v0.5_INTERNAL"
CANDIDATE = "周子靖_中文学术简历_Master_v1.2_CANDIDATE"
SOURCE = ROOT / (INTERNAL + ".md")
OUT = ROOT / "校对稿"


def put(p, text, size=10.5, color="222222"):
    for part in re.split(r"(\*\*.*?\*\*)", text):
        if not part:
            continue
        bold = part.startswith("**") and part.endswith("**")
        run = p.add_run(part[2:-2] if bold else part)
        face = "Source Han Sans CN Bold" if bold else "Source Han Sans CN Regular"
        run.font.name = face
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = RGBColor.from_string(color)
        for name in ("ascii", "hAnsi", "eastAsia", "cs"):
            run._element.get_or_add_rPr().rFonts.set(qn("w:" + name), face)


def link(p, label, uri, size):
    element = OxmlElement("w:hyperlink")
    element.set(qn("r:id"), p.part.relate_to(uri,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True))
    run = p.add_run(label)
    run.font.name = "Source Han Sans CN Regular"
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string("555555")
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Source Han Sans CN Regular")
    element.append(run._r)
    p._p.append(element)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-candidate", action="store_true")
    refresh = parser.parse_args().refresh_candidate
    for stem in (INTERNAL, CANDIDATE):
        if (OUT / (stem + ".docx")).exists() and not refresh:
            raise FileExistsError(stem)
    base = ROOT / "对外PDF/周子靖_中文学术简历_Master_v1.1.docx"
    doc = Document(base)
    def sample(prefix):
        return deepcopy(next(p._p for p in doc.paragraphs if p.text.startswith(prefix)))
    templates = {"name": sample("周子靖"), "contact": sample("Zijing"), "heading": sample("教育背景"),
                 "dated": sample("本科毕业设计"), "bullet": sample("• 仿真自动化"),
                 "body": sample("应用物理学本科"), "doi": sample("DOI"), "citation": sample("雨田")}
    for p in list(doc.paragraphs):
        p._p.getparent().remove(p._p)

    def para(kind):
        e = deepcopy(templates[kind])
        doc._element.body.insert_element_before(e, "w:sectPr")
        p = Paragraph(e, doc._body)
        p.clear()
        return p

    section = None
    publication_gap = False
    for raw in SOURCE.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s:
            publication_gap = section == "代表论文"
            continue
        if s.startswith("# "):
            put(para("name"), "**" + s[2:] + "**", 24)
        elif s.startswith("Zijing"):
            p = para("contact")
            name, email = s.split(" | ")
            put(p, name + "   |   ", 10, "555555")
            link(p, email, "mailto:" + email, 10)
        elif s.startswith("## "):
            section = s[3:]
            p = para("heading")
            p.paragraph_format.space_before = Pt(6)
            put(p, "**" + section + "**", 11.5)
            publication_gap = False
        elif " | " in s:
            label, date = s.rsplit(" | ", 1)
            p = para("dated")
            p.paragraph_format.keep_with_next = section == "科研经历" or label.startswith("**哈尔")
            if section == "精选荣誉":
                p.paragraph_format.space_after = Pt(1)
            if label.startswith("**合作研究"):
                p.paragraph_format.space_before = Pt(4)
            put(p, label)
            put(p, "\t" + date, 9, "555555")
        elif s.startswith("- "):
            put(para("bullet"), "• " + s[2:])
        elif s.startswith("DOI："):
            p = para("doi")
            p.paragraph_format.keep_with_next = "SSPMA" not in s
            put(p, "DOI：", 9, "555555")
            link(p, s[4:], "https://doi.org/" + s[4:], 9)
        else:
            citation = section == "代表论文" and not s.startswith("个人贡献")
            p = para("citation" if citation else "body")
            p.paragraph_format.keep_with_next = citation or s.startswith("指导教师")
            if section == "技术与语言":
                p.paragraph_format.space_after = Pt(1)
            if citation:
                p.paragraph_format.space_before = Pt(5 if publication_gap else 0)
            put(p, s, 10 if s.startswith("算术均分") else 10.5)
            publication_gap = False

    footer = doc.sections[0].footer.paragraphs[0]
    footer.clear()
    put(footer, "v0.5 INTERNAL | 2026-09-26", 8, "777777")
    doc.core_properties.title = "周子靖 | 中文学术简历 | v0.5 INTERNAL"
    doc.core_properties.comments = "Content-enriched internal review; not sent."
    doc.save(OUT / (INTERNAL + ".docx"))
    footer.clear()
    doc.core_properties.title = "周子靖 | 中文学术简历 | Master v1.2 candidate"
    doc.core_properties.comments = "Candidate for renewed master freeze; not sent."
    doc.save(OUT / (CANDIDATE + ".docx"))
    print("Created editable internal and clean candidate using the existing layout.")


if __name__ == "__main__":
    main()
