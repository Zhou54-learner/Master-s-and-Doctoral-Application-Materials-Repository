"""Read-only provenance, anomalous data, and secondary-branch checks."""
from pathlib import Path
from collections import Counter
import json, hashlib, datetime, math, re
import numpy as np
from analyze_audio import OUT, OLD, SRC, save, writecsv, meta

rows=json.loads((OUT/'全量音频重分析.json').read_text(encoding='utf8'))
books=json.loads((OLD/'表格单元格与元数据.json').read_text(encoding='utf8'))
def cells(suffix):return {c['cell']:c['value'] for c in next(b for b in books if b['path'].endswith(suffix))['sheets'][0]['cells']}
archive=json.loads((OUT/'压缩包独有旧版汇总表核读.json').read_text(encoding='utf8'))[0]['archive_sheets'][0]['cells']
external=cells('/R11.6mm_r8.0mm/data3.xlsx');processing=cells('/数据处理/长度关系比较/data3.xlsx')
def nonempty(c):return {k:v for k,v in c.items() if v is not None}
archivecheck={'archive_vs_processing_same_nonempty_cells':nonempty(archive)==nonempty(processing),'external_column_values_same_order_as_archive':{col:[v for k,v in nonempty(archive).items() if re.fullmatch(col+r'\d+',k)]==[v for k,v in nonempty(external).items() if re.fullmatch(col+r'\d+',k)] for col in 'BCDE'},'external_80cm_starts_at':'D7','external_100cm_starts_at':'E12','archive_and_processing_both_start_at_row':2,'interpretation':'数值序列相同，外部家族汇总表移动了数据块；横向同一行不是经校准的相同气流。'}
save('汇总表版本与无效数据核对.json',{'archive':archivecheck,'invalid_record':{'table_cell':cells('/R7.5mm_r5.5mm/20cm/数据/数据01.xlsx')['B4'],'family_summary_B4':cells('/R7.5mm_r5.5mm/data.xlsx')['B4'],'length_summary_B4':cells('/数据处理/长度关系比较/data1.xlsx')['B4'],'meaning':'分表 NaN；汇总表用四个有效值的均值补位。重分析剔除该项，n=4。'}})

checks=json.loads((OUT/'历史分表与全部原音频逐条核对.json').read_text(encoding='utf8'))
tiny=[]
for c in checks:
    if c['difference_hz'] is not None and c['difference_hz']>1e-5:
        r=next(r for r in rows if r['path']==c['path']);pred=r['peak_hz']*r['N']/(r['N']-2)
        tiny.append({**c,'N':r['N'],'bin_hz':r['bin_hz'],'N_over_N_minus_2_prediction_hz':pred,'residual_hz':pred-c['historical_hz']})
save('三项微差的频率轴数值指纹.json',tiny)

pitch=[]
semitones={'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
for r in rows:
    for alias in r['aliases']:
        if alias.startswith('school data/pitch/'):
            parts=Path(alias).stem.split('-');m=re.fullmatch(r'([A-G]#?)(\d)',parts[1]);midi=12*(int(m[2])+1)+semitones[m[1]];target=440*2**((midi-69)/12)
            pitch.append(dict(path=alias,canonical_audio_path=r['path'],note_label=parts[1],token_3=parts[2],token_4=parts[3],penultimate_token=parts[-2],final_token=parts[-1],has_x=parts[0].startswith('x'),equal_temperament_A4_440_hz=target,one_octave_higher_reference_hz=2*target,recomputed_peak_hz=r['peak_hz'],difference_from_literal_label_cents=1200*math.log2(r['peak_hz']/target),difference_from_one_octave_higher_reference_cents=1200*math.log2(r['peak_hz']/(2*target))))
pitch.sort(key=lambda r:(r['has_x'],int(re.search(r'\d+',Path(r['path']).name)[0])))
save('音符匹配支线18份文件.json',pitch);writecsv('音符匹配支线18份文件.csv',pitch)

primary=[r for r in rows if r['kind']=='straight' and r['r'] is not None and r['rep']<=5 and not r['invalid']]
conflicts=[]
for r in rows:
    tags={str(meta(a)) for a in r['aliases'] if meta(a)['kind']!='other'}
    if len(tags)>1:conflicts.append(dict(path=r['path'],tags=sorted(tags)))
save('主分析信号质量与标签去重核查.json',{'records':len(primary),'all_max_sample_abs_below_0999':all(r['clip_fraction']==0 for r in primary),'minimum_near_global_peak_fraction':min(r['near_global_peak_fraction'] for r in primary),'median_near_global_peak_fraction':float(np.median([r['near_global_peak_fraction'] for r in primary])),'minimum_valid_frame_fraction':min(r['valid_frame_fraction'] for r in primary),'exact_byte_aliases_conflicting_parsed_group_labels':conflicts,'note':'诊断基于解码后第一声道；未检出贴近数字满幅不排除上游限幅、自动增益、编码或未保存的处理。'})

records=sum([json.loads((OLD/n).read_text(encoding='utf8')) for n in ['原件索引.json','追加原件索引.json']],[])
failures=[]
for r in records:
    p=Path(r['path'])
    if not p.is_file():failures.append({'path':str(p),'issue':'missing'});continue
    with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
    if p.stat().st_size!=r['bytes'] or h!=r['sha256']:failures.append({'path':str(p),'issue':'size/hash mismatch'})
save('原件保护复核.json',dict(checked_at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),count=len(records),failures=failures,status='PASS' if not failures else 'FAIL',baseline='2026-10-05 原件索引 + 追加原件索引'))
print(json.dumps({'originals':len(records),'failures':failures,'archive':archivecheck,'note_files':len(pitch),'primary_near_global_min':min(r['near_global_peak_fraction'] for r in primary),'alias_conflicts':conflicts},ensure_ascii=False,indent=2))
