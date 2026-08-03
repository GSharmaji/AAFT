/*
 * Results / proof card generator (1080x1350) — same brand system as build.js.
 * Presents real ad-account numbers with NO client or campaign names, so there
 * is nothing to redact. Run:
 *   NODE_PATH="$(npm root -g)" node design/results.js
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT = path.join(__dirname, 'out');
fs.mkdirSync(OUT, { recursive: true });

const BRAND = { name: 'AAFT', person: 'Garvit Sharma', email: 'sharmagarvit11@gmail.com' };

const T = { bg: '#0F1115', text: '#FFFFFF', muted: '#8A8F98', accent: '#C8FF00',
            markBg: '#C8FF00', markText: '#0F1115', ghost: 'rgba(255,255,255,0.05)',
            rule: 'rgba(255,255,255,0.14)', tile: 'rgba(255,255,255,0.04)', tileBorder: 'rgba(255,255,255,0.10)' };

// Real, defensible figures pulled from the shared Google Ads account (lifetime).
const TILES = [
  { n: '₹3.02L', label: 'AD SPEND' },
  { n: '₹68.6L', label: 'IN SALES' },
  { n: '22.7x', label: 'RETURN (ROAS)' },
];

function html() {
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  *{margin:0;padding:0;box-sizing:border-box;-webkit-font-smoothing:antialiased;}
  html,body{width:1080px;height:1350px;}
  .canvas{position:relative;width:1080px;height:1350px;background:${T.bg};color:${T.text};
    padding:84px 84px 78px;display:flex;flex-direction:column;overflow:hidden;}
  .ghost{position:absolute;right:-40px;bottom:-150px;font-family:'Anton';font-size:560px;
    line-height:1;color:${T.ghost};letter-spacing:-8px;z-index:1;}
  .top{display:flex;justify-content:space-between;align-items:center;position:relative;z-index:2;}
  .wordmark{font-family:'Archivo Black';font-size:34px;letter-spacing:1px;}
  .wordmark b{color:${T.accent};}
  .badge{font-family:'Poppins SemiBold';font-size:20px;letter-spacing:3px;color:${T.muted};}
  .block{margin-top:auto;position:relative;z-index:2;}
  .kicker{display:flex;align-items:center;gap:16px;margin-bottom:38px;}
  .kicker .bar{width:52px;height:6px;background:${T.accent};border-radius:3px;}
  .kicker span{font-family:'Poppins SemiBold';font-size:23px;letter-spacing:5px;text-transform:uppercase;color:${T.muted};}
  .headline{font-family:'Anton';text-transform:uppercase;line-height:1.05;letter-spacing:-0.5px;font-size:132px;margin-bottom:34px;}
  .headline mark{background:${T.markBg};color:${T.markText};padding:0.02em 0.12em;border-radius:14px;}
  .sub{font-family:'Poppins Medium';font-size:33px;line-height:1.36;color:${T.muted};max-width:860px;margin-bottom:50px;}
  .tiles{display:flex;gap:22px;margin-bottom:30px;}
  .tile{flex:1;background:${T.tile};border:2px solid ${T.tileBorder};border-radius:22px;padding:34px 30px;}
  .tile .n{font-family:'Anton';font-size:74px;line-height:1;color:${T.accent};letter-spacing:-1px;}
  .tile .l{font-family:'Poppins SemiBold';font-size:21px;letter-spacing:2px;color:${T.muted};margin-top:14px;}
  .micro{font-family:'Poppins SemiBold';font-size:25px;color:${T.text};}
  .micro b{color:${T.accent};}
  .foot{position:relative;z-index:2;margin-top:44px;border-top:2px solid ${T.rule};padding-top:30px;
    display:flex;justify-content:space-between;align-items:center;font-family:'Poppins SemiBold';font-size:26px;}
  .foot .h{color:${T.text};} .foot .s{color:${T.muted};}
  </style></head><body>
    <div class="canvas">
      <div class="ghost">%</div>
      <div class="top"><div class="wordmark">${BRAND.name}<b>.</b></div><div class="badge">CLIENT RESULTS · GOOGLE ADS</div></div>
      <div class="block">
        <div class="kicker"><span class="bar"></span><span>Proof, not promises</span></div>
        <div class="headline">₹3L IN. <mark>₹68L</mark> OUT.</div>
        <div class="sub">Three years of disciplined ad spend on a single client account. Same rupees in, very different rupees out.</div>
        <div class="tiles">
          ${TILES.map(t => `<div class="tile"><div class="n">${t.n}</div><div class="l">${t.label}</div></div>`).join('')}
        </div>
        <div class="micro">Repeatable, not a fluke &mdash; sample months at <b>42x &middot; 34x &middot; 22x</b> ROAS.</div>
      </div>
      <div class="foot"><span class="h">${BRAND.person}</span><span class="s">${BRAND.email}</span></div>
    </div>
  </body></html>`;
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
  await page.setContent(html(), { waitUntil: 'networkidle' });
  await page.evaluate(async () => {
    await Promise.all([
      document.fonts.load("120px 'Anton'"),
      document.fonts.load("34px 'Archivo Black'"),
      document.fonts.load("33px 'Poppins Medium'"),
      document.fonts.load("26px 'Poppins SemiBold'"),
    ]);
    await document.fonts.ready;
  });
  const file = path.join(OUT, 'results-card.png');
  await page.locator('.canvas').screenshot({ path: file });
  console.log('rendered', file);
  await browser.close();
})();
