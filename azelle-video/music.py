# Synthesizes the soundtrack (soft luxury pad + bell arpeggio + sound effects) -> soundtrack.wav
import numpy as np, wave, sys
SR=44100; DUR=20.0; N=int(SR*DUR); t=np.arange(N)/SR
rng=np.random.default_rng(3)
out=np.zeros((N,2))
def hz(m): return 440*2**((m-69)/12)
def add(sig,start,pan=0.0,gain=1.0):
    i=int(start*SR); sig=sig[:max(0,N-i)]
    out[i:i+len(sig),0]+=sig*gain*(1-pan)/1; out[i:i+len(sig),1]+=sig*gain*(1+pan)/1
def env(n,a,r):
    e=np.ones(n); A=int(a*SR); R=int(r*SR)
    e[:A]=np.linspace(0,1,A); e[-R:]*=np.linspace(1,0,R); return e
def pad(notes,dur):
    n=int(dur*SR); tt=np.arange(n)/SR; s=np.zeros(n)
    for m in notes:
        for det in (-0.12,0,0.12):
            f=hz(m)*2**(det/12)
            s+=np.sin(2*np.pi*f*tt)+0.25*np.sin(4*np.pi*f*tt)+0.08*np.sin(6*np.pi*f*tt)
    return s*env(n,0.6,0.8)/len(notes)/3
def bell(m,dur=1.6):
    n=int(dur*SR); tt=np.arange(n)/SR; f=hz(m)
    s=np.sin(2*np.pi*f*tt)+0.4*np.sin(2*np.pi*f*2.76*tt)*np.exp(-tt*6)+0.2*np.sin(2*np.pi*f*5.4*tt)*np.exp(-tt*10)
    return s*np.exp(-tt*3.2)*env(n,0.004,0.05)
# chords: Fmaj7 Am7 Dm9 Bbmaj7 Gm7 C (2.5s each)
B=2.5
prog=[[53,57,60,64],[57,60,64,67],[50,57,62,65,69],[46,53,57,62],[55,58,62,65],[48,55,60,64],[53,57,60,64],[46,53,57,62]]
for k,ch in enumerate(prog):
    add(pad(ch,B+0.8),k*B,gain=0.18)
    add(np.sin(2*np.pi*hz(ch[0]-12)*np.arange(int(B*SR))/SR)*env(int(B*SR),0.05,0.6),k*B,gain=0.16)
# arpeggio from 3.0s, 8ths at 96bpm
step=60/96/2; tm=3.0; k=0
while tm<19.0:
    ch=prog[int(tm//B)%len(prog)]; notes=[x+12 for x in ch]+[ch[1]+24]
    add(bell(notes[(k*3)%len(notes)]),tm,pan=0.35*np.sin(k),gain=0.10)
    tm+=step; k+=1
# soft kick-ish pulse on beats after the ribbon cut
beat=60/96
tm=9.1
while tm<19.0:
    n=int(0.35*SR); tt=np.arange(n)/SR
    add(np.sin(2*np.pi*(50+90*np.exp(-tt*30))*tt)*np.exp(-tt*9),tm,gain=0.35); tm+=beat
# whoosh (curtains)
def whoosh(dur,up=True):
    n=int(dur*SR); x=rng.standard_normal(n); y=np.zeros(n); a=0.0
    cut=np.linspace(0.02,0.25,n) if up else np.linspace(0.25,0.02,n)
    for i in range(n): a+=cut[i]*(x[i]-a); y[i]=a
    return y*np.sin(np.linspace(0,np.pi,n))**2
add(whoosh(1.8),1.6,gain=0.9)
# shimmer glissando (logo / opening)
def gliss(start,m0,cnt,gap,g):
    for i in range(cnt): add(bell(m0+[0,4,7,11,12,16,19,23,24,28][i%10]+12*(i//10),1.2),start+i*gap,pan=(i%2-.5)*.6,gain=g)
gliss(3.6,72,10,0.06,0.10)
# snip + sparkle burst + chime at ribbon cut
n=int(0.05*SR); add(rng.standard_normal(n)*np.exp(-np.arange(n)/SR*90),9.08,gain=0.5)
gliss(9.12,79,14,0.035,0.08)
for m in (65,69,72,77): add(bell(m,2.5),9.25,gain=0.12)
# soft whooshes for scene changes
for st in (7.1,11.3,15.4): add(whoosh(0.9,False),st,gain=0.35)
# tap pop on follow
n=int(0.12*SR); tt=np.arange(n)/SR; add(np.sin(2*np.pi*(900-500*tt/0.12)*tt)*np.exp(-tt*40),17.55,gain=0.35)
gliss(17.8,84,6,0.08,0.07)
# simple stereo reverb (feedback delays)
for d,g in ((0.031,.35),(0.047,.3),(0.071,.25),(0.113,.2),(0.167,.15)):
    D=int(d*SR); out[D:,0]+=out[:-D,1]*g*0.6; out[D:,1]+=out[:-D,0]*g*0.6
# fade in/out, normalize
out[:int(0.3*SR)]*=np.linspace(0,1,int(0.3*SR))[:,None]
fo=int(1.5*SR); out[-fo:]*=np.linspace(1,0,fo)[:,None]
out=np.tanh(out/np.abs(out).max()*1.3)*0.85
w=wave.open(sys.argv[1] if len(sys.argv)>1 else 'soundtrack.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out*32767).astype('<i2').tobytes()); w.close()
