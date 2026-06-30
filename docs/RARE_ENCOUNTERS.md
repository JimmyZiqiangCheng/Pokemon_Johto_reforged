# Rare Encounters

Rare encounters are a curated low-rate layer on top of the main wild tables.
They are intended for rare finds, approved regional forms, strong current forms,
and sparse pseudo-legendary access.

## References

- Export: `exports/perfect_johto/rare_encounters.json`.
- Encounter system overview: `docs/ENCOUNTER_SYSTEMS.md`.
- Full per-area report: `docs/phase6_obtainability_report.md`.
- Main wild tables: `docs/WILD_ENCOUNTERS.md`.

## Slot Rules

- Primary land rare slots use HGSS slot 8 at 4%.
- Curated secondary land rares may use slot 9 at 4%.
- Surf rare slots use slot 3 at 4%.
- Fishing rare slots use slot 4, changed by Phase 6 to 4%.
- Rock Smash is not used for rare placement because it only has 80%/20% slots.
- Legacy non-rare land/surf filler slots and non-rare rod filler slots duplicate
  common species and are not treated as rare finds.

## Placement Rules

- Every meaningful non-Safari encounter area has 1-3 rare species.
- Rare species are reserved for strong current forms, lines whose final form
  reaches 500+ BST, or approved regional forms.
- Rare Finds explicitly include Alolan Geodude, Galarian Zigzagoon, Paldean
  Wooper, Lapras, Kangaskhan, Tauros, early Teddiursa, early Houndour, early
  Hisuian Sneasel, early Ponyta, and pre-League Ice Path Sneasel.
- Rare pseudo-legendary initial forms are intentionally sparse and semantically
  placed, including Larvitar, Bagon, Gible, Beldum, and Riolu in cave, mountain,
  dragon, or expert-training contexts.
- Starter rare access is pushed into Kanto and postgame Kanto contexts.

## Current Audit

- Meaningful non-Safari areas with rare notes: 132.
- Meaningful non-Safari areas with 1-3 rare species: 132 / 132.
- Rare placements are validated to stay in the intended low-rate band.
- Approved later-form placements are restricted to approved Gen 1-4 families.
