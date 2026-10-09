"""
Wraps a resume body fragment in the shared page layout, so each job only stores its content.

  python3 resume/build.py "<path>/<Name>.body.html"   ->  writes "<path>/<Name>.html"
Then render:  NODE_PATH=/opt/node22/lib/node_modules node resume/render.js "<path>/<Name>.html"
"""
import html
import pathlib
import sys

STYLE = """
  @page { size: A4; margin: 9mm 12mm; }
  * { box-sizing: border-box; }
  body { margin: 0; background: #fff; color: #1a1a1a;
         font: 9.4pt/1.28 Arial, Helvetica, sans-serif; }
  h1 { font-size: 19pt; margin: 0 0 1px; letter-spacing: .3px; }
  .tagline { font-weight: bold; font-size: 10pt; margin-bottom: 2px; }
  .contact { color: #444; font-size: 9.2pt; margin-bottom: 5px; }
  h2 { font-size: 10.2pt; text-transform: uppercase; letter-spacing: 1px;
       border-bottom: 1.2px solid #1a1a1a; padding-bottom: 2px; margin: 7px 0 3px; }
  .role { display: flex; justify-content: space-between; font-weight: bold; margin-top: 5px; }
  .org { font-style: italic; color: #333; margin-bottom: 1px; }
  ul { margin: 1px 0 0; padding-left: 15px; }
  li { margin-bottom: 2px; }
  p { margin: 0 0 2px; }
"""

src = pathlib.Path(sys.argv[1])
title = src.name.removesuffix(".body.html")
out = src.with_name(title + ".html")
out.write_text(
    f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
    f"<title>{html.escape(title)}</title>\n<style>{STYLE}</style>\n</head>\n<body>\n"
    f"{src.read_text()}\n</body>\n</html>\n"
)
print("wrote", out)
