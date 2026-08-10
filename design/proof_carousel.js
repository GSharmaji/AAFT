/*
 * PROOF carousel v2 — teach + proof (not just flex). Blends the REAL redacted
 * dashboard clips (assets/proof/*) into a story: result -> the "how" (habits),
 * each backed by a real screenshot -> positioning -> sharp CTA.
 * Same brand system as v2.js. Client/campaign names already blurred in clips.
 *
 * Run:  bash design/install-fonts.sh
 *       python3 design/redact.py
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
  { type: 'text', kicker: '9 MONTHS OF RECEIPTS',
    headline: '₹1 IN. <mark>₹21</mark> OUT.',
    sub: 'Not “reach.” Not “impressions.” The one number that actually lands in the bank — and the screenshots to back it. Swipe. →' },

  { type: 'proof', kicker: 'ONE ACCOUNT · JAN–SEP 2024', clip: 'clip-g-jansep.png',
    headline: '₹1.77L SPENT. <mark>₹38L</mark> BACK.',
    sub: '21.6x over 9 months. My real dashboard — email in the corner. Now the part most agencies go quiet about 👇' },

  { type: 'text', kicker: 'THE PART THEY SKIP',
    headline: 'ANYONE CAN SHOW A NUMBER. FEW SHOW THE <mark>HOW.</mark>',
    sub: 'No hacks. No “secret audience.” Just 4 boring habits I run on every account. Here are 3, with the receipts.' },

  { type: 'proof', kicker: 'HABIT 01', clip: 'clip-g-nov.png',
    headline: 'FEED WINNERS. <mark>STARVE</mark> THE REST.',
    sub: 'One month: ₹6K in → ₹2.5L back (42x). Not luck — budget only ever flowed to what was already working.' },

  { type: 'proof', kicker: 'HABIT 02', clip: 'clip-m-oct.png',
    headline: 'READ ROAS BY <mark>CAMPAIGN.</mark>',
    sub: 'Same month, one campaign hit 50x while others lagged. The account “average” hides your real winners. (Meta — names blurred, numbers real.)' },

  { type: 'wall', kicker: 'HABIT 03',
    headline: 'JUST SHOW UP, <mark>EVERY MONTH.</mark>',
    items: [ { clip: 'clip-g-jul.png', chip: 'JUL · 45.5x' },
             { clip: 'clip-g-oct.png', chip: 'OCT · 34.0x' },
             { clip: 'clip-g-nov.png', chip: 'NOV · 42.5x' } ],
    sub: 'No viral spike. Month after month of small, unglamorous decisions — that’s the whole “secret.”' },

  { type: 'text', kicker: 'WHO’S BEHIND THIS',
    headline: 'I MAKE AD SPEND <mark>PAY FOR ITSELF.</mark>',
    sub: 'Garvit Sharma — performance marketing for D2C & e-commerce, on Meta + Google. Judged on ROAS, not reports.' },

  { type: 'cta', kicker: 'YOUR MOVE',
    headline: 'WANT YOUR ACCOUNT TO <mark>READ LIKE THIS?</mark>',
    sub: 'I take on a few brands at a time. DM me your monthly ad spend — I’ll tell you straight if I can move the number.' },
];

function wallHtml(items) {
  return `<div class="wall">${items.map(it => `
    <div class="witem"><span class="chip">${it.chip}</span>
      <div class="clipcard"><img src="${b64(it.clip)}"></div></div>`).join('')}</div>`;
}

function html(s, i, n) {
  const idx = String(i + 1).padStart(2, '0');
  let visual = '';
  if (s.type === 'proof') visual = `<div class="clipcard big"><img src="${b64(s.clip)}"></div>`;
  else if (s.type === 'wall') visual = wallHtml(s.items);
  const emailBig = s.type === 'cta' ? `<div class="ctamail">✉  ${FOOT.email}</div>` : '';
  const hasVisual = s.type === 'proof' || s.type === 'wall';
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  *{margin:0;padding:0;box-sizing:border-box;-webkit-font-smoothing:antialiased;}
  html,body{width:1080px;height:1350px;}
  .canvas{position:relative;width:1080px;height:1350px;background:${T.bg};color:${T.text};
    padding:74px 72px;display:flex;flex-direction:column;overflow:hidden;}
  .ghost{position:absolute;right:-40px;bottom:-160px;font-family:'Anton';font-size:540px;
    line-height:1;color:${T.ghost};letter-spacing:-8px;z-index:1;}
  .top{display:flex;justify-content:space-between;align-items:center;position:relative;z-index:2;}
  .wordmark{font-family:'Archivo Black';font-size:32px;letter-spacing:1px;}
  .wordmark b{color:${T.accent};}
  .index{font-family:'Poppins SemiBold';font-size:22px;letter-spacing:2px;color:${T.muted};}
  .index em{color:${T.text};font-style:normal;}
  .mid{flex:1;display:flex;flex-direction:column;justify-content:center;position:relative;z-index:2;
    padding-bottom:24px;}
  .kicker{display:flex;align-items:center;gap:14px;margin-bottom:24px;}
  .kicker .bar{width:48px;height:6px;background:${T.accent};border-radius:3px;}
  .kicker span{font-family:'Poppins SemiBold';font-size:21px;letter-spacing:4px;text-transform:uppercase;color:${T.muted};}
  .headline{font-family:'Anton';text-transform:uppercase;line-height:1.14;letter-spacing:-0.5px;
    font-size:${hasVisual ? 84 : 104}px;margin-bottom:24px;}
  .headline mark{background:${T.markBg};color:${T.markText};padding:0.03em 0.12em;border-radius:12px;
    box-decoration-break:clone;-webkit-box-decoration-break:clone;}
  .sub{font-family:'Poppins Medium';font-size:32px;line-height:1.38;color:${T.muted};max-width:900px;}
  .sub.after{margin-top:24px;}
  .clipcard{background:${T.card};border-radius:16px;padding:12px;overflow:hidden;box-shadow:0 24px 70px rgba(0,0,0,0.5);}
  .clipcard img{display:block;width:100%;border-radius:8px;}
  .wall{display:flex;flex-direction:column;gap:22px;}
  .witem{position:relative;}
  .witem .chip{position:absolute;top:-13px;left:16px;z-index:3;background:${T.accent};color:${T.markText};
    font-family:'Poppins SemiBold';font-size:20px;letter-spacing:1px;padding:6px 16px;border-radius:20px;}
  .witem .clipcard{padding:10px;}
  .ctamail{margin-top:30px;font-family:'Poppins SemiBold';font-size:38px;color:${T.accent};}
  .foot{position:relative;z-index:2;border-top:2px solid ${T.rule};padding-top:26px;
    display:flex;justify-content:space-between;align-items:center;font-family:'Poppins SemiBold';font-size:23px;}
  .foot .h{color:${T.text};} .foot .s{color:${T.muted};}
  </style></head><body>
    <div class="canvas">
      <div class="ghost">${idx}</div>
      <div class="top"><div class="wordmark">GS<b>.</b></div><div class="index"><em>${idx}</em> / ${String(n).padStart(2,'0')}</div></div>
      <div class="mid">
        <div class="kicker"><span class="bar"></span><span>${s.kicker}</span></div>
        <div class="headline">${s.headline}</div>
        ${hasVisual ? `<div class="sub">${s.sub}</div>` + visual : `<div class="sub">${s.sub}</div>` + emailBig}
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
        document.fonts.load("100px 'Anton'"),
        document.fonts.load("32px 'Archivo Black'"),
        document.fonts.load("32px 'Poppins Medium'"),
        document.fonts.load("22px 'Poppins SemiBold'"),
      ]);
      await document.fonts.ready;
      const h = document.querySelector('.headline');
      let size = parseInt(getComputedStyle(h).fontSize, 10);
      const MAX_H = 300;
      const over = () => h.scrollWidth > h.clientWidth || h.getBoundingClientRect().height > MAX_H;
      while (over() && size > 44) { size -= 2; h.style.fontSize = size + 'px'; }
    });
    const name = `proof-${String(i + 1).padStart(2, '0')}.png`;
    const file = path.join(OUT, name);
    await page.locator('.canvas').screenshot({ path: file });
    fs.copyFileSync(file, path.join(PUB, name));
    console.log('rendered', name);
  }
  await browser.close();
})();
