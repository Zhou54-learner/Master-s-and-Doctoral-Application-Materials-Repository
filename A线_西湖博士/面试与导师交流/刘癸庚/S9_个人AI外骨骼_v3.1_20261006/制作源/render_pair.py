"""Render S9 v3.1 with real Microsoft PowerPoint 16.0.
The confirmed S8 v3.1 candidate is used only by the separate review compositor.
"""
from pathlib import Path
import argparse,hashlib,json,zipfile,subprocess
from PIL import Image
from pptx import Presentation
import win32com.client
S9=Path(__file__).resolve().parents[1];PI=S9.parent
S8=PI/'S8_项目AI协作_v3.1_20261006'
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(t):return t.replace('\r\n','\n').replace('\r','\n').replace('\x0b','\n').strip()

def render(out,stem,frames,notesfiles,app):
    pre=out/'预览';qa=out/'检查证据'
    pre.mkdir(exist_ok=True);qa.mkdir(exist_ok=True)
    path=out/(stem+'.pptx');before=sha(path);deck=None
    report=dict(renderer='Microsoft PowerPoint '+str(app.Version),pptx_sha256=before,
                frames=frames,slides=len(frames),text_overflow=[],outside_canvas=[],notes=[],shapes=[])
    try:
        deck=app.Presentations.Open(str(path),True,False,False)
        assert deck.Slides.Count==len(frames)
        for i,frame in enumerate(frames,1):
            slide=deck.Slides(i)
            for w,h in [(3840,2160),(1920,1080)]:
                slide.Export(str(pre/f'{frame}_{w}x{h}.png'),'PNG',w,h)
                assert Image.open(pre/f'{frame}_{w}x{h}.png').size==(w,h)
            for sh in slide.Shapes:
                x,y,w,h=[float(getattr(sh,a)) for a in ['Left','Top','Width','Height']]
                r=dict(frame=frame,name=sh.Name,type=sh.Type,rect_pt=[x,y,w,h])
                if x<-.1 or y<-.1 or x+w>float(deck.PageSetup.SlideWidth)+.1 or y+h>float(deck.PageSetup.SlideHeight)+.1:
                    report['outside_canvas'].append(r)
                if sh.HasTextFrame and sh.TextFrame.HasText:
                    tf=sh.TextFrame2;tr=tf.TextRange
                    actual=[float(tr.BoundWidth),float(tr.BoundHeight)]
                    allowed=[w-float(tf.MarginLeft+tf.MarginRight),h-float(tf.MarginTop+tf.MarginBottom)]
                    r.update(text=sh.TextFrame.TextRange.Text,bound_pt=actual,available_pt=allowed,font=tr.Font.Name)
                    if actual[0]>allowed[0]+1 or actual[1]>allowed[1]+1:report['text_overflow'].append(r)
                report['shapes'].append(r)
            note_texts=[sh.TextFrame.TextRange.Text for sh in slide.NotesPage.Shapes if sh.HasTextFrame and sh.TextFrame.HasText]
            expected=(out/notesfiles[i-1]).read_text(encoding='utf8')
            match=any(norm(n)==norm(expected) for n in note_texts)
            (qa/f'{frame}_PowerPoint备注读回.txt').write_text('\n\n'.join(norm(n) for n in note_texts),encoding='utf8',newline='\n')
            report['notes'].append(dict(frame=frame,exact_match=match,source=notesfiles[i-1]))
        deck.SaveAs(str(out/(stem+'.pdf')),32)
    finally:
        if deck is not None:deck.Close()
    report['pptx_unchanged_after_export']=sha(path)==before
    ppt=Presentation(path);report['images']=[]
    for i,s in enumerate(ppt.slides):
        for sh in s.shapes:
            if sh.shape_type==13:
                iw,ih=sh.image.size;err=abs((sh.width/sh.height)/(iw/ih)-1)
                report['images'].append(dict(frame=frames[i],name=sh.name,pixels=[iw,ih],aspect_relative_error=err,
                    crop=[sh.crop_left,sh.crop_top,sh.crop_right,sh.crop_bottom]))
    with zipfile.ZipFile(path) as z:
        media={hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('ppt/media/')}
    derived=json.loads((out/'派生素材说明.json').read_text(encoding='utf8'))
    report['source_checks']=[]
    for info in derived:
        original=Image.open(ROOT/info['source']);cut=Image.open(out/info['output'])
        expected=original.crop(info.get('crop_box',info.get('crop_box_xyxy')))
        report['source_checks'].append(dict(source=info['source'],original_hash_match=sha(ROOT/info['source'])==info['source_sha256'],
            crop_pixels_identical=expected.mode==cut.mode and expected.tobytes()==cut.tobytes(),embedded_bytes_identical=sha(out/info['output']) in media))
    pdf_info=subprocess.check_output(['pdfinfo',str(out/(stem+'.pdf'))]).decode('utf8',errors='replace')
    (qa/'PDF元数据.txt').write_text('\n'.join(line.rstrip() for line in pdf_info.splitlines())+'\n',encoding='utf8',newline='\n')
    assert f'Pages:           {len(frames)}' in pdf_info
    for i,frame in enumerate(frames,1):
        subprocess.run(['pdftoppm','-f',str(i),'-l',str(i),'-png','-scale-to-x','1920','-scale-to-y','1080','-singlefile',
            str(out/(stem+'.pdf')),str(qa/f'{frame}_PDF实际渲染')],check=True,capture_output=True)
    (qa/'PowerPoint实际渲染检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    assert not report['text_overflow'] and not report['outside_canvas'],report
    assert report['pptx_unchanged_after_export'] and all(n['exact_match'] for n in report['notes'])
    assert all(i['aspect_relative_error']<1e-5 and i['crop']==[0,0,0,0] for i in report['images'])
    assert all(all(r[k] for k in ['original_hash_match','crop_pixels_identical','embedded_bytes_identical']) for r in report['source_checks'])
    return dict(folder=out.name,frames=frames,renderer=report['renderer'],overflow=0,outside=0,notes_match=True,pixels_preserved=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--only',choices=['s9'],default='s9');args=parser.parse_args()
    app=win32com.client.DispatchEx('PowerPoint.Application');assert str(app.Version)=='16.0'
    security=app.AutomationSecurity;app.AutomationSecurity=3
    results=[]
    try:
        results.append(render(S9,'S9_个人AI外骨骼_v3.1',['S9-A','S9-B'],['speaker_notes_A.md','speaker_notes_B.md'],app))
    finally:
        app.AutomationSecurity=security
        if app.Presentations.Count==0:app.Quit()
    print(json.dumps(results,ensure_ascii=False))
if __name__=='__main__':main()
