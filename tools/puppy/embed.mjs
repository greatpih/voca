import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const target = path.resolve(dir, '../../math.html');
const data = name => `data:image/webp;base64,${fs.readFileSync(path.join(dir, 'assets', name)).toString('base64')}`;
const assets = {
  manifest: JSON.parse(fs.readFileSync(path.join(dir, 'assets/manifest.json'), 'utf8')),
  atlas: data('puppy-atlas.webp'), poster: data('puppy-poster.webp'), paw: data('puppy-paw.webp')
};
const player = fs.readFileSync(path.join(dir, 'player.js'), 'utf8');
const catDir = path.resolve(dir, '../cat/assets');
const catData = name => `data:image/webp;base64,${fs.readFileSync(path.join(catDir, name)).toString('base64')}`;
const catAssets = {
  manifest: JSON.parse(fs.readFileSync(path.join(catDir, 'manifest.json'), 'utf8')),
  atlas: catData('cat-atlas.webp'), poster: catData('cat-poster.webp'), paw: catData('cat-paw.webp')
};
const block = `<!-- PUPPY-ASSETS-BEGIN -->\n<script>\nconst PUPPY_ASSETS = ${JSON.stringify(assets)};\nconst CAT_ASSETS = ${JSON.stringify(catAssets)};\n${player}\n</script>\n<!-- PUPPY-ASSETS-END -->`;
let html = fs.readFileSync(target, 'utf8');
if (html.includes('<!-- PUPPY-ASSETS-BEGIN -->')) {
  html = html.replace(/<!-- PUPPY-ASSETS-BEGIN -->[\s\S]*?<!-- PUPPY-ASSETS-END -->/, block);
} else {
  const where = html.indexOf('<script>');
  if (where < 0) throw new Error('No script insertion point in math.html');
  html = html.slice(0, where) + block + '\n' + html.slice(where);
}
fs.writeFileSync(target, html);
console.log(`Embedded puppy: ${assets.manifest.frames}, cat: ${catAssets.manifest.frames} frames; math.html ${Buffer.byteLength(html)} bytes`);
