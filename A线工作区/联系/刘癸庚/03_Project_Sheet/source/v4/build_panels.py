"""Model-derived geometry and archived-data plot; never imports research code."""
from pathlib import Path
import argparse, ast, json, re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--output-dir',type=Path,default=HERE.parents[1]/'output_v4_CANDIDATE')
OUT=parser.parse_args().output_dir
OUT.mkdir(parents=True,exist_ok=True)
D=HERE/'data'
mx=np.loadtxt(D/'best_mask_x_12x12.txt',dtype=int)
my=np.loadtxt(D/'best_mask_y_12x12.txt',dtype=int)
assert mx.shape==my.shape==(12,12)
assert set(np.unique(mx))==set(np.unique(my))=={0,1}
assert int(mx.sum())==36 and int(my.sum())==79
text=(D/'best_result_ohmic_sheet_12x12.txt').read_text(encoding='utf-8')
params=ast.literal_eval(next(s.split(': ',1)[1] for s in text.splitlines() if s.startswith('Best parameters ')))
p,h=params[:2]
assert np.array_equal(mx.ravel(),params[2]) and np.array_equal(my.ravel(),params[3])
blue='#246889'; orange='#B87938'; pale='#E9EEF1'
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="181.77mm" height="68.79mm" viewBox="0 0 515.3 195">',
 '<title>Model-derived crossed resistive films and exact unfolded masks</title>',
 '<desc>Exact 12x12 masks; source row zero is at z=0. Assembly projection is schematic. Not a CST screenshot.</desc>',
 '<rect width="515.3" height="195" fill="white"/>']
def label(x,y,s,size=9,color='#333333',anchor='start',bold=False):
    svg.append(f'<text x="{x}" y="{y}" font-family="Source Han Sans CN, Arial, sans-serif" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{700 if bold else 400}">{s}</text>')
def poly(points,color,stroke='#99A8B2',width=.3,opacity=1,ident=None):
    sid=f' id="{ident}"' if ident else ''
    svg.append(f'<polygon{sid} points="'+ ' '.join(f'{x:.3f},{y:.3f}' for x,y in points)+f'" fill="{color}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{width}"/>')
def proj(x,y,z):return (108+5.8*(x-y),137+2.9*(x+y)-7.2*z)
label(24,14,'正交结构示意',10,bold=True)
poly([proj(-p/2,-p/2,0),proj(p/2,-p/2,0),proj(p/2,p/2,0),proj(-p/2,p/2,0)],'#E2E6E9','#A5ADB5',.6)
tiles=[]
for side,mask in [('X',mx),('Y',my)]:
    for i in range(12):
        for j in range(12):
            u0=-p/2+j*p/12;u1=u0+p/12;z0=i*h/12;z1=z0+h/12
            xyz=[(u0,.094,z0),(u1,.094,z0),(u1,.094,z1),(u0,.094,z1)] if side=='X' else [(.094,u0,z0),(.094,u1,z0),(.094,u1,z1),(.094,u0,z1)]
            # Perspective chosen from +x,+y: farther tiles drawn first.
            depth=sum(x+y for x,y,z in xyz)/4
            tiles.append((depth,side,i,j,xyz,int(mask[i,j])))
for _,side,i,j,xyz,kept in sorted(tiles,key=lambda t:t[0]):
    color=(blue if side=='X' else orange) if kept else pale
    poly([proj(*q) for q in xyz],color,'#FFFFFF' if kept else '#B9C5CC',.22,.98 if kept else .30,f'assembly-{side}-{i}-{j}')
label(108,190,'金属背板',8,anchor='middle',color='#666666')
svg.append('<path d="M108 176 L108 181" fill="none" stroke="#8C959E" stroke-width=".6"/>')

