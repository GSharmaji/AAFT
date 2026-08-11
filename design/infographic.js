/*
 * Educational explainer infographic (1080x1350) — the "teach one concept in a
 * clean table" format (à la the SEO/GEO/AEO and DV360 references), in the
 * charcoal/lime brand. Config-driven so any comparison topic can be swapped.
 *
 * Run: bash design/install-fonts.sh
 *      NODE_PATH="$(npm root -g)" node design/infographic.js
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const OUT = path.join(__dirname, 'out');
const PUB = path.join(__dirname, '..', 'assets', 'infographics');
fs.mkdirSync(OUT, { recursive: true }); fs.mkdirSync(PUB, { recursive: true });

const T = { bg: '#0F1115', text: '#FFFFFF', muted: '#8A8F98', accent: '#C8FF00', amber: '#F9AB00',
            markText: '#0F1115', rule: 'rgba(255,255,255,0.12)', card: 'rgba(255,255,255,0.04)',
            cardBorder: 'rgba(255,255,255,0.10)' };
const FOOT = { name: 'GARVIT SHARMA', email: 'sharmagarvit11@gmail.com' };

const DOC = {
  out: 'meta-bid-strategies.png',
  tag: 'PERFORMANCE PLAYBOOK',
  title: 'META BID <mark>STRATEGIES</mark>',
  subtitle: 'Four ways to tell the algorithm what “good” means — and when to use each.',
  rows: [
    { emoji: '📈', name: 'HIGHEST VOLUME', what: 'Gets the most conversions your budget can buy.',
      best: 'Scaling proven winners, filling the funnel.', catch: 'Chases volume, not value — can buy cheap, low-quality conversions.' },
    { emoji: '🎯', name: 'COST PER RESULT', what: 'Maximises volume while holding a target cost per result.',
      best: 'Keeping CPA in check as you scale.', catch: 'Set the cap too low and delivery stalls.' },
    { emoji: '💰', name: 'ROAS GOAL  ·  NEW', what: 'Optimises toward a target return, prioritising higher-value purchases.',
      best: 'Value-based / e-com campaigns chasing profit, not just orders.', catch: 'Only on NEW ad sets — can’t switch an existing one. Duplicate to test.' },
    { emoji: '🎛️', name: 'BID CAP', what: 'Sets the max bid Meta can place in the auction.',
      best: 'Tight bid control in competitive auctions (advanced).', catch: 'Needs real auction data + active management, or it chokes delivery.' },
  ],
  takeaway: 'The bid strategy is a lever, not a setting. Match it to the goal — volume, cost, or profit.',
  question: 'Still defaulting to Highest Volume — or have you tested the new ROAS Goal? 👇',
};

function rowHtml(r) {
  return `<div class="card">
    <div class="emoji">${r.emoji}</div>
    <div class="body">
      <div class="name">${r.name}</div>
      <div class="what">${r.what}</div>
      <div class="meta">
        <div class="tag"><span class="lbl good">BEST FOR</span> ${r.best}</div>
        <div class="tag"><span class="lbl warn">THE CATCH</span> ${r.catch}</div>
      </div>
    </div>
  </div>`;
}

function html(d) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  *{margin:0;padding:0;box-sizing:border-box;-webkit-font-smoothing:antialiased;}
  html,body{width:1080px;height:1350px;}
  .canvas{width:1080px;height:1350px;background:${T.bg};color:${T.text};padding:60px 64px 54px;
    display:flex;flex-direction:column;overflow:hidden;}
  .top{display:flex;justify-content:space-between;align-items:center;}
  .wordmark{font-family:'Archivo Black';font-size:30px;} .wordmark b{color:${T.accent};}
  .tag{font-family:'Poppins SemiBold';font-size:19px;letter-spacing:3px;color:${T.muted};}
  .title{font-family:'Anton';text-transform:uppercase;font-size:78px;line-height:1.0;letter-spacing:-0.5px;margin-top:26px;}
  .title mark{background:${T.accent};color:${T.markText};padding:0 0.1em;border-radius:10px;}
  .subtitle{font-family:'Poppins Medium';font-size:26px;line-height:1.35;color:${T.muted};margin-top:16px;max-width:920px;}
  .rows{display:flex;flex-direction:column;gap:14px;margin-top:26px;}
  .card{display:flex;gap:20px;background:${T.card};border:1.5px solid ${T.cardBorder};border-radius:18px;padding:20px 22px;}
  .emoji{font-size:40px;line-height:1;width:52px;flex:none;text-align:center;}
  .body{flex:1;}
  .name{font-family:'Anton';font-size:33px;letter-spacing:0.3px;color:${T.text};}
  .what{font-family:'Poppins Medium';font-size:22px;line-height:1.3;color:#C9CDD4;margin-top:4px;}
  .meta{display:flex;flex-direction:column;gap:5px;margin-top:11px;}
  .meta .tag{font-family:'Poppins Medium';font-size:19.5px;line-height:1.32;color:${T.muted};letter-spacing:0;}
  .meta .lbl{font-family:'Poppins SemiBold';font-size:16px;letter-spacing:1px;padding:2px 9px;border-radius:6px;margin-right:8px;}
  .lbl.good{background:rgba(200,255,0,0.16);color:${T.accent};}
  .lbl.warn{background:rgba(249,171,0,0.16);color:${T.amber};}
  .takeaway{margin-top:auto;display:flex;gap:16px;align-items:flex-start;padding-top:22px;}
  .takeaway .bar{width:8px;align-self:stretch;background:${T.accent};border-radius:4px;flex:none;}
  .takeaway .tk{font-family:'Poppins SemiBold';font-size:25px;line-height:1.34;color:${T.text};}
  .takeaway .tk b{color:${T.accent};font-weight:inherit;}
  .q{font-family:'Poppins Medium';font-size:23px;color:${T.muted};margin-top:16px;}
  .foot{margin-top:20px;border-top:2px solid ${T.rule};padding-top:20px;display:flex;justify-content:space-between;
    align-items:center;font-family:'Poppins SemiBold';font-size:22px;}
  .foot .h{color:${T.text};} .foot .s{color:${T.muted};}
  </style></head><body>
    <div class="canvas">
      <div class="top"><div class="wordmark">GS<b>.</b></div><div class="tag">${d.tag}</div></div>
      <div class="title">${d.title}</div>
      <div class="subtitle">${d.subtitle}</div>
      <div class="rows">${d.rows.map(rowHtml).join('')}</div>
      <div class="takeaway"><div class="bar"></div><div class="tk">${d.takeaway}</div></div>
      <div class="q">${d.question}</div>
      <div class="foot"><span class="h">${FOOT.name}</span><span class="s">${FOOT.email}</span></div>
    </div>
  </body></html>`;
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
  await page.setContent(html(DOC), { waitUntil: 'networkidle' });
  await page.evaluate(async () => {
    await Promise.all([
      document.fonts.load("78px 'Anton'"), document.fonts.load("30px 'Archivo Black'"),
      document.fonts.load("26px 'Poppins Medium'"), document.fonts.load("22px 'Poppins SemiBold'"),
    ]);
    await document.fonts.ready;
  });
  const file = path.join(OUT, DOC.out);
  await page.locator('.canvas').screenshot({ path: file });
  fs.copyFileSync(file, path.join(PUB, DOC.out));
  console.log('rendered', DOC.out);
  await browser.close();
})();
