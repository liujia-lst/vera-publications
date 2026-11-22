# Adding and updating publications

This guide covers the browser-form option. The team can choose a different workflow after reviewing the maintenance options.

1. Open **Publication editor**. To start from the latest shared data, download `data/catalog.json` from the repository and use **Open catalog.json**. A previous draft restored by your browser may be older than the shared copy.
2. Select **Add publication**, or choose an existing paper from the list.
3. Enter the title, complete author list, year, venue and paper webpage. The webpage may be blank if no public link is available yet. Use **Additional remarks** for awards or other notes.
4. Select one or more topics. To create a topic, enter its name under **New topic name** and click **Add topic**. It becomes available immediately; no HTML edit is needed.
5. Click **Save to draft**. This only saves on your computer.
6. Click **Download updated data**. The download is called `catalog.json` and contains the entire collection.
7. In GitHub, open the repository's **data** folder. Select **Add file → Upload files**, choose the downloaded `catalog.json`, and commit the change to `main`. Replace the file inside `data`; do not add a second copy at the repository root. If the browser added `(1)` to the download name, rename it to `catalog.json` before uploading.
8. Wait for the **Publish publications** action to succeed, then check the website. If it fails, the previous website remains online. Check the data error reported by the build, correct the draft and upload again.

Only someone with write access to the repository can publish. The editor page itself cannot write to GitHub and stores no access token. Anyone can experiment with the form without changing the public website.

When more than one person maintains the data, start from the latest shared file and coordinate who uploads the next change. Uploading a whole older catalogue can overwrite someone else's recent edits. This is the main reason to prefer an online sheet for regular shared maintenance.
