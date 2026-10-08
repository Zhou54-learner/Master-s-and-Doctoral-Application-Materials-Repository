"""Source-backed 2026 reanalysis; all historical inputs are read-only."""
from pathlib import Path
import sys, json, csv, io, zipfile, hashlib, re
import xml.etree.ElementTree as ET
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import signal
from analyze_audio import decode, SRC, OUT, OLD, save, writecsv

FIG=Path(sys.argv[1]) if len(sys.argv)>1 else OUT/'output'; FIG.mkdir(exist_ok=True,parents=True)
plt.rcParams.update({'font.family':'Microsoft YaHei','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','pdf.fonttype':42,'axes.unicode_minus':False})
BLUE='#226899'; ORANGE='#bf6427'; GRAY='#6b7278'
rows=json.loads((OUT/'全量音频重分析.json').read_text(encoding='utf8'))
tracks={r['path']:r for r in json.loads((OUT/'短时频率轨迹.json').read_text(encoding='utf8'))}
groups=json.loads((OUT/'按原始标签分组统计.json').read_text(encoding='utf8'))
def export(fig,name):
    for ext in ['png','svg','pdf']:fig.savefig(FIG/(name+'.'+ext),dpi=300,bbox_inches='tight',facecolor='white')
    svg=FIG/(name+'.svg');svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf8').splitlines())+'\n',encoding='utf8')
    plt.close(fig)
def footer(fig,text): fig.text(.06,.013,text,fontsize=9,color=GRAY,va='bottom')

# Comparable primary cohort: only the five originally tabulated repetitions.
primary=[]
for g in groups:
    if g['kind']!='straight' or g['r'] is None:continue
    rr=[r for r in rows if r['kind']=='straight' and (r['R'],r['L'],r['group'])==(g['R'],g['L'],g['group']) and r['rep']<=5 and not r['invalid']]
    a=np.array([r['peak_hz'] for r in rr]);sd=a.std(ddof=1)
    primary.append({**{k:g[k] for k in ['R','r','L','group']},'n':len(a),'mean_hz':a.mean(),'sd_hz':sd,'cv_pct':100*sd/a.mean(),'values_hz':a.tolist(),'paths':[r['path'] for r in rr]})
primary.sort(key=lambda x:(x['R'],x['L'],x['group']))
save('历史表对应42组统计.json',primary)
writecsv('历史表对应42组统计.csv',[{k:v for k,v in r.items() if k not in ['paths','values_hz']} for r in primary])
geoms=sorted(set((r['R'],r['r'],r['L']) for r in primary))
gaps=[]; summary=[]
for R,r,L in geoms:
    gg=[x for x in primary if (x['R'],x['r'],x['L'])==(R,r,L)]
    d=np.diff([x['mean_hz'] for x in gg])
    for j,v in enumerate(d):
        gaps.append(dict(R=R,r=r,L=L,from_group=gg[j]['group'],to_group=gg[j+1]['group'],gap_hz=float(v),two_L_gap_m_s=float(2*L/100*v)))
    summary.append(dict(R=R,r=r,L=L,means_hz=[x['mean_hz'] for x in gg],gaps_hz=d.tolist(),mean_all_gap_hz=float(d.mean())))
save('各管几何与直接间距.json',summary);writecsv('全部直接相邻台阶间距.csv',gaps)
cv=np.array([g['cv_pct'] for g in primary]);separation=[]
for R,r,L in geoms:
    gg=[x for x in primary if (x['R'],x['L'])==(R,L)]
    separation.extend([(b['mean_hz']-a['mean_hz'])/max(a['sd_hz'],b['sd_hz']) for a,b in zip(gg,gg[1:])])
save('统计要点.json',dict(primary_groups=len(primary),primary_valid_recordings=sum(x['n'] for x in primary),cv_median_pct=float(np.median(cv)),cv_min_pct=float(cv.min()),cv_max_pct=float(cv.max()),groups_cv_below_1pct=int((cv<1).sum()),min_gap_over_max_sd=float(min(separation))))

