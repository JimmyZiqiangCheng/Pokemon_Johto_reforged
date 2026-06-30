# Pokemon Data Changes

This is the reference entry point for Pokemon-specific data changes: base stats,
abilities, typings, learnsets, moves, and evolution access. Use the narrower
docs linked below when you need the full rule detail for a specific subsystem.

## Quick Reference

| Topic | Primary reference |
| --- | --- |
| Scope and allowed species/forms | `docs/PROJECT_SCOPE.md`, `docs/APPROVED_LATER_EXCEPTIONS.md` |
| Base stats, ability slots, and Luminescent source pass | `docs/LUMINESCENT_DATA_REFRESH.md` |
| Type modernization and STAB support | `docs/TYPE_AND_LEARNSET_CHANGES.md` |
| Egg move and late-level learnset rules | `docs/LEARNSET_ACCESSIBILITY.md` |
| Evolution method changes | `docs/EVOLUTIONS.md` |
| One-save obtainability | `docs/POKEMON_AVAILABILITY.md`, `docs/ENCOUNTER_SYSTEMS.md` |

## Source Files

- Species personal data: `hg-engine-main/hg-engine-main/data/Species.c`.
- Hidden ability data: `hg-engine-main/hg-engine-main/data/HiddenAbilityTable.c`.
- Level-up, egg, machine, and tutor learnset source:
  `hg-engine-main/hg-engine-main/data/learnsets/learnsets.json`.
- Learnset build helper:
  `hg-engine-main/hg-engine-main/scripts/build_learnsets.py`.
- Evolution data: `hg-engine-main/hg-engine-main/data/Evolutions.c`.
- Ability item behavior:
  `hg-engine-main/hg-engine-main/src/individual/PartyMenu_HandleUseItemOnMon.c`.
- Natural wild ability rolling:
  `hg-engine-main/hg-engine-main/src/field/enemy_party.c`.

## Scope Rules

- All Generation 1-4 Pokemon are in scope.
- Later-generation direct evolutions, regional forms, and new forms are allowed
  only when they belong to Generation 1-4 families and are listed in
  `docs/APPROVED_LATER_EXCEPTIONS.md`.
- Unrelated Generation 5+ Pokemon, unrelated later forms, Mega Evolution,
  Primal Reversion, Z-Moves, Dynamax/Gigantamax, Terastalization, and similar
  battle gimmicks remain out of scope.
- The engine still contains later-generation species, moves, abilities, items,
  and mechanics as internal capacity. Gameplay exposure is restricted by
  validation, docs, encounters, trainers, marts, scripts, and events.

## Stats And Abilities

- Generation 1-4 base species rows and relevant native Generation 3-4 form rows
  were refreshed against Luminescent Platinum 3.0 as the primary data standard.
- The Luminescent pass covers base stats and ability slots for the target
  species/form set. Renegade Platinum and Polished Crystal remain secondary
  design references, not overrides.
- Ability modernization is allowed when it supports Pokemon identity, role
  variety, and Johto replayability.
- Hidden ability slots are natural wild encounter variety. Wild Pokemon now roll
  across non-empty ability slot 1, ability slot 2, and hidden ability slots,
  preserving duplicate Luminescent slots as intentional weighting.
- Ability Capsule and Ability Patch are part of the badge-gated customization
  economy. Ability Capsule unlocks at 3 badges; Ability Patch unlocks at 6
  badges.
- Custom defensive ability behavior, Immortal Shell, and one-off personalized
  pseudo-legendary ability changes remain out of scope.

## Typing

Typing modernization is restrained and species-identity driven. The complete
type-change list and STAB support audit live in
`docs/TYPE_AND_LEARNSET_CHANGES.md`.

Important constraints:

- No type chart change has been made.
- Rock no longer being weak to Ground remains out of scope.
- Type changes do not by themselves change base stats, evolution methods,
  encounter scope, catch rates, EV yields, held items, or growth data.
- Project-added secondary types are audited for reasonable level-up attacking
  move access.

## Moves And Learnsets

- Move battle behavior and move data are not a project feature area right now;
  no custom move-behavior pass is documented.
- Level-up learnsets preserve local extras and append missing Luminescent
  Platinum 3.0 level-up moves at their Luminescent levels.
- Luminescent move IDs are resolved through Luminescent move names before being
  mapped to local `MOVE_*` constants, because post-Gen 4 numeric IDs do not
  fully match this engine.
- Egg moves are also level-up accessible for every Pokemon with egg moves.
- Non-legendary level-up moves are compressed below level 60. Legendary,
  mythical, Ultra Beast, and comparable one-off Pokemon keep late signature
  pacing.
- Evolved forms inherit earlier-form level-up moves more consistently.

## Evolutions

Evolution changes are documented in `docs/EVOLUTIONS.md`.

The major rules are:

- Approved-scope trade-only evolutions are replaced with item-use or other
  non-trade methods where appropriate.
- Trade-with-item evolutions use direct item-use methods.
- Known-move evolutions are used for Wyrdeer, Annihilape, and Sirfetch'd.
- Dudunsparce Three-Segment and Ursaluna Bloodmoon have simple level-up access
  through their standard final forms.
- Required evolution items are made available through badge-gated marts.

## Validation

Run the master validation before changing Pokemon data:

```powershell
python tools/perfect_johto/validate_project.py
```

Validation covers approved scope, learnset parsing/generation, learnset
accessibility, evolution access, item/mart gates, encounter exposure, trainer
species use, and forbidden gimmick exposure.
