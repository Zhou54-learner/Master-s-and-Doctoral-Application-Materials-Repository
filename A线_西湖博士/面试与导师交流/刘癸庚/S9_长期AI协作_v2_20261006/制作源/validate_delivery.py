"""Check deliverable links, rendered payload hashes, notes and source manifest."""
from pathlib import Path
import hashlib,json,re,subprocess
from pptx import Presentation
from PIL import Image
S9=Path(__file__).resolve().parents[1];S8=S9.parent/'S8_项目AI协作_v2_20261006'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
missing=[];links=0;deliveries=[]
for out,stem,title,frames,notes in [
    (S8,'S8_项目AI协作_v2','第一次比较系统地和 AI 一起做一个项目',['S8'],['本页备注.md']),
    (S9,'S9_长期AI协作_v2','后来，我想让这种协作不要每次都从零开始',['S9-A','S9-B'],['speaker_notes_A.md','speaker_notes_B.md'])]:
    for md in out.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',md.read_text(encoding='utf8')):
            if '://' in target or target.startswith('#'):continue
            links+=1
            if not (md.parent/target.split('#')[0]).exists():missing.append([str(md),target])
    report=json.loads((out/'检查证据/PowerPoint实际渲染检查.json').read_text(encoding='utf8'))
    assert sha(out/(stem+'.pptx'))==report['pptx_sha256']
    ppt=Presentation(out/(stem+'.pptx'));assert len(ppt.slides)==len(frames)
    for i,slide in enumerate(ppt.slides):
        text='\n'.join(s.text for s in slide.shapes if s.has_text_frame)
        assert title in text
        assert not any(s in text for s in ['PROJECT COLLABORATION','LONG-TERM COLLABORATION','Agent orchestration','人–AI 协作方法'])
        assert slide.notes_slide.notes_text_frame.text.strip()==(out/notes[i]).read_text(encoding='utf8').strip()
        for w,h in [(3840,2160),(1920,1080)]:assert Image.open(out/'预览'/f'{frames[i]}_{w}x{h}.png').size==(w,h)
    deliveries.append(dict(directory=out.name,frames=frames,pptx_sha256=sha(out/(stem+'.pptx')),pdf_sha256=sha(out/(stem+'.pdf'))))
assert '但是这种做法还有一个很明显的问题：一个项目做完以后，下一个任务又得重新把背景、目标和现在做到哪里全部告诉它。' in (S8/'本页备注.md').read_text(encoding='utf8')
assert '做这些东西的时候，我其实也会冒出一些暂时想不清楚的问题。' in (S9/'speaker_notes_B.md').read_text(encoding='utf8')
assert not missing,missing
refs=json.loads((S9/'检查证据/连续审阅来源.json').read_text(encoding='utf8'))
root=next(p for p in S9.parents if (p/'申请路线总览.md').exists())
assert all(sha(root/r['path'])==r['sha256'] for r in refs)
result=dict(deliveries=deliveries,links_checked=links,broken_links=missing,review_inputs_unchanged=True,
    exact_user_transitions_present=True,pr_policy='OPEN / no auto-merge; no main merge; no sending',
    current_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip())
(S9/'检查证据/交付核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
