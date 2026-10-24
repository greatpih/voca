import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url)),target=path.resolve(dir,'../../math.html');
const assets={};for(const file of fs.readdirSync(path.join(dir,'assets')).filter(n=>n.endsWith('.webp'))){assets[file.slice(0,-5)]='data:image/webp;base64,'+fs.readFileSync(path.join(dir,'assets',file)).toString('base64');}
if(Object.keys(assets).length!==12)throw Error('Expected 12 bakery assets');
const block=`<!-- BAKERY-ASSETS-BEGIN -->\n<script>\nconst BAKERY_ASSETS=${JSON.stringify(assets)};\nfor(const key of ['room-play','room-wide','plate-mint','plate-lavender'])document.documentElement.style.setProperty('--bakery-'+key,'url("'+BAKERY_ASSETS[key]+'")');\n</script>\n<!-- BAKERY-ASSETS-END -->`;
const style=`/* BAKERY-STYLE-BEGIN */\n${fs.readFileSync(path.join(dir,'style.css'),'utf8')}\n/* BAKERY-STYLE-END */`;
let html=fs.readFileSync(target,'utf8');
html=html.includes('<!-- BAKERY-ASSETS-BEGIN -->')?html.replace(/<!-- BAKERY-ASSETS-BEGIN -->[\s\S]*?<!-- BAKERY-ASSETS-END -->/,()=>block):html.replace('<!-- PUPPY-ASSETS-BEGIN -->',()=>block+'\n<!-- PUPPY-ASSETS-BEGIN -->');
html=html.includes('/* BAKERY-STYLE-BEGIN */')?html.replace(/\/\* BAKERY-STYLE-BEGIN \*\/[\s\S]*?\/\* BAKERY-STYLE-END \*\//,()=>style):html.replace('</style>',()=>style+'\n</style>');
fs.writeFileSync(target,html);console.log('Embedded 12 rendered bakery assets.');
