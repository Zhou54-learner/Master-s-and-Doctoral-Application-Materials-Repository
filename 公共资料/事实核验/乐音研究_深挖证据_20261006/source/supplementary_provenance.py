"""Reproduce archive-member hashes and a limited waveform-source search."""
import json, hashlib, zipfile, math
import numpy as np
from scipy import signal
from analyze_audio import OUT, OLD, SRC, decode, save

records=sum([json.loads((OLD/n).read_text(encoding='utf8')) for n in ['原件索引.json','追加原件索引.json']],[])
known={r['sha256'] for r in records}
archives=[]
for p in sorted(SRC.rglob('*.zip')):
    members=[]
    with zipfile.ZipFile(p) as z:
        for info in z.infolist():
            if info.is_dir():continue
            h=hashlib.sha256(z.read(info)).hexdigest()
            members.append(dict(name=info.filename,bytes=info.file_size,sha256=h,external_byte_match=h in known))
    archives.append(dict(path=p.as_posix(),members=members))
save('压缩包内部字节与外部文件核对.json',archives)

def signal12(path):
    y,fs,_=decode(SRC/path);g=math.gcd(fs,12000)
    x=signal.resample_poly(y,12000//g,fs//g)
    return x-x.mean()
long=signal12('R11.6mm_r8.0mm/80cm/R11.6mmr8mm_80cm_scale.mp3')
rows=json.loads((OUT/'全量音频重分析.json').read_text(encoding='utf8'))
matches=[]
for r in rows:
    if r['kind']=='straight' and (r['R'],r['L'])==(11.6,80):
        x=signal12(r['path']);n=len(x)
        cross=signal.correlate(long,x,mode='valid',method='fft')
        cumulative=np.r_[0,np.cumsum(long**2)];energy=cumulative[n:]-cumulative[:-n]
        corr=np.abs(cross)/np.sqrt(np.maximum(energy*np.sum(x*x),1e-30));idx=int(np.argmax(corr))
        matches.append(dict(path=r['path'],correlation=float(corr[idx]),start_s=idx/12000,duration_s=n/12000,short_file_creation_time_utc=r['created_utc'],short_file_sample_rate=r['fs']))
save('scale录音与单段来源匹配.json',matches)
chain=sorted([r for r in matches if r['correlation']>.9],key=lambda r:r['start_s'])
for i,r in enumerate(chain):
    r['end_s']=r['start_s']+r['duration_s']
    r['gap_from_previous_s']=r['start_s']-chain[i-1]['end_s'] if i else None
save('scale七段共享波形证据链.json',{'method':'第一声道重采样至12kHz、各文件减全局均值；valid全长互相关除以滑动段能量与短段能量乘积的平方根，取绝对值最大点。不是固定整段长文件能量归一。','matches':chain,'sum_short_durations_s':sum(r['duration_s'] for r in chain),'interpretation':'七个短文件依次近无缝覆盖长文件，相关0.956–0.994；短文件创建标签横跨3月29日和31日，强支持历史拼接展示。元数据非不可篡改的采集日志；具体编辑程序、操作方向未找回。不得计为一次独立连续扫气流记录。'})
print(json.dumps({'archives':len(archives),'nonmatched_members':[(a['path'],m['name']) for a in archives for m in a['members'] if not m['external_byte_match']],'maximum_waveform_correlation':max(r['correlation'] for r in matches)},ensure_ascii=False))
