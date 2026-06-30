# Pokemon Johto Reforged Documentation

This folder contains the project-facing documentation for Pokemon Johto
Reforged. Use `FEATURES_AND_CHANGES.md` at the repository root for the general
feature index, then use the category docs here for implementation and future
modification reference.

The interactive web-app explorer is intentionally not part of this ROM hack
phase. Structured exports live in `exports/perfect_johto/` so a future separate
project can consume them.

## Start Here

- `PROJECT_SCOPE.md`: allowed content, forbidden content, and scope policy.
- `POKEMON_DATA.md`: Pokemon stats, abilities, typings, learnsets, and
  evolution references.
- `ENCOUNTER_SYSTEMS.md`: wild tables, rare finds, random legendary surprises,
  proper legendary access, and Nuzlocke encounter claims.
- `TRAINER_TEAMS.md`: trainer roster, level curve, boss, rematch, and validation
  references.
- `GAME_MODES.md`: Normal, Challenge, Hardcore, and Nuzlocke rules.
- `BUILD_AND_TESTING.md`: validation commands, build readiness, and required
  local inputs.

## Feature Categories

Pokemon data and availability:

- `POKEMON_DATA.md`
- `POKEMON_AVAILABILITY.md`
- `APPROVED_LATER_EXCEPTIONS.md`
- `LUMINESCENT_DATA_REFRESH.md`
- `TYPE_AND_LEARNSET_CHANGES.md`
- `LEARNSET_ACCESSIBILITY.md`
- `EVOLUTIONS.md`

Encounters and postgame access:

- `ENCOUNTER_SYSTEMS.md`
- `WILD_ENCOUNTERS.md`
- `RARE_ENCOUNTERS.md`
- `RANDOM_LEGENDARY_SYSTEM.md`
- `LEGENDARIES.md`
- `KANTO_POSTGAME.md`
- `CHAMPION_CIRCUIT.md`

Trainers, battles, and progression:

- `TRAINER_TEAMS.md`
- `BOSS_BATTLES.md`
- `phase7_trainer_report.md`
- `phase8_postgame_report.md`

Systems and economy:

- `GAME_MODES.md`
- `QOL_FEATURES.md`
- `ITEMS_AND_MARTS.md`

Build, release, and audit:

- `BUILD_AND_TESTING.md`
- `PLAYTEST_CHECKLIST.md`
- `RELEASE_CHECKLIST.md`
- `KNOWN_LIMITATIONS.md`
- `phase6_obtainability_report.md`
- `history/FEATURES_AND_CHANGES_v2026-06-27.md`

## Generated Data

Most structured data lives in `exports/perfect_johto/`. The key exports are:

- `trainer_teams.json`
- `boss_battles.json`
- `wild_encounters.json`
- `rare_encounters.json`
- `random_legendary_surprise.json`
- `proper_legendary_events.json`
- `evolutions.json`
- `items_and_marts.json`
- `approved_scope.json`
- `approved_later_exceptions.json`

Run `python tools/perfect_johto/validate_project.py --write` after gameplay
data changes to regenerate exports and generated docs.
