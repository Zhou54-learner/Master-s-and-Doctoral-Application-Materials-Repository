"""Actual Microsoft PowerPoint 16.0 export, geometry and preservation checks.
Only close this deck; never close the user's other presentations.
"""
from pathlib import Path
import hashlib
import json
import zipfile
from PIL import Image, ImageDraw
import win32com.client

OUT = Path(__file__).resolve().parent.parent
ROOT = next(p for p in OUT.parents if (p / '申请路线总览.md').exists())
PREVIEW = OUT / '预览'
PREVIEW.mkdir(exist_ok=True)
path = OUT / 'S6_尘埃等离子体_v1.pptx'
app = win32com.client.DispatchEx('PowerPoint.Application')
version = str(app.Version)
assert version == '16.0', f'Microsoft PowerPoint 16.0 required, got {version}'
previous_security = app.AutomationSecurity
app.AutomationSecurity = 3
deck = None
checks = []
outside_canvas = []
picture_records = []
all_shapes = []
try:
    deck = app.Presentations.Open(str(path), True, False, False)
    assert deck.Slides.Count == 1
    slide = deck.Slides(1)
    slide.Export(str(PREVIEW / 'S6_3840x2160.png'), 'PNG', 3840, 2160)
    slide.Export(str(PREVIEW / 'S6_1920x1080.png'), 'PNG', 1920, 1080)
    deck.SaveAs(str(OUT / 'S6_尘埃等离子体_v1.pdf'), 32)
    for j in range(1, slide.Shapes.Count+1):
        shape = slide.Shapes(j)
        item = {'name': shape.Name, 'rect_pt': [float(shape.Left), float(shape.Top), float(shape.Width), float(shape.Height)]}
        x, y, w_shape, h_shape = item['rect_pt']
        if x < -.1 or y < -.1 or x+w_shape > float(deck.PageSetup.SlideWidth)+.1 or y+h_shape > float(deck.PageSetup.SlideHeight)+.1:
            outside_canvas.append(item)
        if shape.HasTextFrame and shape.TextFrame.HasText:
            tf = shape.TextFrame2
            tr = tf.TextRange
            actual = [float(tr.BoundWidth), float(tr.BoundHeight)]
            allowed = [float(shape.Width-tf.MarginLeft-tf.MarginRight), float(shape.Height-tf.MarginTop-tf.MarginBottom)]
            item.update(text=shape.TextFrame.TextRange.Text, text_bound_pt=actual, available_pt=allowed)
            if actual[0] > allowed[0] + 1 or actual[1] > allowed[1] + 1:
                checks.append(item)
        if shape.Type == 13:
            item['crop_pt'] = [float(getattr(shape.PictureFormat, 'Crop'+side)) for side in ('Left','Top','Right','Bottom')]
            picture_records.append(item)
        all_shapes.append(item)
finally:
    if deck is not None:
        deck.Close()
    app.AutomationSecurity = previous_security
    if app.Presentations.Count == 0:
        app.Quit()

baseline = json.loads((OUT/'来源与保全.json').read_text(encoding='utf-8'))
preserved = []
for item in baseline['sources'] + baseline['reference_files']:
    current = hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()
    preserved.append({'path': item['path'], 'unchanged': current == item['sha256']})
with zipfile.ZipFile(path) as z:
    media = [(p, hashlib.sha256(z.read(p)).hexdigest()) for p in z.namelist() if p.startswith('ppt/media/')]
main_sha = baseline['sources'][0]['sha256']
assert any(value == main_sha for _, value in media), 'Original image bytes not found'
w, h = baseline['original_size_px']
main_picture = next(p for p in picture_records if p['name'] == 'historical_41_position_trajectories')
pw, ph = main_picture['rect_pt'][2:4]
ratio_error = abs((pw/ph)/(w/h)-1)
assert ratio_error < .00001, ratio_error
detail = json.loads((OUT/'派生素材说明.json').read_text(encoding='utf-8'))
detail_picture = next(p for p in picture_records if p['name'] == 'historical_53_53_local_enlargement')
dw, dh = detail['derived_size_px']
dpw, dph = detail_picture['rect_pt'][2:4]
detail_ratio_error = abs((dpw/dph)/(dw/dh)-1)
assert detail_ratio_error < .00001
assert all(all(abs(v)<.01 for v in item['crop_pt']) for item in picture_records)
original_crop = Image.open(ROOT/detail['source']).convert('RGB').crop(tuple(detail['crop_box_px']))
saved_crop = Image.open(OUT/'派生素材/53_53_原图裁白边.png').convert('RGB')
assert original_crop.tobytes() == saved_crop.tobytes()
assert all(p['unchanged'] for p in preserved)
report = {'renderer': 'Microsoft PowerPoint '+version, 'slides': 1, 'slide_inches': [13.333333,7.5], 'export_sizes': [[3840,2160],[1920,1080]], 'text_overflow': checks, 'shapes_outside_canvas': outside_canvas, 'images': picture_records, 'main_image_aspect_relative_error': ratio_error, 'detail_image_aspect_relative_error': detail_ratio_error, 'main_image_original_bytes_embedded': True, 'detail_crop_pixels_match_source': True, 'source_and_reference_preservation': preserved, 'shapes': all_shapes}
(OUT/'排版与保全检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'renderer':report['renderer'], 'overflow_count':len(checks), 'aspect_error':ratio_error, 'all_preserved':all(p['unchanged'] for p in preserved)},ensure_ascii=False))
assert not checks, 'Fix PowerPoint text overflows before acceptance'
assert not outside_canvas

# A review contact sheet only; no combined PowerPoint deck is created.
reference = OUT.parent/'本科毕设_S2-S5_v2.1_20261005/预览'
sheet = Image.new('RGB',(1920,1152),'#e5eaf0')
for i, image_path in enumerate([reference/'S4.png',reference/'S5.png',PREVIEW/'S6_1920x1080.png']):
    im = Image.open(image_path).convert('RGB')
    im.thumbnail((936,527))
    x = 12+(i%2)*960 if i < 2 else 492
    y = 12 if i < 2 else 588
    sheet.paste(im,(x,y))
sheet.save(PREVIEW/'S4-S6_风格对照.png')
