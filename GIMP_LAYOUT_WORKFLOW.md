# From crossword draft to movable GIMP layers

**Plan, not an implemented exporter.** Generate a layout that is already playable in its initial positions, then use GIMP to refine the artwork without having to place every clue by hand.

## Inputs and outputs

- **Authoring draft:** the reviewed grid and solution; for each clue, store the answer slot, clue area, arrow direction and entry point, and either text or a versioned image asset ID. A clue can occupy more than one square. Check the existing player JSON before defining new fields.
- **Clue library:** look up an image before creating another one. Keep the files in `vihjekuvat/` and catalog their IDs, paths, previews, answer associations, and source/credit information locally. The phone doesn't need access to the catalog.
- **Generated pair:** `layout.ora` for editing and `puzzle.json` for the PWA. Compute both from the same grid origin, cell size, and canvas dimensions. Do not include solution letters in either player-facing output unless deliberately implementing a reveal feature.
- **Working master and published image:** open `layout.ora` in GIMP, save a working copy as `layout.xcf`, and export the finished visible layers to `puzzle.png`. Publish the PNG and player JSON together, with the applicable image credits.

## Python export

Use Pillow to draw raster layers. Use Python's `zipfile` and XML tools to package them as OpenRaster (`.ora`): each clue can be a small transparent PNG, with its canvas offset and stacking order described in `stack.xml`. No running GIMP instance is required to generate this file.

| Layers, top to bottom | Initial placement and editing policy |
| --- | --- |
| Grid lines | Draw once at the JSON coordinates. Lock position in GIMP so the mobile input overlay stays aligned. |
| Arrows | One movable layer per arrow, pointing to the intended entry square. Keep endpoints unambiguous at phone size. |
| Image and text clues | One layer per placement. Fit each image to its clue area with padding, preserve its aspect ratio, and center it. Lay out text inside the assigned area. Use names such as `B12 · SAMMAKKO · frog-128-db32` for easy selection. |
| Background and cell fills | Keep separate from clues so colors can be adjusted without redrawing the grid. |

**Text limitation:** OpenRaster text layers are pixels: they can be moved, but their wording isn't editable with GIMP's Text tool. For the pilot, edit wording in the draft and replace the affected layer. If native text editing becomes essential, consider a GIMP 3 Python plug-in that creates native text layers in an XCF instead.

## What can change in GIMP?

Nudging a frog inside its clue area is a visual edit; no player JSON change is needed. Moving a clue to a different area, changing which answer an arrow points to, or moving the grid is a structural edit. Update the authoring draft and regenerate the matching outputs; GIMP does not update the JSON. Generate revisions under new names, never over a hand-edited XCF. Export the final PNG at the original canvas dimensions without cropping or shifting the origin.

## First test before building a full editor

1. Take one real project grid and identify how the existing PWA locates its input squares.
2. Export the grid, the existing DB32 frog sprite, one text clue, and one arrow as separate, named layers. Open the ORA in GIMP and confirm each starts in the intended position.
3. Save an XCF. Nudge only the frog, then export a flattened PNG. Confirm the grid and canvas are unchanged.
4. Open the PNG and companion JSON in the actual PWA. On a phone, check a corner square and a crossing at normal size and zoom: tapping must select the intended cell, the text must be readable, and the arrow must clearly indicate its answer.