fig,axs=plt.subplots(3,3,figsize=(13,10),sharey=True)
for ax,(R,r,L) in zip(axs.flat,geoms):
    gg=[x for x in primary if (x['R'],x['L'])==(R,L)];c=BLUE if R==7.5 else ORANGE
    for i,g in enumerate(gg,1):
        ax.scatter(i+np.linspace(-.10,.10,g['n']),g['values_hz'],s=19,color=c,alpha=.65,zorder=3)
        ax.errorbar(i,g['mean_hz'],yerr=g['sd_hz'],fmt='_',ms=18,color='#172632',capsize=4,lw=1.1)
    ax.plot(range(1,len(gg)+1),[g['mean_hz'] for g in gg],lw=.7,color=c,alpha=.6)
    ax.set(title=f'R/r = {R:g}/{r:g} mm · L = {L} cm',xticks=range(1,len(gg)+1),xticklabels=[g['group'] for g in gg],ylim=(1100,4850))
    ax.grid(axis='y',alpha=.15)
    ax.set_xlabel('原始记录组号');ax.set_ylabel('整段 FFT 主峰 / Hz')
fig.suptitle('同一根管子的多个稳定音调组：42 组、209 份有效录音',fontsize=18,y=.995)
fig.tight_layout(rect=(0,.065,1,.97))
footer(fig,'点为单份录音；横线及误差棒为均值 ± 样本标准差。组号不是流速。20 cm 首组 n=4，其余 n=5。\n2026-10-06 重分析；60 cm 另存的第 6 次录音仅列补充统计，未混入历史五次比较。')
export(fig,'F01_直管42组全部主峰')

fig,axs=plt.subplots(1,2,figsize=(12.5,5))
for ax,R,c in zip(axs,[7.5,11.6],[BLUE,ORANGE]):
    gg=[x for x in gaps if x['R']==R]
    for L in sorted(set(g['L'] for g in gg)):
        vals=[g['gap_hz'] for g in gg if g['L']==L]
        ax.scatter(np.full(len(vals),L)+np.linspace(-1.2,1.2,len(vals)),vals,s=45,color=c,edgecolor='white',zorder=3)
    xx=np.linspace(20 if R==7.5 else 40,102,250)
    ax.plot(xx,15000/xx,'--',color=GRAY,lw=1.2,label='150 / L(m)：尺度参照')
    ax.plot(xx,30000/xx,':',color=GRAY,lw=1.2,label='300 / L(m)：两倍参照')
    ax.set(title=f'R = {R:g} mm',xlabel='管长 L / cm',ylabel='相邻记录组的均值差 / Hz',xticks=[20,40,60,80,100] if R==7.5 else [40,60,80,100],ylim=(0,950))
    ax.grid(alpha=.15);ax.legend(fontsize=9)
fig.suptitle('长度影响更清楚地体现在台阶间距，而不是第一组频率',fontsize=17)
fig.tight_layout(rect=(0,.14,1,.94))
footer(fig,'全部直接间距均保留，包括约两倍的大间距。虚线仅为 1/L 尺度参照，不是拟合或独立声速测量。\n大间距与未激发／未记录的中间台阶相容；尚不能据此指定谐波阶数。2026-10-06 重分析。')
export(fig,'F02_台阶间距与管长')