# Exact, unobstructed flat views. Source row i is mapped upward to physical z.
for side,mask,x,color in [('X',mx,253,blue),('Y',my,389,orange)]:
    w=110; hh=w*h/p; top=36
    label(x+w/2,16,f'{side} 向膜（{side.lower()}–z）',10,anchor='middle',bold=True)
    svg.append(f'<rect x="{x}" y="{top}" width="{w}" height="{hh}" fill="#F4F7F9" stroke="#99A7B0" stroke-width=".6"/>')
    for i in range(12):
        for j in range(12):
            if mask[i,j]:
                xx=x+j*w/12;yy=top+(11-i)*hh/12
                svg.append(f'<rect id="mask-{side}-{i}-{j}" x="{xx:.6f}" y="{yy:.6f}" width="{w/12:.6f}" height="{hh/12:.6f}" fill="{color}"/>')
    for k in range(1,12):
        xx=x+k*w/12;yy=top+k*hh/12
        svg.append(f'<path d="M{xx:.4f} {top}V{top+hh:.4f} M{x} {yy:.4f}H{x+w}" fill="none" stroke="#899DA9" stroke-opacity=".38" stroke-width=".3"/>')
    # Local axes, with z pointing up and in-plane coordinate to the right.
    ax=x-7;ay=top+hh+7
    svg.append(f'<path d="M{ax} {ay-18}V{ay}H{ax+20}" fill="none" stroke="#667581" stroke-width=".6"/>')
    svg.append(f'<path d="M{ax-2} {ay-15}L{ax} {ay-19}L{ax+2} {ay-15} M{ax+17} {ay-2}L{ax+21} {ay}L{ax+17} {ay+2}" fill="none" stroke="#667581" stroke-width=".6"/>')
    label(ax-4,ay-21,'z',7);label(ax+23,ay+3,side.lower(),7)
    rs='140.79' if side=='X' else '35.461'
    label(x+w/2,151,f'片阻 {rs} Ω/□',8.5,color,anchor='middle')
label(376,174,f'p = {p:.4f} mm · h = {h:.4f} mm',8.5,anchor='middle',color='#555555')
label(376,190,'着色：电阻膜   浅色：PET基底',8,anchor='middle',color='#666666')
svg.append('</svg>')
(OUT/'geometry.svg').write_text('\n'.join(svg),encoding='utf-8')

data=np.genfromtxt(D/'reflection_archived.tsv',names=True,delimiter='\t')
f=data['freq_GHz'];r=data['rl_dB']
assert len(f)==201 and np.allclose(np.diff(f),.08)
ok=np.flatnonzero(r < -10)
groups=np.split(ok,np.flatnonzero(np.diff(ok)!=1)+1)
best=max(groups,key=len)
lo=float(f[best[0]]);hi=float(f[best[-1]])
assert abs(lo-4.8)<1e-9 and abs(hi-18)<1e-9
plt.rcParams.update({'font.family':'Arial','font.size':8.5,'svg.fonttype':'none','pdf.fonttype':42,'axes.linewidth':.7})
fig,ax=plt.subplots(figsize=(4.28,2.08),layout='constrained')
ax.plot(f,r,color=blue,lw=1.6)
ax.axhline(-10,color='#777777',ls=(0,(4,3)),lw=.8)
ax.text(2.3,-9.0,'−10 dB',fontsize=8,color='#666666')
ax.set(xlim=(2,18),ylim=(-27,1),xlabel='Frequency (GHz)',ylabel='Co-polar reflection (dB)',xticks=[2,6,10,14,18],yticks=[-25,-20,-15,-10,-5,0])
ax.spines[['top','right']].set_visible(False)
ax.tick_params(length=3,width=.7)
for ext in ['svg','pdf','png']:fig.savefig(OUT/f'reflection.{ext}',dpi=300)
plt.close(fig)
(OUT/'panel_checks.json').write_text(json.dumps({'mask_shape':[12,12],'X_kept':36,'Y_kept':79,'masks_match_result_tuple':True,'physical_row_orientation':'row0 at z=0; row11 at z=h','p_mm':p,'h_mm':h,'curve_samples':201,'interval_GHz':[lo,hi],'bandwidth_GHz':hi-lo,'fresh_simulation':False},ensure_ascii=False,indent=2),encoding='utf-8')
print('Geometry SVG and curve exported from archived data.')
