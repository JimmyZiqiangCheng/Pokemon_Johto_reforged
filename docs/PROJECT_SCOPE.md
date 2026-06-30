# Project Scope

This doc defines what Pokemon Johto Reforged may expose through gameplay data, scripts, trainers, marts, encounters, and documentation.

## In Scope

- All Generation 1-4 Pokemon.
- Later direct evolutions of Generation 1-4 families.
- Later regional forms and new forms of Generation 1-4 families.
- Later evolutions connected to approved regional forms when the family relationship is direct and the implementation is clean.
- HGSS-style quality-of-life improvements that do not introduce forbidden battle gimmicks.
- Static JSON exports and Markdown docs for auditability and future external tools.

## Out Of Scope

- Unrelated Generation 5+ Pokemon lines.
- Later-generation legendary/mythical Pokemon unless they are forms of Generation 1-4 legendary/mythical Pokemon and explicitly approved later.
- Mega Evolution, Primal Reversion, Z-Moves, Dynamax/Gigantamax, Terastalization, and similar battle gimmicks.
- Totem, Noble/Lord, Gigantamax, Mega, Primal, Terastal, and unrelated later-generation form families unless explicitly approved later.
- Rock type no longer weak to Ground.
- Immortal Shell.
- Custom defensive ability behavior.
- Personalized Tyranitar, Salamence, or Dragonite changes.
- Restoring consumed held items after trainer battles.
- Interactive web app or browser explorer inside this ROM hack project.

## Engine Capacity Caveat

HG-Engine contains many later-generation species, forms, moves, abilities, items, and mechanic constants. This repository treats that data as engine capacity only. Gameplay exposure is controlled by project scope, validation, and the generated documentation/exports.

## Reference Docs

- Approved exceptions: `docs/APPROVED_LATER_EXCEPTIONS.md`.
- Pokemon-data policy: `docs/POKEMON_DATA.md`.
- Encounter exposure: `docs/ENCOUNTER_SYSTEMS.md`.
- Trainer exposure: `docs/TRAINER_TEAMS.md`.
- Forbidden-gimmick and release checks: `docs/RELEASE_CHECKLIST.md`.

The web-app explorer is a future separate project, not part of this ROM hack phase. This project provides structured data exports in `exports/perfect_johto/` that a later separate explorer can consume.