# Long recording: segment by midpoint thresholds between independent group means.
name='R11.6mm_r8.0mm/80cm/R11.6mmr8mm_80cm_scale.mp3'
row=next(x for x in rows if x['path']==name);tr=tracks[name]
t=np.array(tr['t']);ridge=np.array(tr['peak_hz']);valid=np.array(tr['valid'])
centers=np.array([g['mean_hz'] for g in primary if (g['R'],g['L'])==(11.6,80)])
classes=np.digitize(ridge,(centers[1:]+centers[:-1])/2)
filtered=signal.medfilt(classes.astype(float),kernel_size=7).astype(int)
runs=[]
for k in range(7):
    inds=np.where(filtered==k)[0];cut=np.split(inds,np.where(np.diff(inds)>1)[0]+1);best=max(cut,key=len)
    start,end=t[best[0]],t[best[-1]]
    use=(t>=start+.25)&(t<=end-.25)&valid
    vals=ridge[use]
    runs.append(dict(plateau=k+1,start_s=float(start),end_s=float(end),interior_start_s=float(start+.25),interior_end_s=float(end-.25),median_hz=float(np.median(vals)),p05_hz=float(np.percentile(vals,5)),p95_hz=float(np.percentile(vals,95)),group_mean_hz=float(centers[k]),median_difference_hz=float(np.median(vals)-centers[k]),frames=int(use.sum())))
save('scale片内七台阶统计.json',runs);writecsv('scale片内七台阶统计.csv',runs)
y,fs,_=decode(SRC/name);yd=signal.resample_poly(y,40,147)
ff,tt,z=signal.stft(yd,12000,window='hann',nperseg=2048,noverlap=1536,boundary=None,padded=False)
db=20*np.log10(np.maximum(abs(z),1e-12)/abs(z).max())
fig,axs=plt.subplots(2,1,figsize=(12,7.2),sharex=True,gridspec_kw={'height_ratios':[1.35,1]})
im=axs[0].pcolormesh(tt,ff,db,shading='auto',cmap='magma',vmin=-55,vmax=0,rasterized=True)
axs[0].set(ylim=(1000,3200),ylabel='频率 / Hz',title='历史音阶展示文件：七段稳定频率，与分段录音共享波形')
axs[1].plot(t,ridge,color=BLUE,lw=1.1,label='本轮短时 FFT 最大谱峰')
figs=json.loads((OLD/'FIG对象核读.json').read_text(encoding='utf8'));figstats=[]
for item in figs:
    lines=[o['properties'] for o in item['objects'] if 'XData' in o.get('properties',{}) and 'YData'in o['properties']]
    if not lines:continue
    xx=np.array(lines[0]['XData']);yy=[np.array(l['YData']) for l in lines]
    stats=dict(path=item['path'],line_count=len(lines),points=len(xx),x_first=float(xx[0]),x_last=float(xx[-1]),x_step_unique=np.unique(np.diff(xx)).tolist(),two_y_exact_equal=bool(np.array_equal(yy[0],yy[1])),max_y_difference=float(np.max(abs(yy[0]-yy[1]))))
    if '/80cm/' in item['path']:
        for i,(line,a) in enumerate(zip(lines,yy)):
            tx=np.array(line['XData'])/fs
            axs[1].scatter(tx,a,s=2,color=ORANGE,alpha=.30,label='历史 NCF 曲线（横轴 / 44100）' if i==0 else None)
            target=np.interp(tx,t,ridge);stats[f'line{i+1}_median_abs_diff_from_stft_hz']=float(np.median(abs(a-target)))
    figstats.append(stats)
save('历史FIG坐标与双曲线核对.json',figstats)
for r in runs:
    axs[0].text((r['start_s']+r['end_s'])/2,3060,str(r['plateau']),ha='center',color='white',weight='bold')
    axs[1].hlines(r['median_hz'],r['interior_start_s'],r['interior_end_s'],color='#153a4d',lw=2)
axs[1].set(xlim=(0,row['duration_s']),ylim=(350,3050),xlabel='录音内时间 / s',ylabel='频率 / Hz');axs[1].grid(alpha=.15);axs[1].legend(loc='lower right',fontsize=9)
fig.tight_layout(rect=(0,.095,1,1))
footer(fig,'文件：R11.6mmr8mm_80cm_scale.mp3，20.98 s；色阶为相对最大值 −55 至 0 dB；本轮重分析。\n七段与短录音的相关为 0.956–0.994，支持历史拼接展示，不能当作连续扫流。NCF 横轴已由样本序号换算为秒。')
export(fig,'F03_历史长录音七个台阶')

