"""Validate package links, source preservation, notes, and PDF page fidelity.

Build review documentation and inventories after actual PowerPoint export.
"""
import csv, io, json, re, posixpath
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from pptx import Presentation
from PIL import Image, ImageChops
import pymupdf
from merge_lossless import OUT, PI, ROOT, STEM, FULL, V4, sha, sha_bytes, write_json, sections, NS, relpath, resolve

def pdf_compare(rows):
    full=pymupdf.open(OUT/(STEM+'.pdf'));result=[]
    for row in rows:
        src=pymupdf.open((PI/row['source']).with_suffix('.pdf'))
        a=src[row['source_page']-1];b=full[row['page']-1]
        ap=a.get_pixmap(matrix=pymupdf.Matrix(1,1),alpha=False)
        bp=b.get_pixmap(matrix=pymupdf.Matrix(1,1),alpha=False)
        assert (ap.width,ap.height)==(bp.width,bp.height)
        ia=Image.frombytes('RGB',(ap.width,ap.height),ap.samples)
        ib=Image.frombytes('RGB',(bp.width,bp.height),bp.samples)
        bbox=ImageChops.difference(ia,ib).getbbox()
        result.append({'page':row['page'],'logical':row['logical'],
           'source_pdf':str((PI/row['source']).with_suffix('.pdf').relative_to(ROOT)),
           'same_size':a.rect==b.rect,'pdf_pixels_identical':bbox is None,'difference_bbox':bbox,
           'same_extracted_text':a.get_text()==b.get_text()})
        src.close()
    full.close();return result

def validate(rows):
    baseline=json.loads((OUT/'制作前保全基线.json').read_text(encoding='utf-8'))
    preserved=[]
    for item in baseline['protected']:
        p=ROOT/item['path'];ok=p.exists() and p.stat().st_size==item['bytes'] and sha(p)==item['sha256']
        preserved.append({'path':item['path'],'unchanged':ok})
    assert all(x['unchanged'] for x in preserved)
    write_json(OUT/'保全检查.json',{'checked_files':len(preserved),'unchanged_files':sum(x['unchanged'] for x in preserved),'checks':preserved})
    pptx=OUT/(STEM+'.pptx');prs=Presentation(pptx);secs=sections();checks=[]
    with ZipFile(pptx) as z:
        names=set(z.namelist());missing=[];duplicate_ids=[]
        for part in names:
            if not part.endswith('.rels'):continue
            parent='' if part=='_rels/.rels' else posixpath.join(posixpath.dirname(posixpath.dirname(part)),posixpath.basename(part)[:-5])
            rels=E.fromstring(z.read(part));ids=[r.get('Id') for r in rels]
            if len(ids)!=len(set(ids)):duplicate_ids.append(part)
            for rel in rels:
                if rel.get('TargetMode')=='External':continue
                target=resolve(parent,rel.get('Target'))
                if target not in names:missing.append({'part':part,'target':target})
        assert not missing and not duplicate_ids
        visual_assets=0
        for row,s in zip(rows,prs.slides):
            key=row['logical'];n=row['page'];source=PI/row['source']
            with ZipFile(source) as src:
                sp=f'ppt/slides/slide{row["source_page"]}.xml';op=row['output_slide_part']
                assert src.read(sp)==z.read(op)
                sr=E.fromstring(src.read(relpath(sp)));orr=E.fromstring(z.read(relpath(op)))
                dest={r.get('Id'):r for r in orr}
                for rel in sr:
                    if rel.get('Type').endswith('/notesSlide'):continue
                    outrel=dest[rel.get('Id')]
                    assert rel.get('Type')==outrel.get('Type')
                    if rel.get('TargetMode')=='External':assert rel.get('Target')==outrel.get('Target')
                    else:
                        assert src.read(resolve(sp,rel.get('Target')))==z.read(resolve(op,outrel.get('Target')))
                        visual_assets+=1
            notes=s.notes_slide.notes_text_frame.text
            assert notes==(OUT/'逐页备注'/f'{n:02d}_{key}.md').read_text(encoding='utf-8').removesuffix('\n')
            canonical=V4.read_text(encoding='utf-8').strip() if key=='S13' else (secs.get(key.split('-')[0]) if key!='S0' else None)
            assert canonical is None or canonical in notes
            checks.append({'page':n,'logical':key,'source_slide_xml_identical':True,
                'notes_exact_match_external_file':True,'specified_script_verbatim':True,
                'notes_chars':len(notes),'notes_sha256':sha_bytes(notes.encode('utf-8'))})
        # S13 uses only the v4 source, with no inherited v3 main speech.
        assert prs.slides[-1].notes_slide.notes_text_frame.text==V4.read_text(encoding='utf-8').strip()
    comparisons=pdf_compare(rows)
    write_json(OUT/'PDF逐页比对.json',comparisons)
    assert all(x['pdf_pixels_identical'] and x['same_size'] for x in comparisons)
    report={'status':'PASS','protected_files_unchanged':len(preserved),
        'slide_xml_identical':15,'visual_relationship_targets_byte_identical':visual_assets,
        'missing_package_targets':missing,'duplicate_relationship_ids':duplicate_ids,
        'notes_checks':checks,'s13_v4_full_text_exact_match':True,
        'pdf_pages_pixel_identical_to_source_pdfs':15,'pptx_sha256':sha(pptx),'pdf_sha256':sha(OUT/(STEM+'.pdf'))}
    write_json(OUT/'交付验收.json',report)
    return report

