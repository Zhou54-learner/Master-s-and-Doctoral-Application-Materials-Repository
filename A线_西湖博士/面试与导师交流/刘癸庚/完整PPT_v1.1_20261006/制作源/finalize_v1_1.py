"""Validate the delivered revision and write provenance and review documentation."""
import csv, json, re, zipfile, hashlib, platform
from pathlib import Path
from importlib.metadata import version
from lxml import etree as E
from pptx import Presentation
from PIL import Image
import pymupdf
from build_v1_1 import OUT, PI, SOURCE, SCRIPT, STEM, DECK, KEYS, NS, sha, jwrite, section

EXPECTED = {
 'S12':[
  '本科这几年做过的事情虽然比较散，','但我慢慢确认了一件事。',
  '我很喜欢从一个还没想清楚的问题出发，','再一点点把它变成可以研究、可以验证的东西。',
  '做得越多，我也越能看到自己的不足：','比起把事情“做出来”，我更需要补的是理论理解和对结果的判断。',
  '所以我想找一个方向真正沉下去做几年，','直到能够对自己的判断和结论负责。'],
 'S13':[
  '我已经做过一些：','电磁仿真 · 周期结构 · 数值优化','但我现在更想继续往下问：','为什么会有这样的响应？',
  '模式 · 边界 · 损耗 · 可靠性','背后到底是哪一部分物理在起作用？','Complex Waves and Fields',
  'topology / non-Hermitian：这些是我接下来很想系统学习的方向',
  '我希望接下来能围绕一个方向连续做深','Westlake Physics · 定导培养']}

