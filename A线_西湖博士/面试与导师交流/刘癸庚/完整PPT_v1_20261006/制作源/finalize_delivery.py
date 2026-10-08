"""Final validation and delivery documentation for the complete external-review deck."""
import csv, json, posixpath, re
from zipfile import ZipFile
from lxml import etree as E
from pptx import Presentation
from PIL import Image, ImageChops
import pymupdf
from merge_lossless import OUT, PI, ROOT, STEM, FULL, sha, sha_bytes, write_json, sections, NS, relpath, resolve, clean_slide_xml

REDACTED={'S0','S1','S8','S9-A','S9-B'}

def pdf_compare(rows):
    full=pymupdf.open(OUT/(STEM+'.pdf')); result=[]
    for row in rows:
        src_path=(PI/row['source']).with_suffix('.pdf')
        src=pymupdf.open(src_path)
        a=src[row['source_page']-1]; b=full[row['page']-1]
        ap=a.get_pixmap(matrix=pymupdf.Matrix(1,1),alpha=False)
        bp=b.get_pixmap(matrix=pymupdf.Matrix(1,1),alpha=False)
        assert (ap.width,ap.height)==(bp.width,bp.height)
        ia=Image.frombytes('RGB',(ap.width,ap.height),ap.samples)
        ib=Image.frombytes('RGB',(bp.width,bp.height),bp.samples)
        bbox=ImageChops.difference(ia,ib).getbbox()
        result.append({'page':row['page'],'logical':row['logical'],
            'source_pdf':str(src_path.relative_to(ROOT)),
            'same_size':a.rect==b.rect,'pdf_pixels_identical':bbox is None,
            'difference_bbox':bbox,'expected_status_redaction':row['logical'] in REDACTED,
            'same_extracted_text':a.get_text()==b.get_text()})
        src.close()
        if row['logical']=='S7':
            current_path=OUT/'检查证据'/'S7_当轮PowerPoint重新导出.pdf'
            current=pymupdf.open(current_path)
            cp=current[0].get_pixmap(matrix=pymupdf.Matrix(1,1),alpha=False)
            ci=Image.frombytes('RGB',(cp.width,cp.height),cp.samples)
            result[-1]['current_source_pdf']=current_path.relative_to(OUT).as_posix()
            result[-1]['current_source_pdf_pixels_identical']=ImageChops.difference(ci,ib).getbbox() is None
            result[-1]['current_source_pdf_text_identical']=current[0].get_text()==b.get_text()
            assert result[-1]['current_source_pdf_pixels_identical'] and result[-1]['current_source_pdf_text_identical']
            current.close()
    full.close(); return result

