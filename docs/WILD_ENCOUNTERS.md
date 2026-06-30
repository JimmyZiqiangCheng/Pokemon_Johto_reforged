# Wild Encounters

Wild encounters are the main one-save obtainability layer for ordinary Pokemon.
For the full encounter-system map, see `docs/ENCOUNTER_SYSTEMS.md`.

## References

- Main export: `exports/perfect_johto/wild_encounters.json`.
- Phase 6 audit report: `docs/phase6_obtainability_report.md`.
- Rare layer: `docs/RARE_ENCOUNTERS.md`.
- Random legendary overlay: `docs/RANDOM_LEGENDARY_SYSTEM.md`.

## Source Files

- Main encounter source: `hg-engine-main/hg-engine-main/data/Encounters.c`.
- Safari source: `hg-engine-main/hg-engine-main/data/SafariEncounters.c`.
- Headbutt source: `hg-engine-main/hg-engine-main/data/Headbutt.c`.
- Generation/audit tool: `tools/perfect_johto/phase6_encounter_tools.py`.

## Main Rules

- Main land encounters use a shared daytime pool: the engine-facing morning and
  day arrays are kept identical, while night remains separate.
- Meaningful land/cave pools and surf/fishing pools are validated separately.
  Each meaningful mode must have at least six species when that mode exists.
- Late-Johto, Kanto, and postgame encounter levels were raised to match the
  stronger trainer curve.
- Gen 3-4 Pokemon are used as normal Johto ecology where slot space allows, not
  only as rare prizes.
- Starter families are placed in late-game or postgame contexts, not as early
  route clutter.
- Non-rare low-rate land, surf, and rod filler slots duplicate common species
  so ordinary Pokemon do not appear as separate rare finds.

## Coverage

- Meaningful non-Safari encounter areas with at least six encounter species:
  132 / 132.
- Meaningful land/cave encounter pools with at least six species: 108 / 108.
- Meaningful surf/fishing encounter pools with at least six species: 71 / 71.
- Non-legendary Gen 1-4 evolution-family components with wild encounter
  coverage: 211 / 211.
- Non-legendary non-starter Gen 3-4 base/pre-evolution species covered in Johto
  main encounters: 95 / 95.
- Unrelated later-generation species found in encounter tables: none.

## Edit Notes

- Prefer editing `tools/perfect_johto/phase6_encounter_tools.py` and
  regenerating rather than hand-editing the large encounter source.
- Keep rare species in the rare layer and ordinary ecology in common slots.
- Keep Safari and Headbutt coverage in mind when validating full one-save
  availability.
- Confirm Pokedex area-data behavior before release.