def final_checks():
    report=json.loads((OUT/'PowerPoint导出与检查.json').read_text(encoding='utf-8'))
    src=Presentation(SOURCE);dst=Presentation(DECK)
    rows=json.loads((OUT/'页码与来源映射.json').read_text(encoding='utf-8'))
    with zipfile.ZipFile(DECK) as z,zipfile.ZipFile(SOURCE) as a:
        assert z.testzip() is None
        changed=[n for n in z.namelist() if z.read(n)!=a.read(n)]
        assert changed==['ppt/slides/slide14.xml','ppt/slides/slide15.xml','ppt/notesSlides/notesSlide14.xml','ppt/notesSlides/notesSlide15.xml']
        markers=[]
        for n in z.namelist():
            if n.endswith('.xml'):
                tree=E.fromstring(z.read(n))
                txt=' '.join(tree.itertext())
                if re.search(r'\b(?:INTERNAL|CANDIDATE|FULL[ _-]?DRAFT|REVIEW[ _-]?DRAFT)\b',txt,re.I):markers.append(n)
        assert not markers
    pdf=pymupdf.open(OUT/(STEM+'.pdf'))
    text_checks=[]
    for idx,key in [(13,'S12'),(14,'S13')]:
        s=dst.slides[idx]
        shape_text='\n'.join(sh.text for sh in s.shapes if sh.has_text_frame)
        flat=lambda x:re.sub(r'\s+','',x)
        pdftext=flat(pdf[idx].get_text())
        for words in EXPECTED[key]:
            assert words in shape_text, (key,words)
            assert flat(words) in pdftext, (key,'PDF',words)
        assert s.notes_slide.notes_text_frame.text==section(idx-1)
        for name in ['section','title','footer_rule','slide_number']:
            old=[sh for sh in src.slides[idx].shapes if sh.name==name][0]
            new=[sh for sh in s.shapes if sh.name==name][0]
            assert E.tostring(old._element)==E.tostring(new._element),(key,name)
        text_checks.append({'logical':key,'user_copy_lines_matched':len(EXPECTED[key]),'PDF_text_matched':True,'title_and_footer_unchanged':True,'notes_exact_v5':True})
    pdf.close()
    for i,s in enumerate(dst.slides):
        if i<13:
            assert src.slides[i].part.blob==s.part.blob
            assert src.slides[i].notes_slide.part.blob==s.notes_slide.part.blob
        note=s.notes_slide.notes_text_frame.text
        assert (OUT/'逐页备注'/f'{i+1:02d}_{KEYS[i]}.md').read_text(encoding='utf-8')==note
        assert (OUT/'检查证据/PowerPoint备注读回'/f'{i+1:02d}_{KEYS[i]}.txt').read_text(encoding='utf-8')==note
    pngs=[]
    for i,key in enumerate(KEYS,1):
        for w,h in [(1920,1080),(3840,2160)]:
            p=OUT/'预览'/f'{i:02d}_{key}_{w}x{h}.png'
            with Image.open(p) as im:assert im.size==(w,h)
            pngs.append({'path':p.relative_to(OUT).as_posix(),'size':[w,h],'sha256':sha(p)})
    baseline=json.loads((OUT/'制作前保全基线.json').read_text(encoding='utf-8'))
    preserved=[];changed_originals=[]
    for row in baseline:
        p=PI/row['path']
        if not p.exists() or sha(p)!=row['sha256']:changed_originals.append(row['path'])
        else:preserved.append(row['path'])
    assert changed_originals==['README.md'],changed_originals
    preservation={'original_files':len(baseline),'unchanged_count':len(preserved),'authorized_index_update':changed_originals,
                  'source_PPTX_unchanged':sha(SOURCE)=='f09effacea63224484c9e8cf41747a6d59dde3669906b3d2a0bd2ff388339514',
                  'old_FULL_DRAFT_and_all_script_sources_unchanged':True}
    jwrite(OUT/'保全检查.json',preservation)
    checks={'PASS':True,'package_changed_parts':changed,'user_copy_checks':text_checks,'S0_S11_XML_and_notes_unchanged':True,
            'S0_S11_pixels_unchanged':report['S0_S11_pixel_identical'],'notes_readback_matches':15,
            'text_overflow_count':report['text_overflow_count'],'objects_outside_count':report['objects_outside_count'],
            'PDF_pages':len(report['pdf_pages']),'PDF_fonts_embedded':report['pdf_all_fonts_embedded'],
            'internal_status_marker_hits':markers,'full_page_PNGs':pngs,'preservation':preservation}
    jwrite(OUT/'交付验收.json',checks)
    jwrite(OUT/'制作源/运行环境.json',{'python':platform.python_version(),'libraries':{n:version(n) for n in ['python-pptx','lxml','Pillow','pywin32','PyMuPDF']},'renderer':report['renderer']})
    return rows,checks

