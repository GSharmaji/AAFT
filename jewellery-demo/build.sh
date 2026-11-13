#!/bin/sh
# Makes index.html (a full web page) from page.html (the page content).
cd "$(dirname "$0")"
{ printf '<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'; cat page.html; } > index.html