def validate(rows):
    baseline=json.loads((OUT/'制作前保全基线.json').read_text(encoding='utf-8'))
    preserved=[]
    for item in baseline['protected']:
        p=ROOT/item['path']; ok=p.exists() and p.stat().st_size==item['bytes'] and sha(p)==item['sha256']
        preserved.append({'path':item['path'],'unchanged':ok})
    assert all(x['unchanged'] for x in preserved)
    write_json(OUT/'保全检查.json',{'checked_files':len(preserved),'unchanged_files':sum(x['unchanged'] for x in preserved),'checks':preserved})
    pptx=OUT/(STEM+'.pptx'); prs=Presentation(pptx); secs=sections(); checks=[]
    with ZipFile(pptx) as z:
        names=set(z.namelist()); missing=[]; duplicate_ids=[]
        for part in names:
            if not part.endswith('.rels'): continue
            parent='' if part=='_rels/.rels' else posixpath.join(posixpath.dirname(posixpath.dirname(part)),posixpath.basename(part)[:-5])
            rels=E.fromstring(z.read(part)); ids=[r.get('Id') for r in rels]
            if len(ids)!=len(set(ids)): duplicate_ids.append(part)
            for rel in rels:
                if rel.get('TargetMode')=='External': continue
                target=resolve(parent,rel.get('Target'))
                if target not in names: missing.append({'part':part,'target':target})
        assert not missing and not duplicate_ids
        visual_assets=0; xml_same=0
        for row,s in zip(rows,prs.slides):
            key=row['logical']; n=row['page']; source=PI/row['source']
            with ZipFile(source) as src:
                sp=f'ppt/slides/slide{row["source_page"]}.xml'; op=row['output_slide_part']
                same=src.read(sp)==z.read(op)
                assert z.read(op)==clean_slide_xml(src.read(sp),key)[0]
                if key in REDACTED: assert not same
                else: assert same
                if same: xml_same+=1
                sr=E.fromstring(src.read(relpath(sp))); orr=E.fromstring(z.read(relpath(op)))
                dest={r.get('Id'):r for r in orr}
                for rel in sr:
                    if rel.get('Type').endswith('/notesSlide'): continue
                    outrel=dest[rel.get('Id')]
                    assert rel.get('Type')==outrel.get('Type')
                    if rel.get('TargetMode')=='External': assert rel.get('Target')==outrel.get('Target')
                    else:
                        assert src.read(resolve(sp,rel.get('Target')))==z.read(resolve(op,outrel.get('Target')))
                        visual_assets+=1
            notes=s.notes_slide.notes_text_frame.text
            external=(OUT/'逐页备注'/f'{n:02d}_{key}.md').read_text(encoding='utf-8').removesuffix('\n')
            actual=(OUT/'检查证据'/'PowerPoint备注读回'/f'{n:02d}_{key}.txt').read_text(encoding='utf-8')
            assert notes==external==secs[key]==actual
            assert not any(x in notes for x in ['INTERNAL','CANDIDATE','FULL DRAFT','REVIEW DRAFT'])
            checks.append({'page':n,'logical':key,'source_slide_xml_identical':same,
                'status_text_removed':key in REDACTED,'notes_exact_match_external_file':True,
                'specified_script_verbatim':True,'notes_chars':len(notes),
                'notes_sha256':sha_bytes(notes.encode('utf-8'))})
        status_hits=[n for n in names if n.endswith('.xml') and re.search(rb'INTERNAL|CANDIDATE|FULL DRAFT|REVIEW DRAFT',z.read(n),re.I)]
        external_media=[]
        for part in names:
            if not part.endswith('.rels'):continue
            for r in E.fromstring(z.read(part)):
                if r.get('TargetMode')=='External' and any(r.get('Type','').endswith('/'+t) for t in ['image','audio','video','oleObject']):external_media.append({'part':part,'target':r.get('Target')})
        assert not status_hits and not external_media
    comparisons=pdf_compare(rows)
    write_json(OUT/'PDF逐页比对.json',comparisons)
    render=json.loads((OUT/'PowerPoint实际导出与排版检查.json').read_text(encoding='utf-8'))
    assert render['notes_matches']==render['identical_outside_status_rectangles']==15
    assert render['text_overflow_count']==render['objects_outside_count']==render['image_ratio_failures']==0
    doc=pymupdf.open(OUT/(STEM+'.pdf'))
    assert len(doc)==15 and not re.search(r'INTERNAL|CANDIDATE|FULL DRAFT|REVIEW DRAFT','\n'.join(p.get_text() for p in doc),re.I)
    doc.close()
    pngs=[]
    for r in rows:
        for width,height in [(1920,1080),(3840,2160)]:
            p=OUT/'预览'/f'{r["page"]:02d}_{r["logical"]}_{width}x{height}.png'
            with Image.open(p) as im:assert im.size==(width,height)
            pngs.append({'path':p.relative_to(OUT).as_posix(),'width':width,'height':height,'sha256':sha(p)})
    assert all(x['same_size'] for x in comparisons)
    assert all(x['pdf_pixels_identical'] or x.get('current_source_pdf_pixels_identical',False) for x in comparisons if not x['expected_status_redaction'])
    assert all((not x['pdf_pixels_identical']) for x in comparisons if x['expected_status_redaction'])
    report={'status':'PASS','protected_files_unchanged':len(preserved),
        'slide_xml_identical_unredacted':xml_same,'status_redaction_pages':sorted(REDACTED),
        'visual_relationship_targets_byte_identical':visual_assets,
        'missing_package_targets':missing,'duplicate_relationship_ids':duplicate_ids,
        'notes_checks':checks,'status_marker_hits':status_hits,'external_media':external_media,'png_files':pngs,'pdf_pages_pixel_identical_to_source_pdfs_unredacted':sum((x['pdf_pixels_identical'] or x.get('current_source_pdf_pixels_identical',False)) and not x['expected_status_redaction'] for x in comparisons),
        'pptx_sha256':sha(pptx),'pdf_sha256':sha(OUT/(STEM+'.pdf'))}
    write_json(OUT/'交付验收.json',report); return report

