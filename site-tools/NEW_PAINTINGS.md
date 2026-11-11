# Adding new paintings from the Google Form

This is the checklist Claude follows every time it checks for new paintings
(nightly at midnight Manitoba time, or whenever asked). Follow every step.

## Where the submissions are

- Google Form: **Add a painting to the website** (in the site owner's Google Drive)
- Responses sheet: **Add a painting to the website (Responses)**,
  file id `1FuB4f09PXltcQxUJIdQEoBUKKTPcT9ILOoyjuf8tqBI`
- Photos: Drive folder **Photo of the painting (File responses)**
- Columns: Timestamp | Photo of the painting | Title |
  Size (height x width) | Medium | Status | Anything else to add?
- Already-published submissions are listed in `site-tools/processed.json`
  (by Timestamp). Only rows NOT in that list are new.

## Steps

1. **Get the sheet.** Download the responses sheet as CSV
   (Google Drive `download_file_content`, `exportMimeType: text/csv`).
   Compare each row's Timestamp with `site-tools/processed.json`.
   If there are no new rows: stop. Do not back up, commit or push anything.

2. **Get each photo.** The Photo column holds a Drive link
   (`...open?id=FILE_ID`). Download that file id with `download_file_content`;
   the large result is saved to a JSON file whose `content` is base64.
   Decode it to an image file in the scratchpad and confirm it opens.
   If a photo is missing or will not open, skip that row and report it.

3. **Tidy the details** (do not change meaning, only fix obvious slips):
   - **Title:** fix minor spelling slips and capitalization
     (Title Case, for example "summer mood" -> "Summer Mood").
     Never rename a painting or guess a different word if unsure.
   - **Size:** always written as height x width, inches first, then cm:
     `30x24 inches (76x61 cm)`. cm = inches x 2.54, rounded to a whole number.
     If only cm were given, convert to inches (nearest whole inch, or .5 if
     clearly intended). Keep extras such as "Double canvas" after the size.
     If the size is unclear (for example only one number), skip the row and report it.
   - **Medium:** fix capitalization and spelling only
     (sentence case, for example "Acrylic on canvas").
   - **Status:** Available, Unavailable, or the "Other" text as written
     (tidied, for example "Available at Dow Art Gallery, Minnesota").
   - **Anything else to add?:** if it describes the painting, publish it as the
     "About" note. If it is a message rather than a description, do not
     publish it; mention it in the report instead.
   - If a painting with the same title is already on the site, skip it and report it.

4. **Back up first.** From the repository root run `bash site-tools/backup.sh`.
   This keeps exactly two separate backup branches on GitHub:
   `backup-newest` (the site just before this change) and `backup-older`
   (the version before that). Never skip this step.

5. **Add the paintings.** For each new row, oldest submission first (so the
   most recent one ends up at the very top), run:
   ```
   python3 site-tools/add_painting.py --image PHOTO --title "..." \
     --size "30x24 inches (76x61 cm)" --medium "..." --status "..." [--about "..."]
   ```
   iPhone photos (HEIC) need `pip install pillow-heif` first.
   The new painting always becomes the FIRST painting on the home page.

6. **Check it.** Serve `Current/` locally and confirm in a browser that the new
   painting is the first tile, that its viewer shows the right title, size,
   medium and status, and that the next painting after it is the previous first one.

7. **Record and publish.** Add each published row to `site-tools/processed.json`
   (timestamp, title as published). Commit with a message like
   `Add painting: Summer Mood` and push to `main`.

8. **Report** what was added, every correction made to the submitted text,
   and anything skipped and why.

## Restoring a backup

If the live site ever breaks, reset `main` to `backup-newest`
(or `backup-older` if that one is also bad) and push.
