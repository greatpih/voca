# 2.5D Tori puppy

Tori uses the approved Blender puppy: cream fur, caramel ears and a mint bandana.
The rabbit and all arithmetic/cookie mechanics remain in the original game code.

The 96 transparent frames share one 2560×3840 WebP atlas (about 0.5 MB).
The browser decodes it once and draws the visible character at 15 fps. Hidden
screens do not draw, background tabs suspend the loop, and reduced-motion users
get still expressions. A static poster remains visible if atlas loading fails.
The same frames are cropped to a bust in the play scene and shown full-body on
the start screen, map and result screen. The two table paws use a matching render.

`math.html` embeds the atlas, poster, paw and player. It still opens offline as a
single file. There are no CDN requests, WebGL requirements or new dependencies.

## Files

- `source.blend`: original editable puppy and studio lighting, Blender 5.2.
- `render.py`: generate normal, happy, gentle wrong-answer, surprised and left/right glance clips.
- `assets/`: shared atlas, poster, table paw and frame manifest.
- `player.js`: canvas playback and visibility handling.
- `embed.mjs`: re-embed the assets and player in `math.html`.

## Rebuild

From the repository root, with Blender, FFmpeg and Node.js available:

```sh
blender -b --python tools/puppy/render.py -- --output-dir /absolute/temporary/puppy
ffmpeg -y -framerate 15 -i /absolute/temporary/puppy/frames/puppy-%03d.png -vf tile=8x12 -frames:v 1 -c:v libwebp -quality 88 -compression_level 6 tools/puppy/assets/puppy-atlas.webp
ffmpeg -y -i /absolute/temporary/puppy/frames/puppy-000.png -c:v libwebp -quality 92 tools/puppy/assets/puppy-poster.webp
ffmpeg -y -i /absolute/temporary/puppy/paw.png -c:v libwebp -quality 92 tools/puppy/assets/puppy-paw.webp
```

Copy the generated `manifest.json` into `tools/puppy/assets/`, then run:

```sh
node tools/puppy/embed.mjs
```

The renderer records its PID, start time, executable and purpose in the chosen
temporary output directory and exits after rendering. Rendered PNG sequences
are build intermediates and do not need to be committed.
