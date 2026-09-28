"""Create/check Master v1.1 without changing the archived public fact master."""
import argparse
import hashlib
import json
import re
from pathlib import Path

from docx import Document

WORK = Path(__file__).resolve().parents[1]
ROOT = WORK / "材料"
INTERNAL = "周子靖_中文学术简历_v0.4_INTERNAL"
MASTER = "周子靖_中文学术简历_Master_v1.1"
OLD_INTERNAL = "周子靖_中文学术简历_v0.3_INTERNAL"
OLD_MASTER = "周子靖_中文学术简历_Master_v1"
TARGETS = [ROOT / "校对稿" / INTERNAL, ROOT / "对外PDF" / MASTER]
OLD_MAJOR = "应用物理学（中外合作）本科，已获学士学位。"
NEW_MAJOR = "应用物理学本科，已获学士学位。"


def artifact(stem, suffix):
    return stem.parent / (stem.name + suffix)


def previous(folder, name):
    archived = folder / "历史版本" / name
    return archived if archived.exists() else folder / name


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest().upper()


def build():
    for stem in TARGETS:
        for suffix in (".docx", ".pdf"):
            if artifact(stem, suffix).exists():
                raise FileExistsError(artifact(stem, suffix))
    old_md = previous(ROOT, OLD_INTERNAL + ".md").read_text(encoding="utf-8")
    new_md = (ROOT / (INTERNAL + ".md")).read_text(encoding="utf-8")
    assert old_md.count(OLD_MAJOR) == 1
    assert old_md.replace(OLD_MAJOR, NEW_MAJOR).strip() == new_md.strip()
    doc = Document(previous(ROOT / "校对稿", OLD_INTERNAL + ".docx"))
    count = 0
    for p in doc.paragraphs:
        for run in p.runs:
            if OLD_MAJOR in run.text:
                run.text = run.text.replace(OLD_MAJOR, NEW_MAJOR)
                count += 1
    assert count == 1
    for p in doc.sections[0].footer.paragraphs:
        for run in p.runs:
            run.text = run.text.replace("v0.3 INTERNAL", "v0.4 INTERNAL")
    doc.core_properties.title = "周子靖 | 中文学术简历 | v0.4 INTERNAL"
    doc.core_properties.comments = "Editable counterpart of Chinese Master v1.1."
    doc.save(artifact(TARGETS[0], ".docx"))
    for p in doc.sections[0].footer.paragraphs:
        p.clear()
    doc.core_properties.title = "周子靖 | 中文学术简历"
    doc.core_properties.subject = "博士申请学术简历"
    doc.core_properties.comments = ""
    doc.save(artifact(TARGETS[1], ".docx"))
    print("Created new DOCX versions; old versions untouched.")


def check():
    import pymupdf

    source = (ROOT / (INTERNAL + ".md")).read_text(encoding="utf-8")
    old = Document(previous(ROOT / "对外PDF", OLD_MASTER + ".docx"))
    clean = Document(artifact(TARGETS[1], ".docx"))
    inner = Document(artifact(TARGETS[0], ".docx"))
    assert old._element.body.xml.replace(OLD_MAJOR, NEW_MAJOR) == clean._element.body.xml
    assert clean._element.body.xml == inner._element.body.xml
    compact = lambda text: re.sub(r"\s+", "", text)
    fragments = [s for line in source.splitlines() for s in
                 re.sub(r"^(#{1,2} |- )", "", line).replace("**", "").split(" | ") if s]
    bodies = []
    outputs = []
    for target in TARGETS:
        with pymupdf.open(artifact(target, ".pdf")) as pdf:
            assert len(pdf) == 1
            text = compact(pdf[0].get_text())
            word_text = compact("\n".join(p.text for p in Document(artifact(target, ".docx")).paragraphs))
            for fragment in fragments:
                assert compact(fragment) in text and compact(fragment) in word_text
            assert "中外合作" not in text
            spans = [s for b in pdf[0].get_text("dict")["blocks"] if "lines" in b
                     for line in b["lines"] for s in line["spans"] if s["text"].strip()]
            glyphs = [c for b in pdf[0].get_text("rawdict")["blocks"] if "lines" in b
                      for line in b["lines"] for s in line["spans"] for c in s["chars"] if c["c"].strip()]
            assert all(pdf[0].rect.contains(pymupdf.Rect(s["bbox"])) for s in spans)
            assert all(49 <= c["bbox"][0] and c["bbox"][2] <= pdf[0].rect.width - 49 for c in glyphs)
            assert len([s for s in spans if "周子靖" in s["text"] and "Bold" in s["font"]]) == 3
            assert all("SourceHanSansCN" in row[3] and pdf.extract_font(row[0])[3] for row in pdf[0].get_fonts())
            assert {link.get("uri") for link in pdf[0].get_links()} == {
                "mailto:zhouzijing54@gmail.com", "https://doi.org/10.20249/j.cnki.2096-5974.2025.01.011",
                "https://doi.org/10.1360/SSPMA-2024-0393"}
            bodies.append([(s["text"], s["bbox"]) for s in spans if s["bbox"][1] < 760])
            if target == TARGETS[1]:
                assert "INTERNAL" not in text + str(pdf.metadata)
                assert all(s["bbox"][1] < 760 for s in spans)
            else:
                assert "v0.4INTERNAL" in text
            outputs.append({"file": str(artifact(target, ".pdf").relative_to(WORK.parent)),
                            "pages": 1, "SHA256": sha(artifact(target, ".pdf"))})
    assert bodies[0] == bodies[1]
    manifest = json.loads((WORK / "接手原件清单_20260926.json").read_text(encoding="utf-8-sig"))
    for entry in manifest["files"]:
        assert sha(WORK.parent / entry["Path"]) == entry["SHA256"]
    report = {"version": "Master v1.1", "status": "READY; frozen; not sent", "only_major_name_changed": True,
              "old_layout_preserved": True, "internal_and_master_bodies_identical": True,
              "fonts_names_links_bounds_checked": True, "original_assets_unchanged": len(manifest["files"]),
              "source_fragments_verified": len(fragments), "outputs": outputs}
    (WORK / "核验/中文CV_Master_v1.1_验收.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    check() if parser.parse_args().check else build()
