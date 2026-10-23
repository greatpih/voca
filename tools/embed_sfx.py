"""tools/sfx/*.mp3 를 base64로 바꿔 math.html 의 SFX-BEGIN/SFX-END 사이에 넣는다.

사용법: python3 tools/embed_sfx.py <mp3 폴더> math.html
"""
import base64, json, os, re, sys

src, html = sys.argv[1], sys.argv[2]
data = {}
for f in sorted(os.listdir(src)):
    if f.endswith('.mp3'):
        with open(os.path.join(src, f), 'rb') as fh:
            data[f[:-4]] = 'data:audio/mpeg;base64,' + base64.b64encode(fh.read()).decode()
text = open(html, encoding='utf-8').read()
new, n = re.subn(r'/\*SFX-BEGIN\*/.*?/\*SFX-END\*/',
                 lambda m: '/*SFX-BEGIN*/' + json.dumps(data, separators=(',', ':')) + '/*SFX-END*/',
                 text, count=1, flags=re.S)
assert n == 1, 'marker not found'
open(html, 'w', encoding='utf-8').write(new)
print(f'embedded {len(data)} sounds, {sum(len(v) for v in data.values())//1024} KB')
