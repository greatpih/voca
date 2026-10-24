const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=require('node:path').resolve(__dirname,'..')+'/';
const assets=kind=>({manifest:JSON.parse(fs.readFileSync(root+kind+'/assets/manifest.json'))});
let now=1000,queue=[],observers=[],listeners={};
const images=[],els=[];
const motion={matches:false,addEventListener(){}};
function el(kind){
  const o={dataset:{character:kind,mood:'normal'},isConnected:true,lastIndex:-1,classList:{toggle(){},add(){}},closest(s){return s==='.screen'?{classList:{contains:()=>true}}:null;}};
  o.canvas={getContext:()=>({clearRect(){},drawImage(img,x,y){o.lastIndex=y/256*8+x/256;}})};
  o.querySelector=()=>o.canvas;return o;
}
els.push(el('tori'),el('bora'));
const doc={hidden:false,body:{},querySelectorAll:()=>els,addEventListener:(n,f)=>listeners[n]=f};
const ctx={window:{},document:doc,performance:{now:()=>now},matchMedia:()=>motion,console,
  PUPPY_ASSETS:assets('puppy'),CAT_ASSETS:assets('cat'),Image:class{constructor(){images.push(this)}},
  MutationObserver:class{constructor(fn){observers.push(fn)}observe(){}},
  requestAnimationFrame:fn=>{queue.push(fn);return queue.length;},cancelAnimationFrame:()=>{queue=[];}};
vm.runInNewContext(fs.readFileSync(root+'puppy/player.js','utf8'),ctx);
images.forEach(i=>i.onload());
function tick(t){now=t;const q=queue;queue=[];q.forEach(f=>f(now));}
const range=(kind,clip,i)=>{const c=ctx[kind==='tori'?'PUPPY_ASSETS':'CAT_ASSETS'].manifest.clips[clip];return i>=c.start&&i<c.start+c.count;};
tick(1000);assert.notEqual(els[0].lastIndex,els[1].lastIndex,'idle clocks differ');
for(const e of els)e.dataset.mood='happy';tick(1100);
assert(range('tori','happy',els[0].lastIndex));assert(!range('bora','happy',els[1].lastIndex),'cat responds after puppy');
tick(1400);assert(range('bora','happy',els[1].lastIndex));
for(const e of els)e.dataset.mood='normal';tick(1800);
assert(range('tori','happy',els[0].lastIndex),'short game timer must not cut off landing');
tick(3500);assert(range('tori','normal',els[0].lastIndex));assert(range('bora','normal',els[1].lastIndex));
for(const e of els)e.dataset.mood='happy';tick(3600);tick(6100);tick(9000);
assert(!range('tori','happy',els[0].lastIndex),'play reaction does not jump forever');
assert(!range('bora','happy',els[1].lastIndex));
els[1].dataset.mood='eat';tick(9100);assert(range('bora','eat',els[1].lastIndex));
const before=els[1].lastIndex;doc.hidden=true;listeners.visibilitychange();tick(14000);assert.equal(els[1].lastIndex,before);
doc.hidden=false;listeners.visibilitychange();tick(14050);assert(range('bora','eat',els[1].lastIndex),'background pause preserves response');
motion.matches=true;els[0].dataset.mood='wow';observers[0]([{type:'attributes'}]);tick(14100);
assert(range('tori','wow',els[0].lastIndex));assert.equal(queue.length,0,'reduced motion has no continuous RAF');
console.log('PASS: independent idle, staggered reaction, complete landing, one-shot stop, eating, background pause, reduced motion');