def documentation(rows,checks):
    mapping='''# v1.1 页码与来源映射

底稿为本人微调后推送的完整 v1，提交 `4dcb9d1`；PPTX SHA-256：`'''+sha(SOURCE)+'''`。

只更新第 14、15 个实体页（S12、S13）；S9-A/B 仍为两个连续实体页。

| 实体页 | 逻辑页 | 页面来源 | Speaker notes 来源 |
|---:|---|---|---|
'''
    for r in rows:mapping+=f'| {r["page"]} | {r["logical"]} | {r["page_source"]} | {r["notes_source"]} |\n'
    mapping+='\n[底稿 PPTX](../完整PPT_v1_20261006/刘癸庚交流_完整PPT_v1_20261006.pptx) · [v5 母稿](../完整讲稿_完整母稿_v5_20261006.md) · [逐页备注](逐页备注/)\n'
    (OUT/'页码与来源映射表.md').write_text(mapping,encoding='utf-8')
    with (OUT/'页码与来源映射表.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (OUT/'README.md').write_text(f'''# 刘癸庚交流｜完整 PPT v1.1 小修版

2026-10-06。以本人微调后的完整 v1 为底稿，仅修订 S12、S13 文案与备注；15 个实体页，S0–S11 原样保留。

## 交付入口

- [完整可编辑 PPTX]({STEM}.pptx)
- [完整 PDF]({STEM}.pdf)
- [4K / 1080p 全页 PNG 与逐页审阅](预览/连续审阅.html)
- [全部 15 页连续审阅长图](预览/全部15页_连续审阅_纵向.png) · [总览](预览/全部15页_总览.png)
- [S11 → S12 → S13 连续审阅](预览/S11-S13_连续审阅.png)
- [页码与来源映射](页码与来源映射表.md) · [检查报告](检查报告.md)

## 修改与验收

S12、S13 使用本人指定页面文案；两页 speaker notes 完整采用[完整母稿 v5](../完整讲稿_完整母稿_v5_20261006.md)对应章节。S0–S11 的备注沿用底稿，不将其他新讲稿自动写回。

PPTX 包仅 4 个部件发生变化：末两页及其备注。其余页面、母版、图片和关系文件均保持。PowerPoint 实际导出验证前 13 页与底稿逐像素一致，文字溢出与对象越界均为 0，15/15 备注读回匹配。白底、深海军蓝、青色强调和 S13 递进顺序保留；未添加图片。

v1 保留为本人微调底稿和本轮溯源材料；旧 PDF/PNG 仍代表旧版本。本目录导出文件与 v1.1 PPTX 配套。PDF 不含 speaker notes；备注在 PPTX 与逐页文本中。现场投影与自然试讲尚待本人完成。

PR #15 保持 OPEN / no auto-merge；不合并 main、不发送材料、不改变 PI 联系状态。
''',encoding='utf-8')
    (OUT/'检查报告.md').write_text(f'''# 完整 PPT v1.1 小修检查报告

2026-10-06｜结果：**PASS**

## 输入与修改范围

底稿为当前分支提交 `4dcb9d1` 中本人微调后的完整 v1，SHA-256 `{sha(SOURCE)}`。它包含本人上一轮的整套微调，本轮没有回退到最初生成版。两页备注来源为 `完整讲稿_完整母稿_v5_20261006.md` 的 S12、S13 章节；不采用其他版本替换 S0–S11。

S12 按本人指定的四段文字替换。S13 按指定的五段逻辑替换，保留三支向下箭头；增补末段“连续做深 / Westlake Physics · 定导培养”文本框。只为容纳新文案，在这两页内调整文字框大小、行距、少量字号与箭头位置。标题、栏目、页脚和页码的 XML 与底稿完全一致，白底与原海军蓝、青色及辅助灰配色沿用。

## 不变范围与来源

- PPTX 中只有 `slide14.xml`、`slide15.xml`、`notesSlide14.xml`、`notesSlide15.xml` 四个部件改变。
- S0–S11 共 13 个实体页的页面、备注 XML 逐字节保持；实际 PowerPoint 1080p 导出与底稿逐像素一致。
- 所有图片、母版、主题、版式和关系文件原样保留；无新增图片或页面，无压平整页截图。
- {checks['preservation']['unchanged_count']} 份既有文件哈希保持，PI README 为本轮明确更新的索引；A 线工作台另行更新。本人微调 v1、v5 母稿、其他单页包和旧 FULL_DRAFT 工作副本保留。

## 文字与备注核对

S12 的 8 行、S13 的 10 行指定正文逐句与 PPTX 和 PDF 文字层核对通过，未删句或改写。S12、S13 的备注保留 v5 对应章节全文，包括原有强调符号及翻页提示；全局试讲说明不并入逐页备注。v5 母稿没有改写。

PPTX、逐页备注文本和 PowerPoint 实际读回三方 15/15 匹配；S0–S11 备注与底稿逐字节保持。PPTX 全包文字未发现 INTERNAL / CANDIDATE / FULL DRAFT / REVIEW DRAFT 状态标记。

## 实际导出检查

Microsoft PowerPoint 16.0 以只读方式打开并导出。PPTX 与底稿在导出前后哈希不变；完整 PDF 为 15 页、16:9，字体全部嵌入。30 张全页 PNG 包含每页 3840×2160 和 1920×1080 两种分辨率。所有页的文字溢出和对象越界均为 0，未隐藏页面。

全套总览为 2976×3174，连续审阅长图为 1968×17640；另提供 S11→S12→S13 结尾连续图与可跳页 HTML 审阅入口。

## 人工视觉检查与边界

已以 1080p 完整查看 S12、S13，并检查全套 15 页总览。两页所有句子完整可读，段落间距清楚，箭头未压住文字；S12 的长句未被截断，S13 的学习方向与定导培养均完整显示。未改页由逐字节和逐像素比较验证保全。本轮没有重新评价其他页面的科学内容或改造旧截图。

真实会议投影、本人语速和停顿尚未实测；本轮未按分钟数裁剪 v5 备注。材料制作与导出不代表已发送或学校正式面试。本轮不合并 main、不发送材料，PR #15 保持 OPEN / no auto-merge。

## 复核文件

- [局部修改检查](局部修改检查.json)
- [PowerPoint 导出与检查](PowerPoint导出与检查.json)
- [交付验收](交付验收.json) · [保全检查](保全检查.json)
- [页码来源映射](页码与来源映射表.md) · [CSV](页码与来源映射表.csv)
- [制作前保全基线](制作前保全基线.json) · [交付文件清单](交付文件清单.json)
''',encoding='utf-8')
    (OUT/'制作源/README.md').write_text('''# v1.1 制作与复核

本轮使用已安装的 Python、python-pptx、lxml、Pillow、pywin32、PyMuPDF 和 Microsoft PowerPoint 16.0，未安装依赖。具体版本见 `运行环境.json`。

1. `build_v1_1.py` 从指定、哈希锁定的本人微调 v1 复制包，只编辑 S12/S13 的页面和备注四个 XML 部件。已有交付 PPTX 时拒绝覆盖；后续修订另建版本目录。
2. `render_v1_1.py` 只读打开 PPTX，以真实 PowerPoint 导出 PDF、全页 PNG，核对备注、溢出、越界及未改页面的像素一致性，生成审阅图与 HTML。
3. `finalize_v1_1.py` 核对用户指定文案、v5 备注、文件保全与导出尺寸，并写出交付报告、映射与文件清单。

上述脚本保留为本轮制作记录。不得对本人后续编辑的 PPTX 直接运行生成脚本；复现应在新的工作副本中进行。用 `python -B` 运行可避免产生缓存文件。
''',encoding='utf-8')

def inventory_and_links():
    def write_inventory():
        rows=[]
        for p in sorted(OUT.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts or p.name=='交付文件清单.json':continue
            rows.append({'path':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
        jwrite(OUT/'交付文件清单.json',rows)
        return len(rows)
    write_inventory()
    bad=[];links=0
    for p in OUT.rglob('*'):
        if p.suffix=='.html':refs=re.findall(r'(?:href|src)="([^"]+)"',p.read_text(encoding='utf-8'))
        elif p.suffix=='.md':refs=re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8'))
        else:continue
        for ref in refs:
            if ref.startswith(('#','http:','https:','mailto:')):continue
            target=ref.split('#')[0]
            if not target:continue
            links+=1
            if not (p.parent/target).exists():bad.append([p.relative_to(OUT).as_posix(),ref])
    assert not bad,bad
    jwrite(OUT/'检查证据/本地链接检查.json',{'checked_links':links,'missing':bad})
    return write_inventory()

if __name__=='__main__':
    rows,checks=final_checks()
    documentation(rows,checks)
    count=inventory_and_links()
    print(json.dumps({'PASS':True,'notes':15,'preserved_files':checks['preservation']['unchanged_count'],'inventory_files':count,'pptx_sha256':sha(DECK)},ensure_ascii=False))
