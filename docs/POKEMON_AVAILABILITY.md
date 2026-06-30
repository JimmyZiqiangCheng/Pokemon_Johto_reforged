# Pokemon Availability

All Generation 1-4 Pokemon are intended to be obtainable in one save file.

## References

- Availability export: `exports/perfect_johto/pokemon_availability.json`.
- Encounter system overview: `docs/ENCOUNTER_SYSTEMS.md`.
- Encounter report: `docs/phase6_obtainability_report.md`.
- Legendary report: `docs/phase8_postgame_report.md`.
- Approved later exceptions: `docs/APPROVED_LATER_EXCEPTIONS.md`.

## Non-Legendary Coverage

- Phase 6 static validation reports non-legendary Gen 1-4 evolution-family
  coverage as complete across main wild, Safari, and Headbutt encounter sources.
- The generated Phase 6 report records 211/211 non-legendary Gen 1-4
  evolution-family components covered.
- Every non-legendary, non-starter Gen 3-4 base/pre-evolution species is
  represented in Johto main encounters.
- Approved later regional forms and direct family exceptions are placed only
  where they belong to Gen 1-4 families.
- No unrelated Gen 5+ Pokemon are intentionally exposed through encounters,
  trainers, marts, or Phase 8 Dojo gameplay files.

## Starter Access

Starter families are not used as early-route clutter. Starter access is pushed
into late-game and postgame contexts, including late Johto, Kanto, and postgame
Kanto wild placements.

## Legendary And Mythical Coverage

- Native Raikou and Entei remain Burned Tower roamers.
- Phase 8 Saffron Fighting Dojo dossiers provide proper scripted access for
  the remaining Gen 1-4 legendary/mythical roster.
- The random legendary surprise overlay is separate from proper access. It is a
  repeatable low-rate wild overlay and does not write roamer save state.

## Known Follow-Up

Release blocker/TODO: confirm whether Pokedex area data is derived from
encounter tables or needs a separate regeneration step.
