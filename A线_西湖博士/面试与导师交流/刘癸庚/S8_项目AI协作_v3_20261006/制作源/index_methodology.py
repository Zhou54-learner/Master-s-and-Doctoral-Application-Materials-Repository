"""Read-only evidence index; does not copy the independent repository into this one."""
from pathlib import Path
import hashlib,json,subprocess
OUT=Path(__file__).resolve().parents[1]
ROOT=Path('F:/Physics_Learning_Assistant')
items=[
('AI部门化工作法-v0.2-弹性化人类Agent协作操作手册.md',['v0.1 解决的核心问题是','不是所有任务都需要完整部门化','人类总控不应亲自承担','## 19. 人类总控降负机制','## 27. 简短案例']),
('AI部门化工作法-Codex-GPT人类总控操作手册.md',['关键节点强制分窗，执行窗口不审自己','自动测试、构建、扫描和安装验证只能证明工程候选状态','## 15. 简短案例']),
('Physics_Learning_Assistant_新成员入门手册.md',['### 2.8 人也需要在项目中成长','### 4.2 它是一个真实训练场','### 9.5 独立审查窗口为什么重要','### 9.10 人类要保留判断空间','### 11.2 Agent 做出来了'])]
records=[]
for name,needles in items:
    p=ROOT/'docs/methodology'/name;lines=p.read_text(encoding='utf-8-sig').splitlines();quotes=[]
    for needle in needles:
        j=next(i for i,t in enumerate(lines) if needle in t)
        quotes.append({'line':j+1,'excerpt':'\n'.join(lines[j:j+5])})
    records.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'used_passages':quotes})
data={'verified_on':'2026-10-06','repo':str(ROOT),'repo_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
      'evidence_level':'Local methodology text and self-described history; not independent validation of every practice or product efficacy.',
      'read_only':True,'source_of_origin_story':'User instruction in the current S8/S9 v3 request; not inferred from documents or screenshots.','files':records}
(OUT/'检查证据/方法论来源.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print('Indexed three methodology sources.')
