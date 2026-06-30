# Encounter Systems

This is the reference entry point for all encounter mechanisms: ordinary wild tables, rare finds, Safari/Headbutt support, random legendary surprises, native roamers, Dojo dossier encounters, and Nuzlocke encounter claims.

## Quick Reference

| Mechanism | Primary reference |
| --- | --- |
| Main wild tables and level curve | `docs/WILD_ENCOUNTERS.md` |
| Per-area Phase 6 audit | `docs/phase6_obtainability_report.md` |
| Rare-find layer | `docs/RARE_ENCOUNTERS.md` |
| Random legendary surprise overlay | `docs/RANDOM_LEGENDARY_SYSTEM.md` |
| Proper legendary/mythical access | `docs/LEGENDARIES.md`, `docs/phase8_postgame_report.md` |
| Kanto Dojo postgame hub | `docs/KANTO_POSTGAME.md` |
| Nuzlocke area claims | `docs/GAME_MODES.md` |

## Source Files

- Main wild encounters: `hg-engine-main/hg-engine-main/data/Encounters.c`.
- Safari encounters: `hg-engine-main/hg-engine-main/data/SafariEncounters.c`.
- Headbutt encounters: `hg-engine-main/hg-engine-main/data/Headbutt.c`.
- Encounter generation hook: `hg-engine-main/hg-engine-main/src/field/enemy_party.c`.
- Encounter generation/audit tool: `tools/perfect_johto/phase6_encounter_tools.py`.
- Master validation/export runner: `tools/perfect_johto/validate_project.py`.

## Main Wild Encounters

- Main encounters were rebuilt for broad Generation 1-4 one-save obtainability.
- Morning and day land arrays are intentionally kept identical as a shared daytime pool; night remains separate for night-specific flavor.
- Land/cave pools and surf/fishing pools are validated separately. Meaningful pools are expected to have at least six species when that encounter mode exists.
- Johto routes and dungeons include Generation 3-4 Pokemon as normal ecology, not only as rare prizes.
- Kanto and late-Johto wild levels were raised so wild Pokemon remain useful alongside the stronger trainer curve.
- Starter access is delayed into late-game and postgame contexts rather than crowding early Johto routes.

## Rare Finds

- Every meaningful non-Safari main encounter area has one to three rare species.
- Primary land rares use slot 8 at 4%; curated secondary land rares may use slot 9 at 4%.
- Surf rares use slot 3 at 4%.
- Fishing rares use slot 4, changed by Phase 6 to a 4% slot.
- Non-rare low-rate filler duplicates common species so ordinary Pokemon are not accidentally treated as rare finds by future tools or wiki views.
- Rare species are reserved for strong current forms, lines whose final form reaches 500+ BST, or approved regional forms.
- Rock Smash is not used for the rare layer because its slot structure is only 80%/20%.

## Legendary And Mythical Access

Two systems intentionally coexist:

- Proper access: native Raikou/Entei roamers plus Saffron Fighting Dojo dossier encounters for the rest of the Generation 1-4 legendary/mythical roster.
- Surprise access: a low-rate random legendary overlay that can replace a normal wild encounter after the normal encounter flow succeeds.

The proper access system sets caught flags only on successful capture, so fled or fainted dossier battles remain retryable. The surprise overlay is repeatable, does not write roamer save state, and respects Repel through the existing normal encounter flow.

## Nuzlocke Claims

Nuzlocke mode uses the encounter/gift/static creation paths to claim map sections. Wild encounters claim the current map section when generated, gift and egg Pokemon claim before being awarded, and illegal catch attempts fail during ball shake resolution. See `docs/GAME_MODES.md` for the full rules.

## Known Follow-Up

Pokedex area data still needs release confirmation. If HG-Engine does not derive area data from the regenerated encounter archives, add or document the regeneration step before release.
