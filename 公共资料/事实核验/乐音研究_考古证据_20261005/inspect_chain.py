"""Read-only source inspection; new numerical checks explicitly dated 2026-10-05."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,'C:/Users/zzj/AppData/Local/Temp/codex-music-audit-deps')
import numpy as np
from scipy.io import loadmat
import hashlib,json,datetime,zipfile,subprocess,xml.etree.ElementTree as E,shutil,re,collections
OUT=Path(__file__).resolve().parent
SRC=Path('E:/2023/traindata')
def save(n,x): (OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def rec(p):
 s=p.stat();return dict(path=p.as_posix(),bytes=s.st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mtime=datetime.datetime.fromtimestamp(s.st_mtime,datetime.timezone(datetime.timedelta(hours=8))).isoformat())
extra=[]
for name in ['test3.m','test.m','pitch.m','main_frequencies.xlsx']:
 p=Path('E:/matlab/work')/name;extra.append(rec(p))
 if p.suffix=='.m':shutil.copyfile(p,OUT/('历史源码_'+p.name))
p=SRC/'数据处理/pitchtest.m';shutil.copyfile(p,OUT/'历史源码_pitchtest.m')
for name in ['History.xml','MATLAB_Editor_State.xml']:
 p=Path('C:/Users/zzj/AppData/Roaming/MathWorks/MATLAB/R2022b')/name;extra.append(rec(p));r=E.parse(p).getroot()
 if name=='History.xml':
  sessions=[]
  for s in r.findall('session'):
   stamp=s.find('command').text
   if '2024/' in (stamp or ''):sessions.append(dict(session=stamp,commands=[dict(text=c.text,attributes=c.attrib) for c in s.findall('command')[1:]]))
  save('MATLAB历史命令_2024选段.json',sessions)
 else:
  save('MATLAB编辑器路径选段.json',[e.attrib for e in r.findall('File') if 'matlab\\work' in e.get('absPath','') or 'traindata' in e.get('absPath','')])
for p in [Path('E:/QQ Files/Chat/Tencent Files/1439037249/FileRecv/附件5：哈尔滨工业大学中国国际大学生创新大赛主赛道团队项目申报书——龙之鸣——基于波纹管发音的新型乐器.docx'),Path('E:/QQ Files/Chat/Tencent Files/1439037249/FileRecv/旋转塑料波纹管发声特性的研究.pdf'),Path('E:/2022/download/U型波纹管声学传递损失的数值分析与实验验证_薛飞.pdf')]:extra.append(rec(p))
save('追加原件索引.json',extra)

models=[]
for p in Path('E:/COMSOL 6.2/test').glob('*.mph'):
 with zipfile.ZipFile(p) as z:
  r=E.fromstring(z.read('dmodel.xml'));inf=E.fromstring(z.read('modelinfo.xml'))
  nodes=[]
  for e in r.iter():
   if e.tag in ['Physics','PhysicsFeature','MultiphysicsCoupling','StudyFeature','GeomFeature','MeshFeature','ResultFeature']:
    ps=[c.attrib for c in e if c.tag in ['param','propertyValue']]
    nodes.append(dict(kind=e.tag,attributes=e.attrib,properties=ps))
  models.append(dict(path=p.as_posix(),root=r.attrib,modelinfo=inf.attrib,history=inf.find('historyInfo').attrib,physics=inf.find('physicsInfo').attrib,geometry=[x.attrib for x in inf.findall('geometryInfo/geom')],parameters=[e.attrib for e in r.findall('ModelParam/expressions')],nodes=nodes,solution_members=[dict(name=x.filename,bytes=x.file_size) for x in z.infolist() if 'solution' in x.filename],couplings=[dict(kind=e.tag,attributes=e.attrib) for e in r.iter() if 'fsi' in e.get('tag','') or 'FluidSolid' in e.get('op','')]))
save('COMSOL静态模型摘要.json',models)
print('models',[(Path(x['path']).name, x['physics'],[n['attributes'] for n in x['nodes'] if n['kind']=='StudyFeature']) for x in models])

figs=[]
def walk(x,path,found):
 if isinstance(x,dict):
  if x.get('type') in ['axes','graph2d.lineseries','line','text']:
   props=x.get('properties',{});item={'tree':path,'type':x.get('type'),'properties':{}}
   for k in ['String','XData','YData','DisplayName','XLim','YLim']:
    if k in props:
     v=props[k]
     item['properties'][k]=v.tolist() if isinstance(v,np.ndarray) else v
   found.append(item)
  for k,v in x.items():walk(v,path+'/'+k,found)
 elif isinstance(x,(list,np.ndarray)):
  for i,v in enumerate(x):walk(v,path+'/'+str(i),found)
for p in (SRC/'R11.6mm_r8.0mm').rglob('*.fig'):
 a=loadmat(p,simplify_cells=True);found=[];walk(a,'',found);figs.append(dict(path=p.as_posix(),objects=found))
save('FIG对象核读.json',figs)
print('figs',[(x['path'],[(o['type'], {k:(len(v) if isinstance(v,list) else v) for k,v in o['properties'].items()}) for o in x['objects']]) for x in figs])

# Newly decoded audio + isolated reimplementation. Does not run MATLAB source.
checks=[]
for group in ['01','02','03']:
 for i in range(1,6):
  p=SRC/f'R11.6mm_r8.0mm/100cm/R11.6mmr8mm_100cm_{group}_{i}.m4a'
  j=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
  s=next(s for s in j['streams'] if s['codec_type']=='audio');fs=int(s['sample_rate'])
  raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-af','pan=mono|c0=c0','-f','f32le','-'])
  y=np.frombuffer(raw,dtype='<f4').astype(float);N=len(y);a=abs(np.fft.rfft(y))/N;a[1:-1]*=2;k=int(a.argmax())
  checks.append(dict(path=p.as_posix(),fs=fs,source_channels=s['channels'],N=N,duration=N/fs,peak_hz=k*fs/N,peak_amplitude=float(a[k]),frequency_bin_hz=fs/N,source_creation=s.get('tags',{}).get('creation_time'),group=group,index=i))
save('音频FFT核对_本轮复算非历史结果.json',checks)
print('audio_checks',checks)

rows=json.loads((OUT/'原件索引.json').read_text(encoding='utf8'))
byhash=collections.defaultdict(list)
for r in rows:byhash[r['sha256']].append(r['path'])
save('字节去重摘要.json',dict(files=len(rows),unique=len(byhash),audio_files=sum(r['path'].lower().endswith(('.m4a','.mp3')) for r in rows),audio_unique=len({r['sha256'] for r in rows if r['path'].lower().endswith(('.m4a','.mp3'))}),duplicate_groups=[v for v in byhash.values() if len(v)>1]))