curved=[g for g in groups if g['kind']=='curved']
cg=sorted(set((g['R'],g['L']) for g in curved if g['R']!=11.8))
fig,axs=plt.subplots(2,4,figsize=(15,7.3),sharey=True)
for ax,(R,L) in zip(axs.flat,cg):
    gg=sorted([g for g in curved if (g['R'],g['L'])==(R,L)],key=lambda x:float(x['group']))
    for i,g in enumerate(gg):
        vals=[r['peak_hz'] for r in rows if r['path'] in g['paths']]
        ax.scatter(i+np.linspace(-.065,.065,g['n']),vals,color=BLUE,s=24)
        ax.errorbar(i,g['mean_hz'],yerr=g['sd_hz'],fmt='_',color='black',ms=14,capsize=4)
    if R==11.6 and L==80:
        typo=next(g for g in curved if g['R']==11.8)
        ax.scatter(2.13,typo['mean_hz'],marker='x',s=40,color=ORANGE,label='R11.8 原标签');ax.legend(fontsize=8,loc='upper left')
    ax.set(title=f'R 标签 {R:g} mm · {L} cm',xticks=range(len(gg)),xticklabels=[g['group'] for g in gg],xlabel='原文件第三字段',ylabel='FFT 主峰 / Hz',ylim=(1050,3420));ax.grid(axis='y',alpha=.15)
axs.flat[-1].axis('off');axs.flat[-1].text(.04,.75,'64 份原始录音\n21 个主体条件 + 1 个异名标签\n\n第三字段含义及单位尚未确认\n不能直接标成曲率或气流',va='top',fontsize=12,linespacing=1.7)
fig.suptitle('弯管实验确有成组数据，但条件字段需要恢复',fontsize=18)
fig.tight_layout(rect=(0,.07,1,.96))
footer(fig,'2026-10-06 重分析；点为独立文件，未证明独立实验。R11.8 的单个标签保留，不自动并入 R11.6。\n横轴等距列出记录条件，既不是有单位的连续量，也不表示相等曲率增量。')
export(fig,'F04_弯管全部原始标签')

# Archive-only older workbook: inspect in-memory, never extract/modify originals.
def cells_from_bytes(data):
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        out=[]
        for sn in z.namelist():
            if re.fullmatch(r'xl/worksheets/sheet\d+.xml',sn):
                cc={}
                for c in ET.fromstring(z.read(sn)).findall('.//m:c',ns):
                    v=c.find('m:v',ns);val=v.text if v is not None else ''.join(c.find('m:is',ns).itertext()) if c.find('m:is',ns)is not None else None
                    if c.get('t')=='s' and val is not None:val=strings[int(val)]
                    cc[c.get('r')]=val
                out.append({'sheet':sn,'cells':cc})
        return out
archive=[]
for zpath in SRC.rglob('*.zip'):
    with zipfile.ZipFile(zpath) as z:
        for member in z.namelist():
            if member.endswith('/data3.xlsx'):
                data=z.read(member);external=SRC/member
                if external.exists() and data!=external.read_bytes():
                    arc=cells_from_bytes(data);ext=cells_from_bytes(external.read_bytes());ac=arc[0]['cells'];ec=ext[0]['cells']
                    changes=[{'cell':k,'archive':ac.get(k),'external':ec.get(k)} for k in sorted(set(ac)|set(ec)) if ac.get(k)!=ec.get(k)]
                    archive.append(dict(archive=str(zpath),member=member,archive_sha256=hashlib.sha256(data).hexdigest(),archive_sheets=arc,differences=changes))
save('压缩包独有旧版汇总表核读.json',archive)
print(json.dumps({'statistics':json.loads((OUT/'统计要点.json').read_text(encoding='utf8')),'plateaus':runs,'figs':figstats,'archive_different_cells':[len(x['differences']) for x in archive]},ensure_ascii=False,indent=2))
