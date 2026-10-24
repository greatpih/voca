// Deterministic soft mallet/wood cues. No sampled instruments or external assets.
import fs from 'node:fs';
import path from 'node:path';
import cp from 'node:child_process';
import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url));
const out=path.resolve(process.argv[2]||path.join(dir,'../sfx'));
const work=path.resolve(process.argv[3]||path.join(out,'build'));
fs.mkdirSync(out,{recursive:true});fs.mkdirSync(work,{recursive:true});
const SR=44100;let seed=7319;
const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296*2-1;};
const signal=(duration,fn)=>Float64Array.from({length:Math.round(duration*SR)},(_,i)=>fn(i/SR,i));
const mix=(...parts)=>{const n=Math.max(...parts.map(([t,x])=>Math.round(t*SR)+x.length));const y=new Float64Array(n);for(const [t,x]of parts){const at=Math.round(t*SR);for(let i=0;i<x.length;i++)y[at+i]+=x[i];}return y;};
function mallet(f,d=.40){return signal(d,t=>{
  const attack=1-Math.exp(-t/0.003);
  return attack*(Math.sin(2*Math.PI*f*t)*Math.exp(-t/.095)+.20*Math.sin(2*Math.PI*f*2.76*t)*Math.exp(-t/.028)+.045*Math.sin(2*Math.PI*f*4*t)*Math.exp(-t/.016));
});}
function wood(f,d=.12){let low=0;return signal(d,t=>{low+=.13*(random()-low);return (1-Math.exp(-t/.0015))*(Math.sin(2*Math.PI*f*t)*Math.exp(-t/.018)+low*.5*Math.exp(-t/.006));});}
function air(d=.18,cutoff=950){let low=0;const a=1-Math.exp(-2*Math.PI*cutoff/SR);return signal(d,t=>{low+=a*(random()-low);return low*Math.sin(Math.PI*t/d)**2;});}
const notes=(freqs,spacing=.09,d=.4)=>mix(...freqs.map((f,i)=>[i*spacing,mallet(f,d)]));
const sounds={
 click:[wood(360,.09),.15],pick:[wood(510,.11),.18],land:[wood(220,.13),.17],
 tick:[mallet(392,.24),.22],whoosh:[air(.18),.11],
 bundle:[notes([392,494,587],.10,.42),.28],unpack:[notes([587,494,392],.08,.32),.24],
 nom:[mix([0,air(.045,1250)],[.065,air(.040,1100)],[.125,wood(190,.065)]),.14],
 correct:[notes([523.25,659.25,783.99],.10,.48),.31],wrong:[notes([392,329.63],.14,.26),.18],
 fanfare:[mix([0,notes([392,493.88,587.33],.14,.42)],[.52,notes([523.25,659.25,783.99],.06,.55)]),.34],
 star:[mallet(659.25,.4),.23],gem:[notes([659.25,783.99],.09,.40),.25],
 boop:[notes([329.63,293.66],.08,.2),.16],wipe:[mix([0,air(.26,800)],[.15,mallet(523.25,.28)]),.13]
};
const metrics={};
const processRecord={pid:process.pid,startTime:new Date(Date.now()-process.uptime()*1000).toISOString(),executable:process.execPath,cwd:process.cwd(),purpose:'Generate 15 soft local game sound effects',keepRunning:false,children:[]};
const processPath=path.join(work,'audio-process.json');
fs.writeFileSync(processPath,JSON.stringify(processRecord,null,2));
for(const [name,[samples,peak]]of Object.entries(sounds)){
  let max=0;for(const x of samples)max=Math.max(max,Math.abs(x));
  const pcm=Buffer.alloc(samples.length*2);let energy=0,actual=0;
  for(let i=0;i<samples.length;i++){
    const fade=Math.min(1,i/(SR*.002),(samples.length-1-i)/(SR*.012));
    const x=samples[i]/max*peak*Math.max(0,fade);energy+=x*x;actual=Math.max(actual,Math.abs(x));pcm.writeInt16LE(Math.round(x*32767),i*2);
  }
  const header=Buffer.alloc(44);header.write('RIFF');header.writeUInt32LE(36+pcm.length,4);header.write('WAVEfmt ',8);header.writeUInt32LE(16,16);header.writeUInt16LE(1,20);header.writeUInt16LE(1,22);header.writeUInt32LE(SR,24);header.writeUInt32LE(SR*2,28);header.writeUInt16LE(2,32);header.writeUInt16LE(16,34);header.write('data',36);header.writeUInt32LE(pcm.length,40);
  const wav=path.join(work,name+'.wav');fs.writeFileSync(wav,Buffer.concat([header,pcm]));
  const r=cp.spawnSync('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',wav,'-codec:a','libmp3lame','-b:a','96k',path.join(out,name+'.mp3')],{windowsHide:true,encoding:'utf8'});
  processRecord.children.push({pid:r.pid,executable:'ffmpeg',purpose:'Encode '+name,exitCode:r.status});
  if(r.status!==0)throw Error(r.stderr);
  metrics[name]={seconds:samples.length/SR,peakDbfs:20*Math.log10(actual),rmsDbfs:20*Math.log10(Math.sqrt(energy/samples.length))};
}
processRecord.finishedAt=new Date().toISOString();fs.writeFileSync(processPath,JSON.stringify(processRecord,null,2));
fs.writeFileSync(path.join(work,'levels.json'),JSON.stringify(metrics,null,2));
console.log('Generated 15 dry, short cues with distinct low peaks.');
