# Learnset Accessibility

The active learnset source is `hg-engine-main/hg-engine-main/data/learnsets/learnsets.json`.

This doc covers project-wide learnset accessibility rules. Type-specific move
support is documented in `docs/TYPE_AND_LEARNSET_CHANGES.md`, and the
Luminescent import behavior is documented in `docs/LUMINESCENT_DATA_REFRESH.md`.

## Rules

- Every egg move listed for a Pokemon must also be learnable through that Pokemon's level-up learnset.
- Missing egg moves are inserted across levels 5-55 in egg-list order, keeping inherited moves naturally accessible without putting every inherited move at level 1.
- Non-legendary level-up moves must occur before level 60.
- Legendary, mythical, Ultra Beast, and comparable special one-off Pokemon are exempt from the pre-60 compression rule so their late signature pacing can remain intact.
- Duplicate level-up move names are removed, keeping the earliest occurrence.

## Current Audit

- Learnset rows with egg moves: 907.
- Egg move entries covered by level-up learnsets: 5520.
- Non-legendary level 60+ moves after compression: 0.
- Duplicate level-up move names after cleanup: 0.
- Legendary/special level 60+ entries intentionally preserved: 419.

`tools/perfect_johto/validate_project.py` enforces these rules through the Learnset accessibility validation check.

## Edit Notes

- Regenerate learnset outputs with the HG-Engine learnset builder after changing
  `learnsets.json`.
- Do not add duplicate level-up move names to solve access problems; move the
  earliest useful instance instead.
- Keep late legendary and mythical signature pacing unless the species is no
  longer treated as a special one-off.
