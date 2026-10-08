"""PowerPoint 16.0 export and geometry/notes/pixel validation for only S8 v3.1."""
from pathlib import Path
import hashlib, json, subprocess, zipfile
from PIL import Image
from pptx import Presentation
import win32com.client

OUT = Path(__file__).resolve().parents[1]
PRE, QA = OUT / '预览', OUT / '检查证据'
STEM = 'S8_项目AI协作_v3.1'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def norm(value):
    return value.replace('\r\n', '\n').replace('\r', '\n').replace('\x0b', '\n').strip()

def main():
    path = OUT / (STEM + '.pptx')
    before = sha(path)
    app = win32com.client.DispatchEx('PowerPoint.Application')
    assert str(app.Version) == '16.0'
    security = app.AutomationSecurity
    app.AutomationSecurity = 3
    deck = None
    report = {'renderer': 'Microsoft PowerPoint ' + str(app.Version), 'slides': 1, 'pptx_sha256': before,
              'text_overflow': [], 'outside_canvas': [], 'shapes': [], 'notes': [], 'images': [], 'source_checks': []}
    try:
        deck = app.Presentations.Open(str(path), True, False, False)
        assert deck.Slides.Count == 1
        slide = deck.Slides(1)
        for w, h in [(3840, 2160), (1920, 1080)]:
            output = PRE / f'S8_{w}x{h}.png'
            slide.Export(str(output), 'PNG', w, h)
            assert Image.open(output).size == (w, h)
        for sh in slide.Shapes:
            x, y, w, h = [float(getattr(sh, a)) for a in ['Left', 'Top', 'Width', 'Height']]
            record = {'name': sh.Name, 'type': sh.Type, 'rect_pt': [x, y, w, h]}
            if x < -.1 or y < -.1 or x+w > float(deck.PageSetup.SlideWidth)+.1 or y+h > float(deck.PageSetup.SlideHeight)+.1:
                report['outside_canvas'].append(record)
            if sh.HasTextFrame and sh.TextFrame.HasText:
                tf, tr = sh.TextFrame2, sh.TextFrame2.TextRange
                actual = [float(tr.BoundWidth), float(tr.BoundHeight)]
                allowed = [w-float(tf.MarginLeft+tf.MarginRight), h-float(tf.MarginTop+tf.MarginBottom)]
                record.update(text=sh.TextFrame.TextRange.Text, bound_pt=actual, available_pt=allowed, font=tr.Font.Name)
                if actual[0] > allowed[0]+1 or actual[1] > allowed[1]+1:
                    report['text_overflow'].append(record)
            report['shapes'].append(record)
        texts = [sh.TextFrame.TextRange.Text for sh in slide.NotesPage.Shapes if sh.HasTextFrame and sh.TextFrame.HasText]
        expected = (OUT / 'speaker_notes.md').read_text(encoding='utf8')
        report['notes'] = [{'exact_match': any(norm(t) == norm(expected) for t in texts), 'source': 'speaker_notes.md'}]
        (QA / 'S8_PowerPoint备注读回.txt').write_text('\n\n'.join(norm(t) for t in texts), encoding='utf8', newline='\n')
        deck.SaveAs(str(OUT / (STEM + '.pdf')), 32)
    finally:
        if deck is not None:
            deck.Close()
        app.AutomationSecurity = security
        # Never close the user's other presentations or their application session.
        if app.Presentations.Count == 0:
            app.Quit()
    report['pptx_unchanged_after_export'] = sha(path) == before
    with zipfile.ZipFile(path) as package:
        media = {hashlib.sha256(package.read(n)).hexdigest() for n in package.namelist() if n.startswith('ppt/media/')}
    ppt = Presentation(path)
    for sh in ppt.slides[0].shapes:
        if sh.shape_type == 13:
            iw, ih = sh.image.size
            report['images'].append({'name': sh.name, 'pixels': [iw, ih],
                                     'aspect_relative_error': abs((sh.width/sh.height)/(iw/ih)-1),
                                     'crop': [sh.crop_left, sh.crop_top, sh.crop_right, sh.crop_bottom]})
    for record in json.loads((OUT / '派生素材说明.json').read_text(encoding='utf8')):
        source, derived = OUT / record['packaged_original'], OUT / record['output']
        with Image.open(source) as im, Image.open(derived) as crop:
            expected = im.crop(record['crop_box'])
            pixels_match = expected.mode == crop.mode and expected.tobytes() == crop.tobytes()
        report['source_checks'].append({'key': record['key'], 'source_hash_match': sha(source) == record['source_sha256'],
                                        'crop_pixels_identical': pixels_match, 'embedded_bytes_identical': sha(derived) in media})
    pdf = OUT / (STEM + '.pdf')
    pdfinfo = subprocess.check_output(['pdfinfo', str(pdf)]).decode('utf8', errors='replace')
    (QA / 'PDF元数据.txt').write_text('\n'.join(line.rstrip() for line in pdfinfo.splitlines())+'\n', encoding='utf8', newline='\n')
    # Microsoft 365 branding is used in PDF metadata; the COM renderer supplies the version.
    report['pdf_powerpoint_creator'] = 'Microsoft' in pdfinfo and 'PowerPoint' in pdfinfo
    report['powerpoint16_version_verified'] = report['renderer'] == 'Microsoft PowerPoint 16.0'
    assert 'Pages:           1' in pdfinfo
    subprocess.run(['pdftoppm', '-f', '1', '-l', '1', '-png', '-scale-to-x', '1920', '-scale-to-y', '1080',
                    '-singlefile', str(pdf), str(QA / 'S8_PDF实际渲染')], check=True, capture_output=True)
    (QA / 'PowerPoint实际渲染检查.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
    assert not report['text_overflow'] and not report['outside_canvas'], report
    assert report['notes'][0]['exact_match'] and report['pptx_unchanged_after_export']
    assert len(report['images']) == 3
    assert all(r['aspect_relative_error'] < 1e-5 and r['crop'] == [0, 0, 0, 0] for r in report['images'])
    assert all(all(r[k] for k in ['source_hash_match', 'crop_pixels_identical', 'embedded_bytes_identical']) for r in report['source_checks'])
    assert report['pdf_powerpoint_creator'] and report['powerpoint16_version_verified']
    print(json.dumps({'renderer': report['renderer'], 'overflow': 0, 'outside': 0,
                      'notes_match': True, 'original_crops_preserved': 3}, ensure_ascii=False))

if __name__ == '__main__':
    main()