def docs(rows,validation):
    render=json.loads((OUT/'PowerPoint实际导出与排版检查.json').read_text(encoding='utf-8'))
    build=json.loads((OUT/'合并结构检查.json').read_text(encoding='utf-8'))
    fonts=sorted({f['font'].split('+')[-1] for p in render['pdf_pages'] for f in p['font_embedding']})
    assert all(f['embedded'] for p in render['pdf_pages'] for f in p['font_embedding'])
    table=['# 页码 → 来源版本映射表','','2026-10-06｜完整 PPT v1。共 15 张实体幻灯片、14 个逻辑主题；S9-A/B 连续保留。',
      '','| PPT/PDF 实体页 | 逻辑主题 | 页面来源 | 来源内页 | Speaker notes |','|---:|---|---|---:|---|']
    for r in rows:
        label=r['source'].split('/')[0]
        if r['logical']=='S10': label+=' · 方案 A'
        table.append(f'| {r["page"]} | {r["logical"]} | [{label}](../{r["source"]}) | {r["source_page"]} | [{r["notes_source"]}](逐页备注/{r["page"]:02d}_{r["logical"]}.md) |')
    table += ['', '页面源文件、页 XML、备注和输出文件的 SHA-256 见[机器可读映射](页码与来源映射.json)。页面中原有的状态文字已从输出页面移除；科学术语和结果标签保持原样。',
      '', '讲稿基准：[完整讲稿_最新合并版_v3_20261006.md](../'+FULL.name+')；15 页备注逐页取自该文件对应章节。']
    (OUT/'页码与来源映射表.md').write_text('\n'.join(table)+'\n',encoding='utf-8')
    with (OUT/'页码与来源映射表.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['page','logical','source','source_page','notes_source','source_sha256','source_slide_xml_sha256','notes_sha256']); w.writeheader(); w.writerows({k:r[k] for k in w.fieldnames} for r in rows)
    per_page=['| 实体页 | 主题 | 原对象数 | 文字溢出 | 对象越界 | 与来源图像 | 备注匹配 |','|---:|---|---:|---:|---:|---|---|']
    red=set(REDACTED)
    for r in rows:
        pix='状态文字移除后不同' if r['logical'] in red else '逐像素相同'
        per_page.append(f'| {r["page"]} | {r["logical"]} | {r["shape_count"]} | 0 | 0 | {pix} | 是 |')
    report=f'''# 完整 PPT v1 合并检查报告

2026-10-06｜验收：**PASS**

## 结果与范围

输入基线为当前分支 HEAD `{build["source_head"]}`；全部 11 份页面源 PPTX 及指定 v3 讲稿均已逐字节对照 HEAD。PR 状态的只读快照见 [PR15状态.json](检查证据/PR15状态.json)。

完整合并 15 张实体幻灯片，顺序为 S0、S1、S2–S5、S6、S7、S8、S9-A、S9-B、S10、S11、S12、S13。S10 使用方案 A；S9 两帧连续保留。页面部件、图片资源、版式和可编辑对象直接从指定版本组合，没有把页面截图替代为图片。

采用 S0 v1、S1 v2、S2–S5 正式版 v0.1、S6 v1、S7 v2 A、S8 v3.1、S9 v3.1 A/B、S10 v2 A、S11 v2、S12 v2.1、S13 v2。

S0、S1、S8、S9-A、S9-B 的页面状态文字已移除；其余页面 XML 与来源逐字节相同。移除状态文字没有改变图片资源、放置和页面尺寸。为避免母版 ID 冲突，单独保留 S2–S5 正式版的页面母版、分配唯一 ID；备注页统一采用一份备注母版。图片与页面直接引用的视觉资源逐字节保持。全部 15 页的 speaker notes 均来自 `{FULL.name}` 对应章节，PowerPoint 实际读回与外置逐页备注完全匹配。

## PowerPoint 实测

- Microsoft PowerPoint 16.0 实际打开并导出 PDF、1080p 和 4K PNG；完整 PDF 为 15 页、16:9。
- 文字溢出、对象越界、图片比例异常均为 0；字体在 PDF 中保持嵌入。
- 9 个未改动页与归档源 PDF 逐像素相同；S7 与本轮从同一源 PPTX 重新导出的 PDF 逐像素相同。S7 归档 PDF 存在约 0.123% 像素差异，文字内容相同；重新导出复核确认该差异并非本次合并引入。详见 [S7 PDF 差异复核](检查证据/S7_PDF差异复核.json)。5 个状态文字移除页在 PowerPoint PNG 中均只在允许的文字框范围内变化。
- PPTX 导出前后 SHA-256 不变，内部关系无缺失目标或重复关系 ID。

## Speaker notes 核对

逐页外置备注、PPTX 备注文本和 PowerPoint 实际读回三方 **15/15 通过**。全部页面均以用户指定的 **v3 合并讲稿**为唯一备注来源，不以单页包内旧备注替代。S9 在原文 `〔切 S9-B〕` 之后分到 B 页，A/B 拼接可还原该节全文，没有双份朗读或漏段。讲稿顶部的全局状态与末尾全局试讲清单不属于逐页讲稿，不写入备注；章节内原文、事实边界、强调符号和翻页提示完整保留。v4 文件虽在 HEAD 中，但未采用，v3 和 v4 原文件均保持不变。

## 逐页结果

{chr(10).join(per_page)}

## 文件保全与格式

{validation['protected_files_unchanged']} 份既有文件 SHA-256 保持，包含接手时已修改的旧完整稿工作副本；该副本未被覆盖或加入本轮提交。保留全部源页包用于溯源，未移动正在使用的稿件。{build['objects']} 个页面对象保留；正文文字、图形和线条仍可编辑，原始截图内部文字仍为图片。30 张 PNG 为 15 页 × 两种分辨率（3840×2160、1920×1080）。连续审阅图为 1968×17640，另有 3×5 总览与本地 HTML 翻页入口。

PDF 是页面版，不包含 speaker notes；备注在 PPTX 和逐页文本中。PDF 字体嵌入通过；图件无外链，PPTX 全包和 PDF 文字扫描均无内部状态标记。保留“内部场分布”“GA 提候选”等正常科研用语。

## 目视检查与使用边界

逐页视觉记录见 [人工视觉检查.md](人工视觉检查.md)。页面顺序、主图、标题、图注、转场及 S9 两帧已检查；S6 细线、S8/S9 原型截图中的细字和 S11 暗色网页的现场投影可读性尚未经真实会议环境测试。长备注保留全文，不按时长删节；本人自然试讲仍待完成。

## 交付边界

本目录是可供本人核看的外发候选版；本轮不发送材料、不提交系统、不改变 PI 联系状态。原单页版本、旧完整稿和科研原件均保留。PR #15 保持 OPEN / no auto-merge；不合并 main。

## 可复核证据

- [页码与来源映射](页码与来源映射表.md) / [CSV](页码与来源映射表.csv) / [JSON](页码与来源映射.json)
- [PowerPoint 实际导出与排版检查](PowerPoint实际导出与排版检查.json)
- [PDF 逐页比对](PDF逐页比对.json)
- [交付验收](交付验收.json) / [制作前保全基线](制作前保全基线.json) / [保全检查](保全检查.json)
- [文件清单与哈希](交付文件清单.json)
'''
    (OUT/'合并检查报告.md').write_text(report,encoding='utf-8')
    readme=f'''# 刘癸庚交流｜完整 PPT v1

2026-10-06｜完整外发候选版，15 张实体幻灯片、14 个逻辑主题；S9-A/B 连续、S10 方案 A。页面状态文字已移除，备注按最新 v3 合并讲稿逐页写入。

## 交付

1. [完整可编辑 PPTX]({STEM}.pptx)
2. [Microsoft PowerPoint 16.0 实际导出 PDF]({STEM}.pdf)
3. [4K / 1080p 全页 PNG 入口](预览/连续审阅.html) · [总览](预览/全部15页_总览.png) · [连续审阅图](预览/全部15页_连续审阅_纵向.png) · [可跳页审阅](预览/连续审阅.html)
4. [页码 → 来源映射](页码与来源映射表.md) · [CSV](页码与来源映射表.csv)
5. [合并检查报告](合并检查报告.md)

## 验收

15/15 页备注与 `{FULL.name}` 对应章节逐字匹配；文字溢出、对象越界、图片比例异常均为 0。5 页按要求移除页面状态文字，其余页面与来源渲染逐像素相同。完整 deck 未发送，PR #15 保持 OPEN / no auto-merge，未合并 main。
'''
    (OUT/'README.md').write_text(readme,encoding='utf-8')

def inventory():
    files=[p for p in OUT.rglob('*') if p.is_file() and p.name!='交付文件清单.json' and '__pycache__' not in p.parts]
    write_json(OUT/'交付文件清单.json',[{'path':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)])

if __name__=='__main__':
    rows=json.loads((OUT/'页码与来源映射.json').read_text(encoding='utf-8'))
    result=validate(rows); docs(rows,result); inventory()
    print(json.dumps({k:v for k,v in result.items() if k not in ('notes_checks','png_files')},ensure_ascii=False),flush=True)
