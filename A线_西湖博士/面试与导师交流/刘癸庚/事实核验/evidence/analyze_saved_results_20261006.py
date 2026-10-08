"""Arithmetic on saved results only; no new electromagnetic solve."""
from pathlib import Path
import csv,json,math,hashlib
P=Path(__file__).resolve().parent
def curve(name):
    return [(float(r['x']),complex(float(r['real']),float(r['imag']))) for r in csv.DictReader((P/name).open())]
def band(f,db):
    groups=[];start=None
    for i,v in enumerate(db+[float('inf')]):
        if v<=-10 and start is None: start=i
        elif v>-10 and start is not None:
            groups.append([f[start],f[i-1],f[i-1]-f[start]]);start=None
    return groups
s={}; summary={}
for i in (1,2):
    for j in (1,2):
        a=curve(f'1D_Results_S-Parameters_SZmax({i}),Zmax({j}).csv')
        f=[r[0] for r in a];v=[r[1] for r in a];db=[20*math.log10(max(abs(z),1e-300)) for z in v]
        s[i,j]=(f,v)
        summary[f'S{i}{j}']={'count':len(f),'unique_frequencies':len(set(f)),'min_dB':min(db),'max_dB':max(db),'max_power_ratio':max(abs(z)**2 for z in v),'bands_le_minus10_dB':band(f,db),'samples':{str(q):{'actual_f_GHz':f[min(range(len(f)),key=lambda k:abs(f[k]-q))],'dB':db[min(range(len(f)),key=lambda k:abs(f[k]-q))]} for q in (2,4.8,8.8,12,15.5,18)}}
ga=list(csv.DictReader((Path(r'F:\biyesheji\最终结果ohmic_sheet_12x12_multitemplate_topology_ga')/'best_s11_ohmic_sheet_12x12.txt').open(),delimiter='\t'))
gaf=[float(r['freq_GHz']) for r in ga];gadb=[float(r['rl_dB']) for r in ga]
summary['GA']={'count':len(ga),'min_dB':min(gadb),'bands':band(gaf,gadb)}
matches=[]
for f,d in zip(gaf,gadb):
    k=min(range(len(s[1,1][0])),key=lambda k:abs(s[1,1][0][k]-f))
    if abs(s[1,1][0][k]-f)<1e-8: matches.append(abs(20*math.log10(abs(s[1,1][1][k]))-d))
summary['GA_vs_saved_adaptive']={'matched_points':len(matches),'max_absolute_dB_difference':max(matches),'same_curve':max(matches)<1e-6}
for j in (1,2):
    pin=curve(f'1D_Results_Power_Excitation__Zmax({j})__Power_Stimulated.csv')
    po=curve(f'1D_Results_Power_Excitation__Zmax({j})__Power_Outgoing_all_Ports.csv')
    ld=curve(f'1D_Results_Power_Excitation__Zmax({j})__Loss_in_Dielectrics.csv')
    lm=curve(f'1D_Results_Power_Excitation__Zmax({j})__Loss_in_Metals.csv')
    power=[]
    for (f,inc),(_,out),(_,d),(_,m) in zip(pin,po,ld,lm):
        k=min(range(len(s[1,j][0])),key=lambda k:abs(s[1,j][0][k]-f))
        refl=sum(abs(s[i,j][1][k])**2 for i in (1,2))
        power.append({'f_GHz':f,'pin_W':inc.real,'pout_W':out.real,'loss_W':(d+m).real,'loss_fraction':((d+m)/inc).real,'balance_residual_fraction':((inc-out-d-m)/inc).real,'s_power_sum':refl,'s_frequency_used':s[1,j][0][k]})
    summary[f'power_mode{j}']=power
orders=[]
for m,n in [(0,0),(1,0),(0,1),(1,1),(2,0),(2,1),(2,2)]:
    fc=299792458/(13.1409e-3)*math.hypot(m,n)/1e9
    orders.append({'abs_m':m,'abs_n':n,'cutoff_GHz':fc,'propagating_2_18':fc<2,'alpha_at18_per_m':math.sqrt(max(0,(2*math.pi*math.hypot(m,n)/.0131409)**2-(2*math.pi*18e9/299792458)**2))})
summary['cutoffs']=orders
meta=json.loads((P/'port_mode_metadata.json').read_text('utf-8'))
summary['metadata_check']={'count':len(meta),'modes':sorted(set(x['data']['port mode meta data']['mode id'] for x in meta)),'max_beta_relative_error':max(abs(d['gamma imag (beta)']/(2*math.pi*d['calculation frequency']/299792458)-1) for x in meta for d in x['data']['port mode meta data']['mode meta data'])}
(P/'saved_results_analysis.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
for k,v in summary.items():
    if k.startswith('power'): print(k,'n=',len(v),'loss_range=',min(r['loss_fraction'] for r in v),max(r['loss_fraction'] for r in v),'max_balance_error=',max(abs(r['balance_residual_fraction']) for r in v))
    else: print(k,json.dumps(v,ensure_ascii=False))
