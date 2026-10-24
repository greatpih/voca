const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const sources=[];
const param=()=>({value:0,setTargetAtTime(v){this.value=v;}});
const node=()=>({gain:param(),connect(){},disconnect(){this.disconnected=true;}});
class AudioContext{
  constructor(){this.currentTime=0;this.state='running';this.destination={};}
  createGain(){return node();}
  createDynamicsCompressor(){return {...node(),threshold:param(),knee:param(),ratio:param(),attack:param(),release:param()};}
  createBufferSource(){const s={...node(),playbackRate:param(),start(t){this.when=t;},stop(){this.stopped=true;this.onended?.();}};sources.push(s);return s;}
  decodeAudioData(){return Promise.resolve({});}
}
const context=vm.createContext({window:{AudioContext,SFX_SRC:{}},store:{settings:{sfx:true,volume:.8}},document:{addEventListener(){}},Uint8Array,atob,assert,sources});
vm.runInContext(fs.readFileSync(__dirname+'/player.js','utf8')+`
ensureAudio(); SND.land={}; SND.tick={};
assert.equal(master.gain.value,.8);
sfx('land'); sfx('land'); assert.equal(audioVoices.length,1,'duplicate landing is throttled');
for(let i=1;i<=20;i++){ac.currentTime=i*.1;sfx('tick',{rate:12});}
assert.equal(audioVoices.length,8,'live voice cap');
assert.equal(sources.at(-1).playbackRate.value,1.7,'pitch ceiling');
assert.ok(sources[0].stopped&&sources[0].disconnected,'evicted voices release nodes');
const last=audioVoices.at(-1);last.source.onended();assert.equal(audioVoices.length,7);assert.ok(last.gain.disconnected);
store.settings.volume=.45;syncAudioSettings();assert.equal(master.gain.value,.45);
store.settings.sfx=false;syncAudioSettings();assert.equal(audioVoices.length,0);assert.equal(master.gain.value,0);
const n=sources.length; sfx('tick');assert.equal(sources.length,n,'mute prevents new voices');
store.settings.sfx=true;syncAudioSettings();assert.equal(master.gain.value,.45);
`,context);
console.log('PASS: throttle, pitch ceiling, voice limit, completion cleanup, volume and mute.');
