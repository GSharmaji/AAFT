#!/usr/bin/env bash
# Installs the display fonts used by design/build.js into the user font path so
# Chromium (via fontconfig) can render them.
#
# NOTE: This project references fonts by SYSTEM family name rather than CSS
# @font-face, because the bundled Chromium cannot rasterize @font-face web
# fonts (it reports them "loaded" but paints a serif fallback). Full,
# non-subset TTFs are required — subset TTFs get rejected by FreeType.
#
# Run once before `node design/build.js`.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${HOME}/.local/share/fonts/aaft"
mkdir -p "$DEST"
cp "$DIR/fonts/"*.ttf "$DEST/"
fc-cache -f "$DEST" >/dev/null 2>&1 || fc-cache -f >/dev/null 2>&1 || true
echo "Installed fonts to $DEST"
fc-list | grep -iE "anton|archivo|poppins" | sed 's#.*/##' || true
