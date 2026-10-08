"""Compose review PNGs from existing exports. No editing/merging other slides."""
from pathlib import Path
import hashlib, json
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1]
PI = OUT.parent
ROOT = next(p for p in PI.parents if (p / '申请路线总览.md').exists())
PRE, QA = OUT / '预览', OUT / '检查证据'
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 25)
refs = [
    (PI / 'S7_乐音研究_v2_20261006/预览/S7_v2_A_1920x1080.png', 'S7A · 既有 v2 A，原样引用'),
    (PRE / 'S8_1920x1080.png', 'S8 v3.1 · 想法、Demo 与协作闭环'),
    (PI / 'S9_个人AI外骨骼_v3_20261006/预览/S9-A_1920x1080.png', 'S9-A v3 · 长期状态 / 空间进度'),
    (PI / 'S9_个人AI外骨骼_v3_20261006/预览/S9-B_1920x1080.png', 'S9-B v3 · 当前执行 / 下一步行动'),
    (PI / 'S10_反思_v2_20261006/预览/S10_1920x1080.png', 'S10 · 既有 v2 A，原样引用'),
]
vertical = Image.new('RGB', (1944, 5*1130+24), '#E8EDF2')
horizontal = Image.new('RGB', (5*972+12, 610), '#E8EDF2')
dv, dh = ImageDraw.Draw(vertical), ImageDraw.Draw(horizontal)
records = []
for i, (path, label) in enumerate(refs):
    with Image.open(path) as source:
        im = source.convert('RGB')
    assert im.size == (1920, 1080)
    y = 12+i*1130
    dv.text((18, y), label, font=font, fill='#172B43')
    vertical.paste(im, (12, y+38))
    x = 12+i*972
    dh.text((x, 10), label, font=font, fill='#172B43')
    horizontal.paste(im.resize((960, 540), Image.Resampling.LANCZOS), (x, 54))
    records.append({'order': i+1, 'label': label, 'path': path.relative_to(ROOT).as_posix(),
                    'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'operation': 'Read-only reuse of actual PowerPoint export.'})
stem = 'S7A-S8v3.1-S9Av3-S9Bv3-S10_连续审阅'
vertical.save(PRE / (stem + '_纵向.png'))
horizontal.save(PRE / (stem + '_横向.png'))
(QA / '连续审阅来源.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf8')
print('Created both five-frame review images; other candidates unchanged.')
