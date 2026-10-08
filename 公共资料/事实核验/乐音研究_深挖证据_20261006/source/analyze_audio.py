"""2026-10-06 full historical audio re-analysis. Never writes source directories."""
from pathlib import Path
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
import csv, hashlib, json, math, re, subprocess
import numpy as np
from scipy import signal

OUT=Path(__file__).resolve().parent.parent
SRC=Path('E:/2023/traindata')
OLD=OUT.parent/'乐音研究_考古证据_20261005'

def save(n,x): (OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def writecsv(name,rows):
    if not rows:return
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def meta(name):
    if name.startswith('弯管数据/'):
        m=re.match(r'R([\d.]+)mm_(\d+)cm_([\d.]+)_(\d+)',Path(name).stem)
        if m:return dict(kind='curved',R=float(m[1]),r=None,L=int(m[2]),group=m[3],rep=int(m[4]),invalid=False)
    if name.startswith(('R7.5','R11.6','R10.0')):
        m=re.match(r'R?([\d.]+)mm(?:r([\d.]+)mm)?_(\d+)cm_(\d+)_(\d+)',Path(name).stem)
        if m:return dict(kind='straight',R=float(m[1]),r=float(m[2]) if m[2] else None,L=int(m[3]),group=m[4],rep=int(m[5]),invalid='无效' in name)
    return dict(kind='other',R=None,r=None,L=None,group=None,rep=None,invalid=False)

def decode(path):
    j=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)]))
    s=next(x for x in j['streams'] if x['codec_type']=='audio')
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-af','pan=mono|c0=c0','-f','f32le','-'])
    return np.frombuffer(raw,dtype='<f4').astype(float),int(s['sample_rate']),s

