from pathlib import Path
import json,hashlib,re,html,urllib.parse,zipfile
import markdown
from pptx import Presentation
import pymupdf
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
AUD=ROOT/'公共资料/事实核验/本科毕设紧急审计_20261008'
css='''body{font:18px/1.85 "Microsoft YaHei",sans-serif;color:#142c46;max-width:1000px;margin:32px auto;padding:0 24px;background:#fff}h1{font-size:30px;line-height:1.5}h2{margin-top:2em;font-size:24px;color:#087d7d;border-top:1px solid #dce5eb;padding-top:18px}h3{font-size:21px}a{color:#087d7d}table{border-collapse:collapse;font-size:15px;width:100%;display:block;overflow:auto}td,th{border:1px solid #dce5eb;padding:9px 12px;vertical-align:top}th{background:#eef5f6}code{font-size:16px;background:#eef3f6;padding:2px 4px}img{max-width:100%}.nav{background:#edf5f5;padding:14px 20px;border-radius:8px;margin:20px 0}.card{display:block;padding:16px 20px;margin:10px 0;background:#f0f5f7;border-radius:8px;text-decoration:none}.small{font-size:15px;color:#637184}@media print{body{font-size:12pt;max-width:none;margin:0}h2{break-after:avoid}table{font-size:9pt}.nav{display:none}}'''
docs=list(OUT.glob('*.md'))+[AUD/'科研流程审计.md']
for p in docs:
    content=markdown.markdown(p.read_text(encoding='utf-8'),extensions=['tables','fenced_code','toc'])
    def fix(m):
        href=html.unescape(m.group(1))
        if href.lower().startswith(('http:','https:','#','mailto:')): return m.group(0)
        target=p.parent/urllib.parse.unquote(href)
        if re.match(r'^[A-Za-z]:[/\\]',href):target=Path(href)
        if target.suffix=='.md' and target.resolve() in [q.resolve() for q in docs]:target=target.with_suffix('.html')
        return 'href="'+html.escape(target.resolve().as_uri())+'"'
    content=re.sub(r'href="([^"]+)"',fix,content)
    p.with_suffix('.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+p.stem+'</title><style>'+css+'</style><body>'+content+'</body></html>',encoding='utf-8')
links=[('先看：面试前15分钟备忘单','面试前15分钟备忘单.html'),('12页可编辑PPT','周子靖_田静逸交流_12页修订版_v1_20261008.pptx'),('PDF备用版','周子靖_田静逸交流_12页修订版_v1_20261008.pdf'),('逐页讲稿','逐页讲稿.html'),('20张技术追问卡','技术追问卡_20题.html'),('修改说明与一致性核查','修改说明与一致性核查.html'),('完整科研流程审计',str((AUD/'科研流程审计.html').as_uri()))]
body='<h1>田静逸老师交流 · 面试准备</h1><p>2026年10月9日10:00，北京时间。建议先复述实际工作流程，再看演示稿。</p><div class="nav">今晚优先练：Q1数据链、Q2材料、Q6端口、Q8指标、Q12算法、Q13贡献。<br>一条直接答案 → 一个真实动作/证据 → 一个具体边界 → 停。</div>'
body+=''.join('<a class="card" href="'+html.escape(u)+'">'+html.escape(t)+'</a>' for t,u in links)
body+='<p class="small">本包未发送。内部审计与追问卡仅供本人准备；分享屏幕时打开幻灯片。所有原始科研资料保持原样。本轮只读恢复历史结果，没有运行新仿真。</p><h2>12页总览</h2><img src="12页总览.jpg" alt="12页PPT总览">'
(OUT/'00_面试入口.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>田静逸面试准备</title><style>'+css+'</style><body>'+body+'</body></html>',encoding='utf-8')
broken=[]
for p in docs:
    for u in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        u=u.strip('<>')
        if u.startswith(('http:','https:','#')):continue
        dest=Path(u) if re.match(r'^[A-Za-z]:[/\\]',u) else p.parent/u.split('#')[0]
        if not dest.exists() and dest.name!='最终验收.json':broken.append({'file':str(p),'target':u})
manifest=json.loads((AUD/'来源哈希.json').read_text(encoding='utf-8'))
changed=[]
for row in manifest:
    p=Path(row['path'])
    if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:changed.append(str(p))
ppt=OUT/'周子靖_田静逸交流_12页修订版_v1_20261008.pptx';prs=Presentation(ppt)
pdf=pymupdf.open(OUT/'周子靖_田静逸交流_12页修订版_v1_20261008.pdf')
notes=(OUT/'逐页讲稿.md').read_text(encoding='utf-8')
matches=[]
for i,sl in enumerate(prs.slides,1):
    n=sl.notes_slide.notes_text_frame.text.split('\n\n【证据】')[0]
    matches.append(n in notes)
qa=(OUT/'技术追问卡_20题.md').read_text(encoding='utf-8')
result={'ppt_pages':len(prs.slides),'pdf_pages':len(pdf),'notes_match':sum(matches),'question_count':len(re.findall(r'^## Q\d+｜',qa,re.M)),'source_files_unchanged':not changed,'changed_sources':changed,'broken_local_links':broken,'layout':json.loads((OUT/'版式检查.json').read_text(encoding='utf-8')),'native_preservation':json.loads((AUD/'native/原件保全.json').read_text(encoding='utf-8')),'not_verified':['本人独立复述与实际计时','现场屏幕分享','PET有效损耗设置及物性来源','独立数值收敛、制造和实测']}
(OUT/'最终验收.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
