from pathlib import Path
import numpy as np, json,csv,collections,re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pptx import Presentation
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
BASE=Path('F:/biyesheji/最终结果ohmic_sheet_12x12_multitemplate_topology_ga')
plt.rcParams.update({'font.family':'Microsoft YaHei','axes.spines.top':False,'axes.spines.right':False,'font.size':12,'axes.labelcolor':'#142c46','text.color':'#142c46'})
def load(tag,name):
    a=np.loadtxt(OUT/'native'/f'{tag}_{name}.csv',delimiter=',',skiprows=1)
    return a[:,0],a[:,1]+1j*a[:,2]
report={}
for tag in ['ga','adaptive']:
    for mode in [1,2]:
        f,pin=load(tag,f'pin{mode}'); _,pout=load(tag,f'pout{mode}');_,metal=load(tag,f'metal{mode}');_,diel=load(tag,f'dielectric{mode}')
        residual=((pin-pout-metal-diel)/pin).real
        fs,s1=load(tag,f'S1{mode}');_,s2=load(tag,f'S2{mode}')
        inds=np.array([np.abs(fs-v).argmin() for v in f]); assert np.max(abs(fs[inds]-f))<1e-8
        r=abs(s1[inds])**2+abs(s2[inds])**2
        report[f'{tag}_mode{mode}']=dict(power_samples=len(f),max_dielectric_loss_W=float(max(abs(diel))),max_energy_residual=float(max(abs(residual))),max_S_power_mismatch=float(max(abs(r-(pout/pin).real))),at_18=dict(R=float(r[-1]),loss_fraction=float(((metal+diel)/pin).real[-1])))
    for ij in ['11','12','21','22']:
        f,s=load(tag,'S'+ij)
        prev=ROOT/'A线_西湖博士/面试与导师交流/刘癸庚/事实核验/evidence'
        q=prev/'ga_winner'/f'S{ij}.csv' if tag=='ga' else prev/f'1D_Results_S-Parameters_SZmax({ij[0]}),Zmax({ij[1]}).csv'
        a=np.loadtxt(q,delimiter=',',skiprows=1)
        assert np.array_equal(f,a[:,0]) and np.array_equal(s,a[:,1]+1j*a[:,2])
f,s=load('ga','S11');db=20*np.log10(abs(s));ok=db<=-10
bw=13.2;total=sum(ok)*np.mean(np.diff(f));margin=np.mean(-10-db[ok]);shallow=np.mean(db[ok]>-11)
flo=float(f[np.flatnonzero(ok)[0]])
score=3.2*bw+.2*total+14+(8+4*(5-flo))+(7 if flo<=4.8 else 0)+6+(14+4*(bw-13.120000000000001))+.05*min(abs(min(db)),50)+.1*min(margin,18)-2*shallow
report['fitness_recalculation']=dict(bw=bw,f_low=flo,bonus_at_4p8_applied=flo<=4.8,total_effective_estimate=float(total),mean_margin=float(margin),shallow_ratio=float(shallow),score=float(score),display_rounded_f_low_would_add=7)
assert abs(score-89.63868001716894)<1e-10
raw=np.genfromtxt(BASE/'best_s11_ohmic_sheet_12x12.txt',names=True,delimiter='\t')
report['max_native_vs_original_magnitude_difference']=float(np.max(abs(raw['s11_mag']-abs(s))))
assert report['max_native_vs_original_magnitude_difference']<1e-14
trace=[]
for line in (BASE/'individual_trace_ohmic_sheet_12x12.txt').read_text(encoding='utf-8').splitlines():
    trace.append(dict(x.split('=',1) for x in line.split('\t') if '=' in x))
report['trace_counts']=dict(collections.Counter(x['status'] for x in trace))
win=[x for x in trace if x['gen']=='7' and x['idx']=='6' and x['status']=='finished_cst'][0]
seed=[x for x in trace if x['gen']=='0' and x['idx']=='0' and x['status']=='finished_cst'][0]
report['winner_mask_equals_seed']=all(win[k]==seed[k] for k in ['mask_x','mask_y'])
report['unique_finished_masks']=len({(x['mask_x'],x['mask_y']) for x in trace if x['status']=='finished_cst'})
(OUT/'本轮数值复核.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
fig,ax=plt.subplots(figsize=(8.4,4.2),layout='constrained')
for tag,label,col in [('ga','GA 获选工程（未开启网格自适应）','#098c8b'),('adaptive','后期工程（已开启内部自适应）','#c35e39')]:
    f,s=load(tag,'S11');ax.plot(f,20*np.log10(abs(s)),label=label,color=col,lw=2.2)
ax.axhline(-10,color='#637184',ls='--',lw=1);ax.set(xlim=(2,18),ylim=(-37,1),xlabel='频率 / GHz',ylabel='同偏振反射 20 log10|S11| / dB')
ax.legend(fontsize=10,loc='lower left');ax.grid(alpha=.15)
fig.savefig(OUT/'两工程同偏振对照.png',dpi=200);plt.close(fig)
fig,ax=plt.subplots(figsize=(7.5,3.5),layout='constrained')
for ij,label,col in [('11','mode 1：y 偏振','#098c8b'),('22','mode 2：x 偏振','#c35e39')]:
    f,s=load('ga','S'+ij);ax.plot(f,20*np.log10(abs(s)),label=label,color=col,lw=2)
ax.axhline(-10,color='#637184',ls='--',lw=1);ax.set(xlim=(2,18),ylim=(-27,1),xlabel='频率 / GHz',ylabel='同偏振反射 / dB');ax.legend(fontsize=10);ax.grid(alpha=.15)
fig.savefig(OUT/'两偏振对照.png',dpi=200);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(6,3),layout='constrained')
for ax,xy in zip(axs,['x','y']):
    a=np.loadtxt(BASE/f'best_mask_{xy}_12x12.txt');ax.imshow(a,cmap='Greys',vmin=0,vmax=1);ax.set_title(xy.upper()+' 面电阻图案');ax.set_xticks([]);ax.set_yticks([])
fig.savefig(OUT/'最终图案.png',dpi=200);plt.close(fig)
print(json.dumps(report,ensure_ascii=False,indent=2))
