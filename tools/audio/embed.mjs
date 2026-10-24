import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url)),target=path.resolve(dir,'../../math.html');
const sounds={};for(const file of fs.readdirSync(path.resolve(dir,'../sfx')).filter(n=>n.endsWith('.mp3')).sort())sounds[file.slice(0,-4)]='data:audio/mpeg;base64,'+fs.readFileSync(path.resolve(dir,'../sfx',file)).toString('base64');
if(Object.keys(sounds).length!==15)throw Error('Expected 15 sound effects');
let html=fs.readFileSync(target,'utf8');
html=html.replace(/\/\*SFX-BEGIN\*\/[\s\S]*?\/\*SFX-END\*\//,()=> '/*SFX-BEGIN*/'+JSON.stringify(sounds)+'/*SFX-END*/');
html=html.replace(/\/\/ AUDIO-PLAYER-BEGIN[\s\S]*?\/\/ AUDIO-PLAYER-END/,()=> '// AUDIO-PLAYER-BEGIN\n'+fs.readFileSync(path.join(dir,'player.js'),'utf8')+'\n// AUDIO-PLAYER-END');
fs.writeFileSync(target,html);console.log('Embedded 15 soft sounds and bounded audio mixer.');
