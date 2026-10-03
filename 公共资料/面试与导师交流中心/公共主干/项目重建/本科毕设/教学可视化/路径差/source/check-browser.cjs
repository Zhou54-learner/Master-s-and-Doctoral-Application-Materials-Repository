const { chromium } = require('E:/CodexData/profile/cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');const path=require('path');const {pathToFileURL}=require('url');
(async()=>{
 const out=path.resolve(__dirname,'../output');
 const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1280,height:1100}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(out,'index.html')).href);
 for(const angle of [0,45,80,90]){
  await page.locator(`[data-angle="${angle}"]`).click();
  const g=await page.evaluate(()=>window.currentGeometry);
  if(g.angle!==angle || g.delta < -1e-10 || g.delta>1+1e-10)throw Error('Geometry/input failure');
  if(angle===0&&Math.abs(g.delta)>1e-10)throw Error('Zero-angle failure');
  if(angle===90&&Math.abs(g.delta-1)>1e-10)throw Error('Grazing failure');
 }
 await page.locator('[data-angle="45"]').click();
 await page.locator('#distance').evaluate(e=>{e.value='30';e.dispatchEvent(new Event('input',{bubbles:true}))});
 const far=await page.evaluate(()=>window.currentGeometry);
 if(far.d!==30||Math.abs(far.delta-far.approx)>.001)throw Error('Far-field check failure');
 await page.locator('#distance').evaluate(e=>{e.value='3';e.dispatchEvent(new Event('input',{bubbles:true}))});
 await page.screenshot({path:path.join(out,'interactive-preview.png'),fullPage:true});
 await page.setViewportSize({width:390,height:844});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 if(overflow)throw Error('Mobile horizontal overflow');
 await page.screenshot({path:path.join(out,'mobile-preview.png'),fullPage:true});
 if(errors.length)throw Error(errors.join('\n'));
 fs.writeFileSync(path.join(out,'browser-checks.json'),JSON.stringify({status:'PASS',angles:[0,45,80,90],far,errors,mobileOverflow:overflow},null,2));
 await browser.close();console.log('Browser checks PASS: angle presets, distance slider, limits, far-field comparison, mobile layout, no JS errors.');
})().catch(e=>{console.error(e);process.exit(1)});
