import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url)),target=path.resolve(dir,'../../math.html');
let html=fs.readFileSync(target,'utf8');
const css=`/* EXPERIENCE-CSS-BEGIN */\n${fs.readFileSync(path.join(dir,'experience.css'),'utf8')}\n/* EXPERIENCE-CSS-END */`;
const js=`// EXPERIENCE-JS-BEGIN\n${fs.readFileSync(path.join(dir,'experience.js'),'utf8')}\n// EXPERIENCE-JS-END`;
html=html.includes('/* EXPERIENCE-CSS-BEGIN */')?html.replace(/\/\* EXPERIENCE-CSS-BEGIN \*\/[\s\S]*?\/\* EXPERIENCE-CSS-END \*\//,()=>css):html.replace('</style>',()=>css+'\n</style>');
html=html.includes('// EXPERIENCE-JS-BEGIN')?html.replace(/\/\/ EXPERIENCE-JS-BEGIN[\s\S]*?\/\/ EXPERIENCE-JS-END/,()=>js):html.replace('function startRound(st,list){',()=>js+'\n\nfunction startRound(st,list){');
// Include the existing full Korean font so new lesson text works offline.
// Arrow/star symbols use the system fallback; this font has empty symbol glyphs.
const font=fs.readFileSync(path.resolve(dir,'../fonts/Cafe24Ssurround.woff')).toString('base64');
html=html.replace(/\/\*FONT-BEGIN\*\/[\s\S]*?\/\*FONT-END\*\//,()=>`/*FONT-BEGIN*/@font-face{font-family:'Cafe24Ssurround';font-display:block;src:url(data:font/woff;base64,${font}) format('woff');unicode-range:U+0020-007E,U+1100-11FF,U+3130-318F,U+AC00-D7A3}/*FONT-END*/`);
fs.writeFileSync(target,html);console.log('Embedded staged lesson presentation.');
