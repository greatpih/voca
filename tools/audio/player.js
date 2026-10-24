// One mixer with headroom, a modest voice cap and cleanup on completion.
let ac=null,master=null,limiter=null;const SND={},audioVoices=[],lastSound=new Map();
function syncAudioSettings(){
  if(!ac||!master)return;
  const volume=Math.max(0,Math.min(1,Number(store.settings.volume??.8)));
  master.gain.setTargetAtTime(store.settings.sfx?volume:0,ac.currentTime,.015);
  if(!store.settings.sfx)for(const v of [...audioVoices]){try{v.source.stop();}catch(e){}}
}
function ensureAudio(){
  try{
    if(!ac){
      const C=window.AudioContext||window.webkitAudioContext;if(!C)return;
      ac=new C();master=ac.createGain();limiter=ac.createDynamicsCompressor();
      limiter.threshold.value=-18;limiter.knee.value=12;limiter.ratio.value=3;
      limiter.attack.value=.004;limiter.release.value=.12;
      master.connect(limiter);limiter.connect(ac.destination);syncAudioSettings();
      for(const [key,url]of Object.entries(window.SFX_SRC||{})){
        const raw=atob(url.slice(url.indexOf(',')+1)),bytes=new Uint8Array(raw.length);
        for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);
        ac.decodeAudioData(bytes.buffer).then(buffer=>{SND[key]=buffer;}).catch(()=>{});
      }
    }
    if(ac.state==='suspended')ac.resume();
  }catch(e){}
}
function sfx(name,o={}){
  if(!store.settings.sfx||!ac||!SND[name])return;
  try{
    const when=ac.currentTime+Math.max(0,o.delay||0);
    const gap=({land:.09,pick:.065,tick:.065,nom:.18,whoosh:.25})[name]||.035;
    if(Math.abs(when-(lastSound.get(name)??-100))<gap)return;
    lastSound.set(name,when);
    if(audioVoices.length>=8){
      const old=audioVoices.find(v=>v.start<=ac.currentTime)||audioVoices[0];
      audioVoices.splice(audioVoices.indexOf(old),1);
      old.gain.gain.setTargetAtTime(.0001,ac.currentTime,.006);
      try{old.source.stop(ac.currentTime+.02);}catch(e){}
    }
    const source=ac.createBufferSource(),gain=ac.createGain();source.buffer=SND[name];
    source.playbackRate.value=Math.max(.8,Math.min(1.7,o.rate||1));
    gain.gain.value=Math.max(0,Math.min(1,o.vol??1));
    source.connect(gain);gain.connect(master);
    const voice={source,gain,start:when};audioVoices.push(voice);
    source.onended=()=>{const i=audioVoices.indexOf(voice);if(i>=0)audioVoices.splice(i,1);source.disconnect();gain.disconnect();};
    source.start(when);
  }catch(e){}
}
const PENTA=[0,2,4,5,7,7,9,9,12,12,12,12,12];
const semi=n=>Math.pow(2,n/12);
document.addEventListener('pointerdown',ensureAudio,{passive:true});
