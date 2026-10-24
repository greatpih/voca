# 2.5D Bora cat

Bora uses the same Blender studio, proportions and soft material treatment as
Tori. Triangular lavender ears, a pink nose, whiskers, forehead marks and a long
curled tail distinguish the cat. The scarf is lavender and the paws are ivory.

The 112 transparent frames share one 2560×4480 WebP atlas. Clips include idle,
happy jump, gentle wrong-answer reaction, surprise, left/right glances and a
dedicated chewing animation. Bora appears on the start, play and result screens.
The play scene uses a bust crop and matching rendered table paws.

The shared player in `../puppy/player.js` decodes one atlas per character and
uses a single animation loop. Only visible screens draw, background tabs pause,
and reduced-motion users see still expressions. The poster is a loading fallback.
All assets are embedded in `math.html`; no internet or Blender is needed to play.

## Rebuild

From the repository root, with Blender 5.2, FFmpeg and Node.js available:

```sh
# Optional: rebuild the editable cat from the puppy source.
blender -b --python tools/cat/build_model.py -- --preview /absolute/temporary/cat/preview.png
blender -b --python tools/puppy/render.py -- --character cat --source /absolute/repository/tools/cat/source.blend --output-dir /absolute/temporary/cat
ffmpeg -y -framerate 15 -i /absolute/temporary/cat/frames/cat-%03d.png -vf tile=8x14 -frames:v 1 -c:v libwebp -quality 88 -compression_level 6 tools/cat/assets/cat-atlas.webp
ffmpeg -y -i /absolute/temporary/cat/frames/cat-000.png -c:v libwebp -quality 92 tools/cat/assets/cat-poster.webp
ffmpeg -y -i /absolute/temporary/cat/paw.png -c:v libwebp -quality 92 tools/cat/assets/cat-paw.webp
```

Copy the generated `manifest.json` into `tools/cat/assets/`, then run
`node tools/puppy/embed.mjs` to embed both characters. Blender exits after rendering;
process ownership is recorded in the chosen temporary output folder.
