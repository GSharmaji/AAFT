/*
 * "Fundamentals > Hype" LinkedIn carousel generator (1080x1350 slides).
 * Same brand system as build.js / results.js: system fonts (NOT @font-face —
 * this Chromium paints @font-face as serif), ink theme, Anton headline with a
 * lime <mark>, ghost number, auto-fit headline.
 *
 * Proof visuals are designed Google-Ads-style stat tiles built from real
 * numbers — no client or campaign name appears anywhere.
 *
 * Run:  bash design/install-fonts.sh   (once)
 *       NODE_PATH="$(npm root -g)" node design/carousel.js
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT = path.join(__dirname, 'out');
const PUB = path.join(__dirname, '..', 'assets', 'carousel');
fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(PUB, { recursive: true });

const T = {
  bg: '#0F1115', text: '#FFFFFF', muted: '#8A8F98', accent: '#C8FF00',
  markBg: '#C8FF00', markText: '#0F1115', ghost: 'rgba(255,255,255,0.05)',
  rule: 'rgba(255,255,255,0.14)',
};

// Google-Ads-style tile colors.
const G = { blue: '#4285F4', red: '#EA4335', amber: '#F9AB00', green: '#34A853' };

// ---- Slides ---------------------------------------------------------------
// tiles: array of { label, value, color } rendered as a colored metric strip.
const SLIDES = [
  { kicker: 'PERFORMANCE MARKETING',
    headline: 'EVERYONE WANTS THE HACK. NOBODY WANTS THE <mark>HABIT.</mark>',
    sub: 'The most profitable ad account I have ever run had zero “growth hacks” in it.',
    swipe: true },

  { kicker: 'ONE CLIENT · 3 YEARS',
    headline: '₹3L IN. <mark>₹68L</mark> OUT.',
    sub: 'Real account. No viral moment. No trick. Here is what it actually took →',
    tiles: [
      { label: 'COST', value: '₹3.02L', color: G.blue },
      { label: 'PURCHASES', value: '1.13K', color: G.red },
      { label: 'IN SALES', value: '₹68.6L', color: G.amber },
      { label: 'ACTUAL ROAS', value: '2,273%', color: G.green },
    ] },

  { kicker: 'THE REAL LESSON',
    headline: 'THE NUMBER ISN’T THE FLEX. THE <mark>BORING</mark> IS.',
    sub: '22x isn’t a campaign. It’s four unglamorous habits, repeated until they compounded. Here they are.' },

  { kicker: 'HABIT 01',
    headline: 'KILL LOSERS <mark>FAST.</mark>',
    sub: 'Most marketers protect underperformers out of ego. We cut anything below target in days — so budget only ever fed winners.',
    tiles: [
      { label: 'SPEND (1 MONTH)', value: '₹6K', color: G.blue },
      { label: 'IN SALES', value: '₹2.5L', color: G.amber },
      { label: 'ROAS', value: '42x', color: G.green },
    ] },

  { kicker: 'HABIT 02',
    headline: 'FIX THE <mark>OFFER</mark>, NOT THE AUDIENCE.',
    sub: 'Everyone edits the targeting. We rewrote the reason to buy. Cost-per-purchase fell to ₹150–500 while order value climbed.' },

  { kicker: 'HABIT 03',
    headline: 'READ ROAS BY <mark>CAMPAIGN.</mark>',
    sub: 'Same account, same month: one campaign returned 40x, another 12x. Blend them and you’ll cut the wrong one. Averages lie.',
    tiles: [
      { label: 'CAMPAIGN A', value: '40x', color: G.green },
      { label: 'CAMPAIGN B', value: '12x', color: G.red },
    ] },

  { kicker: 'HABIT 04',
    headline: 'BE IN THE ACCOUNT <mark>DAILY.</mark>',
    sub: 'No set-and-forget. A 22x return is a hundred small decisions — pause, shift, test — repeated for 36 months straight.' },

  { kicker: 'FOR THE INDUSTRY',
    headline: 'THE HACK IS THAT THERE IS <mark>NO HACK.</mark>',
    sub: 'While everyone chases the next AI trick, the fundamentals sit right there — unglamorous and undefeated.\n\nWhat’s one “growth hack” you’ve watched quietly die? 👇',
    cta: 'Garvit Sharma · sharmagarvit11@gmail.com' },
];

function tilesHtml(tiles) {
  if (!tiles) return '';
  const cell = (t) => {
    const dark = t.color === G.amber;
    const txt = dark ? '#0F1115' : '#FFFFFF';
    const lab = dark ? 'rgba(15,17,21,0.72)' : 'rgba(255,255,255,0.82)';
    return `<div class="cell" style="background:${t.color};color:${txt}">
      <div class="cl" style="color:${lab}">${t.label}</div>
      <div class="cv">${t.value}</div>
    </div>`;
  };
  return `<div class="tiles">${tiles.map(cell).join('')}</div>`;
}

function html(slide, i, n) {
  const idx = String(i + 1).padStart(2, '0');
  const total = String(n).padStart(2, '0');
  const swipe = slide.swipe ? `<div class="swipe">SWIPE →</div>` : '';
  const cta = slide.cta ? `<div class="ctaline">${slide.cta}</div>` : '';
  const subHtml = (slide.sub || '').split('\n\n').map(p => `<p>${p}</p>`).join('');
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  *{margin:0;padding:0;box-sizing:border-box;-webkit-font-smoothing:antialiased;}
  html,body{width:1080px;height:1350px;}
  .canvas{position:relative;width:1080px;height:1350px;background:${T.bg};color:${T.text};
    padding:84px 84px 78px;display:flex;flex-direction:column;overflow:hidden;}
  .ghost{position:absolute;right:-40px;bottom:-160px;font-family:'Anton';font-size:600px;
    line-height:1;color:${T.ghost};letter-spacing:-8px;z-index:1;}
  .top{display:flex;justify-content:space-between;align-items:center;position:relative;z-index:2;}
  .wordmark{font-family:'Archivo Black';font-size:34px;letter-spacing:1px;}
  .wordmark b{color:${T.accent};}
  .index{font-family:'Poppins SemiBold';font-size:22px;letter-spacing:2px;color:${T.muted};}
  .index em{color:${T.text};font-style:normal;}
  .block{margin-top:auto;position:relative;z-index:2;}
  .kicker{display:flex;align-items:center;gap:16px;margin-bottom:36px;}
  .kicker .bar{width:52px;height:6px;background:${T.accent};border-radius:3px;}
  .kicker span{font-family:'Poppins SemiBold';font-size:22px;letter-spacing:5px;text-transform:uppercase;color:${T.muted};}
  .headline{font-family:'Anton';text-transform:uppercase;line-height:1.28;letter-spacing:-0.5px;font-size:118px;margin-bottom:34px;}
  .headline mark{background:${T.markBg};color:${T.markText};padding:0.04em 0.13em;border-radius:14px;
    box-decoration-break:clone;-webkit-box-decoration-break:clone;}
  .sub p{font-family:'Poppins Medium';font-size:34px;line-height:1.38;color:${T.muted};max-width:880px;}
  .sub p + p{margin-top:22px;color:${T.text};}
  .tiles{display:flex;gap:16px;margin-top:44px;}
  .cell{flex:1;border-radius:20px;padding:30px 26px;min-height:160px;display:flex;flex-direction:column;justify-content:space-between;}
  .cell .cl{font-family:'Poppins SemiBold';font-size:19px;letter-spacing:1.5px;}
  .cell .cv{font-family:'Anton';font-size:66px;line-height:0.9;letter-spacing:-1px;}
  .swipe{margin-top:46px;font-family:'Poppins SemiBold';font-size:26px;color:${T.accent};letter-spacing:2px;}
  .ctaline{margin-top:40px;font-family:'Poppins SemiBold';font-size:30px;color:${T.accent};}
  .foot{position:relative;z-index:2;margin-top:44px;border-top:2px solid ${T.rule};padding-top:28px;
    display:flex;justify-content:space-between;align-items:center;font-family:'Poppins SemiBold';font-size:24px;}
  .foot .h{color:${T.text};} .foot .s{color:${T.muted};}
  </style></head><body>
    <div class="canvas">
      <div class="ghost">${idx}</div>
      <div class="top">
        <div class="wordmark">AAFT<b>.</b></div>
        <div class="index"><em>${idx}</em> / ${total}</div>
      </div>
      <div class="block">
        <div class="kicker"><span class="bar"></span><span>${slide.kicker}</span></div>
        <div class="headline">${slide.headline}</div>
        <div class="sub">${subHtml}</div>
        ${tilesHtml(slide.tiles)}
        ${swipe}${cta}
      </div>
      <div class="foot"><span class="h">GARVIT SHARMA</span><span class="s">Marketing that compounds</span></div>
    </div>
  </body></html>`;
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
  for (let i = 0; i < SLIDES.length; i++) {
    const slide = SLIDES[i];
    await page.setContent(html(slide, i, SLIDES.length), { waitUntil: 'networkidle' });
    await page.evaluate(async (hasTiles) => {
      await Promise.all([
        document.fonts.load("118px 'Anton'"),
        document.fonts.load("34px 'Archivo Black'"),
        document.fonts.load("34px 'Poppins Medium'"),
        document.fonts.load("24px 'Poppins SemiBold'"),
        document.fonts.load("66px 'Anton'"),
      ]);
      await document.fonts.ready;
      const h = document.querySelector('.headline');
      const MAX_H = hasTiles ? 430 : 620;
      let size = 118;
      h.style.fontSize = size + 'px';
      const over = () => h.scrollWidth > h.clientWidth || h.getBoundingClientRect().height > MAX_H;
      while (over() && size > 54) { size -= 2; h.style.fontSize = size + 'px'; }
    }, !!slide.tiles);
    const name = `slide-${String(i + 1).padStart(2, '0')}.png`;
    const file = path.join(OUT, name);
    await page.locator('.canvas').screenshot({ path: file });
    fs.copyFileSync(file, path.join(PUB, name));
    console.log('rendered', name);
  }
  await browser.close();
})();
