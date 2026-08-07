/*
 * V2 post designs — one creative treatment per idea, not one template for all.
 * Three archetypes: 'stat' (number-forward proof), 'versus' (two-panel compare),
 * 'statement' (bold one-liner). Same brand system as build.js/results.js
 * (system fonts, ink/cream/lime, Anton + Poppins, 1080x1350, auto-fit headline).
 *
 * Run:  bash design/install-fonts.sh   (once)
 *       NODE_PATH="$(npm root -g)" node design/v2.js [index]
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT = path.join(__dirname, 'out');
const PUB = path.join(__dirname, '..', 'assets', 'v2');
fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(PUB, { recursive: true });

const FOOT = { name: 'GARVIT SHARMA', tag: 'Performance marketing' };
const G = { blue: '#4285F4', red: '#EA4335', amber: '#F9AB00', green: '#34A853' };

const THEMES = {
  ink:   { bg: '#0F1115', text: '#FFFFFF', muted: '#8A8F98', accent: '#C8FF00',
           markBg: '#C8FF00', markText: '#0F1115', ghost: 'rgba(255,255,255,0.05)', rule: 'rgba(255,255,255,0.14)' },
  cream: { bg: '#F3ECE1', text: '#16130F', muted: '#6B6155', accent: '#0F1115',
           markBg: '#0F1115', markText: '#C8FF00', ghost: 'rgba(0,0,0,0.05)', rule: 'rgba(0,0,0,0.14)' },
  lime:  { bg: '#C8FF00', text: '#0F1115', muted: '#4B5A05', accent: '#0F1115',
           markBg: '#0F1115', markText: '#C8FF00', ghost: 'rgba(0,0,0,0.06)', rule: 'rgba(0,0,0,0.18)' },
};

// tile/panel text color: dark ink text on light fills (amber/lime), else white.
const onColor = (c) => (c === G.amber || c === '#C8FF00') ? '#0F1115' : '#FFFFFF';
const onColorMuted = (c) => (c === G.amber || c === '#C8FF00') ? 'rgba(15,17,21,0.7)' : 'rgba(255,255,255,0.8)';

const POSTS = [
  { n: 1, theme: 'ink', type: 'stat', kicker: 'THE 3-YEAR ACCOUNT',
    headline: 'NO HACK. JUST <mark>36 MONTHS.</mark>', sub: 'The boring stuff isn’t the price of the result. It IS the result.',
    tiles: [ {l:'AD SPEND',v:'₹3.02L',c:G.blue}, {l:'IN SALES',v:'₹68.6L',c:G.amber}, {l:'ROAS',v:'22.7x',c:G.green} ] },

  { n: 2, theme: 'ink', type: 'stat', kicker: 'RUTHLESS PRUNING',
    headline: 'I KILLED <mark>60%</mark> OF MY ADS.', sub: 'Then budget only ever fed the winners. One month:',
    tiles: [ {l:'SPEND',v:'₹6K',c:G.blue}, {l:'IN SALES',v:'₹2.5L',c:G.amber}, {l:'ROAS',v:'42x',c:G.green} ] },

  { n: 3, theme: 'ink', type: 'stat', kicker: 'TEST TINY',
    headline: 'A <mark>₹49</mark> TEST BEAT A ₹49,000 GUESS.', sub: 'Small tests find winners. Big budgets just multiply what you already have.',
    tiles: [ {l:'TEST SPEND',v:'₹49',c:G.blue}, {l:'RETURN',v:'~130x',c:G.green} ] },

  { n: 4, theme: 'ink', type: 'versus', kicker: 'READ IT RIGHT',
    headline: 'THE AVERAGE <mark>LIED.</mark>', sub: 'Same account, same month. Blended ROAS hides your winners.',
    panels: [ {l:'CAMPAIGN A',v:'40x',note:'quietly carrying it',c:G.green},
              {l:'CAMPAIGN B',v:'12x',note:'felt busy, wasn’t',c:G.red} ] },

  { n: 5, theme: 'cream', type: 'statement', kicker: 'ACCOUNT STRUCTURE',
    headline: 'TEST IN ONE PLACE. <mark>SCALE</mark> IN ANOTHER.', sub: 'Most accounts are just a junk drawer of half-tested ideas.' },

  { n: 6, theme: 'ink', type: 'stat', kicker: 'OFFER > CREATIVE',
    headline: 'THE <mark>OFFER</mark> BEAT THE CREATIVE.', sub: 'Same audience. Same-ish ads. A different reason to buy now.',
    tiles: [ {l:'CREATIVES TESTED',v:'11',c:G.blue}, {l:'CPP AFTER',v:'₹150–500',c:G.green} ] },

  { n: 7, theme: 'ink', type: 'statement', kicker: 'SCALING',
    headline: 'EVERY WINNING AD HAS AN <mark>EXPIRY DATE.</mark>', sub: 'Frequency. Fatigue. Saturation. The three quiet killers.' },

  { n: 8, theme: 'cream', type: 'statement', kicker: 'CREATIVE TESTING',
    headline: 'TEST <mark>THE ANGLE</mark>, NOT THE ART.', sub: 'Your favourite ad and the winning ad are rarely the same one.' },

  { n: 9, theme: 'ink', type: 'versus', kicker: 'GOOGLE vs META',
    headline: 'TWO HALVES OF <mark>ONE JOB.</mark>', sub: 'Kill one and you leak buyers. Kill the other and growth caps out.',
    panels: [ {l:'GOOGLE',v:'CATCHES',note:'demand that already exists',c:G.blue},
              {l:'META',v:'CREATES',note:'demand from scratch',c:'#C8FF00'} ] },

  { n: 10, theme: 'cream', type: 'statement', kicker: 'DAILY ROUTINE',
    headline: '<mark>10 BORING MINUTES</mark> BEAT ONE PANIC MEETING.', sub: 'Accounts don’t blow up. They rot from small things nobody checked.' },

  { n: 11, theme: 'lime', type: 'statement', kicker: 'FESTIVE PLAYBOOK',
    headline: 'DIWALI IS WON IN <mark>SEPTEMBER.</mark>', sub: 'The brands crushing peak season started before the rush.' },

  { n: 12, theme: 'ink', type: 'statement', kicker: 'SCALING MISTAKE',
    headline: 'SCALE <mark>IN GEARS</mark>, NOT LEAPS.', sub: 'A huge budget jump resets learning — and you pay the tuition twice.' },
];

function tilesHtml(tiles, t) {
  return `<div class="tiles">${tiles.map(x => `
    <div class="tile" style="background:${x.c};color:${onColor(x.c)}">
      <div class="tl" style="color:${onColorMuted(x.c)}">${x.l}</div>
      <div class="tv">${x.v}</div>
    </div>`).join('')}</div>`;
}

function versusHtml(panels) {
  return `<div class="versus">${panels.map(p => `
    <div class="panel" style="background:${p.c};color:${onColor(p.c)}">
      <div class="pl" style="color:${onColorMuted(p.c)}">${p.l}</div>
      <div class="pv">${p.v}</div>
      <div class="pn" style="color:${onColorMuted(p.c)}">${p.note}</div>
    </div>`).join('')}</div>`;
}

function html(p) {
  const t = THEMES[p.theme];
  const idx = String(p.n).padStart(2, '0');
  let visual = '';
  if (p.type === 'stat') visual = tilesHtml(p.tiles, t);
  else if (p.type === 'versus') visual = versusHtml(p.panels);
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  *{margin:0;padding:0;box-sizing:border-box;-webkit-font-smoothing:antialiased;}
  html,body{width:1080px;height:1350px;}
  .canvas{position:relative;width:1080px;height:1350px;background:${t.bg};color:${t.text};
    padding:84px 84px 78px;display:flex;flex-direction:column;overflow:hidden;}
  .ghost{position:absolute;right:-40px;bottom:-160px;font-family:'Anton';font-size:600px;
    line-height:1;color:${t.ghost};letter-spacing:-8px;z-index:1;}
  .top{display:flex;justify-content:space-between;align-items:center;position:relative;z-index:2;}
  .wordmark{font-family:'Archivo Black';font-size:32px;letter-spacing:1px;}
  .wordmark b{color:${t.accent};}
  .index{font-family:'Poppins SemiBold';font-size:22px;letter-spacing:2px;color:${t.muted};}
  .index em{color:${t.text};font-style:normal;}
  .block{margin-top:auto;position:relative;z-index:2;}
  .kicker{display:flex;align-items:center;gap:16px;margin-bottom:34px;}
  .kicker .bar{width:52px;height:6px;background:${t.accent};border-radius:3px;}
  .kicker span{font-family:'Poppins SemiBold';font-size:22px;letter-spacing:5px;text-transform:uppercase;color:${t.muted};}
  .headline{font-family:'Anton';text-transform:uppercase;line-height:1.28;letter-spacing:-0.5px;font-size:112px;margin-bottom:32px;}
  .headline mark{background:${t.markBg};color:${t.markText};padding:0.04em 0.13em;border-radius:14px;
    box-decoration-break:clone;-webkit-box-decoration-break:clone;}
  .sub{font-family:'Poppins Medium';font-size:33px;line-height:1.36;color:${t.muted};max-width:880px;}
  .tiles{display:flex;gap:16px;margin-top:42px;}
  .tile{flex:1;border-radius:20px;padding:30px 26px;min-height:170px;display:flex;flex-direction:column;justify-content:space-between;}
  .tile .tl{font-family:'Poppins SemiBold';font-size:19px;letter-spacing:1.5px;}
  .tile .tv{font-family:'Anton';font-size:64px;line-height:0.9;letter-spacing:-1px;}
  .versus{display:flex;gap:20px;margin-top:42px;}
  .panel{flex:1;border-radius:22px;padding:34px 30px;min-height:250px;display:flex;flex-direction:column;justify-content:space-between;}
  .panel .pl{font-family:'Poppins SemiBold';font-size:20px;letter-spacing:2px;}
  .panel .pv{font-family:'Anton';font-size:96px;line-height:0.85;letter-spacing:-1px;}
  .panel .pn{font-family:'Poppins Medium';font-size:24px;line-height:1.2;}
  .foot{position:relative;z-index:2;margin-top:44px;border-top:2px solid ${t.rule};padding-top:28px;
    display:flex;justify-content:space-between;align-items:center;font-family:'Poppins SemiBold';font-size:24px;}
  .foot .h{color:${t.text};} .foot .s{color:${t.muted};}
  </style></head><body>
    <div class="canvas">
      <div class="ghost">${idx}</div>
      <div class="top"><div class="wordmark">GS<b>.</b></div><div class="index"><em>${idx}</em> / 12</div></div>
      <div class="block">
        <div class="kicker"><span class="bar"></span><span>${p.kicker}</span></div>
        <div class="headline">${p.headline}</div>
        <div class="sub">${p.sub}</div>
        ${visual}
      </div>
      <div class="foot"><span class="h">${FOOT.name}</span><span class="s">${FOOT.tag}</span></div>
    </div>
  </body></html>`;
}

(async () => {
  const only = process.argv[2] ? parseInt(process.argv[2], 10) : null;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
  for (const p of POSTS) {
    if (only && p.n !== only) continue;
    await page.setContent(html(p), { waitUntil: 'networkidle' });
    await page.evaluate(async (hasVisual) => {
      await Promise.all([
        document.fonts.load("112px 'Anton'"),
        document.fonts.load("32px 'Archivo Black'"),
        document.fonts.load("33px 'Poppins Medium'"),
        document.fonts.load("24px 'Poppins SemiBold'"),
        document.fonts.load("64px 'Anton'"),
      ]);
      await document.fonts.ready;
      const h = document.querySelector('.headline');
      const MAX_H = hasVisual ? 400 : 620;
      let size = 112;
      h.style.fontSize = size + 'px';
      const over = () => h.scrollWidth > h.clientWidth || h.getBoundingClientRect().height > MAX_H;
      while (over() && size > 52) { size -= 2; h.style.fontSize = size + 'px'; }
    }, p.type !== 'statement');
    const name = `v2-${String(p.n).padStart(2, '0')}.png`;
    const file = path.join(OUT, name);
    await page.locator('.canvas').screenshot({ path: file });
    fs.copyFileSync(file, path.join(PUB, name));
    console.log('rendered', name);
  }
  await browser.close();
})();
