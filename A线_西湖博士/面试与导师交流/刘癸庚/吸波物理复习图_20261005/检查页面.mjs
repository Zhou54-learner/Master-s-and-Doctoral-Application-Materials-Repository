// 本地浏览器验收；只检查当前HTML，不运行任何科研程序。
import {spawn} from 'node:child_process';
import {readFileSync,writeFileSync,existsSync,mkdtempSync,mkdirSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {tmpdir} from 'node:os';
import {createHash} from 'node:crypto';
const base=dirname(fileURLToPath(import.meta.url)),file=resolve(base,'index.html'),out=resolve(base,'验收');
mkdirSync(out,{recursive:true});
const chrome=process.env.CHROME_PATH||['C:/Program Files/Google/Chrome/Application/chrome.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find(existsSync);
if(!chrome)throw Error('需要本地Chrome或Edge，可设置CHROME_PATH');
const profile=mkdtempSync(resolve(tmpdir(),'absorber-review-'));
const child=spawn(chrome,['--headless=new','--remote-debugging-pipe','--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run','--no-default-browser-check',`--user-data-dir=${profile}`,'about:blank'],{stdio:['ignore','ignore','ignore','pipe','pipe'],windowsHide:true});
let seq=0,buf='',session;const pending=new Map(),events=[];
child.stdio[4].setEncoding('utf8');child.stdio[4].on('data',s=>{buf+=s;let p;while((p=buf.indexOf('\0'))>=0){const raw=buf.slice(0,p);buf=buf.slice(p+1);if(!raw)continue;const m=JSON.parse(raw);if(m.id&&pending.has(m.id)){const q=pending.get(m.id);pending.delete(m.id);clearTimeout(q.timer);m.error?q.reject(Error(JSON.stringify(m.error))):q.resolve(m.result)}else events.push(m)}});
function send(method,params={},sid=session){return new Promise((resolve,reject)=>{const id=++seq,timer=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout: '+method))},15000);pending.set(id,{resolve,reject,timer});child.stdio[3].write(JSON.stringify({id,method,params,...(sid?{sessionId:sid}:{})})+'\0')})}
async function js(expression){const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value}
const checks=[];function assert(name,ok,detail){checks.push({name,ok,detail});if(!ok)throw Error(name+': '+JSON.stringify(detail))}
async function settle(){await js('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')}
async function go(id){await js(`location.hash=${JSON.stringify(id)}`);await settle()}
async function screenshot(name){const r=await send('Page.captureScreenshot',{format:'png'});writeFileSync(resolve(out,name),Buffer.from(r.data,'base64'))}
try{
const {targetId}=await send('Target.createTarget',{url:'about:blank'},null);session=(await send('Target.attachToTarget',{targetId,flatten:true},null)).sessionId;
await send('Page.enable');await send('Runtime.enable');await send('Network.enable');
await send('Page.navigate',{url:pathToFileURL(file).href});
await js('new Promise(r=>document.readyState==="complete"?r():window.addEventListener("load",r,{once:true}))');
const ids=await js('[...document.querySelectorAll("main section")].map(s=>s.id)');assert('14个主题',ids.length===14,ids);
const measurements=[];
for(const [width,height] of [[1440,900],[1600,1000],[1920,1080],[2048,1320],[390,844]]){
 await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});
 for(const theme of ['light','dark']){
  await js(`document.documentElement.dataset.theme=${JSON.stringify(theme)}`);
  for(const id of ids){await go(id);const m=await js('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,active:document.querySelector("section.active")?.id,nav:document.querySelector("nav a[aria-current=page]")?.hash,overflow:[...document.querySelectorAll("section.active p,section.active .formula,section.active td,section.active .card")].filter(e=>e.scrollWidth>e.clientWidth+2).map(e=>e.textContent.slice(0,60))})');measurements.push({width,height,theme,id,...m});assert('章节与导航 '+width+'/'+theme+'/'+id,m.active===id&&m.nav==='#'+id,m);assert('无横向溢出 '+width+'/'+theme+'/'+id,m.scrollWidth<=width&&m.overflow.length===0,m)}
 }
}
await send('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});await js('document.documentElement.dataset.theme="light"');await go('overview');await screenshot('总览_1440_浅色.png');
await go('impedance');await screenshot('输入阻抗_1440_浅色.png');
await go('energy');await js('document.documentElement.dataset.theme="dark"');await screenshot('能量账_1440_深色.png');
await send('Emulation.setDeviceMetricsOverride',{width:2048,height:1320,deviceScaleFactor:1,mobile:false});await go('overview');await screenshot('总览_2048_深色.png');
await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:false});await go('ohmic');await js('document.documentElement.dataset.theme="light"');await screenshot('手机_390_浅色.png');
const navigation=await js(`document.querySelector('nav a[href="#pattern"]').click();true`);await settle();assert('真实链接导航',await js('document.querySelector("section.active").id==="pattern"'),navigation);
await js('document.querySelector("#search").value="377";document.querySelector("#search").dispatchEvent(new Event("input"))');assert('搜索可见章节',await js('[...document.querySelectorAll("nav a")].filter(a=>getComputedStyle(a).display!=="none").length')<14,await js('document.querySelector("#searchStatus").textContent'));
await go('impedance');await js('document.querySelector("#matchReset").click()');assert('匹配点R=0',await js('document.querySelector("#reflectValue").textContent==="0.00%"'));
await js('document.querySelector("#rin").value=0;document.querySelector("#xin").value=0;document.querySelector("#rin").dispatchEvent(new Event("input"))');assert('零输入阻抗全反射',await js('document.querySelector("#reflectValue").textContent==="100.00%"'));
await go('energy');for(const val of [0,.12,.92]){await js(`document.querySelector('#crossPower').value=${val};document.querySelector('#crossPower').dispatchEvent(new Event('input'))`);const a=await js('parseFloat(document.querySelector("#totalA").textContent)');assert('能量账 '+val,Math.abs(a-(.92-val)*100)<.001,a)}
await go('height');const wavelength=await js('parseFloat(document.querySelector("#lambdaValue").textContent)');assert('10GHz空气波长',Math.abs(wavelength-29.9792458)<.01,wavelength);
const refs=await js('[...document.querySelectorAll("a[href]")].map(a=>a.getAttribute("href")).filter(h=>!h.startsWith("http")&&!h.startsWith("#"))');for(const ref of refs)assert('本地链接 '+ref,existsSync(resolve(base,decodeURIComponent(ref))));
const internal=await js(`[...document.querySelectorAll('a[href^="#"]')].map(a=>a.getAttribute("href").slice(1)).filter(id=>!document.getElementById(id))`);assert('所有页内链接有效',internal.length===0,internal);
await send('Emulation.setEmulatedMedia',{media:'print'});assert('打印展示全部章节',await js('[...document.querySelectorAll("section")].every(s=>getComputedStyle(s).display!=="none")'));await send('Emulation.setEmulatedMedia',{media:''});
const errors=events.filter(e=>e.method==='Runtime.exceptionThrown');assert('无运行异常',errors.length===0,errors);
const remote=events.filter(e=>e.method==='Network.requestWillBeSent'&&/^https?:/.test(e.params.request.url));assert('打开页面无外部网络依赖',remote.length===0,remote.map(e=>e.params.request.url));
const html=readFileSync(file);const receipt={artifact:'../index.html',sha256:createHash('sha256').update(html).digest('hex'),bytes:html.length,checks:checks.length,passed:checks.filter(c=>c.ok).length,viewportThemeChapterCombinations:measurements.length,measurements,visualReview:'pending',notes:'正文分章节可纵向滚动；不以隐藏内容换取首屏容纳。截图需人工检查。'};
writeFileSync(resolve(out,'页面验收.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({ok:true,sha256:receipt.sha256,checks:receipt.checks,combinations:measurements.length,visualReview:receipt.visualReview}));
}catch(e){writeFileSync(resolve(out,'页面失败记录.json'),JSON.stringify({error:String(e),checks},null,2));throw e}finally{try{await send('Browser.close',{},null)}catch{}child.kill()}
