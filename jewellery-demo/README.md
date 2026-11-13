# Jewellery demo store

A sample product page that shows jewellery in live 3D. No photos are used.

- `page.html` is the page content. Edit this one.
- `styles.css` is the look. `app.js` builds the pieces and runs the viewer.
- `vendor/` holds the three.js 3D library (MIT licence).
- `index.html` is made from `page.html`. Run `./build.sh` after editing.

To view it on your computer:

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000 in a browser.

Pieces, names and prices are examples. Shot six ("On model") is an empty slot for a real photo.
