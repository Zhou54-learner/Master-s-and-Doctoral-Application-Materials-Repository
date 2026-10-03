from pathlib import Path
from math import sin, cos, radians, hypot
import json

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)

def geometry(theta, distance):
    x, z = distance*sin(radians(theta)), distance*cos(radians(theta))
    a, b = hypot(x+.5,z), hypot(x-.5,z)
    return x,z,a,b,a-b

def text(x,y,value,size=20,color='#253248',anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{value}</text>'

def line(x1,y1,x2,y2,color,width=3,dash=''):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'

parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1260" height="650" viewBox="0 0 1260 650" role="img" aria-labelledby="title desc">',
'<title id="title">相邻单元到同一观察点：路程差怎样变化</title><desc id="desc">精确有限距离几何。A、B间距p，观察点P距中点O为3p，分别取与法线夹角0、45、80度。蓝线AP，橙线BP。路径差始终不超过p。</desc>',
'<rect width="1260" height="650" fill="#f4f7fb"/><g font-family="Microsoft YaHei,Arial,sans-serif">',
text(32,45,'相邻单元到同一观察点：到底差了多少路？',28),
text(32,78,'蓝线 = AP    橙线 = BP    A、B 间距固定为 p；三图都取 OP = 3p，按同一比例绘制。',18,'#526078')]
for idx,angle in enumerate([0,45,80]):
    tx=25+idx*413
    x,z,a,b,diff=geometry(angle,3)
    ox,oy,scale=91,285,73
    ax,bx=ox-scale*.5,ox+scale*.5
    px,py=ox+x*scale,oy-z*scale
    parts += [f'<g id="panel-{idx}" transform="translate({tx},110)">',
      '<rect width="385" height="456" rx="16" fill="white" stroke="#dae2ed"/>',
      text(19,35,['① 正上方：0°','② 斜上方：45°','③ 接近沿表面：80°'][idx],23),
      line(23,oy,360,oy,'#bac5d3',2),line(ox,oy,ox,65,'#a9b5c5',1.5,'5 6'),
      text(20,90,'法线',15,'#758298'),
      line(ax,oy,px,py,'#2073c8',4),line(bx,oy,px,py,'#dd7830',4),
      f'<circle cx="{ax}" cy="{oy}" r="6" fill="#2073c8"/><circle cx="{bx}" cy="{oy}" r="6" fill="#dd7830"/><circle cx="{px}" cy="{py}" r="7" fill="#8056c9"/>',
      text(ax-9,oy+27,'A',19,'#2073c8'),text(bx+2,oy+27,'B',19,'#dd7830'),text(ox,oy+27,'O',15,'#758298','middle'),
      text(px+14 if angle==0 else px-10,py+15 if angle==0 else py-15,'观察点 P',18,'#8056c9','start' if angle==0 else 'end'),
      line(ax,oy+46,bx,oy+46,'#67758a',2),line(ax,oy+40,ax,oy+52,'#67758a',2),line(bx,oy+40,bx,oy+52,'#67758a',2),
      text(ox,oy+71,'AB = p',18,'#526078','middle'),
      text(19,393,f'AP = {a:.3f}p    BP = {b:.3f}p',19),
      text(19,432,f'路程差 = {diff:.3f}p',23,'#8056c9'),'</g>']
parts += [text(32,604,'为什么不会超过 p？直达 A→P，总不会比绕路 A→B→P 更长。',22),
          text(32,635,'因此 AP ≤ p + BP，即 AP − BP ≤ p。交换 A、B，得到 |AP − BP| ≤ p。',19,'#526078'),'</g></svg>']
svg=''.join(parts)
(ROOT/'source'/'figure.svg').write_text(svg,encoding='utf-8')
(OUT/'figure.svg').write_text(svg,encoding='utf-8')

