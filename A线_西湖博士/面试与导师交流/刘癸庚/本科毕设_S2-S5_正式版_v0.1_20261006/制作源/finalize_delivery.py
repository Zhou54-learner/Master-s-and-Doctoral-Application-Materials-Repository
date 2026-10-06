"""Generate the formal-version archive index and final checks."""
from pathlib import Path
from zipfile import ZipFile
from pptx import Presentation
import hashlib, json, re, subprocess

OUT = Path(__file__).resolve().parents[1]
PI = OUT.parent
ROOT = next(p for p in PI.parents if (p / '申请路线总览.md').exists())
SOURCE = PI / 'FULL_DRAFT_v0.1_20261006' / '刘癸庚交流_INTERNAL_FULL_DRAFT_v0.1_20261006.pptx'
TARGET = OUT / '本科毕设_S2-S5_正式版_v0.1.pptx'
PDF = OUT / '本科毕设_S2-S5_正式版_v0.1.pdf'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def check():
    assert TARGET.exists() and PDF.exists()
    source_hash = sha(SOURCE)
    registration = json.loads((OUT / '来源与版本登记.json').read_text(encoding='utf-8'))
    report = json.loads((OUT / 'PowerPoint排版检查.json').read_text(encoding='utf-8'))
    assert registration['source_sha256'] == source_hash
    assert report['status'] == 'PASS'
    assert report['physical_slides'] == 4
    assert report['text_overflow_count'] == report['objects_outside_count'] == report['image_ratio_failures'] == 0
    assert report['notes_matches'] == report['source_render_pixel_identical'] == 4
    prs = Presentation(TARGET)
    assert len(prs.slides) == 4
    with ZipFile(SOURCE) as source, ZipFile(TARGET) as target:
        rows = []
        for page, source_page in enumerate(range(3, 7), start=1):
            sslide, oslide = f'ppt/slides/slide{source_page}.xml', f'ppt/slides/slide{page}.xml'
            snote, onote = f'ppt/notesSlides/notesSlide{source_page}.xml', f'ppt/notesSlides/notesSlide{page}.xml'
            assert source.read(sslide) == target.read(oslide)
            assert source.read(snote) == target.read(onote)
            rows.append({'page': page, 'logical': f'S{page + 1}', 'source_page': source_page,
                         'object_count': len(prs.slides[page - 1].shapes),
                         'notes_chars': len(prs.slides[page - 1].notes_slide.notes_text_frame.text),
                         'source_slide_xml_sha256': sha_bytes(source.read(sslide)),
                         'formal_slide_xml_sha256': sha_bytes(target.read(oslide)),
                         'source_notes_xml_sha256': sha_bytes(source.read(snote)),
                         'formal_notes_xml_sha256': sha_bytes(target.read(onote))})
    return source_hash, rows, report


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def write_docs(source_hash, rows, report):
    diff = '''# S2–S5 当前正式版本变更登记

2026-10-06｜**INTERNAL / FORMAL v0.1**

本版本从用户当前编辑中的完整稿直接抽取 S2–S5，作为目前本科毕设四页的正式留档版本。页面对象、图片、字体、版式比例和 speaker notes 均来自当前完整稿；没有重绘或重新设计。旧 `本科毕设_S2-S5_v1_20261005`、`v2_20261005`、`v2.1_20261005` 全部保留为历史对照。

## 当前稿相对 v2.1 的页面可见变化

| 页 | 当前采用内容 |
|---|---|
| S2 | 移除页面底部来源说明；将“正入射 / 沿 −z”合并为“正入射沿 −z”；将结论行改为“反射要少 → 阻抗匹配 / 能量耗散在电阻膜中 → 欧姆耗散”。 |
| S3 | 移除页面底部来源说明和 Floquet/PEC 解释脚注；保留当前物理理解；去掉两处句号以适配页面文字。 |
| S4 | 标题改为“我如何决定下一步优化什么？”；压缩阶段文案；加入“提升效果出现瓶颈”“找到表现更好的结构后，再沿着这个思路继续细化”；保留“（细化电脑遭不住）”；片阻段改为“允许基于当前片阻的小区间做扫描”；工作流行保留 GA → Python → CST。 |
| S5 | 移除页面底部来源说明；将“把开放传播通道的功率 / 算清楚”合并为一行；将“结果可靠后，再解释 / 为什么会有宽带响应”合并为一行；删去页面内“尚不能认定为总吸收带宽”的小字，相关边界仍保留在 speaker notes 和完整讲稿中。 |

上述登记只记录页面可见变化，不把页面删减解释为科研事实边界变化。备注仍保留完整口述与备查边界，科研原件未改。

## 来源和隔离

- 来源完整稿：`../FULL_DRAFT_v0.1_20261006/刘癸庚交流_INTERNAL_FULL_DRAFT_v0.1_20261006.pptx`
- 来源 SHA-256：`{source_hash}`
- 来源页：完整稿第 3–6 页，对应 S2–S5。
- 当前完整稿仍是工作副本；本版本不反向覆盖完整稿。
- S0、S1、S6–S13 不进入本版本；等待其他页面最新版本完成后的明确合并指令。
- 未修改科研原件，未运行 CST/GA/MATLAB 历史脚本。
'''
    (OUT / 'S2-S5_当前正式版本变更登记.md').write_text(diff, encoding='utf-8')

    fonts = sorted({font for page in report['pdf_pages'] for font in page['fonts']})
    readme = f'''# 本科毕设 S2–S5｜当前正式留档版

2026-10-06｜**INTERNAL / FORMAL v0.1**

本目录保留用户当前编辑完整稿中的 S2–S5，作为目前本科毕设四页的正式版本。四页均为可编辑 PowerPoint 页面，原对象与当前修改原样保留。

## 交付

- [可编辑正式版 PPTX](本科毕设_S2-S5_正式版_v0.1.pptx)
- [PowerPoint 16.0 导出 PDF](本科毕设_S2-S5_正式版_v0.1.pdf)
- [四页连续总览](预览/四页总览.png)
- [S2 1920×1080](预览/S2_1920x1080.png) · [S3](预览/S3_1920x1080.png) · [S4](预览/S4_1920x1080.png) · [S5](预览/S5_1920x1080.png)
- [来源与版本登记](来源与版本登记.json)
- [当前正式版本变更登记](S2-S5_当前正式版本变更登记.md)
- [PowerPoint 排版检查](PowerPoint排版检查.json)
- [交付文件清单](交付文件清单.json)

## 验收结果

- 4 页实体幻灯片，16:9，PowerPoint 实际读取尺寸 960 × 540 pt。
- 溢出 0、对象越界 0、图片比例异常 0。
- 4/4 页 speaker notes 由 PowerPoint 16.0 实际读回并匹配。
- 4/4 页正式版与来源完整稿对应页的 PowerPoint PNG 渲染逐像素一致。
- 18 个图片对象均保留原始可编辑图片资源与裁切信息；PDF 字体已嵌入：{', '.join(fonts)}。
- 正式版 PPTX 在 PowerPoint 只读打开和导出前后 SHA-256 不变。

## 当前状态和后续合并规则

本目录是 **INTERNAL / FORMAL v0.1**，用于当前版本留档和审阅，不代表已发送或 READY。后续合并完整交流 PPT 时，应以本目录四页替换旧完整稿中的 S2–S5；在用户明确发出合并指令之前，不自动改写完整稿，也不把其他页面并入本目录。

S0、S1、S6–S13 保持在各自候选/工作版本中；本轮不处理它们。旧 v1/v2/v2.1 文件保留，不删除、不覆盖。

来源完整稿当前仍有未提交工作副本修改；本轮只推送本正式四页版本和索引，不推送完整稿工作副本本身。

## 制作源

- [抽取源](制作源/extract_current_s2s5.py)：只做 OPC 页面/备注抽取、关系重映射与文档属性更新，不重绘页面。
- [实际渲染检查](制作源/render_check.py)：使用 Microsoft PowerPoint 16.0 打开来源和正式版，导出 PDF/PNG，核对备注、边界、字体和渲染一致性。
- [交付收尾](制作源/finalize_delivery.py)：核对来源字节、生成登记和交付清单。
'''
    (OUT / 'README.md').write_text(readme, encoding='utf-8')

    mapping = {'status': 'INTERNAL / FORMAL v0.1', 'source_full_draft': str(SOURCE.relative_to(ROOT).as_posix()),
               'source_full_draft_sha256': source_hash, 'formal_pptx': TARGET.name,
               'formal_pptx_sha256': sha(TARGET), 'formal_pdf': PDF.name, 'formal_pdf_sha256': sha(PDF),
               'slides': rows, 'powerpoint_check': report}
    write_json(OUT / '正式版本验收.json', mapping)


def inventory():
    files = [p for p in OUT.rglob('*') if p.is_file() and p.name != '交付文件清单.json' and '__pycache__' not in p.parts]
    write_json(OUT / '交付文件清单.json', [{'path': p.relative_to(OUT).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in sorted(files)])


if __name__ == '__main__':
    source_hash, rows, report = check()
    write_docs(source_hash, rows, report)
    inventory()
    print(json.dumps({'status': 'PASS', 'slides': 4, 'formal_pptx_sha256': sha(TARGET), 'formal_pdf_sha256': sha(PDF)}, ensure_ascii=False), flush=True)
