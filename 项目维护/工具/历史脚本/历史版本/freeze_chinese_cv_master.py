"""Apply four scoped edits to the existing CV layout; never overwrite a version."""
import argparse
import hashlib
import json
import re
from pathlib import Path

from docx import Document

WORK = Path(__file__).resolve().parents[1]
ROOT = WORK / "材料"
OLD = "周子靖_中文学术简历_v0.2_INTERNAL"
INTERNAL = "周子靖_中文学术简历_v0.3_INTERNAL"
MASTER = "周子靖_中文学术简历_Master_v1"
TARGETS = [ROOT / "校对稿" / INTERNAL, ROOT / "对外PDF" / MASTER]
EDITS = {
    "计算材料物理 · 科学机器学习 · 物理驱动的逆向设计":
        "计算物理 · 科学机器学习 · 物理驱动的逆向设计",
    "科研指导：李均教授，哈尔滨工业大学": "指导教师：李均教授，哈尔滨工业大学",
    "扩展结构几何、图案与双向片阻参数空间，设计分阶段搜索策略，并结合结构连通性等约束筛选候选结构。":
        "扩展几何、图案与双向片阻等设计变量，构建分阶段搜索流程，并按连通性等几何约束筛选候选结构。",
    "个人项目版本管理。": "项目版本管理。",
}


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest().upper()


def artifact(stem, suffix):
    return stem.parent / (stem.name + suffix)


def preserve_check():
    baseline = json.loads((WORK / "核验/中文CV_v0.2_验收.json").read_text(encoding="utf-8"))
    for item in baseline["outputs"]:
        assert sha(WORK.parent / item["path"]) == item["SHA256"], item["path"]
    manifest = json.loads((WORK / "接手原件清单_20260926.json").read_text(encoding="utf-8-sig"))
    for item in manifest["files"]:
        assert sha(WORK.parent / item["Path"]) == item["SHA256"], item["Path"]
    return len(manifest["files"])


def build():
    preserve_check()
    for path in TARGETS:
        for suffix in (".docx", ".pdf"):
            if artifact(path, suffix).exists():
                raise FileExistsError(artifact(path, suffix))
    original = (ROOT / f"{OLD}.md").read_text(encoding="utf-8")
    for old, new in EDITS.items():
        assert original.count(old) == 1
        original = original.replace(old, new)
    assert original.strip() == (ROOT / f"{INTERNAL}.md").read_text(encoding="utf-8").strip()

    document = Document(ROOT / "校对稿" / f"{OLD}.docx")
    for old, new in EDITS.items():
        count = 0
        for p in document.paragraphs:
            for run in p.runs:
                if old in run.text:
                    run.text = run.text.replace(old, new)
                    count += 1
        assert count == 1, old
    for p in document.sections[0].footer.paragraphs:
        for run in p.runs:
            run.text = run.text.replace("v0.2 INTERNAL", "v0.3 INTERNAL")
    document.core_properties.title = "周子靖 | 中文学术简历 | v0.3 INTERNAL"
    document.core_properties.comments = "Editable counterpart of frozen Chinese Master v1."
    document.save(artifact(TARGETS[0], ".docx"))

    for p in document.sections[0].footer.paragraphs:
        p.clear()
    document.core_properties.title = "周子靖 | 中文学术简历"
    document.core_properties.subject = "博士申请学术简历"
    document.core_properties.comments = ""
    document.save(artifact(TARGETS[1], ".docx"))
    for path in TARGETS:
        print(artifact(path, ".docx"))


def check():
    import pymupdf

    originals = preserve_check()
    compact = lambda text: re.sub(r"\s+", "", text)
    source = (ROOT / f"{INTERNAL}.md").read_text(encoding="utf-8")
    fragments = [part for line in source.splitlines()
                 for part in re.sub(r"^(#{1,2} |- )", "", line).replace("**", "").split(" | ") if part]
    base = Document(ROOT / "校对稿" / f"{OLD}.docx")
    master_doc = Document(artifact(TARGETS[1], ".docx"))
    inner_doc = Document(artifact(TARGETS[0], ".docx"))
    assert master_doc._element.body.xml == inner_doc._element.body.xml
    assert len(base.paragraphs) == len(master_doc.paragraphs)
    for before, after in zip(base.paragraphs, master_doc.paragraphs):
        assert before._p.pPr.xml == after._p.pPr.xml, "Unexpected paragraph layout change"

    results = []
    expected_links = {"mailto:zhouzijing54@gmail.com", "https://doi.org/10.20249/j.cnki.2096-5974.2025.01.011",
                      "https://doi.org/10.1360/SSPMA-2024-0393"}
    body_lines = []
    for target in TARGETS:
        with pymupdf.open(artifact(target, ".pdf")) as pdf:
            assert len(pdf) == 1
            page = pdf[0]
            text = compact(page.get_text())
            doc_text = compact("\n".join(p.text for p in Document(artifact(target, ".docx")).paragraphs))
            for part in fragments:
                assert compact(part) in text and compact(part) in doc_text, part
            if target == TARGETS[1]:
                assert not any(word in text + str(pdf.metadata) for word in ("INTERNAL", "内部校对", "v0.2", "v0.3"))
            else:
                assert "v0.3INTERNAL" in text
            spans = [s for b in page.get_text("dict")["blocks"] if "lines" in b for l in b["lines"] for s in l["spans"] if s["text"].strip()]
            assert all(page.rect.contains(pymupdf.Rect(s["bbox"])) for s in spans)
            glyphs = [c for b in page.get_text("rawdict")["blocks"] if "lines" in b for l in b["lines"] for s in l["spans"] for c in s["chars"] if c["c"].strip()]
            assert all(49 <= c["bbox"][0] and c["bbox"][2] <= page.rect.width - 49 for c in glyphs)
            assert len([s for s in spans if "周子靖" in s["text"] and "Bold" in s["font"]]) == 3
            assert {link.get("uri") for link in page.get_links()} == expected_links
            assert all("SourceHanSansCN" in row[3] and pdf.extract_font(row[0])[3] for row in page.get_fonts())
            body_lines.append([(s["text"], s["bbox"]) for s in spans if s["bbox"][1] < 760])
            if target == TARGETS[1]:
                assert all(s["bbox"][1] < 760 for s in spans), "Master still has footer text"
            results.append({"file": str(artifact(target, ".pdf").relative_to(WORK.parent)), "pages": 1,
                            "text_fragments_verified": len(fragments), "SHA256": sha(artifact(target, ".pdf"))})
    assert body_lines[0] == body_lines[1], "Internal and clean PDF bodies differ"
    report = {"version": "Master v1", "status": "READY; frozen public fact master; not sent",
              "original_assets_unchanged": originals, "v02_md_docx_pdf_unchanged": True,
              "only_four_body_edits": True, "paragraph_layout_unchanged": True,
              "pdf_body_text_and_positions_identical": True, "master_footer_and_internal_metadata_removed": True,
              "name_bold_links_fonts_bounds_checked": True, "outputs": results}
    (WORK / "核验/中文CV_Master_v1_验收.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else build()
