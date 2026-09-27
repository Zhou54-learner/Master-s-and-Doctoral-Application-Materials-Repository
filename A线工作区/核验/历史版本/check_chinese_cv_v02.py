"""Validate local CV exports and preservation; do not modify source evidence."""
import hashlib
import json
import re
from pathlib import Path

import pymupdf
from docx import Document

WORK = Path(__file__).resolve().parents[1]
PROJECT = WORK.parent
MATERIAL = WORK / "材料"
STEM = "周子靖_中文学术简历_v0.2_INTERNAL"
MD = MATERIAL / f"{STEM}.md"
DOCX = MATERIAL / "校对稿" / f"{STEM}.docx"
PDF = MATERIAL / "校对稿" / f"{STEM}.pdf"
HISTORICAL = {
    "材料/中文学术简历_v0.1_INTERNAL.md": "D32019B305931C84A509F22A6AC3CF176C1A83736EB363B6874EE384C3DAA13A",
    "材料/校对稿/周子靖_中文学术简历_v0.1_INTERNAL.pdf": "C8F662E902D790FC3A2E6002D784D1C9E10ABBB9AB1E258625243BCE96E45394",
    "核验/build_chinese_cv.py": "E99A880ADCC91ED9B5048DBFCADD4C5AE7788C469F8737C8C7CD6C75DE15B3B8",
    "材料/Academic_CV_v1.1_READY.md": "F65F4894007F98E39982B21ADE81D8AC3EADC60E41560800A962935AE0CF33FD",
    "材料/对外PDF/Zijing_Zhou_CV_v1.1.pdf": "81183079FB30CD6643274B54BE9A50A0799845F2078ECF736771373101C47A81",
}


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def compact(text):
    return re.sub(r"\s+", "", text)


def main():
    source = MD.read_text(encoding="utf-8")
    doc = Document(DOCX)
    pdf = pymupdf.open(PDF)
    assert len(pdf) == 1, "Review layout before allowing a second page"
    word_text = compact("\n".join(p.text for p in doc.paragraphs))
    pdf_text = compact(pdf[0].get_text())
    fragments = []
    for line in source.splitlines():
        clean = re.sub(r"^(#{1,2} |- )", "", line).replace("**", "")
        fragments.extend(part for part in clean.split(" | ") if part)
    for fragment in fragments:
        assert compact(fragment) in word_text, f"DOCX missing: {fragment}"
        assert compact(fragment) in pdf_text, f"PDF missing: {fragment}"
    forbidden = ["开发了遗传算法", "全新遗传算法", "独立开发", "熟练", "DFT", "VASP", "PyTorch",
                 "13.20", "82.5%", "AI辅助", "实验参与有限", "1439037249@qq.com"]
    assert not any(item in source for item in forbidden)
    assert source.index("用于无线通信") < source.index("二维尘埃")

    page = pdf[0]
    spans = [s for b in page.get_text("dict")["blocks"] if "lines" in b
             for line in b["lines"] for s in line["spans"] if s["text"].strip()]
    assert all(page.rect.contains(pymupdf.Rect(s["bbox"])) for s in spans)
    glyphs = [char for b in page.get_text("rawdict")["blocks"] if "lines" in b
              for line in b["lines"] for s in line["spans"] for char in s["chars"] if char["c"].strip()]
    assert all(c["bbox"][0] >= 49 and c["bbox"][2] <= page.rect.width - 49 for c in glyphs)
    own_names = [s for s in spans if "周子靖" in s["text"]]
    assert len(own_names) == 3 and all("Bold" in s["font"] for s in own_names)
    body_spans = [s for s in spans if 95 < s["bbox"][1] < 760 and not s["text"].startswith("DOI")]
    assert min(s["size"] for s in body_spans) >= 8.9
    fonts = page.get_fonts()
    assert all("SourceHanSansCN" in row[3] for row in fonts), fonts
    assert all(len(pdf.extract_font(row[0])[3]) > 0 for row in fonts)
    links = {link.get("uri") for link in page.get_links()}
    assert links == {
        "mailto:zhouzijing54@gmail.com",
        "https://doi.org/10.20249/j.cnki.2096-5974.2025.01.011",
        "https://doi.org/10.1360/SSPMA-2024-0393",
    }
    dated_texts = [line.rsplit(" | ", 1)[1] for line in source.splitlines()
                   if " | " in line and not line.startswith("Zijing")]
    for date in dated_texts:
        matches = [s for s in spans if compact(s["text"]) == compact(date)]
        assert len(matches) == 1 and abs(matches[0]["bbox"][2] - 544.3) < 3, date

    manifest = json.loads((WORK / "接手原件清单_20260926.json").read_text(encoding="utf-8-sig"))
    original_checks = []
    for entry in manifest["files"]:
        actual = digest(PROJECT / entry["Path"])
        assert actual == entry["SHA256"].upper(), entry["Path"]
        original_checks.append({"path": entry["Path"], "unchanged": True})
    for path, expected in HISTORICAL.items():
        assert digest(WORK / path) == expected, path

    link_files = [PROJECT / "A线_工作台.md", MATERIAL / "材料版本与发送说明.md",
                  MATERIAL / "中文CV_v0.2_修改与真实性检查.md"]
    local_links = 0
    for path in link_files:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            dest = (path.parent / target).resolve()
            # This report is generated immediately after link validation.
            if dest == Path(__file__).with_name("中文CV_v0.2_验收.json"):
                continue
            assert dest.exists(), f"Broken link: {path}: {target}"
            local_links += 1

    report = {
        "date": "2026-09-26", "version": "v0.2 INTERNAL", "pdf_pages": len(pdf),
        "word_pages": 1, "word_page_count_source": "Word ComputeStatistics during PDF export",
        "source_fragments_matched_in_docx_and_pdf": len(fragments),
        "pdf_font_families": sorted({s["font"] for s in spans}),
        "all_fonts_embedded": True, "all_text_inside_page_and_horizontal_margins": True,
        "dates_right_aligned": len(dated_texts), "own_name_bold_instances": len(own_names),
        "hyperlinks": sorted(links), "local_document_links_checked": local_links,
        "original_assets": original_checks, "historical_versions_unchanged": list(HISTORICAL),
        "outputs": [{"path": str(p.relative_to(PROJECT)), "SHA256": digest(p)} for p in [MD, DOCX, PDF]],
        "limits": ["Text/layout checks do not independently prove applicant contributions",
                   "No CST execution, Gmail send test, external upload, email send or application submission"],
    }
    output = Path(__file__).with_name("中文CV_v0.2_验收.json")
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ("original_assets", "outputs")},
                     ensure_ascii=False, indent=2))
    print(f"Original assets unchanged: {len(original_checks)}; report: {output}")


if __name__ == "__main__":
    main()
