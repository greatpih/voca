import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url));
if(!process.argv[2])throw Error('Usage: node tools/art/package.mjs <render-directory>');
const from=path.resolve(process.argv[2]),to=path.join(dir,'assets');fs.mkdirSync(to,{recursive:true});
const rec={pid:process.pid,startTime:new Date(Date.now()-process.uptime()*1000).toISOString(),executable:process.execPath,cwd:process.cwd(),purpose:'Encode rendered bakery assets',keepRunning:false,children:[]};
for(const file of fs.readdirSync(from).filter(n=>n.endsWith('.png'))){
  const r=cp.spawnSync('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',path.join(from,file),'-c:v','libwebp','-quality','92','-compression_level','6',path.join(to,file.replace('.png','.webp'))],{windowsHide:true,encoding:'utf8'});
  rec.children.push({pid:r.pid,executable:'ffmpeg',purpose:'Encode '+file,exitCode:r.status});if(r.status!==0)throw Error(r.stderr);
}
rec.finishedAt=new Date().toISOString();fs.writeFileSync(path.join(from,'encode-process.json'),JSON.stringify(rec,null,2));