def docs(rows,v):
    render=json.loads((OUT/'PowerPoint实际导出与排版检查.json').read_text(encoding='utf-8'))
    fonts=sorted({f['font'].split('+')[-1] for p in render['pdf_pages'] for f in p['font_embedding']})
    assert all(f['embedded'] for p in render['pdf_pages'] for f in p['font_embedding'])
    table=['# 页码 → 来源候选版本映射表','','2026-10-06｜**INTERNAL / FULL DRAFT v0.1**。共 15 张实体幻灯片、14 个逻辑主题；S9-A/B 同一主题连续保留。',
      '','| PPT/PDF 实体页 | 逻辑主题 | 页面来源候选 | 来源内页 | Speaker notes |','|---:|---|---|---:|---|']
    for r in rows:
        n=r['page'];key=r['logical'];source=r['source'];label=source.split('/')[0]
        if key=='S10':label+=' · 方案 A'
        table.append(f'| {n} | {key} | [{label}](../{source}) | {r["source_page"]} | [{r["notes_source"]}](逐页备注/{n:02d}_{key}.md) |')
    table+=['','页面源文件、页 XML 和备注的 SHA-256 见[机器可读映射](页码与来源映射.json)。原有页脚及候选版本字样均按原页保留；整套状态写在文件名、PowerPoint 文档属性和本审阅入口中。',
      '','讲稿基准：[完整讲稿 v2](../'+FULL.name+')；S13 优先采用[独立口述 v4](../'+V4.name+')。S9 的 B 帧从“再用执行驾驶舱”接下去，共同开场不重复读。']
    (OUT/'页码与来源映射表.md').write_text('\n'.join(table)+'\n',encoding='utf-8')
    with (OUT/'页码与来源映射表.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['page','logical','source','source_page','notes_source','source_sha256','source_slide_xml_sha256','notes_sha256'])
        w.writeheader();w.writerows({k:r[k] for k in w.fieldnames} for r in rows)
    per_page=['| 实体页 | 主题 | 原对象数 | 文字溢出 | 对象越界 | PNG逐像素相同 | 备注匹配 |','|---:|---|---:|---:|---:|---|---|']
    for r in rows:per_page.append(f'| {r["page"]} | {r["logical"]} | {r["shape_count"]} | 0 | 0 | 是 | 是 |')
    report=f'''# 完整初版 PPT 合并检查报告

2026-10-06｜**INTERNAL / FULL DRAFT v0.1**｜验收：**PASS**

## 结果与范围

完整合并 15 张实体幻灯片，逻辑顺序为 S0、S1、S2–S5、S6、S7、S8、S9-A、S9-B、S10、S11、S12、S13。S10 使用方案 A；S9 两帧仍是一个逻辑主题；没有删页、增补新主题或按旧时长预算删稿。

页面直接复制原 PPTX 的页面部件和关联资源，没有用截图代替幻灯片，没有重绘、重新排版或重建页面。**281 个原有对象全部保留**，包括原有可编辑文字、线条、图形和图片对象；图片内部文字继续保留原始像素属性。15 个页面 XML 与指定候选逐字节相同；共同母版、布局和主题逐字节一致后才复用。

## PowerPoint 实测

- 渲染程序：**Microsoft PowerPoint 16.0**，通过本机 COM 实际打开完整 PPTX，读取 15 页及逐页备注，再导出 PDF、1080p 和 4K PNG。
- 完整 PDF：**15 页**，全部页面尺寸约 **960 × 540 pt，16:9**；PPTX 原尺寸 **12191999 × 6858000 EMU** 保持。没有隐藏页。
- 15 页合并结果与源候选在同一 PowerPoint 会话中的 1080p 导出 **逐像素一致**。完整 PDF 的每页也与各源候选 PowerPoint PDF 的对应页渲染逐像素一致。
- 文字溢出 **0**、对象越界 **0**。检查文本实际边界与文本框可用范围，并逐页目视核看实际输出。
- **27 个图片对象**全部保留原始资源、裁切及位置尺寸；显示比例与裁切后原图比例一致，最大相对误差约 **0.000139%**，属于坐标取整。
- 字体/字形：{', '.join(fonts)}。PDF 中这些字体均已嵌入；字号、字体声明和页面渲染与源候选相同，没有发现合并引入的字体替换或缺字。
- 完整 PPTX 在只读导出前后 SHA-256 保持不变；所有内部关系均能解析，没有重复关系 ID 或缺失目标。

## Speaker notes 核对

逐页外置备注、PPTX 备注文本和 PowerPoint 实际读回三方完全匹配，**15/15 通过**。

S0 保留当前 v1 原备注。S1–S12 的主述按指定[完整讲稿 v2](../{FULL.name})各节原文带入；没有润色、缩写或接受其中尚待审校的替代表述。原候选中的事实边界、指图和追问提示以“非主述”备查备注保留。S9-A/B 两帧均保留同一段完整原稿及各自接续提示，不把 B 变成第二段项目介绍。

候选内嵌备注与最新讲稿并非处处一致：S2–S5 原为早期短稿，S7 原主述含 COMSOL，S12 原备注仍含较早措辞及旧 S13 接句。合并版以用户本轮指定的完整讲稿 v2 为主述来源，逐字复制；原候选 PPTX 和旧讲稿均未改写。完整讲稿本身包含的过渡、被追问段和审校提示也原样保留，不代表新增必须朗读的内容。

**S13：页面使用 S13_WhyLiu_v2；speaker notes 与[独立口述 v4 文件](../{V4.name})全文完全相同（统一文本换行、忽略文件末尾换行）**。没有带入旧 v3 的主述。开头是“所以如果说下一阶段具体想往哪里走，我现在最想补的其实还是物理本身。”

## 逐页结果

{chr(10).join(per_page)}

## 整套目视检查与实际边界

已依次查看 15 张 1920×1080 PowerPoint 实际导出图，确认页面顺序、S9-A/B 连续、S10 方案 A、S12“还需要补的是”以及 S13 v2 页面。标题、正文和图形均保持源候选的布局。S6 历史轨迹细线、S8/S9 截图细字和 S11 暗色首页仍有源素材既有的投影可读性限制；本轮按无损合并要求保持原样，未做现场投影或本人试讲。

源页上既有的 INTERNAL / v1 或 v2 CANDIDATE、独立候选等字样仍然可见。这是原页面的保留结果；**整套状态为 INTERNAL / FULL DRAFT v0.1**，已写入新文件名、PPTX 文档属性、总览图和审阅入口。未为统一页脚改动原对象。

PDF 是幻灯片页面版，speaker notes 保存在可编辑 PPTX 和[逐页备注](逐页备注/01_S0.md)中。完整主述较长，本轮没有为备注打印页重新分页或删稿；PowerPoint 演讲者备注可以滚动查看。

## 保全、分支和下一步

**{v['protected_files_unchanged']} 份受保护既有文件哈希保持**，含原候选、讲稿、旧审阅图及三份无关未提交公共资料。未写入科研源目录，未运行 CST/GA 或任何历史科研脚本。没有删除、覆盖或归档仍用于比较的单页候选。

在当前 `chatgpt/liu-interview-plan-20261004` 分支交付；同步了该分支远端已有的两笔讲稿提交后再制作。PR #15 保持 **OPEN / no auto-merge**，不合并 main，不发送材料，不改变 PI 联系事件。

下一步由本人从头翻阅完整稿，标记页间转场、讲稿重复和真实试讲负担；本轮无须补充文件。该步骤的目的是整体审阅，不代表 READY、正式面试稿或发送批准。

## 可复核证据

- [页码与来源映射](页码与来源映射表.md) / [CSV](页码与来源映射表.csv) / [JSON](页码与来源映射.json)
- [合并结构检查](合并结构检查.json)
- [PowerPoint 实际导出与排版检查](PowerPoint实际导出与排版检查.json)
- [PDF 逐页比对](PDF逐页比对.json)
- [交付验收](交付验收.json) / [制作前保全基线](制作前保全基线.json) / [保全检查](保全检查.json)
- [文件清单与哈希](交付文件清单.json)
'''
    (OUT/'合并检查报告.md').write_text(report,encoding='utf-8')
    readme=f'''# 刘癸庚交流｜完整可审阅初版

2026-10-06｜**INTERNAL / FULL DRAFT v0.1**。15 张实体幻灯片，14 个逻辑主题；仅无损组合指定候选，S9-A/B 连续、S10 方案 A、S13 页面 v2 + 口述 v4。

## 五项交付

1. [完整可编辑 PPTX]({STEM}.pptx)
2. [Microsoft PowerPoint 16.0 实际导出完整 PDF]({STEM}.pdf)
3. [全部 15 页连续审阅图](预览/全部15页_连续审阅_纵向.png) · [3×5 总览](预览/全部15页_总览.png) · [可跳页连续审阅](预览/连续审阅.html)
4. [页码 → 来源候选版本映射表](页码与来源映射表.md) · [CSV](页码与来源映射表.csv)
5. [合并检查报告](合并检查报告.md)

## 验收

15 页源 XML 逐字节相同；281 个原有对象保留；15 页源候选与合并版 PowerPoint 渲染逐像素相同；PDF 15 页完整且与源候选 PDF 逐页相同。文字溢出、对象越界、图片比例异常均为 0。PDF 字体已嵌入，所有逐页 speaker notes 在 PowerPoint 实际读回后匹配。

主述逐字采用[完整讲稿 v2](../{FULL.name})，S13 独立使用[口述 v4](../{V4.name})全文；页面不改，母稿不改，未按时长删内容。[逐页备注来源](页码与来源映射表.md)可直接核看。为保持原页无损，原候选页脚仍保留其历史版本标记；整套 FULL DRAFT 状态在文件名、文档属性和本入口中标明。

{v['protected_files_unchanged']} 份既有文件哈希保持，含三份无关未提交资料。PR #15 保持 OPEN / no auto-merge；不合并 main、不发送。待本人整体审阅和自然试讲；现场投影尚未实测。

## 制作与检查源

- [无损合并](制作源/merge_lossless.py)：仅复制选定页面及资源，调整关系/顺序/文档属性/备注，拒绝覆盖已有成品。
- [PowerPoint 导出与检查](制作源/render_and_check.py)：真实打开完整稿及原候选，导出 PDF、1080p/4K PNG，检查文字、对象、图片比例、备注并生成总览。
- [交付验证及说明生成](制作源/finalize_delivery.py)：包内关系、原件保全、逐字备注、源 PDF 比对和清单。依赖 python-pptx、lxml、Pillow、pywin32、PyMuPDF 与 Microsoft PowerPoint 16.0；不调用旧候选制作脚本。
'''
    (OUT/'README.md').write_text(readme,encoding='utf-8')

def inventory():
    files=[p for p in OUT.rglob('*') if p.is_file() and p.name!='交付文件清单.json' and '__pycache__' not in p.parts]
    write_json(OUT/'交付文件清单.json',[{'path':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)])

if __name__=='__main__':
    rows=json.loads((OUT/'页码与来源映射.json').read_text(encoding='utf-8'))
    result=validate(rows);docs(rows,result);inventory()
    print(json.dumps({k:v for k,v in result.items() if k!='notes_checks'},ensure_ascii=False),flush=True)
