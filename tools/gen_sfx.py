"""토리의 쿠키 셈놀이 효과음 만들기.

GM 사운드폰트(pretty_midi 패키지에 들어 있는 TimGM6mb.sf2)로 악기 소리를 내고,
나머지(뽁, 쉭, 와삭 등)는 numpy로 직접 합성해 MP3로 저장한다.

  pip install numpy scipy pretty_midi tinysoundfont   # ffmpeg 필요
  python3 tools/gen_sfx.py tools/sfx <TimGM6mb.sf2 경로>
  python3 tools/embed_sfx.py tools/sfx math.html

만들어 둔 소리는 tools/sfx/*.mp3 에 있으니, 소리를 바꿀 때만 다시 만들면 된다.
"""
import sys, numpy as np, tinysoundfont, subprocess, os
from scipy.signal import butter, lfilter, fftconvolve
SR=44100; OUT=sys.argv[1]; SF=sys.argv[2]
rng=np.random.default_rng(7)
def t(d): return np.arange(int(SR*d))/SR
def env(n,a=0.005,d=None,curve=6):
    x=np.arange(n)/SR; e=np.minimum(1,x/max(a,1e-4)); dur=n/SR
    return e*np.exp(-curve*x/dur) if d is None else e*np.exp(-x/d)
def bp(x,lo,hi,o=2): b,a=butter(o,[lo/(SR/2),hi/(SR/2)],'band'); return lfilter(b,a,x)
def lp(x,f,o=2): b,a=butter(o,f/(SR/2),'low'); return lfilter(b,a,x)
def hp(x,f,o=2): b,a=butter(o,f/(SR/2),'high'); return lfilter(b,a,x)
def sweep(f0,f1,d,shape='exp'):
    n=int(SR*d); k=np.linspace(0,1,n)
    f=f0*(f1/f0)**k if shape=='exp' else f0+(f1-f0)*k
    return np.sin(2*np.pi*np.cumsum(f)/SR)
def mix(*parts):
    n=max(len(p[1])+int(p[0]*SR) for p in parts); y=np.zeros(n)
    for off,s in parts: i=int(off*SR); y[i:i+len(s)]+=s
    return y
IR=None
def reverb(x,wet=.18,dur=.9):
    global IR
    if IR is None:
        n=int(SR*dur); IR=rng.standard_normal(n)*np.exp(-np.arange(n)/SR*6.5); IR=lp(IR,6000); IR/=np.sqrt(np.sum(IR**2))
    y=np.concatenate([x,np.zeros(int(SR*dur))]); w=fftconvolve(y,IR)[:len(y)]
    return y*(1-wet)+w*wet*1.0
synth=tinysoundfont.Synth(samplerate=SR); sfid=synth.sfload(SF); synth.start() if False else None
def inst(program, notes, dur, vel=100, bank=0):
    """notes: list of (time, midi, length, vel)"""
    s=tinysoundfont.Synth(samplerate=SR); sid=s.sfload(SF); s.program_select(0,sid,bank,program)
    total=int(SR*dur); buf=np.zeros((total,2),np.float32); ev=[]
    for (tm,m,ln,v) in notes: ev.append((tm,'on',m,v)); ev.append((tm+ln,'off',m,0))
    ev.sort(key=lambda e:e[0]); pos=0
    for tm,kind,m,v in ev:
        k=min(int(tm*SR),total)
        if k>pos: buf[pos:k]=np.frombuffer(s.generate(k-pos),np.float32).reshape(-1,2); pos=k
        if kind=='on': s.noteon(0,m,v)
        else: s.noteoff(0,m)
    if pos<total: buf[pos:]=np.frombuffer(s.generate(total-pos),np.float32).reshape(-1,2)
    return buf.mean(1).astype(np.float64)
def fade(x,ms=20):
    n=int(SR*ms/1000); x=x.copy(); x[-n:]*=np.linspace(1,0,n); return x
def norm(x,peak=.89):
    x=x-np.mean(x); m=np.max(np.abs(x)); return x/m*peak if m>0 else x
def trim(x,th=1e-3):
    idx=np.where(np.abs(x)>th*np.max(np.abs(x)))[0]; return x[:idx[-1]+int(SR*.02)] if len(idx) else x
def save(name,x,peak=.89):
    x=fade(trim(norm(x,peak))); wav=os.path.join(OUT,name+'.wav')
    import wave
    with wave.open(wav,'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x,-1,1)*32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg','-v','error','-y','-i',wav,'-codec:a','libmp3lame','-b:a','64k',os.path.join(OUT,name+'.mp3')],check=True)
    os.remove(wav); print(name, round(len(x)/SR,2),'s')

