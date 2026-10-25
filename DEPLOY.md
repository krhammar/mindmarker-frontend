# Deploying MindMarker

The site is deployed to **Cloudflare Pages** as a completely static site. There
is **no Python server to host**: [Stlite](https://github.com/whitphx/stlite) runs
Streamlit and the app's Python code inside each visitor's browser using
[Pyodide](https://pyodide.org/) (Python compiled to WebAssembly).

That means Cloudflare only serves:

- `index.html` (the Stlite bootstrap)
- `app.py`, `backend_api.py`, and `pages/*.py`
- `requirements.txt` (Stlite installs the extra Python packages in the browser)

## How it works

1. `index.html` loads the Stlite runtime from jsDelivr.
2. Stlite fetches the Python files listed in its `files` option and mounts them
   into an in-browser file system.
3. `app.py` is executed by Pyodide and Streamlit renders the UI.
4. `scripts/build.sh` assembles those files into `dist/`, which is what
   Cloudflare Pages publishes.

## One-time Cloudflare Pages setup

1. Push this repository to GitHub.
2. In the Cloudflare dashboard go to **Workers & Pages → Create → Pages →
   Connect to Git** and select the repository.
3. Use these build settings:

   | Setting | Value |
   | --- | --- |
   | Framework preset | None |
   | Build command | `bash scripts/build.sh` |
   | Build output directory | `dist` |
   | Root directory | `/` (default) |

4. Click **Save and Deploy**.

That's it. Cloudflare now deploys automatically:

- Every push to the production branch (usually `main`) updates the live site.
- Pushes to other branches and pull requests get their own preview URL.

No API tokens or GitHub Actions secrets are needed for this; the Git
integration is what triggers the builds.

## Local preview

Build the same output Cloudflare uses:

```bash
bash scripts/build.sh
```

Then serve it locally. The simplest option (only needs Python) is:

```bash
python -m http.server 8000 --directory dist
```

If you have Node.js, Wrangler additionally emulates Cloudflare's `_redirects`
and `_headers`:

```bash
npx wrangler pages dev dist
```

Normal local development is unchanged: `python -m streamlit run app.py`.

## Important differences from running a real Streamlit server

Because all Python runs in the browser, keep these constraints in mind:

- **First load is slow.** The browser downloads the Python runtime, Streamlit,
  and any packages (tens of MB). Expect roughly 10–30 seconds on a first visit;
  later visits are cached by the browser. The `Loading MindMarker…` text is
  shown until the app renders.
- **The API must allow CORS.** `backend_api.py` calls
  `https://api.mindmarker.dev` from the browser, so that API must return
  `Access-Control-Allow-Origin` for the Pages domain and any custom domain
  (for example `https://mindmarker.pages.dev`). Otherwise requests fail with a
  CORS error even though they work locally.
- **Deep links to a subpage open the home page.** Stlite always boots into the
  app's default page on a fresh load. Known page URLs are redirected to `/`
  (see `_redirects`) so a refresh does not show a 404, but the page itself is
  not restored. In-app navigation is unaffected.
- **No server-side code or secrets.** Anything in the Python files is public.
  Never put API keys or private credentials in this repository.
- **Only pure-Python or Pyodide-compatible packages work.** Native packages
  without a Pyodide build cannot be installed. Plain `streamlit` and `requests`
  work; `requests` is automatically routed through the browser's `fetch` by
  Stlite.
- **Some Streamlit features behave differently in a browser.** For example,
  `time.sleep()` is a no-op (use `asyncio.sleep()` with top-level `await`) and
  long blocking calls freeze the UI.

## Updating the app

Just commit and push. The Python files are not bundled into the HTML, so
changing `app.py` or anything under `pages/` is picked up by the next
deployment—no changes to `index.html` are required.

When you add a **new top-level `.py` file that the app imports or navigates
to**, add it to the `files` list in `index.html` as well. New pages under
`pages/` also need their URL path in `_redirects` so a hard refresh on that URL
redirects to the app instead of showing a 404 (Streamlit derives the path from
the filename, for example `pages/topics.py` becomes `/topics`).

When you add a dependency to `requirements.txt`, no change is needed: Stlite
reads that file in the browser and installs what it can. Dependencies must be
available for Pyodide.

When you add a **static asset** (an image used by `st.image()`, `page_icon`,
etc.), register it in **two** places:

1. `index.html` — add it to the `files` map so Stlite mounts it into the
   in-browser file system. Streamlit reads images from the Python file system,
   not over HTTP, so a file that is only served is still invisible to
   `st.image()`.
2. `scripts/build.sh` — copy it into `dist/` so Cloudflare serves it (the
   `Assets/` directory is copied automatically; subdirectories you add need the
   same treatment).

Forgetting either one produces the classic "works locally, broken in
production" image: locally the file exists on disk, but on Cloudflare it is
either not deployed or not mounted.

## Updating Stlite

`index.html` pins an exact Stlite version (`@stlite/browser@1.12.0`) so a new
release cannot break the deployed site unexpectedly. To upgrade, change the
version in both the `<link>` and the `import` URL, then test locally and push.

## Troubleshooting

- **Blank page / infinite loading:** open the browser console. A failed fetch of
  a `.py` file, a CDN block, or a Python traceback from Stlite will appear
  there. Check that the file is listed in `index.html` and exists in the
  deployed output.
- **`ModuleNotFoundError`:** the package is either missing from
  `requirements.txt` or has no Pyodide build.
- **A hard refresh on `/explore` goes back to the home page.** Stlite always
  boots into the default page, so `_redirects` sends those refreshes to `/`
  rather than showing a 404. In-app navigation works normally; only a full page
  reload or a shared deep link returns to the start.
- **API requests fail only in production:** almost always CORS or a mixed-content
  (HTTP vs HTTPS) issue.
- **Images render locally but not on the live site:** the asset is missing from
  either `dist/` or the Stlite `files` map in `index.html`. See "Updating the
  app" above.
- **Old version still showing:** hard-refresh. The `_headers` file marks the
  app files as `no-cache`, but a service worker or browser cache can still hold
  on to a previous page.

## Custom domain

Add the domain under the Pages project's **Custom domains** tab, then create the
DNS record Cloudflare shows. If the API is also on Cloudflare, add the final
`https://<your-domain>` origin to the API's CORS allow-list.
