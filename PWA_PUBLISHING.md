# Selling crossword magazine issues through the existing PWA

**Planning note, not an implemented feature.** Keep one installable crossword reader, with one home-screen icon and a **My Issues** library. Sell each issue once rather than requiring a subscription or a separate app install. Keep the player and solver progress local where possible. The main architectural decision is how a purchase becomes an issue in the reader's library, especially on a second phone.

## Delivery options

| Option | Purchase and restore | Upkeep and trade-offs |
| --- | --- | --- |
| **A. Downloadable issue (start here)** | A hosted storefront sells a file. The reader downloads it and chooses **Import issue** in the PWA. Restore by importing a saved copy or downloading it again through the store. | Static hosting; no backend of our own. Choose a store that supports repeat downloads. Phone file import is the main usability risk. Buyers can share their downloaded file. |
| **B. Hosted checkout + small unlock service** | After checkout, the issue appears in the library. An emailed sign-in link lets a buyer restore their library on another phone. | Maintain a serverless function, a purchase database, private file storage, and the restore flow. Better phone experience; still no server calls needed while solving a downloaded puzzle. |
| **C. Provider-managed access** | The reader pays and signs in through a commerce platform; the PWA retrieves owned issues through its supported integration. | Less custom purchase logic, but fees, dependence on the provider, and less control over the mobile flow. Confirm support for individual purchases, library restore, and offline downloads before choosing a service. |

A payment processor and a merchant of record offer different services. For international sales, check who handles VAT/sales tax and remittance in the intended markets, as well as fees and refund handling. This decision is separate from the choice of issue format.

## Portable issue package

Start with one downloadable archive per issue. Check the existing player's puzzle JSON before inventing new fields. Suggested contents:

- `issue.json`: format version, stable issue ID, issue title, cover path, and ordered puzzles with stable IDs and relative file paths.
- **One player JSON and one finished clue image per puzzle.** Generate the image and the input-square geometry from the same authoring data so they align on different phone screens. Keep the editable clues, full solution, and editorial notes in the authoring project. Decide separately whether to publish reveal/check-answer data.
- **Cover and credits.** Include attribution and license information in the package so that credits work offline, too.

The importer should check the format version and required files before adding the issue to the library. Keep entered letters separate from the issue assets, keyed by issue and puzzle ID. Re-importing the same issue must not erase progress. Downloading a purchased issue restores the content, **not** the reader's entered letters; offer progress export/import if backups are needed without accounts.

## Pilot checklist — run on both iPhone and Android

- [ ] Install the PWA from the browser and launch it from the home-screen icon in standalone mode.
- [ ] Follow a test purchase from checkout to the receipt email. Download the issue, find it in the phone's file picker, and import it into the installed PWA without developer assistance.
- [ ] Open the issue and solve a crossing. Verify that both directions share one letter and the input squares align with the clue image at normal size and zoom.
- [ ] With the issue downloaded, close the app, switch to airplane mode, and reopen it. Verify that the reader can resume the same puzzle, see the clues and credits, and keep solving.
- [ ] Re-import the issue; confirm there is one library entry and the entered letters remain intact.
- [ ] Test restore on another phone or a clean test installation: retrieve the purchased file and re-import it. Test progress restoration separately if export/import is offered.

## When to add a backend

Use Option A for the first issue. Watch a reader try the receipt-to-first-puzzle flow on each phone. If finding or importing the download repeatedly needs explanation, keep the package and player unchanged and replace manual delivery with Option B.

For Option B, grant access only after verifying the checkout provider's payment notification, not from a browser success redirect. Record the buyer and issue ID; handle duplicate notifications without creating duplicate purchases. Authorize a short-lived download link to private storage, then let the PWA store the issue offline. Test refunds and email-based library restore. Cross-device progress sync can remain a separate decision.

Do not put all paid issues on the public site behind a local JavaScript `purchased` flag. Protect delivery of unbought issues; do not promise copy protection for files legitimately delivered for offline reading.
