// Shared helpers for the Azelle videos. Everything is CSS animation, so the renderer can seek any frame.
let _seed = 11;
const rnd = () => (_seed = (_seed * 16807) % 2147483647) / 2147483647;
const $ = id => document.getElementById(id);
const el = (cls, parent, css = {}, vars = {}) => {
  const d = document.createElement('div'); d.className = cls; Object.assign(d.style, css);
  for (const k in vars) d.style.setProperty(k, vars[k]);
  parent.appendChild(d); return d;
};

function petals(parent, n = 22, start = 0) {
  const cols = ['#f6a3b8', '#f9c0cd', '#f3d9c9', '#ee8fa8', '#fde4dc'];
  for (let i = 0; i < n; i++) {
    const d = 8 + rnd() * 6;
    el('petal', parent, { left: rnd() * 1080 + 'px' }, {
      '--w': (22 + rnd() * 26) + 'px', '--c': cols[i % cols.length], '--d': d + 's',
      '--dl': (start - rnd() * d) + 's', '--sx': (rnd() * 160 - 80) + 'px'
    });
  }
}

function sparks(parent, n, box = [80, 300, 1000, 1600], start = 0) {
  for (let i = 0; i < n; i++) {
    el('spark', parent, { left: box[0] + rnd() * (box[2] - box[0]) + 'px', top: box[1] + rnd() * (box[3] - box[1]) + 'px' },
      { '--s': (30 + rnd() * 50) + 'px', '--d': (1.4 + rnd() * 1.6) + 's', '--dl': (start + rnd() * 2) + 's' });
  }
}

function confetti(parent, x, y, n, delay) {
  const cols = ['#c99a3e', '#f1d48a', '#0e5c34', '#f4a9bd', '#ffffff', '#e07895'];
  for (let i = 0; i < n; i++) {
    const a = -Math.PI / 2 + (rnd() - 0.5) * Math.PI * 1.4, v = 300 + rnd() * 750;
    const c = el('conf', parent, { left: x + 'px', top: y + 'px', background: cols[i % cols.length] }, {
      '--x': Math.cos(a) * v + 'px', '--y': Math.sin(a) * v + 'px', '--r': (rnd() * 1440 - 720) + 'deg',
      '--d': (2 + rnd() * 1.5) + 's', '--dl': delay + 's'
    });
    if (rnd() < .3) Object.assign(c.style, { width: '14px', height: '14px', borderRadius: '50%' });
  }
}

window.seek = ms => document.getAnimations().forEach(a => { a.pause(); a.currentTime = ms; });
