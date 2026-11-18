# Light, romantic soundtrack generator for the Azelle brand videos.
# usage: python3 music_brand.py <v1|v2|v3> <out.wav>
import numpy as np, wave, sys
SR = 44100; DUR = 15.0; N = int(SR * DUR)
rng = np.random.default_rng(5)
out = np.zeros((N, 2))
hz = lambda m: 440 * 2 ** ((m - 69) / 12)

def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR)
    if i >= N: return
    sig = sig[:N - i]; out[i:i+len(sig), 0] += sig*gain*(1-pan); out[i:i+len(sig), 1] += sig*gain*(1+pan)

def env(n, a, r):
    e = np.ones(n); A, R = max(1, int(a*SR)), max(1, int(r*SR))
    e[:A] = np.linspace(0, 1, A); e[-R:] *= np.linspace(1, 0, R); return e

def pad(notes, dur):
    n = int(dur*SR); t = np.arange(n)/SR; s = np.zeros(n)
    for m in notes:
        for det in (-0.1, 0, 0.1):
            f = hz(m) * 2 ** (det/12); s += np.sin(2*np.pi*f*t) + 0.2*np.sin(4*np.pi*f*t)
    return s * env(n, 0.5, 0.7) / len(notes) / 3

def pluck(m, dur=1.2, bright=1.0):
    n = int(dur*SR); t = np.arange(n)/SR; f = hz(m)
    s = np.sin(2*np.pi*f*t) + 0.5*bright*np.sin(4*np.pi*f*t)*np.exp(-t*8) + 0.3*bright*np.sin(2*np.pi*f*3.01*t)*np.exp(-t*14)
    return s * np.exp(-t*4) * env(n, 0.003, 0.05)

def bell(m, dur=1.6):
    n = int(dur*SR); t = np.arange(n)/SR; f = hz(m)
    return (np.sin(2*np.pi*f*t) + 0.4*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*6)) * np.exp(-t*3) * env(n, 0.003, 0.05)

def gliss(start, root, cnt, gap, g):
    sc = [0, 4, 7, 11, 12, 16, 19, 23, 24, 28, 31, 35]
    for i in range(cnt): add(bell(root + sc[i % 12], 1.2), start + i*gap, pan=(i % 2 - .5)*.6, gain=g)

def whoosh(dur, up=True):
    n = int(dur*SR); x = rng.standard_normal(n); y = np.zeros(n); a = 0.0
    cut = np.linspace(.02, .2, n) if up else np.linspace(.2, .02, n)
    for i in range(n): a += cut[i]*(x[i]-a); y[i] = a
    return y * np.sin(np.linspace(0, np.pi, n))**2

def pop(at, g=.35):
    n = int(.1*SR); t = np.arange(n)/SR; add(np.sin(2*np.pi*(1000-600*t/.1)*t)*np.exp(-t*45), at, gain=g)

P = {
 'v1': dict(bpm=100, prog=[[60,64,67,71],[57,60,64,67],[53,57,60,64],[55,59,62,67]], beat_from=7.0,
            sfx=lambda: (add(whoosh(1.2), .9, gain=.6), gliss(1.5, 72, 12, .07, .09), gliss(3.1, 84, 6, .05, .06),
                         gliss(7.0, 79, 12, .035, .08), [add(bell(m, 2.4), 7.05, gain=.11) for m in (72, 76, 79, 84)],
                         [add(whoosh(.7, False), t, gain=.3) for t in (5.4, 9.4, 12.3)], pop(13.7))),
 'v2': dict(bpm=108, prog=[[57,60,64,67],[53,57,60,64],[60,64,67,72],[55,59,62,67]], beat_from=2.9,
            sfx=lambda: (gliss(1.3, 76, 8, .05, .08), [add(whoosh(.6), t-.1, gain=.35) for t in (2.9, 5.15, 7.4, 9.65)],
                         [add(bell(m, 1.5), t+.15, gain=.12) for t, m in ((2.9, 79), (5.15, 81), (7.4, 83), (9.65, 84))],
                         gliss(12.9, 79, 10, .04, .08), pop(13.4))),
 'v3': dict(bpm=112, prog=[[60,64,67,72],[55,59,62,67],[57,60,64,69],[53,57,60,65]], beat_from=1.2,
            sfx=lambda: (pop(2.0), [add(pluck(72 + i, .3), 2.3 + i*.1, gain=.08) for i in range(13)], gliss(3.65, 84, 8, .05, .08),
                         [pop(t, .25) for t in (5.9, 6.2, 6.5, 6.8)], [add(whoosh(.6, False), t, gain=.3) for t in (5.0, 9.5)],
                         [pop(t, .22) for t in (10.3, 10.7, 11.1, 11.5)], pop(13.15, .4), gliss(13.3, 84, 6, .06, .07))),
}
cfg = P[sys.argv[1]]
B = 60 / cfg['bpm'] * 4
for k in range(int(DUR / B) + 1):
    ch = cfg['prog'][k % 4]; add(pad(ch, B + .7), k*B, gain=.16)
    nb = int(B*SR); add(np.sin(2*np.pi*hz(ch[0]-12)*np.arange(nb)/SR)*env(nb, .05, .5), k*B, gain=.13)
step = 60 / cfg['bpm'] / 2; t = .4; k = 0
while t < DUR - .6:
    ch = cfg['prog'][int(t // B) % 4]; notes = [x+12 for x in ch] + [ch[2]+24]
    add(pluck(notes[(k*2) % 5] if k % 4 else notes[0], 1.0, .8), t, pan=.3*np.sin(k*.9), gain=.09); t += step; k += 1
beat = 60 / cfg['bpm']; t = cfg['beat_from']
while t < DUR - .5:
    n = int(.3*SR); tt = np.arange(n)/SR
    add(np.sin(2*np.pi*(55+80*np.exp(-tt*30))*tt)*np.exp(-tt*10), t, gain=.3)
    nn = int(.05*SR); add(rng.standard_normal(nn)*np.exp(-np.arange(nn)/SR*80)*.25, t + beat/2, pan=.2, gain=.25)
    t += beat
cfg['sfx']()
for d, g in ((.029, .35), (.043, .3), (.067, .25), (.109, .2), (.151, .15)):
    D = int(d*SR); out[D:, 0] += out[:-D, 1]*g*.6; out[D:, 1] += out[:-D, 0]*g*.6
out[:int(.2*SR)] *= np.linspace(0, 1, int(.2*SR))[:, None]
fo = int(1.2*SR); out[-fo:] *= np.linspace(1, 0, fo)[:, None]
out = np.tanh(out / np.abs(out).max() * 1.3) * .85
w = wave.open(sys.argv[2], 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out*32767).astype('<i2').tobytes()); w.close()
