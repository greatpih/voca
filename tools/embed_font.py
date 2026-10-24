"""math.html 에 쓰인 글자만 남긴 글꼴(woff2)을 만들어 FONT-BEGIN/FONT-END 사이에 넣는다.

인터넷 없이도 같은 글씨가 나오게 하려고 글꼴을 파일 안에 넣는다.
글자를 새로 쓰면(문구 추가 등) 이 스크립트를 다시 돌려야 그 글자도 들어간다.

  pip install fonttools brotli
  python3 tools/embed_font.py tools/fonts/Cafe24Ssurround.woff math.html

원본 글꼴: tools/fonts/Cafe24Ssurround.woff (카페24 써라운드, tools/fonts/README.md 참고)
"""
import base64, io, re, string, sys
from fontTools import subset
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

font_path, html = sys.argv[1], sys.argv[2]
text = open(html, encoding='utf-8').read()
# 이미 넣어 둔 소리·글꼴 데이터는 글자 수집에서 뺀다
plain = re.sub(r'data:[\w/+.-]+;base64,[A-Za-z0-9+/=]+', '', text)
chars = set(plain) | set(string.printable) | set('×−▶…·')
chars = {c for c in chars if c.isprintable() and c not in '\t\n\r'}

font = TTFont(font_path, recalcTimestamp=False)  # 다시 돌려도 같은 결과가 나오게
# 글꼴에 자리만 있고 모양이 빈 글자(▶ × → 등)는 빼서 기기 기본 글꼴로 그리게 한다
cmap, glyphs = font.getBestCmap(), font.getGlyphSet()
def has_outline(c):
    if c.isspace():
        return True
    name = cmap.get(ord(c))
    if not name:
        return False
    pen = BoundsPen(glyphs)
    glyphs[name].draw(pen)
    return pen.bounds is not None
chars = {c for c in chars if has_outline(c)}
opts = subset.Options()
opts.flavor = 'woff2'
opts.layout_features = ['*']
opts.name_IDs = []
opts.notdef_outline = True
sub = subset.Subsetter(opts)
sub.populate(unicodes=[ord(c) for c in chars])
sub.subset(font)
buf = io.BytesIO()
font.flavor = 'woff2'
font.save(buf)
b64 = base64.b64encode(buf.getvalue()).decode()

face = ("@font-face{font-family:'Cafe24Ssurround';font-display:block;"
        f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
new, n = re.subn(r'/\*FONT-BEGIN\*/.*?/\*FONT-END\*/', lambda m: '/*FONT-BEGIN*/' + face + '/*FONT-END*/',
                 text, count=1, flags=re.S)
assert n == 1, 'marker not found'
open(html, 'w', encoding='utf-8').write(new)
print(f'{len(chars)} chars, font {len(buf.getvalue())//1024} KB')
