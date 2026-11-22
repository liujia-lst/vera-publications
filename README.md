# Vera Demberg — Publications

Live preview: https://liujia-lst.github.io/vera-publications/

A standalone publication page with topic filtering and a browser-based data editor. It uses plain HTML, CSS and JavaScript; the build uses Python 3's standard library.

## Current content

- 258 entries imported from the [Demberg lab publication list](https://www.uni-saarland.de/lehrstuhl/demberg/publications.html), retrieved on 22 November 2026.
- All source years and entries are retained, including the source's 2027 section and papers without Vera in the author list. This is a migration of the lab list, not a newly curated personal bibliography.
- 229 entries have a paper or project link; 29 still need a stable link. Source links that point to local files or temporary signed downloads are omitted. The report lists unresolved records.
- All topic assignments are proposed. The forwarded email gives tag examples and the `other` fallback, but does not contain the tagged HTML attachment. The meeting names three topic labels. No assignment is represented as supervisor-approved.
- The page is marked as a review preview and includes `noindex` and a restrictive `robots.txt`. These discourage indexing; they do not make a public GitHub Pages URL private.

The maintenance comparison is in `docs/Maintenance_Options.html`. Kanda's form instructions are in `docs/Kanda_Guide.md`.

## Data and local use

`data/catalog.json` is the source of truth. Each publication has title, authors, year, venue, paper URL, remarks, one or more topic IDs and optional additional links. Topics have separate IDs and display labels.

Run:

```sh
python3 scripts/build.py
```

This validates all records, rebuilds `index.html` and the editor's initial data, and exports CSV templates. No package installation is needed. Open `index.html` and `editor.html` in a browser, or serve the folder with a local static server. Links use relative paths and work under a GitHub project-site subpath.

## GitHub Pages deployment

1. Create a new repository in the selected account or team organization. A project repository such as `vera-publications` is sufficient; it need not be named `username.github.io`.
2. Upload this repository's contents, including `.github/workflows/pages.yml`, to the `main` branch. Do not upload the source email or working reference files.
3. In **Settings → Pages → Build and deployment → Source**, select **GitHub Actions**.
4. Open **Actions → Publish publications**, run the workflow if needed, and wait for the deploy job to succeed. The job reports the exact website URL.
5. Check the public page on desktop and mobile, try each topic, combine topics, clear the selection, and check external links and awards.

The workflow validates `catalog.json`, rebuilds the page and deploys the public files. Invalid data fails the build before publication. GitHub retains the last successful deployment. Only `main` publishes.

For a formal launch, agree on the categories, review `docs/Content_Review.md`, replace the review notice in `templates/index.html`, remove its robots meta tag, and change `robots.txt` to allow indexing. The existing university page has not been modified.

## Maintenance choices

The browser form and download path are implemented. Kanda can edit without writing code, then upload the exported `catalog.json` to the repository's `data/` folder and commit through GitHub's web interface.

Google Sheets and Decap CMS are alternatives, not enabled services. `scripts/import_csv.py` and `scripts/sync_sheets.py` prepare the Sheets path. No Google Sheet, OAuth app, cron schedule, CMS account or credential has been created. Choose one authoritative editing workflow before using the site for regular updates.

## Checks

```sh
python3 scripts/check.py
node --check assets/filters.js
node --check assets/editor.js
```

Verified on 22 November 2026: source coverage (258 entries), schema and CSV round-trip checks, all ten topic counts, combined topics, reset and browser history. The live page fits 390 px mobile, 960 px and 1280 px desktop widths. The editor loads existing records and awards, rejects missing topics, creates a paper and a topic, exports a complete catalogue, and imports the original 258-entry catalogue again. No test record was published. Browser checks reported no console errors. GitHub Actions build and deployment both passed: https://github.com/liujia-lst/vera-publications/actions/runs/45069323621 .
