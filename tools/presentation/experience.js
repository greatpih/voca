// Embedded inside the game's closure. All lesson callbacks belong to one problem.
let lessonRun=0,lessonTimers=[],explanationTimers=[];
const calmMotion=matchMedia('(prefers-reduced-motion: reduce)');
function resetLesson(){
  lessonRun++;
  lessonTimers.forEach(clearTimeout);lessonTimers=[];
  explanationTimers.forEach(clearTimeout);explanationTimers=[];
  clearTimeout(nextTimer);
  scene.querySelectorAll('[data-lesson-ui]').forEach(e=>e.remove());
  [PL,PR].forEach(P=>P.el.classList.remove('exchange-focus'));
  scene.classList.remove('is-exchanging');
  return lessonRun;
}
function lessonLater(fn,ms,run=lessonRun){
  const id=setTimeout(()=>{if(R&&run===lessonRun)fn();},ms);lessonTimers.push(id);return id;
}
function sourceEcho(it){
  if(calmMotion.matches)return;
  const r=sceneXY(it),echo=document.createElement('i');
  echo.className='source-echo'+(it.classList.contains('rod')?' rod-echo':'');
  echo.style.cssText=`left:${r.x}px;top:${r.y}px;width:${r.w}px;height:${r.h}px`;
  echo.dataset.lessonUi='';fx.appendChild(echo);setTimeout(()=>echo.remove(),950);
}
function exchangeFocus(mode,P){
  const grouping=mode!=='unpack';
  const veil=document.createElement('div'),card=document.createElement('div');
  veil.className='exchange-veil';card.className='exchange-card';
  veil.dataset.lessonUi='';card.dataset.lessonUi='';card.setAttribute('role','status');
  const dots=`<div class="exchange-side"><div class="exchange-dots">${'<i></i>'.repeat(10)}</div><span>낱개 <b>10</b>개</span></div>`;
  const rod='<div class="exchange-side"><div class="exchange-rod"></div><span>묶음 <b>1</b>개</span></div>';
  card.innerHTML=`<span class="exchange-title">${mode==='bundle'?'받아올림':mode==='group'?'10개 묶기':'받아내림'}</span>${grouping?dots:rod}<span class="exchange-arrow">→</span>${grouping?rod:dots}`;
  scene.append(veil,card);P.el.classList.add('exchange-focus');scene.classList.add('is-exchanging');
  const lights=[...card.querySelectorAll('.exchange-dots i')];
  return {count(n){lights.forEach((el,i)=>el.classList.toggle('lit',i<n));},
    convert(){card.classList.add('convert');lights.forEach(el=>el.classList.add('lit'));},
    close(){if(card.isConnected)P.el.classList.remove('exchange-focus');veil.remove();card.remove();if(!scene.querySelector('.exchange-card'))scene.classList.remove('is-exchanging');}};
}
function correctAccent(){
  const wash=document.createElement('div');wash.className='answer-wash';fx.appendChild(wash);setTimeout(()=>wash.remove(),1300);
  if(calmMotion.matches)return;
  for(let i=0;i<12;i++){const ray=document.createElement('i');ray.className='correct-ray';ray.style.setProperty('--a',i*30+'deg');ray.style.animationDelay=(i%3)*.035+'s';fx.appendChild(ray);setTimeout(()=>ray.remove(),1100);}
}
function retireAnswers(){
  const els=[...dock.querySelectorAll('.ans,.key')];
  if(calmMotion.matches)return Promise.resolve();
  return Promise.all(els.map((b,i)=>b.animate([{opacity:1,transform:'none'},{opacity:0,transform:'translateY(24px) scale(.92)'}],{duration:180,delay:Math.min(i*35,240),easing:'ease-in',fill:'forwards'}).finished.catch(()=>{})));
}
function animateExplanation(){
  explanationTimers.forEach(clearTimeout);explanationTimers=[];
  explain.dataset.step='0';
  const p=R.p,run=lessonRun;
  let labels;
  if(p.op==='count')labels=['묶음 세기','낱개 세기','모두 합치기'];
  else if(p.op==='add'&&O(p.a)+O(p.b)>=10)labels=['낱개 계산','받아올림','묶음 계산','정답'];
  else if(p.op==='sub'&&O(p.b)>O(p.a))labels=['묶음 풀기','낱개 계산','묶음 계산','정답'];
  else labels=['낱개 계산','묶음 계산','정답'];
  const nav=document.createElement('div');nav.className='explain-stages';nav.setAttribute('aria-label','풀이 순서');
  nav.innerHTML=labels.map((x,i)=>`<span>${i+1} ${x}</span>`).join('');explain.appendChild(nav);
  const rows=[...explain.querySelectorAll(p.op==='count'?'.cntrow':'.vsteps .st')];
  const times=labels.length===4?[850,1550,2300,3100]:[850,1950,3100];
  function select(i){
    [...nav.children].forEach((n,j)=>{n.classList.toggle('current',i===j);n.classList.toggle('done',j<i);});
    rows.forEach((n,j)=>{n.classList.toggle('current',i===j);n.classList.toggle('done',j<i);});
    explain.dataset.step=String(i+1);
  }
  times.forEach((ms,i)=>explanationTimers.push(setTimeout(()=>{if(R&&run===lessonRun)select(i);},calmMotion.matches?0:ms)));
}
function explainControls(){
  clearTimeout(nextTimer);
  const last=R.i>=R.probs.length-1,run=lessonRun;
  dock.innerHTML=`<button type="button" class="explain-control" id="explainReplay">풀이 다시 보기</button><button type="button" class="explain-control" id="explainPause" aria-pressed="${!!R.slowExplain}">${R.slowExplain?'자동으로 넘기기':'천천히 보기'}</button><button type="button" class="nextbtn" id="nextBtn"><div class="tm" id="nextTm"></div><span>${last?'결과 보기 ▶':'다음 문제 ▶'}</span></button>`;
  const go=()=>{if(!R||run!==lessonRun)return;clearTimeout(nextTimer);sfx('click');nextProblem();};
  let progress;
  const schedule=()=>{
    clearTimeout(nextTimer);if(progress)progress.cancel();
    if(R.slowExplain)return;
    progress=$('#nextTm').animate([{width:'0%'},{width:'100%'}],{duration:8000,easing:'linear',fill:'forwards'});
    nextTimer=setTimeout(()=>{if(!R||run!==lessonRun)return;if(modal.classList.contains('on')){schedule();return;}if(!window.__holdNext)go();},8000);
  };
  $('#nextBtn').onclick=go;
  $('#explainReplay').onclick=()=>{sfx('click');showExplain();};
  $('#explainPause').onclick=()=>{R.slowExplain=!R.slowExplain;const b=$('#explainPause');b.setAttribute('aria-pressed',String(R.slowExplain));b.textContent=R.slowExplain?'자동으로 넘기기':'천천히 보기';schedule();};
  schedule();
}
function rewardReveal(rewards){
  $('#scrClear').querySelectorAll('.reward-spotlight').forEach(el=>el.remove());
  const box=document.createElement('div');box.className='reward-spotlight';box.dataset.phase='entering';box.setAttribute('aria-label','학습 보상');
  const total=rewards.reduce((s,r)=>s+r[1],0);
  box.innerHTML=`<div class="reward-ribbon"><h2>오늘도 잘했어요!</h2><div class="earned"><svg viewBox="0 0 40 40" aria-hidden="true"><use href="#i-gem"/></svg><span>보석 +${total}</span></div><small>${rewards.map(r=>r[0]).join(' · ')}</small></div>`;
  $('#scrClear').appendChild(box);
  setTimeout(()=>{if(box.isConnected)box.dataset.phase='shown';},calmMotion.matches?0:2300);
  setTimeout(()=>box.remove(),4700);
}
