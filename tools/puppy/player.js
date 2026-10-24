/* Independent idle clocks and character-specific, complete one-shot reactions. */
window.Puppy25 = (() => {
  'use strict';
  const models = {
    tori: {assets:PUPPY_ASSETS,label:'강아지 토리',offset:510,curiousAt:5.1,period:11.7,delay:0,cheerEvery:10700},
    bora: {assets:CAT_ASSETS,label:'고양이 보라',offset:2370,curiousAt:8.4,period:15.3,delay:170,cheerEvery:13900}
  };
  for(const m of Object.values(models)){m.meta=m.assets.manifest;m.atlas=new Image();m.ready=false;}
  const instances=new Map(), reduceMotion=matchMedia('(prefers-reduced-motion: reduce)');
  const priorities={lookLeft:1,lookRight:1,eat:2,wow:3,happy:4,sad:4};
  let raf=0,lastTick=0,hiddenAt=0;
  function markup(kind='tori') {
    const {assets,label}=models[kind];
    return `<span class="chr puppy25" data-character="${kind}" data-mood="normal" role="img" aria-label="${label}"><img class="puppy-poster" src="${assets.poster}" alt="" draggable="false"><canvas width="256" height="256" aria-hidden="true"></canvas></span>`;
  }
  function paws(kind='tori') {
    const {assets}=models[kind];
    return `<span class="puppy-paws" aria-hidden="true"><img class="p p1" src="${assets.paw}" alt="" draggable="false"><img class="p p2" src="${assets.paw}" alt="" draggable="false"></span>`;
  }
  function attach() {
    document.querySelectorAll('.puppy25').forEach(el=>{
      if(instances.has(el))return;
      const canvas=el.querySelector('canvas'),bust=!!el.closest('#chTori, #chBora'),model=models[el.dataset.character||'tori'];
      canvas.width=model.meta.cell;
      canvas.height=bust?Math.round(model.meta.cell*model.meta.crop[3]/model.meta.crop[2]):model.meta.cell;
      el.classList.toggle('puppy-bust',bust);
      const tablePaws=bust?document.getElementById(el.dataset.character==='bora'?'pawsBora':'pawsTori'):null;
      instances.set(el,{el,model,canvas,ctx:canvas.getContext('2d'),bust,tablePaws,action:null,mood:'',hop:'',look:'',frame:-1,visible:false,
        idleEpoch:performance.now()-model.offset,showcase:!!el.closest('#splashChars, #scrClear'),nextCheer:0});
    });
    for(const [el] of instances)if(!el.isConnected)instances.delete(el);
    wake();
  }
  function visible(el){const screen=el.closest('.screen');return el.isConnected&&(!screen||screen.classList.contains('on'));}
  function startAction(s,clip,now){
    const info=s.model.meta.clips[clip];if(!info)return;
    if(s.action){
      if(priorities[clip]<priorities[s.action.clip])return;
      // Fast taps should not rewind the same response before it can be seen.
      if(clip===s.action.clip&&now-s.action.start<350)return;
    }
    const delay=clip==='eat'||clip.startsWith('look')?0:s.model.delay;
    s.action={clip,start:now+delay,duration:info.count/s.model.meta.fps*1000};
  }
  function idleFrame(s,now){
    const {meta,curiousAt,period}=s.model,seconds=(now-s.idleEpoch)/1000;
    const cycle=((seconds%period)+period)%period,curious=meta.clips.curious;
    if(curious&&cycle>=curiousAt&&cycle<curiousAt+curious.count/meta.fps)return curious.start+Math.floor((cycle-curiousAt)*meta.fps);
    const normal=meta.clips.normal,interval=normal.count/meta.fps+1.3;
    const local=Math.floor(((seconds%interval+interval)%interval)*meta.fps);
    return normal.start+Math.min(normal.count-1,local);
  }
  function draw(s,now){
    const {meta,atlas}=s.model,mood=s.el.dataset.mood||'normal',hop=s.el.dataset.hop||'',look=s.el.dataset.look||'';
    if(!s.visible){s.mood='';s.hop='';s.look='';s.action=null;s.nextCheer=now+s.model.cheerEvery;}
    if(s.action&&now>=s.action.start+s.action.duration){s.action=null;s.idleEpoch=now;}
    if((mood!==s.mood||hop!==s.hop)&&priorities[mood])startAction(s,mood,now);
    if(look!==s.look&&look&&mood==='normal')startAction(s,look==='left'?'lookLeft':'lookRight',now);
    s.mood=mood;s.hop=hop;s.look=look;s.visible=true;
    if(s.showcase&&now>s.nextCheer&&!s.action){startAction(s,'happy',now);s.nextCheer=now+s.model.cheerEvery;}
    let index=idleFrame(s,now),motion=index>=meta.clips.curious.start&&index<meta.clips.curious.start+meta.clips.curious.count?'curious':'normal';
    if(s.action&&now>=s.action.start){const clip=meta.clips[s.action.clip];motion=s.action.clip;index=clip.start+Math.min(clip.count-1,Math.floor((now-s.action.start)*meta.fps/1000));}
    if(reduceMotion.matches){const clip=meta.clips[mood]||meta.clips.normal;index=clip.start+(clip.poster||0);motion=mood;}
    if(s.tablePaws)s.tablePaws.dataset.motion=motion;
    if(index===s.frame)return;s.frame=index;
    const x=index%meta.columns*meta.cell,y=Math.floor(index/meta.columns)*meta.cell,ctx=s.ctx;
    ctx.clearRect(0,0,s.canvas.width,s.canvas.height);ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
    if(s.bust){const [cx,cy,cw,ch]=meta.crop;ctx.drawImage(atlas,x+cx,y+cy,cw,ch,0,0,s.canvas.width,s.canvas.height);}
    else ctx.drawImage(atlas,x,y,meta.cell,meta.cell,0,0,s.canvas.width,s.canvas.height);
    s.el.classList.add('puppy-ready');
  }
  function tick(now){
    raf=0;if(document.hidden)return;
    let active=false;const due=now-lastTick>=1000/24-2;
    for(const s of instances.values()){
      if(s.model.ready&&visible(s.el)){active=true;if(due)draw(s,now);}else s.visible=false;
    }
    if(due)lastTick=now;
    if(active&&!reduceMotion.matches)raf=requestAnimationFrame(tick);
  }
  function wake(){if(Object.values(models).some(m=>m.ready)&&!document.hidden&&!raf){lastTick=0;raf=requestAnimationFrame(tick);}}
  function hop(el){if(el)el.dataset.hop=String((Number(el.dataset.hop)||0)+1);wake();}
  function look(el,side){if(el)el.dataset.look=side||'';wake();}
  for(const m of Object.values(models)){
    m.atlas.onload=()=>{m.ready=true;attach();};
    m.atlas.onerror=()=>console.warn(`${m.label}: animation unavailable; static preview retained.`);
    m.atlas.src=m.assets.atlas;
  }
  new MutationObserver(records=>{if(records.some(r=>r.type==='childList'))attach();else wake();})
    .observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['data-mood','data-look','data-hop','class']});
  document.addEventListener('visibilitychange',()=>{
    if(document.hidden){hiddenAt=performance.now();if(raf){cancelAnimationFrame(raf);raf=0;}}
    else{const pause=hiddenAt?performance.now()-hiddenAt:0;for(const s of instances.values()){s.idleEpoch+=pause;s.nextCheer+=pause;if(s.action)s.action.start+=pause;}hiddenAt=0;wake();}
  });
  reduceMotion.addEventListener('change',()=>{for(const s of instances.values())s.frame=-1;wake();});
  attach();return Object.freeze({markup,paws,hop,look});
})();
