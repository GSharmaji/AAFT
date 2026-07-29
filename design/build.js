/*
 * Social post design generator.
 * Renders each post in content calendar to a 1080x1350 (4:5) PNG using a locked
 * brand template. Text is real DOM text -> always crisp, never misspelled.
 *
 * Run:  NODE_PATH=/opt/node22/lib/node_modules node design/build.js [index]
 *       (optional index 1..N renders just that one post, for previews)
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(__dirname, 'out');
fs.mkdirSync(OUT, { recursive: true });

// ---- Brand ----------------------------------------------------------------
const BRAND = { name: 'AAFT', handle: '@aaft.marketing', site: 'aaft.com' };

const THEMES = {
  ink:   { bg: '#0F1115', text: '#FFFFFF', muted: '#8A8F98', accent: '#C8FF00',
           markBg: '#C8FF00', markText: '#0F1115', ghost: 'rgba(255,255,255,0.05)', rule: 'rgba(255,255,255,0.14)' },
  cream: { bg: '#F3ECE1', text: '#16130F', muted: '#6B6155', accent: '#0F1115',
           markBg: '#0F1115', markText: '#C8FF00', ghost: 'rgba(0,0,0,0.05)', rule: 'rgba(0,0,0,0.14)' },
  lime:  { bg: '#C8FF00', text: '#0F1115', muted: '#4B5A05', accent: '#0F1115',
           markBg: '#0F1115', markText: '#C8FF00', ghost: 'rgba(0,0,0,0.06)', rule: 'rgba(0,0,0,0.18)' },
};

// ---- Content (image copy — the caption text lives in content/posts.yaml) ---
const POSTS = [
  { kicker: 'CONSISTENCY', theme: 'ink',
    headline: '<mark>CONSISTENCY</mark> BEATS PERFECTION.',
    sub: 'The algorithm rewards showing up — not showing off.' },
  { kicker: 'SEO', theme: 'cream',
    headline: 'SEO ISN’T KEYWORDS. IT’S BEING <mark>USEFUL.</mark>',
    sub: 'Fast pages. One clear answer. Content people actually finish.' },
  { kicker: 'BRANDING', theme: 'lime',
    headline: 'A LOGO IS <mark>NOT</mark> A BRAND.',
    sub: 'Your brand is what they say when you’ve logged off.' },
  { kicker: 'POSITIONING', theme: 'ink',
    headline: 'TRENDS SPIKE. POSITIONING <mark>COMPOUNDS.</mark>',
    sub: 'One clear message beats a hundred trending audios.' },
  { kicker: 'PAID ADS', theme: 'cream',
    headline: '“BOOST POST” IS <mark>NOT</mark> A STRATEGY.',
    sub: 'Ads pour fuel on fire. No fire? You just burn cash faster.' },
  { kicker: 'EXECUTION', theme: 'ink',
    headline: '<mark>DONE</mark> BEATS PERFECT. EVERY TIME.',
    sub: 'Your competitor is posting while you’re still “planning.”' },
  { kicker: 'COPYWRITING', theme: 'cream',
    headline: 'NOBODY READS YOUR <mark>“ABOUT US.”</mark>',
    sub: 'They read 7 words of your headline, then decide.' },
  { kicker: 'METRICS', theme: 'lime',
    headline: 'FOLLOWERS = VANITY. <mark>REVENUE</mark> = SANITY.',
    sub: '1,000 people who trust you beat 100k who don’t.' },
  { kicker: 'PSYCHOLOGY', theme: 'ink',
    headline: 'THEY DON’T BUY THE DRILL. THEY BUY <mark>THE HOLE.</mark>',
    sub: 'Sell the outcome three steps down. That’s where the money is.' },
  { kicker: 'THE PROMISE', theme: 'ink', cta: true,
    headline: '10 POSTS. 3 WEEKS. <mark>PROMISE KEPT.</mark>',
    sub: 'We did it for our own brand. Imagine what we do for yours.' },
];

// Fonts are loaded from the SYSTEM font path (see design/install-fonts.sh), not
// via @font-face — this Chromium build cannot rasterize @font-face web fonts
// (it reports them "loaded" but paints a serif fallback), while system fonts
// resolved through fontconfig render correctly.

function html(post, i, n) {
  const t = THEMES[post.theme];
  const idx = String(i + 1).padStart(2, '0');
  const total = String(n).padStart(2, '0');
  const ctaBlock = post.cta ? `
      <div class="cta">
        <span class="pill">LET’S TALK &rarr;</span>
        <span class="ctasite">${BRAND.site}</span>
      </div>` : '';
  const pillColor = post.theme === 'lime' ? t.markText : t.bg;
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  *{margin:0;padding:0;box-sizing:border-box;-webkit-font-smoothing:antialiased;}
  html,body{width:1080px;height:1350px;}
  .canvas{position:relative;width:1080px;height:1350px;background:${t.bg};color:${t.text};
    padding:84px 84px 78px;display:flex;flex-direction:column;overflow:hidden;}
  .ghost{position:absolute;right:-34px;bottom:-160px;font-family:'Anton';font-size:660px;
    line-height:1;color:${t.ghost};letter-spacing:-10px;pointer-events:none;user-select:none;z-index:1;}
  .top{display:flex;justify-content:space-between;align-items:center;position:relative;z-index:2;}
  .wordmark{font-family:'Archivo Black';font-size:34px;letter-spacing:1px;}
  .wordmark b{color:${t.accent};}
  .index{font-family:'Poppins SemiBold';font-size:22px;letter-spacing:2px;color:${t.muted};}
  .index em{color:${t.text};font-style:normal;}
  .block{margin-top:auto;position:relative;z-index:2;}
  .kicker{display:flex;align-items:center;gap:16px;margin-bottom:40px;}
  .kicker .bar{width:52px;height:6px;background:${t.accent};border-radius:3px;}
  .kicker span{font-family:'Poppins SemiBold';font-size:23px;letter-spacing:5px;text-transform:uppercase;color:${t.muted};}
  .headline{font-family:'Anton';text-transform:uppercase;line-height:1.32;letter-spacing:-0.5px;
    font-size:120px;margin-bottom:36px;}
  .headline mark{background:${t.markBg};color:${t.markText};
    padding:0.04em 0.14em;border-radius:14px;
    box-decoration-break:clone;-webkit-box-decoration-break:clone;}
  .sub{font-family:'Poppins Medium';font-size:35px;line-height:1.36;color:${t.muted};max-width:840px;}
  .cta{display:flex;align-items:center;gap:26px;margin-top:44px;}
  .cta .pill{font-family:'Poppins SemiBold';font-size:30px;background:${t.accent};
    color:${pillColor};padding:20px 40px;border-radius:60px;}
  .cta .ctasite{font-family:'Poppins SemiBold';font-size:30px;color:${t.text};}
  .foot{position:relative;z-index:2;margin-top:44px;border-top:2px solid ${t.rule};
    padding-top:30px;display:flex;justify-content:space-between;align-items:center;
    font-family:'Poppins SemiBold';font-size:26px;}
  .foot .h{color:${t.text};} .foot .s{color:${t.muted};}
  </style></head><body>
    <div class="canvas">
      <div class="ghost">${idx}</div>
      <div class="top">
        <div class="wordmark">${BRAND.name}<b>.</b></div>
        <div class="index"><em>${idx}</em> / ${total}</div>
      </div>
      <div class="block">
        <div class="kicker"><span class="bar"></span><span>${post.kicker}</span></div>
        <div class="headline">${post.headline}</div>
        <div class="sub">${post.sub}</div>
        ${ctaBlock}
      </div>
      <div class="foot"><span class="h">${BRAND.handle}</span><span class="s">${BRAND.site}</span></div>
    </div>
  </body></html>`;
}

(async () => {
  const only = process.argv[2] ? parseInt(process.argv[2], 10) : null;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
  for (let i = 0; i < POSTS.length; i++) {
    if (only && i + 1 !== only) continue;
    await page.setContent(html(POSTS[i], i, POSTS.length), { waitUntil: 'networkidle' });
    await page.evaluate(async () => {
      await Promise.all([
        document.fonts.load("118px 'Anton'"),
        document.fonts.load("34px 'Archivo Black'"),
        document.fonts.load("34px 'Poppins Medium'"),
        document.fonts.load("26px 'Poppins SemiBold'"),
      ]);
      await document.fonts.ready;
      // Auto-fit: shrink the headline until it fits its width and a max height,
      // so hooks of different lengths all sit cleanly in the block.
      const h = document.querySelector('.headline');
      const MAX_H = 640;
      let size = 120;
      h.style.fontSize = size + 'px';
      const overflows = () => h.scrollWidth > h.clientWidth || h.getBoundingClientRect().height > MAX_H;
      while (overflows() && size > 58) { size -= 2; h.style.fontSize = size + 'px'; }
    });
    if (process.env.DBG) {
      const info = await page.evaluate(() => {
        const h = document.querySelector('.headline');
        return { font: getComputedStyle(h).fontFamily, check: document.fonts.check("118px 'Anton'"),
                 faces: [...document.fonts].map(f => f.family + ':' + f.status) };
      });
      console.log('DBG', JSON.stringify(info));
    }
    const file = path.join(OUT, `post-${String(i + 1).padStart(2, '0')}.png`);
    await page.locator('.canvas').screenshot({ path: file });
    console.log('rendered', path.relative(ROOT, file));
  }
  await browser.close();
})();
