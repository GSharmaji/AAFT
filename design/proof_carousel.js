/*
 * PROOF carousel — blends the REAL redacted dashboard clips (assets/proof/*)
 * into branded slides. Client/campaign names are already blurred in the clips;
 * email is kept (hero clip + every footer). Same brand system as v2.js.
 *
 * Run:  bash design/install-fonts.sh   (once)
 *       python3 design/redact.py        (make the clips)
 *       NODE_PATH="$(npm root -g)" node design/proof_carousel.js
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT = path.join(__dirname, 'out');
const PUB = path.join(__dirname, '..', 'assets', 'proof-carousel');
const CLIPS = path.join(__dirname, '..', 'assets', 'proof');
fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(PUB, { recursive: true });

const T = { bg: '#0F1115', text: '#FFFFFF', muted: '#8A8F98', accent: '#C8FF00',
            markBg: '#C8FF00', markText: '#0F1115', ghost: 'rgba(255,255,255,0.05)',
            rule: 'rgba(255,255,255,0.14)', card: '#FFFFFF' };
const FOOT = { name: 'GARVIT SHARMA', email: 'sharmagarvit11@gmail.com' };

const b64 = (f) => 'data:image/png;base64,' + fs.readFileSync(path.join(CLIPS, f)).toString('base64');

const SLIDES = [
  { type: 'hook', kicker: 'RECEIPTS, NOT ADJECTIVES',
    headline: 'I DON’T SAY “TRUST ME.” I SHOW THE <mark>SCREENSHOTS.</mark>',
    sub: '9 months of a real ad account — numbers unedited, names blurred. Swipe. →' },

  { type: 'proof', kicker: 'GOOGLE ADS · JAN–SEP 2024',
    headline: '₹1.77L IN. <mark>₹38L</mark> OUT.',
    clip: 'clip-g-jansep.png',
    sub: '9 months. 21.6x return. One account. (Yep — that’s my email in the corner.)' },

  { type: 'wall', kicker: 'MONTH AFTER MONTH',
    headline: 'NOT A <mark>FLUKE.</mark>',
    items: [ { clip: 'clip-g-apr.png', chip: 'APR · 24.8x' },
             { clip: 'clip-g-may.png', chip: 'MAY · 19.7x' },
             { clip: 'clip-g-jun.png', chip: 'JUN · 19.0x' } ],
    sub: 'Different spend, different month. Same result: green.' },

  { type: 'wall', kicker: 'AND IT KEPT CLIMBING',
    headline: 'THEN JULY HIT <mark>45x.</mark>',
    items: [ { clip: 'clip-g-jul.png', chip: 'JUL · 45.5x' },
             { clip: 'clip-g-oct.png', chip: 'OCT · 34.0x' },
             { clip: 'clip-g-nov.png', chip: 'NOV · 42.5x' } ],
    sub: 'The best months came from doing the boring things longer.' },

  { type: 'proof', kicker: 'META ADS · OCT 2024',
    headline: 'AND THAT’S JUST <mark>GOOGLE.</mark>',
    clip: 'clip-m-oct.png',
    sub: 'Meta too — one campaign at 50x. Client + campaign names blurred; the numbers are real.' },

  { type: 'cta', kicker: 'YOUR MOVE',
    headline: 'IMAGINE THIS ON <mark>YOUR</mark> ACCOUNT.',
    sub: 'If your ad spend could use a year like this, my inbox is open.' },
];

function wallHtml(items) {
  return `<div class="wall">${items.map(it => `
    <div class="witem">
      <span class="chip">${it.chip}</span>
      <div class="clipcard"><img src="${b64(it.clip)}"></div>
    </div>`).join('')}</div>`;
}

function html(s, i, n) {
  const idx = String(i + 1).padStart(2, '0');
  let visual = '';
  if (s.type === 'proof') visual = `<div class="clipcard big"><img src="${b64(s.clip)}"></div>`;
  else if (s.type === 'wall') visual = wallHtml(s.items);
  const emailBig = s.type === 'cta' ? `<div class="ctamail">${FOOT.email}</div>` : '';
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  *{margin:0;padding:0;box-sizing:border-box;-webkit-font-smoothing:antialiased;}
  html,body{width:1080px;height:1350px;}
  .canvas{position:relative;width:1080px;height:1350px;background:${T.bg};color:${T.text};
    padding:74px 72px 70px;display:flex;flex-direction:column;overflow:hidden;}
  .ghost{position:absolute;right:-40px;bottom:-160px;font-family:'Anton';font-size:560px;
    line-height:1;color:${T.ghost};letter-spacing:-8px;z-index:1;}
  .top{display:flex;justify-content:space-between;align-items:center;position:relative;z-index:2;}
  .wordmark{font-family:'Archivo Black';font-size:32px;letter-spacing:1px;}
  .wordmark b{color:${T.accent};}
  .index{font-family:'Poppins SemiBold';font-size:22px;letter-spacing:2px;color:${T.muted};}
  .index em{color:${T.text};font-style:normal;}
  .block{margin-top:auto;position:relative;z-index:2;}
  .kicker{display:flex;align-items:center;gap:14px;margin-bottom:26px;}
  .kicker .bar{width:48px;height:6px;background:${T.accent};border-radius:3px;}
  .kicker span{font-family:'Poppins SemiBold';font-size:21px;letter-spacing:4px;text-transform:uppercase;color:${T.muted};}
  .headline{font-family:'Anton';text-transform:uppercase;line-height:1.16;letter-spacing:-0.5px;font-size:96px;margin-bottom:26px;}
  .headline mark{background:${T.markBg};color:${T.markText};padding:0.03em 0.12em;border-radius:12px;
    box-decoration-break:clone;-webkit-box-decoration-break:clone;}
  .sub{font-family:'Poppins Medium';font-size:31px;line-height:1.36;color:${T.muted};max-width:900px;}
  .clipcard{background:${T.card};border-radius:16px;padding:12px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.45);}
  .clipcard img{display:block;width:100%;border-radius:8px;}
  .clipcard.big{margin-top:20px;}
  .wall{display:flex;flex-direction:column;gap:20px;margin-top:24px;}
  .witem{position:relative;}
  .witem .chip{position:absolute;top:-13px;left:16px;z-index:3;background:${T.accent};color:${T.markText};
    font-family:'Poppins SemiBold';font-size:20px;letter-spacing:1px;padding:6px 16px;border-radius:20px;}
  .witem .clipcard{padding:10px;}
  .sub.after{margin-top:26px;}
  .ctamail{margin-top:34px;font-family:'Poppins SemiBold';font-size:40px;color:${T.accent};}
  .foot{position:relative;z-index:2;margin-top:36px;border-top:2px solid ${T.rule};padding-top:26px;
    display:flex;justify-content:space-between;align-items:center;font-family:'Poppins SemiBold';font-size:23px;}
  .foot .h{color:${T.text};} .foot .s{color:${T.muted};}
  </style></head><body>
    <div class="canvas">
      <div class="ghost">${idx}</div>
      <div class="top"><div class="wordmark">GS<b>.</b></div><div class="index"><em>${idx}</em> / ${String(n).padStart(2,'0')}</div></div>
      <div class="block">
        <div class="kicker"><span class="bar"></span><span>${s.kicker}</span></div>
        <div class="headline">${s.headline}</div>
        ${s.type === 'proof' || s.type === 'wall' ? visual + `<div class="sub after">${s.sub}</div>` : `<div class="sub">${s.sub}</div>` + emailBig}
      </div>
      <div class="foot"><span class="h">${FOOT.name}</span><span class="s">${FOOT.email}</span></div>
    </div>
  </body></html>`;
}

(async () => {
  const only = process.argv[2] ? parseInt(process.argv[2], 10) : null;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
  for (let i = 0; i < SLIDES.length; i++) {
    if (only && i + 1 !== only) continue;
    await page.setContent(html(SLIDES[i], i, SLIDES.length), { waitUntil: 'networkidle' });
    await page.evaluate(async () => {
      await Promise.all([
        document.fonts.load("96px 'Anton'"),
        document.fonts.load("32px 'Archivo Black'"),
        document.fonts.load("31px 'Poppins Medium'"),
        document.fonts.load("22px 'Poppins SemiBold'"),
      ]);
      await document.fonts.ready;
      const h = document.querySelector('.headline');
      let size = 96;
      const MAX_H = 300;
      h.style.fontSize = size + 'px';
      const over = () => h.scrollWidth > h.clientWidth || h.getBoundingClientRect().height > MAX_H;
      while (over() && size > 46) { size -= 2; h.style.fontSize = size + 'px'; }
    });
    const name = `proof-${String(i + 1).padStart(2, '0')}.png`;
    const file = path.join(OUT, name);
    await page.locator('.canvas').screenshot({ path: file });
    fs.copyFileSync(file, path.join(PUB, name));
    console.log('rendered', name);
  }
  await browser.close();
})();
