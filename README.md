# Vera Demberg — Publications

Publications organized by research topic.

- [Publications website](https://liujia-lst.github.io/vera-publications/)
- [Publication editor](https://liujia-lst.github.io/vera-publications/editor.html)

## Updating publications

Use the publication editor to add or edit papers and topics. Download the updated `catalog.json`, then upload it to the repository’s `data/` folder. GitHub Actions rebuilds and publishes the website automatically.

See the [editing guide](docs/Kanda_Guide.md) for the upload steps.

## Maintenance options

| Option | Editing | Publishing | Setup and trade-offs |
| --- | --- | --- | --- |
| Google Sheets | Edit publication rows; select topics from a dropdown and add new topics in a separate sheet. | A configured synchronization job imports the sheet data and rebuilds the website. | Convenient for shared editing. Requires a shared sheet, public CSV exports and synchronization setup. Import scripts are available; the sheet is not connected yet. |
| Decap CMS | Log in, fill in a publication form and select or create topics. | The CMS saves changes to GitHub, triggering the website build. | Editing and publishing in one interface. Requires repository access and an authentication service; setup is needed. |
| Browser form + GitHub upload | Use the existing publication editor and download `catalog.json`. | Upload the file to the repository’s `data/` folder. | Available now. Requires repository write access and a manual upload. Start from the latest shared data file to avoid overwriting another editor’s changes. |

Google Sheets is a practical choice if Kanda prefers spreadsheets. The browser form is ready to use; a CMS may be useful later for managing the full team website.

References: [Google Sheets dropdowns](https://support.google.com/docs/answer/186103), [publishing sheet data](https://support.google.com/docs/answer/183965), [Decap CMS GitHub backend](https://decapcms.org/docs/github-backend/).