HTML=r'''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>两条传播路径的路程差</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f4f7fb;color:#253248;font-family:"Microsoft YaHei",system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:28px 22px}h1{font-size:29px;margin:0 0 10px}p{line-height:1.8;margin:8px 0}.muted{color:#617087}.panel{background:white;border:1px solid #dbe3ee;border-radius:16px;padding:20px;margin-top:18px}.controls{display:grid;grid-template-columns:1fr 1fr;gap:24px}label{display:block;font-weight:600}input[type=range]{width:100%;margin:18px 0;accent-color:#8056c9}button{border:1px solid #cdd7e5;background:#fff;border-radius:8px;padding:9px 14px;color:#253248;cursor:pointer;margin:2px}button:hover{background:#edf0fa}button:focus-visible,input:focus-visible{outline:3px solid #8056c9;outline-offset:3px}svg{width:100%;height:auto;display:block}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.card{background:#f4f7fb;border-radius:10px;padding:14px}.num{font-size:25px;font-weight:650;margin:6px 0}.blue{color:#2073c8}.orange{color:#dd7830}.purple{color:#8056c9}.explain{border-left:4px solid #8056c9;padding-left:16px}.formula{font-size:21px;line-height:1.8}summary{cursor:pointer;font-weight:600}small{line-height:1.7;display:block}@media(max-width:650px){.controls{grid-template-columns:1fr;gap:8px}.cards{grid-template-columns:1fr 1fr}main{padding:18px 12px}h1{font-size:24px}.panel{padding:14px}}
</style><main>
<h1>同一个观察点，两条路差多少？</h1>
<p>固定两个相邻单元 A、B，间距为 <b>p</b>。拖动角度，让同一个观察点 P 绕中点 O 移动。蓝色看 AP，橙色看 BP。</p>
<p class="muted">一般波动几何教学。不是 CST 仿真或毕设历史结果。所有长度用单元间距 p 作单位。</p>
<section class="panel controls"><div><label for="angle">观察角度 θ：<output id="angleValue">45°</output></label><input id="angle" type="range" min="0" max="90" value="45" step="1"><small>从向上的法线量起：0° 在正上方；90° 沿阵列表面。</small><div><button data-angle="0">正上方 0°</button><button data-angle="45">斜上方 45°</button><button data-angle="80">接近表面 80°</button><button data-angle="90">沿表面 90°</button></div></div>
<div><label for="distance">观察距离 D / p：<output id="distanceValue">3</output></label><input id="distance" type="range" min="2" max="30" value="3" step="1"><small>D 是中点 O 到 P 的距离。增大 D，可比较精确路程差与远处近似。图会自动缩放，实际间距 p 保持不变。</small></div></section>
<section class="panel"><svg id="scene" viewBox="0 0 1000 450" role="img" aria-label="A、B到同一个观察点P的真实路径"></svg>
<div class="cards" aria-live="polite"><div class="card blue">蓝色路径 AP<div id="la" class="num"></div></div><div class="card orange">橙色路径 BP<div id="lb" class="num"></div></div><div class="card purple">精确差值 AP − BP<div id="delta" class="num"></div></div><div class="card">远处近似 p sinθ<div id="approx" class="num"></div></div></div>
<p id="meaning" class="explain"></p><small class="muted">所有路径是直线距离；屏幕上的线段按几何比例绘制。90° 时两条路径共线，虚线橙色用于显露重合部分。</small></section>
<section class="panel"><h2 style="font-size:21px;margin-top:0">不超过 p，是三角形的性质</h2><p>从 A 到同一个 P，可以直接走，也可以先走到 B，再到 P。</p><p class="formula">直达 AP ≤ 绕路 AB + BP = p + BP<br>所以 AP − BP ≤ p</p><p>交换 A、B 再做一次，就得到 <b>|AP − BP| ≤ p</b>。这个上限对近处、远处都成立；90° 共线且 P 在 B 右侧时取等号。</p><details><summary>远处近似为什么是 p sinθ？</summary><p>观察点很远时，两条传播方向近似平行。相邻间距在观察方向上的投影就是额外路程，因此 Δℓ ≈ p sinθ。有限距离图中两条线并不完全平行，所以卡片分别显示精确值与近似值。</p><p>本图 θ=0° 时，P 恰在 AB 的中垂线上，因此 AP=BP 严格成立，不只是近似。</p><p class="muted">符号：Δℓ 为路程差；p 为单元间距；D=OP 为观察距离，三者均是长度。θ 为与法线的夹角。数值显示除以 p 后的比例。</p></details></section>
</main><script>
function distances(angle,d){const t=angle*Math.PI/180,x=d*Math.sin(t),z=d*Math.cos(t),a=Math.hypot(x+.5,z),b=Math.hypot(x-.5,z);return{x,z,a,b,delta:a-b,approx:Math.sin(t)}}
function draw(){
 const angle=Number(document.getElementById('angle').value),d=Number(document.getElementById('distance').value),g=distances(angle,d);
 const scale=Math.min(290/d,680/(d+.5)),ox=195,oy=345,ax=ox-scale/2,bx=ox+scale/2,px=ox+g.x*scale,py=oy-g.z*scale;
 const line=(x,y,X,Y,color,w=3,dash='')=>`<line x1="${x}" y1="${y}" x2="${X}" y2="${Y}" stroke="${color}" stroke-width="${w}" ${dash?'stroke-dasharray="'+dash+'"':''}/>`;
 const label=(x,y,s,c='#526078',anchor='start',size=19)=>`<text x="${x}" y="${y}" fill="${c}" text-anchor="${anchor}" font-size="${size}" font-family="Microsoft YaHei,Arial,sans-serif">${s}</text>`;
 const arcR=53,ex=ox+arcR*Math.sin(angle*Math.PI/180),ey=oy-arcR*Math.cos(angle*Math.PI/180);
 document.getElementById('scene').innerHTML=
 line(45,oy,930,oy,'#b5c1d1',2)+line(ox,oy,ox,25,'#a5b1c3',2,'6 7')+label(ox-20,70,'法线','#526078','end')+
 line(ox,oy,px,py,'#c5cdd8',1,'3 5')+
 line(ax,oy,px,py,'#2073c8',5)+line(bx,oy,px,py,'#dd7830',4,angle===90?'10 6':'')+
 (angle>0?`<path d="M ${ox} ${oy-arcR} A ${arcR} ${arcR} 0 0 1 ${ex} ${ey}" fill="none" stroke="#8056c9" stroke-width="2"/>`:'')+
 label(ox+75*Math.sin(angle*Math.PI/360),oy-75*Math.cos(angle*Math.PI/360),'θ','#8056c9','middle')+
 `<circle cx="${ax}" cy="${oy}" r="7" fill="#2073c8"/><circle cx="${bx}" cy="${oy}" r="7" fill="#dd7830"/><circle cx="${px}" cy="${py}" r="8" fill="#8056c9"/>`+
 label(ax-12,oy+31,'A','#2073c8','end')+label(bx+12,oy+31,'B','#dd7830')+label(ox,oy+31,'O','#758298','middle',16)+label(px+14,py-12,'同一个观察点 P','#8056c9')+
 line(ax,400,bx,400,'#67758a',2)+line(ax,393,ax,407,'#67758a',2)+line(bx,393,bx,407,'#67758a',2)+label(ox,432,'AB = p','#526078','middle')+
 label(610,420,'D = OP = '+d+'p','#758298');
 document.getElementById('angleValue').textContent=angle+'°';document.getElementById('distanceValue').textContent=d;
 for(const [id,value] of [['la',g.a],['lb',g.b],['delta',g.delta],['approx',g.approx]])document.getElementById(id).textContent=value.toFixed(4)+'p';
 document.getElementById('meaning').textContent=angle===0?'P 在 A、B 的中垂线上：两条路严格等长，路程差为 0。':angle===90?'A、B、P 共线：从 A 出发比从 B 出发恰好多走 AB，所以路程差恰好是 p。':`现在从 A 出发多走 ${g.delta.toFixed(4)}p。朝表面方向转动，差值逐渐接近 p，但不会超过它。`;
 window.currentGeometry={angle,d,...g};
}
document.querySelectorAll('input').forEach(e=>e.addEventListener('input',draw));document.querySelectorAll('[data-angle]').forEach(e=>e.addEventListener('click',()=>{document.getElementById('angle').value=e.dataset.angle;draw()}));draw();
</script></html>'''
(OUT/'index.html').write_text(HTML,encoding='utf-8')

checks=[]
for d in [2,3,10,30,100]:
    vals=[geometry(a,d)[4] for a in range(91)]
    assert abs(vals[0])<1e-12 and abs(vals[-1]-1)<1e-12
    assert all(-1e-12<=v<=1+1e-12 for v in vals)
    assert all(vals[i]<=vals[i+1]+1e-12 for i in range(90))
    checks.append({'D_over_p':d,'zero':vals[0],'ninety':vals[-1],'max_error_vs_sine':max(abs(vals[a]-sin(radians(a))) for a in range(91))})
(OUT/'geometry-checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print('Created SVG and offline interactive HTML; geometry checks passed.')
