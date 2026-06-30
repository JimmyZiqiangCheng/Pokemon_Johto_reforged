# Pokemon Johto Reforged - Features and Changes

Document version: v2026.06.30-game-modes
Last updated: 2026-06-30

This is the current feature/change index for Pokemon Johto Reforged. The older
long-form phase ledger was archived so this file can stay readable while still
preserving history.

## Document Versions

| Version | Date | Notes |
| --- | --- | --- |
| v2026.06.27-long-ledger | 2026-06-27 | Original detailed phase-by-phase project ledger. Archived at `docs/history/FEATURES_AND_CHANGES_v2026-06-27.md`. |
| v2026.06.28-consolidated | 2026-06-28 | Consolidated current-state doc. Added early Running Shoes QOL implementation and documented the Cherrygrove Guide skip. |
| v2026.06.28-encounter-type-learnset-balance | 2026-06-28 | Rebalanced rare/common encounter slots, separated land/cave and surf/fishing variety validation, re-audited progression, and added Gen 3-4 semantic type plus learnset support. |
| v2026.06.28-random-legendary-rate-balance | 2026-06-28 | Reduced random legendary surprise rates to 1/500 for weaker legends and 1/1000 for true/cover-story legends. |
| v2026.06.29-luminescent-ability-refresh | 2026-06-29 | Refreshed Gen 1-4 base and relevant Gen 3-4 form ability slots against Luminescent Platinum 3.0, with Renegade Platinum and Polished Crystal kept as secondary design references. Hidden ability slots now participate in normal wild ability rolls. |
| v2026.06.29-luminescent-data-refresh | 2026-06-29 | Extended the Luminescent Platinum 3.0 source-of-truth pass to Gen 1-4 base stats and level-up learnsets. Local extra moves are preserved, missing Luminescent level-up moves are appended at Luminescent levels, and move IDs are mapped by Luminescent move names before resolving local constants. |
| v2026.06.29-learnset-accessibility-refresh | 2026-06-29 | Made every egg move in the active learnset data level-up accessible, cleaned duplicate level-up moves, and re-applied the non-legendary pre-level-60 learnset philosophy across the full shared learnset file. |
| v2026.06.29-rare-encounter-starter-rebalance | 2026-06-29 | Rebalanced rare encounters so Teddiursa, Houndour, Hisuian Sneasel, and Ponyta appear earlier, reduced early Riolu saturation, and pushed starter rare access back into Kanto/postgame Kanto contexts. |
| v2026.06.30-game-modes | 2026-06-30 | Added New Game mode selection before Oak's speech: Normal, Challenge, Hardcore, and Nuzlocke. Challenge modes enforce dynamic level caps, Set battle style, and trainer-battle item restrictions; Hardcore/Nuzlocke release fainted Pokemon while preserving the last non-Egg party Pokemon; Nuzlocke enforces first encounter/gift/static claims per map section. |

## Project Goals

- Build a HeartGold/HG-Engine-based definitive Johto experience.
- Make all Generation 1-4 Pokemon obtainable in one save file.
- Allow only approved later-generation direct evolutions, regional forms, and
  new forms tied to Generation 1-4 families.
- Improve Johto pacing, Kanto postgame structure, trainer rosters, and boss
  teams.
- Keep HGSS-style quality-of-life improvements without adding unrelated later
  battle gimmicks.
- Keep validation, exports, and documentation auditable for future build and
  playtest passes.

## Global Restrictions

- No Mega Evolution, Primal Reversion, Z-Moves, Dynamax/Gigantamax,
  Terastalization, or similar later-generation battle gimmicks.
- No unrelated Generation 5+ Pokemon lines.
- No later-generation legendary/mythical Pokemon unless explicitly approved as
  a form of a Generation 1-4 legendary/mythical Pokemon.
- No trainer-battle held-item restoration.
- No interactive web-app explorer in this ROM hack project. Static exports in
  `exports/perfect_johto/` may feed a future separate project.
- Do not commit or redistribute ROMs, pre-patched ROMs, or copyrighted ROM
  data.

## Current Feature Set

### Scope and Pokemon Availability

- One-save obtainability target covers all Generation 1-4 Pokemon.
- Approved later exceptions are limited to direct evolutions, regional forms,
  and new forms of Generation 1-4 families.
- Phase 6 encounter validation reports non-legendary Generation 1-4 family
  coverage across main, Safari, Headbutt, fishing, and surfing sources.
- Phase 8 covers Generation 1-4 legendary/mythical access through native roamers
  and the Saffron Fighting Dojo dossier system.

### Pokemon Data, Evolutions, and Learnsets

- Selected approved-scope Pokemon received restrained type modernization.
- Generation 1-4 base species and relevant native Gen 3-4 form rows now use
  Luminescent Platinum 3.0 ability slot and base-stat data as the primary
  standard, with Renegade Platinum and Polished Crystal treated as secondary
  design references.
- Ability modernization is allowed when it supports Pokemon identity, role
  variety, and Johto replayability; later-generation abilities are acceptable
  data modernization, while later battle gimmicks remain out of scope.