def inspect(item):
    h,paths=item
    # Keep original root families first; mirrored straight/backup folders are aliases.
    paths=sorted(paths,key=lambda x:(x.startswith(('数据库备份/','直管数据/')),len(x),x))
    name=paths[0];p=SRC/name
    try:
        y,fs,s=decode(p);n=len(y)
        a=np.abs(np.fft.rfft(y))/n
        a[1:-1 if n%2==0 else None]*=2
        f=np.fft.rfftfreq(n,1/fs);k=int(a.argmax())
        peaks,_=signal.find_peaks(a,distance=max(1,round(20*n/fs)))
        tops=sorted(peaks,key=lambda q:a[q],reverse=True)[:8]
        g=math.gcd(fs,12000);yd=signal.resample_poly(y,12000//g,fs//g)
        ff,tt,z=signal.stft(yd,12000,window='hann',nperseg=2048,noverlap=1536,boundary=None,padded=False)
        power=np.abs(z)**2;band=(ff>=80)&(ff<=5500)
        pp=power[band];freq=ff[band];ki=pp.argmax(axis=0);ridge=freq[ki];best=pp[ki,np.arange(len(tt))]
        total=pp.sum(axis=0);quality=best/np.maximum(total,1e-30)
        valid=(total>=total.max()*0.01)&(quality>=0.1)
        vals=ridge[valid]
        row=dict(sha256=h,path=name,aliases=paths,**meta(name),fs=fs,channels=s['channels'],N=n,duration_s=n/fs,
                 peak_hz=float(f[k]),peak_amplitude=float(a[k]),bin_hz=fs/n,rms=float(np.sqrt(np.mean(y*y))),
                 clip_fraction=float(np.mean(abs(y)>=.999)),created_utc=s.get('tags',{}).get('creation_time'),
                 top_peaks=[dict(hz=float(f[q]),relative_amplitude=float(a[q]/a[k])) for q in tops],
                 valid_frame_fraction=float(np.mean(valid)),ridge_median=float(np.median(vals)) if len(vals) else None,
                 ridge_p05=float(np.percentile(vals,5)) if len(vals) else None,ridge_p95=float(np.percentile(vals,95)) if len(vals) else None,
                 near_global_peak_fraction=float(np.mean(abs(vals-f[k])<=max(20,.02*f[k]))) if len(vals) else None)
        track=dict(path=name,t=np.round(tt,4).tolist(),peak_hz=np.round(ridge,3).tolist(),valid=valid.tolist(),relative_band_power=np.round(total/max(total.max(),1e-30),6).tolist())
        return row,track
    except Exception as e:return dict(path=name,sha256=h,error=str(e)),None

def main():
    paths=[p for p in SRC.rglob('*') if p.is_file() and p.suffix.lower() in ['.m4a','.mp3','.mp4']]
    hashes=defaultdict(list)
    for p in paths:hashes[sha(p)].append(p.relative_to(SRC).as_posix())
    rows=[];tracks=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,(row,track) in enumerate(pool.map(inspect,hashes.items()),1):
            rows.append(row)
            if track:tracks.append(track)
            if i%50==0:print('decoded',i,flush=True)
    save('全量音频重分析.json',rows)
    (OUT/'短时频率轨迹.json').write_text('[\n'+',\n'.join(json.dumps(t,ensure_ascii=False,separators=(',',':')) for t in tracks)+'\n]\n',encoding='utf8')
    writecsv('全量音频索引与频率.csv',[{k:v for k,v in x.items() if k not in ['aliases','top_peaks']} for x in rows])
    groups=defaultdict(list)
    for r in rows:
        if 'error' not in r and r['kind'] in ['straight','curved']:
            groups[(r['kind'],r['R'],r['r'],r['L'],r['group'])].append(r)
    stats=[]
    for (kind,R,r,L,group),rr in sorted(groups.items(),key=lambda kv:str(kv[0])):
        used=[x for x in rr if not x['invalid']]
        a=np.array([x['peak_hz'] for x in used]);sd=float(np.std(a,ddof=1)) if len(a)>1 else None
        stats.append(dict(kind=kind,R=R,r=r,L=L,group=group,n=len(a),mean_hz=float(a.mean()),sd_hz=sd,min_hz=float(a.min()),max_hz=float(a.max()),cv_pct=100*sd/float(a.mean()) if sd is not None else None,paths=[x['path'] for x in used],excluded=[x['path'] for x in rr if x['invalid']]))
    save('按原始标签分组统计.json',stats);writecsv('分组统计.csv',[{k:v for k,v in x.items() if k not in ['paths','excluded']} for x in stats])
    books=json.loads((OLD/'表格单元格与元数据.json').read_text(encoding='utf8'))
    tablechecks=[]
    for b in books:
        rel=Path(b['path']).relative_to(SRC).as_posix()
        if rel.startswith('直管数据/') or '/数据/数据' not in rel:continue
        cells={x['cell']:x['value'] for x in b['sheets'][0]['cells']}
        family=rel.split('/')[0];L=int(re.search(r'/(\d+)cm/',rel)[1]);g=re.search(r'数据(\d+)\.xlsx',rel)[1]
        for row in rows:
            if row.get('kind')=='straight' and row['path'].startswith(family+'/') and row['L']==L and row['group']==g and row['rep']<=5:
                old=float(cells['B'+str(row['rep']+1)])
                tablechecks.append(dict(path=row['path'],table=rel,cell='B'+str(row['rep']+1),historical_hz=old if math.isfinite(old) else None,new_hz=row['peak_hz'],difference_hz=abs(old-row['peak_hz']) if math.isfinite(old) else None,invalid=row['invalid']))
    save('历史分表与全部原音频逐条核对.json',tablechecks);writecsv('历史分表逐条核对.csv',tablechecks)
    summary=dict(source_file_count=len(paths),unique_file_count=len(rows),decode_errors=[r for r in rows if 'error'in r],kind_counts=dict(Counter(r.get('kind') for r in rows)),groups=dict(Counter(r['kind'] for r in stats)),historical_table_cells=len(tablechecks),numerical_mismatches=[x for x in tablechecks if x['difference_hz'] is not None and x['difference_hz']>1e-5])
    save('覆盖摘要.json',summary);print(json.dumps(summary,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
