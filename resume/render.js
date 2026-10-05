/*
 * Renders resume/garvit-sharma-google-sgc.html to a PDF next to it.
 * Run:  NODE_PATH=/opt/node22/lib/node_modules node resume/render.js
 */
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const src = path.join(__dirname, 'garvit-sharma-google-sgc.html');
  const out = src.replace(/\.html$/, '.pdf');
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + src);
  await page.pdf({ path: out, format: 'A4', preferCSSPageSize: true, printBackground: true });
  await browser.close();
  console.log('wrote', out);
})();