- Hidden abilities are treated as normal encounter variety for wild Pokemon:
  wild generation rolls across non-empty slot 1, slot 2, and hidden ability
  slots, preserving Luminescent duplicate slots as intentional weighting.
- Level-up learnsets preserve existing local extras and append missing
  Luminescent Platinum 3.0 moves at their Luminescent levels. Luminescent move
  IDs are resolved through Luminescent move-name text before mapping to local
  `MOVE_*` constants because this engine's post-Gen 4 numeric move IDs do not
  fully match Luminescent's table.
- Egg moves are also level-up accessible for every Pokemon. Missing egg moves
  are inserted across levels 5-55 in egg-list order, keeping inherited moves
  available without front-loading every inherited option at level 1.
- Non-legendary level-up learnsets are compressed below level 60. Legendary,
  mythical, Ultra Beast, and comparable special one-off Pokemon keep their
  late-level pacing.
- Generation 3-4 semantic type updates now include Chingling/Chimecho,
  Huntail/Gorebyss, Cranidos/Rampardos, Carnivine, and Finneon/Lumineon.
- Custom or modernized typings were audited so project-added secondary types
  have suitable level-up attacking moves.
- Trade-only evolutions and trade-with-item evolutions were replaced with
  item-use methods where appropriate.
- Stantler, Primeape, and Galarian Farfetch'd use known-move evolutions for
  Wyrdeer, Annihilape, and Sirfetch'd.
- Evolved forms inherit earlier-form level-up moves more consistently.

### Items, Marts, and Customization

- Badge-gated standard mart stock adds EV/IV training items, mints, Ability
  Capsule/Patch, evolution items, and Max Candy.
- Max Candy sets all six IVs to 31.
- Health, Mighty, Tough, Smart, Courage, and Quick Candy each set one matching
  IV to 31.
- Mints, Ability Capsule/Patch, vitamins, Power items, feathers, and
  EV-reduction berries have reduced prices.

### Encounters

- Main wild encounters were rebuilt for broader Generation 1-4 availability.
- Rare encounter layer adds low-rate area-specific Pokemon without replacing
  the main encounter identity.
- Starter rare access is concentrated in Kanto and postgame Kanto contexts;
  early Johto rare slots now favor local flavor, regional forms, and strong
  non-starter lines.
- Teddiursa, Houndour, Hisuian Sneasel, and Ponyta have earlier rare access,
  while Riolu keeps one low-level placement and a few later aura-themed
  placements.
- Shinx was removed from the Route 29 early-game mix but retained as a later
  normal Route 42 land encounter.
- Low-rate filler slots now duplicate normal common species unless they are a
  deliberate rare placement, keeping ordinary filler out of future rare-find
  wiki views.
- Land/cave and surf/fishing encounter pools are validated separately; each
  meaningful mode now has at least six species when that mode exists.
- Kanto wild levels were raised for a stronger postgame.
- Random legendary surprise encounters are badge-gated, Repel-aware,
  Safari-excluded, separate from native roamer save state, and tiered at
  1/500 for weaker legends versus 1/1000 for true/cover-story legends.

### Trainers and Bosses

- Trainer rosters and levels were rebuilt for smoother but stronger
  progression.
- The trainer and boss level curve was re-audited after the encounter and
  regular-trainer variety passes; no additional trainer-level raise was needed.
- Gym Leaders, Elite Four, Champions, Red, and other major bosses use full
  six-Pokemon teams.
- Rematch and late-game trainer records were updated.
- Champion Circuit battles were added for late postgame challenges.

### Game Modes and Difficulty

- New Game now presents a mode selector before Professor Oak's speech.
- Normal preserves the current QOL and balance without level caps.
- Challenge adds dynamic badge/story level caps, forced Set battle style, and
  blocks player Bag item use in trainer battles.
- Level caps stop battle EXP at cap and also prevent Rare Candy from leveling
  Pokemon beyond the active cap.
- Hardcore includes Challenge rules and releases/deletes fainted non-Egg party
  Pokemon after battle. The last non-Egg party Pokemon is never released by
  this rule.
- Nuzlocke includes Hardcore rules and enforces one wild encounter/gift/static
  claim per map section. Optional Nuzlocke rules are left to the player.

### Kanto Postgame and Legendaries

- Saffron Fighting Dojo acts as a postgame hub.
- Dossier encounters cover proper Gen 1-4 legendary/mythical access while
  keeping the script patch centralized and buildable.
- Native Raikou and Entei roamers remain separate from the dossier system.
- Latias and Latios use separate dossier flags from native roamer state.

## Core QOL Status

Implemented:

- Running from the beginning: Mom now gives the Running Shoes during the initial
  home conversation.
- Cherrygrove Guide skip: if the player already has Running Shoes, the Guide
  Gent says the player already has them, skips the forced walking tour, hides
  himself, and advances Cherrygrove to the later Map Card callback state.
