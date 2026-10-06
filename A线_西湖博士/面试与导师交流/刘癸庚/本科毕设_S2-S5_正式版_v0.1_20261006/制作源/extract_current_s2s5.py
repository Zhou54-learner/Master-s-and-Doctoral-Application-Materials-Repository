"""Extract S2-S5 from the user's currently edited FULL_DRAFT without redrawing.

Slide XML, slide relationships, media, layouts, themes and notes are copied from
the current source package. The output is a four-slide editable presentation.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
from pptx import Presentation
import hashlib, json, re, posixpath, subprocess

OUT = Path(__file__).resolve().parents[1]
PI = OUT.parent
ROOT = next(p for p in PI.parents if (p / '申请路线总览.md').exists())
SOURCE = PI / 'FULL_DRAFT_v0.1_20261006' / '刘癸庚交流_INTERNAL_FULL_DRAFT_v0.1_20261006.pptx'
TARGET = OUT / '本科毕设_S2-S5_正式版_v0.1.pptx'
SLIDE_SRC = [3, 4, 5, 6]
NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
    'ct': 'http://schemas.openxmlformats.org/package/2006/content-types',
}


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return sha_bytes(path.read_bytes())


def xml(data):
    return E.fromstring(data)


def dump(node):
    return E.tostring(node, xml_declaration=True, encoding='UTF-8', standalone=True)


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def is_slide_part(name):
    return re.fullmatch(r'ppt/slides/slide\d+\.xml', name) is not None


def is_slide_rel(name):
    return re.fullmatch(r'ppt/slides/_rels/slide\d+\.xml\.rels', name) is not None


def is_notes_part(name):
    return re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', name) is not None


def is_notes_rel(name):
    return re.fullmatch(r'ppt/notesSlides/_rels/notesSlide\d+\.xml\.rels', name) is not None


def build_package():
    assert SOURCE.exists(), SOURCE
    assert not TARGET.exists(), 'Do not overwrite a formal archive; create a new version.'
    source_sha = sha(SOURCE)
    with ZipFile(SOURCE) as src:
        original = {name: src.read(name) for name in src.namelist()}

    data = {
        name: blob for name, blob in original.items()
        if not (is_slide_part(name) or is_slide_rel(name) or is_notes_part(name) or is_notes_rel(name))
    }

    # Add selected slide and notes parts under new four-slide names. All media,
    # layouts, themes, masters and other package parts remain source bytes.
    for out_i, source_i in enumerate(SLIDE_SRC, start=1):
        src_slide = f'ppt/slides/slide{source_i}.xml'
        out_slide = f'ppt/slides/slide{out_i}.xml'
        data[out_slide] = original[src_slide]

        sr = xml(original[f'ppt/slides/_rels/slide{source_i}.xml.rels'])
        for rel in sr:
            if rel.get('Type', '').endswith('/notesSlide'):
                rel.set('Target', f'../notesSlides/notesSlide{out_i}.xml')
        data[f'ppt/slides/_rels/slide{out_i}.xml.rels'] = dump(sr)

        src_note = f'ppt/notesSlides/notesSlide{source_i}.xml'
        out_note = f'ppt/notesSlides/notesSlide{out_i}.xml'
        data[out_note] = original[src_note]
        nr = xml(original[f'ppt/notesSlides/_rels/notesSlide{source_i}.xml.rels'])
        for rel in nr:
            if rel.get('Type', '').endswith('/slide'):
                rel.set('Target', f'../slides/slide{out_i}.xml')
        data[f'ppt/notesSlides/_rels/notesSlide{out_i}.xml.rels'] = dump(nr)

    # Presentation slide list and slide relationships.
    presentation = xml(data['ppt/presentation.xml'])
    slide_list = presentation.find('p:sldIdLst', NS)
    for child in list(slide_list):
        slide_list.remove(child)
    for i in range(1, 5):
        E.SubElement(slide_list, f'{{{NS["p"]}}}sldId',
                     id=str(255 + i),
                     attrib={f'{{{NS["r"]}}}id': f'rId{i}'})
    presentation_rels = xml(data['ppt/_rels/presentation.xml.rels'])
    for rel in list(presentation_rels):
        if rel.get('Type', '').endswith('/slide'):
            presentation_rels.remove(rel)
    existing_ids = {rel.get('Id') for rel in presentation_rels}
    for i in range(1, 5):
        rid = f'rId{i}'
        if rid in existing_ids:
            rid = f'rIdSlide{i}'
            slide_list[i - 1].set(f'{{{NS["r"]}}}id', rid)
        E.SubElement(presentation_rels, f'{{{NS["rel"]}}}Relationship',
                     Id=rid,
                     Type=f'{NS["r"]}/slide',
                     Target=f'slides/slide{i}.xml')
    data['ppt/_rels/presentation.xml.rels'] = dump(presentation_rels)
    # Serialize after resolving relationship-ID collisions with the slide master.
    data['ppt/presentation.xml'] = dump(presentation)

    # Content types: remove old slide/note overrides and add the four new paths.
    types = xml(data['[Content_Types].xml'])
    for child in list(types):
        part = child.get('PartName', '')
        if re.fullmatch(r'/ppt/(slides/slide\d+|notesSlides/notesSlide\d+)\.xml', part):
            types.remove(child)
    slide_ct = 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml'
    notes_ct = 'application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml'
    for i in range(1, 5):
        E.SubElement(types, f'{{{NS["ct"]}}}Override',
                     PartName=f'/ppt/slides/slide{i}.xml', ContentType=slide_ct)
        E.SubElement(types, f'{{{NS["ct"]}}}Override',
                     PartName=f'/ppt/notesSlides/notesSlide{i}.xml', ContentType=notes_ct)
    data['[Content_Types].xml'] = dump(types)

    # Update package metadata without touching any slide object.
    app = xml(data['docProps/app.xml'])
    for node in app.iter():
        if node.tag.endswith('Slides') or node.tag.endswith('Notes'):
            node.text = '4'
        if node.tag.endswith('contentStatus'):
            node.text = 'INTERNAL / FORMAL v0.1'
    data['docProps/app.xml'] = dump(app)
    core = xml(data['docProps/core.xml'])
    core_ns = 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties'
    dc_ns = 'http://purl.org/dc/elements/1.1/'
    values = {
        f'{{{dc_ns}}}title': '本科毕设 S2–S5｜INTERNAL / FORMAL v0.1',
        f'{{{dc_ns}}}subject': '从当前 FULL_DRAFT 抽出的 S2–S5 正式留档版本',
        f'{{{core_ns}}}contentStatus': 'INTERNAL / FORMAL v0.1',
        f'{{{dc_ns}}}description': 'Current edited S2–S5 extracted from the working FULL_DRAFT; other pages intentionally excluded.',
    }
    for tag, value in values.items():
        node = core.find(tag)
        if node is None:
            node = E.SubElement(core, tag)
        node.text = value
    data['docProps/core.xml'] = dump(core)

    OUT.mkdir(parents=True, exist_ok=True)
    with ZipFile(TARGET, 'w', ZIP_DEFLATED) as out:
        for name, blob in data.items():
            out.writestr(name, blob)

    # Basic editable-package check before PowerPoint rendering.
    prs = Presentation(TARGET)
    assert len(prs.slides) == 4
    assert (prs.slide_width, prs.slide_height) == (12192000, 6858000)
    for i, slide in enumerate(prs.slides, start=1):
        assert slide.notes_slide.notes_text_frame.text.strip()
    rows = []
    with ZipFile(SOURCE) as src, ZipFile(TARGET) as out:
        for page, source_page in enumerate(SLIDE_SRC, start=1):
            source_slide = f'ppt/slides/slide{source_page}.xml'
            output_slide = f'ppt/slides/slide{page}.xml'
            source_note = f'ppt/notesSlides/notesSlide{source_page}.xml'
            output_note = f'ppt/notesSlides/notesSlide{page}.xml'
            rows.append({
                'page': page,
                'logical': f'S{source_page - 1}',
                'source_full_draft': str(SOURCE.relative_to(ROOT).as_posix()),
                'source_full_draft_sha256': source_sha,
                'source_page': source_page,
                'source_slide_xml_sha256': sha_bytes(src.read(source_slide)),
                'output_slide_xml_sha256': sha_bytes(out.read(output_slide)),
                'source_notes_xml_sha256': sha_bytes(src.read(source_note)),
                'output_notes_xml_sha256': sha_bytes(out.read(output_note)),
                'slide_xml_byte_identical': src.read(source_slide) == out.read(output_slide),
                'notes_xml_byte_identical': src.read(source_note) == out.read(output_note),
                'object_count': len(prs.slides[page - 1].shapes),
                'notes_chars': len(prs.slides[page - 1].notes_slide.notes_text_frame.text),
            })
    assert all(r['slide_xml_byte_identical'] and r['notes_xml_byte_identical'] for r in rows)
    write_json(OUT / '来源与版本登记.json', {
        'status': 'INTERNAL / FORMAL v0.1',
        'source': str(SOURCE.relative_to(ROOT).as_posix()),
        'source_sha256': source_sha,
        'source_is_current_working_copy': True,
        'selected_source_pages': [3, 4, 5, 6],
        'excluded_pages': [1, 2, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        'rows': rows,
        'method': 'OPC package extraction only; selected slide and notes XML copied byte-for-byte; no slide redraw or source modification.',
    })
    print(json.dumps({'source_sha256': source_sha, 'target': str(TARGET), 'slides': len(prs.slides)}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    build_package()
