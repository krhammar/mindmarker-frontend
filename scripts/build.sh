#!/usr/bin/env bash
#
# Build the static site that Cloudflare Pages publishes.
#
# The Python sources are not compiled: Stlite downloads them at runtime and
# runs them with Pyodide inside the visitor's browser. This script only
# assembles the files that need to be served.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"

rm -rf "$DIST"
mkdir -p "$DIST/pages"

cp "$ROOT/index.html" "$ROOT/_redirects" "$ROOT/_headers" "$ROOT/requirements.txt" "$DIST/"
cp "$ROOT"/*.py "$DIST/"
cp "$ROOT"/pages/*.py "$DIST/pages/"

# Static assets referenced from Python (st.image, page_icon, ...). These have
# to be served over HTTP *and* mounted into Stlite's in-browser file system
# (see the files map in index.html), otherwise they render locally but 404 on
# the deployed site.
cp -R "$ROOT/Assets" "$DIST/Assets"

echo "Built static site in $DIST"
