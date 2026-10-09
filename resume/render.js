/*
 * Renders a resume HTML file to a PDF next to it, and reports the page count.
 * Run:  NODE_PATH=/opt/node22/lib/node_modules node resume/render.js <path/to/resume.html>
 */
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const arg = process.argv[2];
  if (!arg) { console.error('usage: node resume/render.js <resume.html>'); process.exit(1); }
  const src = path.resolve(arg);
  const out = src.replace(/\.html$/, '.pdf');
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + src);
  await page.pdf({ path: out, format: 'A4', preferCSSPageSize: true, printBackground: true });
  await browser.close();
  console.log('wrote', out);
})();
