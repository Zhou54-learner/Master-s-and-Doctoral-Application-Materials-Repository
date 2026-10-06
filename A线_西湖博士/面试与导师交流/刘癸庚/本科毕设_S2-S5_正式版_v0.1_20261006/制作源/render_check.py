"""PowerPoint 16.0 render, geometry, notes and source-page fidelity checks."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
from zipfile import ZipFile
from PIL import Image, ImageChops, ImageDraw, ImageFont
from pptx import Presentation
import win32com.client
import pymupdf
import json, hashlib

OUT = Path(__file__).resolve().parents[1]
PI = OUT.parent
ROOT = next(p for p in PI.parents if (p / '申请路线总览.md').exists())
SOURCE = PI / 'FULL_DRAFT_v0.1_20261006' / '刘癸庚交流_INTERNAL_FULL_DRAFT_v0.1_20261006.pptx'
TARGET = OUT / '本科毕设_S2-S5_正式版_v0.1.pptx'
PDF = OUT / '本科毕设_S2-S5_正式版_v0.1.pdf'
PREVIEW = OUT / '预览'
SOURCE_PREVIEW = OUT / '检查证据' / '当前FULL_DRAFT源页'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def notes_from_com(slide):
    result = []
    for i in range(1, slide.NotesPage.Shapes.Count + 1):
        shape = slide.NotesPage.Shapes(i)
        try:
            if shape.PlaceholderFormat.Type == 2 and shape.HasTextFrame:
                result.append(shape.TextFrame.TextRange.Text)
        except Exception:
            pass
    assert len(result) == 1, len(result)
    return result[0].replace('\r\n', '\n').replace('\r', '\n')


def inspect_shapes(slide, width, height):
    records, overflow, outside = [], [], []
    for i in range(1, slide.Shapes.Count + 1):
        shape = slide.Shapes(i)
        x, y, w, h = [float(getattr(shape, attr)) for attr in ('Left', 'Top', 'Width', 'Height')]
        record = {'name': shape.Name, 'type': int(shape.Type), 'rect_pt': [x, y, w, h]}
        if x < -.1 or y < -.1 or x + w > width + .1 or y + h > height + .1:
            outside.append(record)
        if shape.HasTextFrame and shape.TextFrame.HasText:
            tf, tr = shape.TextFrame2, shape.TextFrame2.TextRange
            actual = [float(tr.BoundWidth), float(tr.BoundHeight)]
            available = [w - float(tf.MarginLeft + tf.MarginRight), h - float(tf.MarginTop + tf.MarginBottom)]
            record.update(text=shape.TextFrame.TextRange.Text, text_bound_pt=actual,
                          available_pt=available, font_name=tr.Font.Name,
                          font_size_pt=float(tr.Font.Size), font_far_east=tr.Font.NameFarEast)
            if actual[0] > available[0] + 1 or actual[1] > available[1] + 1:
                overflow.append(record)
        records.append(record)
    return {'shapes': records, 'text_overflow': overflow, 'objects_outside': outside}


def image_checks(pptx):
    prs = Presentation(pptx)
    records = []
    for page, slide in enumerate(prs.slides, start=1):
        for shape in slide.shapes:
            if shape.shape_type != 13:
                continue
            width, height = shape.image.size
            effective = width * (1 - shape.crop_left - shape.crop_right) / (height * (1 - shape.crop_top - shape.crop_bottom))
            display = shape.width / shape.height
            error = abs(display / effective - 1)
            records.append({'page': page, 'name': shape.name, 'native_px': [width, height],
                            'crop': [shape.crop_left, shape.crop_top, shape.crop_right, shape.crop_bottom],
                            'relative_ratio_error': error, 'pass': error < .003})
    return records


def render():
    PREVIEW.mkdir(parents=True, exist_ok=True)
    SOURCE_PREVIEW.mkdir(parents=True, exist_ok=True)
    before = sha(TARGET)
    expected = Presentation(TARGET)
    source_expected = Presentation(SOURCE)
    app = win32com.client.DispatchEx('PowerPoint.Application')
    assert str(app.Version) == '16.0', app.Version
    security = app.AutomationSecurity
    app.AutomationSecurity = 3
    formal = source = None
    pages = []
    try:
        formal = app.Presentations.Open(str(TARGET), True, False, False)
        source = app.Presentations.Open(str(SOURCE), True, False, False)
        assert formal.Slides.Count == source.Slides.Count == 4 or (formal.Slides.Count == 4 and source.Slides.Count == 15)
        assert formal.Slides.Count == 4 and source.Slides.Count == 15
        width, height = float(formal.PageSetup.SlideWidth), float(formal.PageSetup.SlideHeight)
        for page in range(1, 5):
            fslide, sslide = formal.Slides(page), source.Slides(page + 2)
            check = inspect_shapes(fslide, width, height)
            for pixels in ((1920, 1080), (3840, 2160)):
                fslide.Export(str(PREVIEW / f'S{page + 1}_{pixels[0]}x{pixels[1]}.png'), 'PNG', *pixels)
            s_path = SOURCE_PREVIEW / f'S{page + 1}_source_1920x1080.png'
            sslide.Export(str(s_path), 'PNG', 1920, 1080)
            formal_img = Image.open(PREVIEW / f'S{page + 1}_1920x1080.png').convert('RGB')
            source_img = Image.open(s_path).convert('RGB')
            diff = ImageChops.difference(formal_img, source_img)
            check.update(page=page, logical=f'S{page + 1}', source_page=page + 2,
                         notes_exact_match=notes_from_com(fslide) == expected.slides[page - 1].notes_slide.notes_text_frame.text,
                         source_render_pixel_identical=diff.getbbox() is None,
                         source_render_difference_bbox=diff.getbbox())
            assert check['notes_exact_match'] and check['source_render_pixel_identical']
            pages.append(check)
            print(f'S{page + 1}: overflow={len(check["text_overflow"])} outside={len(check["objects_outside"])} notes=True pixels=True', flush=True)
        formal.SaveAs(str(PDF), 32)
    finally:
        if formal is not None:
            formal.Close()
        if source is not None:
            source.Close()
        app.AutomationSecurity = security
        if app.Presentations.Count == 0:
            app.Quit()
    assert sha(TARGET) == before, 'Read-only PowerPoint export changed formal PPTX.'

    doc = pymupdf.open(PDF)
    assert len(doc) == 4
    pdf_pages = []
    for i, page in enumerate(doc, start=1):
        pdf_pages.append({'page': i, 'size_pt': [page.rect.width, page.rect.height],
                          'text_chars': len(page.get_text()),
                          'fonts': sorted({font[3] for font in page.get_fonts(full=True)})})
        assert abs(page.rect.width - 960) < .01 and abs(page.rect.height - 540) < .01
    doc.close()

    report = {'status': 'PASS', 'renderer': 'Microsoft PowerPoint 16.0',
              'source_full_draft': str(SOURCE.relative_to(ROOT).as_posix()),
              'source_full_draft_sha256': sha(SOURCE),
              'target_pptx_sha256_before': before, 'target_pptx_sha256_after': sha(TARGET),
              'pptx_unchanged_by_render': True, 'physical_slides': 4,
              'slide_size_pt': [width, height], 'pdf_pages': pdf_pages,
              'slides': pages, 'images': image_checks(TARGET),
              'text_overflow_count': sum(len(p['text_overflow']) for p in pages),
              'objects_outside_count': sum(len(p['objects_outside']) for p in pages),
              'notes_matches': sum(p['notes_exact_match'] for p in pages),
              'source_render_pixel_identical': sum(p['source_render_pixel_identical'] for p in pages),
              'image_ratio_failures': sum(not p['pass'] for p in image_checks(TARGET)),
              'pdf_sha256': sha(PDF),
              'checked_at': datetime.now(timezone(timedelta(hours=8))).isoformat()}
    write_json(OUT / 'PowerPoint排版检查.json', report)
    assert report['text_overflow_count'] == report['objects_outside_count'] == report['image_ratio_failures'] == 0
    assert report['notes_matches'] == report['source_render_pixel_identical'] == 4
    return report


def overview():
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 32)
    tile_w, tile_h, label_h, gap = 1880, 1058, 54, 20
    canvas = Image.new('RGB', (2 * tile_w + 3 * gap, 2 * (tile_h + label_h + gap) + 90), '#EAF0F3')
    draw = ImageDraw.Draw(canvas)
    draw.text((20, 20), '本科毕设 S2–S5 · INTERNAL / FORMAL v0.1', font=font, fill='#172B43')
    for i in range(4):
        x = gap + (i % 2) * (tile_w + gap)
        y = 75 + (i // 2) * (tile_h + label_h + gap)
        draw.text((x, y), f'S{i + 2}', font=font, fill='#172B43')
        img = Image.open(PREVIEW / f'S{i + 2}_1920x1080.png').convert('RGB')
        canvas.paste(img.resize((tile_w, tile_h), Image.Resampling.LANCZOS), (x, y + label_h))
    canvas.save(PREVIEW / '四页总览.png')


if __name__ == '__main__':
    result = render()
    overview()
    print(json.dumps({k: result[k] for k in ('renderer', 'physical_slides', 'notes_matches',
                                               'source_render_pixel_identical', 'text_overflow_count',
                                               'objects_outside_count', 'image_ratio_failures')}, ensure_ascii=False), flush=True)