# 1. tick (count tap) - marimba C5, pitched via playbackRate in game
save('tick', reverb(inst(12,[(0,72,.25,110)],.9),.12))
# 2. pick (lift) - bubbly bloop up
n=t(.12); save('pick', sweep(320,900,.12)*env(len(n),.004,curve=5)*.8 + sweep(640,1800,.12)*env(len(n),.004,curve=9)*.15)
# 3. land - soft thud + ceramic clink
thud=lp(rng.standard_normal(int(SR*.08)),400)*env(int(SR*.08),.001,curve=9)*3
clink=(np.sin(2*np.pi*2630*t(.25))+.5*np.sin(2*np.pi*4110*t(.25))+.25*np.sin(2*np.pi*5870*t(.25)))*env(int(SR*.25),.0008,d=.045)
save('land', reverb(mix((0,thud),(0.004,clink*.35)),.1),.8)
# 4. whoosh
nz=rng.standard_normal(int(SR*.42)); k=np.linspace(0,1,len(nz)); out=np.zeros_like(nz)
for i,(a,b) in enumerate([(300,900),(900,2400),(1600,4000)]):
    seg=bp(nz,a,b); out+=seg*np.sin(np.pi*k)**2*(1-.3*i)
save('whoosh', out*.6,.6)
# 5. bundle - celesta arpeggio + shimmer
arp=inst(8,[(i*.075,m,.5,105) for i,m in enumerate([72,76,79,84,88])],1.6)
sh=hp(rng.standard_normal(int(SR*.9)),6000)*env(int(SR*.9),.2,curve=5)*.05
save('bundle', reverb(mix((0,arp),(0.1,sh)),.25))
# 6. unpack - pop cascade + celesta down
pops=[]
for i in range(10):
    f=1400-i*70; p=sweep(f*1.6,f*.6,.05)*env(int(SR*.05),.001,curve=7); pops.append((i*.04,p*.5))
arp2=inst(8,[(i*.06,m,.4,95) for i,m in enumerate([88,84,79,76,72])],1.2)
save('unpack', reverb(mix(*pops,(0,arp2*.9)),.2))
# 7. nom (give to bunny) - crunch + squeak
cr=[]
for i,o in enumerate([0,.09]):
    b=bp(rng.standard_normal(int(SR*.07)),1500,5000)*env(int(SR*.07),.001,curve=8)
    cr.append((o,b*.7))
sq=sweep(900,1500,.14)*env(int(SR*.14),.01,curve=4)*.35
save('nom', reverb(mix(*cr,(0.2,sq)),.1))
# 8. correct - glockenspiel ding ding + sparkle
g=inst(9,[(0,84,.4,120),(.12,91,.9,120)],1.6)
g2=inst(10,[(0,84,.4,90),(.12,91,.9,90)],1.6)
spark=sum(np.pad(np.sin(2*np.pi*f*t(.12))*env(int(SR*.12),.001,curve=8),(int(SR*o),0)) [:int(SR*1.0)] if True else 0 for f,o in [(3520,.2),(4186,.28),(3136,.34),(4700,.42)]) if False else None
sp=np.zeros(int(SR*1.2))
for f,o in [(3520,.22),(4186,.3),(3136,.37),(4699,.45),(3951,.52)]:
    s=np.sin(2*np.pi*f*t(.15))*env(int(SR*.15),.001,curve=8)*.12; i=int(SR*o); sp[i:i+len(s)]+=s
save('correct', reverb(mix((0,g),(0,g2*.5),(0,sp)),.22))
# 9. wrong - gentle muted trumpet wah-wah down
w=inst(59,[(0,67,.22,90),(.26,63,.5,90)],1.1)
save('wrong', reverb(w,.15),.7)
# 10. fanfare
mel=[(0,72,.14),(.15,72,.14),(.3,72,.14),(.45,76,.45),(.95,74,.14),(1.1,76,.14),(1.25,79,.9)]
tr=inst(56,[(a,m,l,115) for a,m,l in mel],2.8)
br=inst(61,[(.45,60,.5,90),(.45,64,.5,90),(1.25,60,1.2,100),(1.25,64,1.2,100),(1.25,67,1.2,100)],2.8)
gl=inst(9,[(1.25,91,1,110),(1.4,96,1,100)],2.8)
save('fanfare', reverb(mix((0,tr),(0,br*.8),(0,gl*.6)),.25))
# 11. star - music box high note
save('star', reverb(mix((0,inst(10,[(0,88,.6,120)],1.4)),(0,inst(9,[(0,100,.3,80)],1.4)*.4)),.3))
# 12. click - soft wood tap
save('click', reverb(inst(115,[(0,76,.1,90)],.35),.05),.6)
# 13. gem - coin bling
save('gem', reverb(inst(9,[(0,83,.1,120),(.08,88,.6,120)],1.1),.2))
# 14. boop - hint / nope
save('boop', inst(12,[(0,55,.2,100),(.1,52,.3,90)],.7),.6)
# 15. pageflip-ish swoosh for star wipe (reuse whoosh longer + chime)
nz=rng.standard_normal(int(SR*.7)); k=np.linspace(0,1,len(nz))
sw=bp(nz,500,3500)*np.sin(np.pi*k)**3
save('wipe', reverb(mix((0,sw*.5),(.25,inst(8,[(0,84,.3,80),(.06,91,.5,80)],1.0)*.7)),.25),.7)