- Fast text through `FAST_TEXT_PRINTING`.
- Deletable HMs through `DELETABLE_HMS`.
- Reusable TMs through existing HG-Engine configuration.
- Reusable Repels, capture EXP, critical captures, EV/IV viewer, nature stat
  indicators, expanded PC boxes, updated vitamin EV caps, Hidden Abilities, and
  disabled overworld poison damage are preserved.
- Hidden ability slots are obtainable through ordinary wild encounters in
  addition to Ability Patch/scripted hidden-ability support.
- Max Candy and IV stat candies are party-use convenience items.

Still deferred:

- AutoRun/toggle-run as an input-mode feature. Running from the start is now
  implemented through early Running Shoes, but automatic running remains a
  separate field/input task.
- Fast Surf.
- Field moves without teaching the HM move.
- Optional QOL/settings NPC.

## Validation and Exports

- `tools/perfect_johto/validate_project.py` is the master static validation,
  export, and generated-doc runner.
- Structured JSON exports live in `exports/perfect_johto/`.
- Generated Markdown summaries live in `docs/`.
- The latest known validation state from the archived ledger: static checks and
  local native ROM build passed. Current static validation passes with three
  known environment/release warnings: Dudunsparce Three-Segment and Ursaluna
  Bloodmoon special-form access are still deferred, Pokedex area data still
  needs release confirmation, and this machine is missing several build tools
  on `PATH`.

Common commands:

```powershell
python tools/perfect_johto/validate_project.py
python tools/perfect_johto/validate_project.py --write
```

## Key Docs

- `docs/PROJECT_SCOPE.md`
- `docs/GAME_MODES.md`
- `docs/LUMINESCENT_DATA_REFRESH.md`
- `docs/LEARNSET_ACCESSIBILITY.md`
- `docs/QOL_FEATURES.md`
- `docs/POKEMON_AVAILABILITY.md`
- `docs/TYPE_AND_LEARNSET_CHANGES.md`
- `docs/EVOLUTIONS.md`
- `docs/WILD_ENCOUNTERS.md`
- `docs/RARE_ENCOUNTERS.md`
- `docs/RANDOM_LEGENDARY_SYSTEM.md`
- `docs/TRAINER_TEAMS.md`
- `docs/BOSS_BATTLES.md`
- `docs/LEGENDARIES.md`
- `docs/CHAMPION_CIRCUIT.md`
- `docs/ITEMS_AND_MARTS.md`
- `docs/KANTO_POSTGAME.md`
- `docs/BUILD_AND_TESTING.md`
- `docs/PLAYTEST_CHECKLIST.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/KNOWN_LIMITATIONS.md`
- `docs/history/FEATURES_AND_CHANGES_v2026-06-27.md`

## Phase Summary

- Phase 1: repository audit and project planning.
- Phase 2: baseline config cleanup and build-environment documentation.
- Phase 3: approved Pokemon scope and core QOL config foundation.
- Phase 4: Pokemon type modernization, no-trade evolutions, and learnset
  cleanup.
- Phase 5: customization economy, Max Candy, IV candies, and evolution-item
  mart access.
- Phase 6: wild encounters, rare layer, obtainability reporting, and random
  legendary surprise encounters.
- Phase 7: trainer rosters, boss teams, rematches, and level curve.
- Phase 8: Kanto postgame Dojo hub, proper legendary/mythical dossier
  encounters, and Champion Circuit battles.
- Phase 9: validation, static exports, generated docs, build readiness, and
  playtest package preparation.
- Phase 10: early Running Shoes QOL and documentation consolidation.
- Phase 11: encounter-rate cleanup, separated land/water variety validation,
  progression re-audit, and Gen 3-4 type/learnset polish.
- Phase 12: random legendary surprise rates reduced from the old 1/100
  aggregate roll to tiered 1/500 and 1/1000 rolls.
- Phase 13: Luminescent Platinum 3.0 ability refresh for Generation 1-4 Pokemon
  and relevant native forms, plus natural wild hidden-ability rolls.
- Phase 14: New Game mode selector and enforced Normal, Challenge, Hardcore,
  and Nuzlocke rules.

## Known Limitations and TODO

- Runtime playtesting is still required for the generated playtest patch and
  the new early Running Shoes/Guide skip flow.
- Confirm whether Pokedex area data is derived from encounter tables or needs a
  separate regeneration step.
- Runtime-test approved regional/new form display, form handling, and
  evolution behavior.
- Runtime-test trainer curve, boss teams, Rocket/Silver fights, rematches, Red,
  Champion Circuit unlocks, Dojo retries, and legendary/mythical caught flags.
- Runtime-test random legendary surprise encounters with Repel, Safari
  exclusion, native roamer coexistence, level scaling, and badge-gated pools.
- Runtime-test New Game mode selection, level caps, Rare Candy cap handling,
  trainer-battle item blocking, Set battle style, Hardcore release behavior,
  and Nuzlocke encounter/gift/static area claims.
- Investigate AutoRun/toggle-run, fast Surf, and field-move-without-HM-teaching
  as separate future field/input tasks.
- Add exact source provenance for the HG-Engine checkout.
- Keep local ROM inputs out of git.
