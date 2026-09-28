from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import argparse
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path);args=parser.parse_args()
OUT=args.output_dir or HERE.parent/'output';OUT.mkdir(parents=True,exist_ok=True)
data=np.genfromtxt(HERE/'reflection_archived.tsv',names=True,delimiter='\t')
plt.rcParams.update({'font.family':'Arial','font.size':8,'svg.fonttype':'none','pdf.fonttype':42,'axes.linewidth':0.7})
fig,ax=plt.subplots(figsize=(3.55,2.0),layout='constrained')
ax.plot(data['freq_GHz'],data['rl_dB'],color='#226287',lw=1.35)
ax.axhline(-10,color='#666666',lw=0.8,ls='--')
ax.text(2.4,-9,'−10 dB',fontsize=7,color='#555555')
ax.set(xlim=(2,18),ylim=(-27,1),xlabel='Frequency (GHz)',ylabel='Co-polar reflection (dB)',xticks=[2,6,10,14,18],yticks=[-25,-20,-15,-10,-5,0])
ax.spines[['top','right']].set_visible(False)
ax.tick_params(length=3,width=0.7)
for ext in ['pdf','svg','png']:fig.savefig(OUT/f'reflection.{ext}',dpi=300)
print('Archived-data plot exported; no simulation or smoothing.')
