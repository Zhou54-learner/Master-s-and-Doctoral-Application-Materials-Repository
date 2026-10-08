"""Preserve old candidates; archive supplied screenshot and recover one intact ZIP member.
No old recovery script is executed. No full ZIP is written or uploaded.
"""
from pathlib import Path
import base64,hashlib,io,json,struct,zlib,shutil,subprocess
from PIL import Image

REVIEW=Path(__file__).resolve().parent.parent
PI=REVIEW.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
FACTS=ROOT/'公共资料/事实核验/个人探索_20261006'
PACK=ROOT/'公共资料/面试与导师交流中心/公共主干/面试素材/Personal_Explorations_20261004'
NAMES={'S10':'S10_反思_v2_20261006','S11':'S11_表达_v2_20261006','S12':'S12_WhyPhD_v2_20261006','S13':'S13_WhyLiu_v2_20261006'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rec(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')

assert not FACTS.exists() and all(not (PI/n).exists() for n in NAMES.values()), 'New directories only.'
protected=[p for d in PI.iterdir() if d.is_dir() and d!=REVIEW and
           (d.name.startswith(('S0_','S1_','S6_','S7_','S8_','S9_','S10_','S11_','S12_','S13_',
                               '本科毕设_S2-S5_','新增候选页_联合审阅_v1_')))
           for p in sorted(d.rglob('*')) if p.is_file()]
sources=[PI/n for n in ['S10-S13_v2制作指令_20261006.md','S10-S13_重构提案_v2_20261006.md',
                        'Why_PhD母稿_用户原文_20261005.md','S13_WhyWestlake-Liu_最终口述_20261005.md',
                        '完整主线与明日问答训练框架_20261005.md','完整讲稿_当前定稿内容合并版_v1_20261005.md']]
sources += [p for p in sorted(PACK.rglob('*')) if p.is_file()]
sources += [p for p in sorted((ROOT/'公共资料/事实核验/个人探索_20261004').rglob('*')) if p.is_file()]
unrelated=[ROOT/'公共资料/面试与导师交流中心/公共主干'/n for n in
           ['README.md','项目重建/本科毕设/README.md','项目重建/本科毕设/13_实际工作梳理与研究叙事底稿.md']]
baseline=dict(date='2026-10-06',base_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),
              protected_candidates=[rec(p) for p in protected],sources=[rec(p) for p in sources],unrelated=[rec(p) for p in unrelated])
write(REVIEW/'制作前保全基线.json',baseline)
(FACTS/'素材').mkdir(parents=True)
(FACTS/'制作源').mkdir()
attachment=Path('C:/Users/zzj/AppData/Local/Temp/codex-clipboard-5368a3e1-ba9c-4ec9-bea9-a42e6e173e18.jpg')
copy=FACTS/'素材/公众号首篇文章_用户补图_20261006.jpg'
shutil.copyfile(attachment,copy);assert sha(copy)==sha(attachment)
attachment_record=dict(source=str(attachment),copy=copy.relative_to(ROOT).as_posix(),bytes=copy.stat().st_size,
                       sha256=sha(copy),pixels=list(Image.open(copy).size),operation='Original bytes copied; no image edits.')

# The four legacy Base64 parts cannot reconstruct the full archive. Recover ONLY a
# complete member from part04, checking its local header and central directory CRC.
parts=sorted((PACK/'packed').glob('part*.b64'))
joined=''.join(p.read_text().strip() for p in parts)
assert len(joined)%4==1
raw=parts[-1].read_text().strip()[3:]
fragment=base64.b64decode(raw,validate=True)
offset=fragment.index(b'PK\x03\x04')
h=struct.unpack_from('<4s5H3I2H',fragment,offset)
name=fragment[offset+30:offset+30+h[9]].decode('utf8')
assert name=='images/07_personal_site_uselessdream.jpg'
assert h[2]==0 and h[3]==8
start=offset+30+h[9]+h[10]
data=zlib.decompress(fragment[start:start+h[7]],-15)
assert len(data)==h[8] and zlib.crc32(data)==h[6]
central=None;pos=fragment.find(b'PK\x01\x02')
while pos>=0:
    c=struct.unpack_from('<4s6H3I5H2I',fragment,pos)
    nm=fragment[pos+46:pos+46+c[10]].decode('utf8')
    if nm==name:central=c;break
    pos=fragment.find(b'PK\x01\x02',pos+46+c[10]+c[11]+c[12])
assert central is not None and (central[7],central[8],central[9])==(h[6],h[7],h[8])
im=Image.open(io.BytesIO(data));im.load()
home=FACTS/'素材/个人艺术网页首页_workcopy600.jpg';home.write_bytes(data)
recovery=dict(source_pack=PACK.relative_to(ROOT).as_posix(),parts=[rec(p) for p in parts],
              whole_archive_status='NOT RECONSTRUCTABLE: 74997 Base64 chars, length modulo 4 is 1; original ZIP SHA cannot be verified.',
              expected_whole_zip_sha256='70f1a46f4b91207f4eb81f301624eacc7c6b7cd1ada66aa7f44dd068d793169b',
              method='Read part04 only, discard first 3 chars to align complete Base64 groups; decode remaining fragment. Extract one complete raw-deflate member. Compare local header and central-directory sizes and CRC32. Never execute legacy recovery script.',
              fragment_local_header_offset=offset,member=name,compressed_bytes=h[7],uncompressed_bytes=h[8],
              crc32=f'{h[6]:08x}',local_crc_matches=True,central_crc_matches=True,
              output=home.relative_to(ROOT).as_posix(),output_sha256=sha(home),pixels=list(im.size),
              quality='Legacy 600 px compressed workcopy; no high-resolution original recovered; no synthetic upscaling.')
write(FACTS/'来源与恢复核验.json',dict(date='2026-10-06',attachment=attachment_record,homepage=recovery))
for key,dirname in NAMES.items():
    out=PI/dirname
    for sub in ['制作源','派生素材','预览']:(out/sub).mkdir(parents=True,exist_ok=False)
    write(out/'来源与保全.json',baseline)
    write(out/'制作源/config.json',dict(slide=key,stem=dirname.rsplit('_20261006',1)[0]))
write(REVIEW/'候选目录.json',NAMES)
print(json.dumps(dict(archived=attachment_record,homepage=recovery,protected_files=len(protected),source_files=len(sources)),ensure_ascii=False))
