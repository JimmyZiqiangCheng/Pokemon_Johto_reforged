# Pokemon Johto Reforged - Features and Changes

Last updated: 2026-06-27

This document is the running project ledger for Pokemon Johto Reforged, an
HG-Engine / HeartGold-based "definitive Johto" hack. Phase 1 was audit and
planning only. Phase 2 was
baseline configuration cleanup and build-environment documentation only. Phase 3
updated the approved Pokemon scope policy and enabled only clean foundational
QOL config switches. No Pokemon data, trainer data, encounter data, scripts,
maps, items, or marts were intentionally changed in Phase 1, Phase 2, or Phase
3. Phase 4 made the first Pokemon data, evolution, and learnset changes for the
approved Pokemon scope. Phase 5 added the badge-gated customization/evolution
item economy and Max Candy support. Phase 6 overhauled main wild encounters,
added a rare encounter layer, raised Kanto encounter levels, added static
obtainability reporting, and implemented a badge-gated random legendary
surprise overlay. Phase 7 overhauled trainer rosters, boss teams, rematches,
and the trainer level curve. Phase 8 added the Kanto postgame Dojo hub,
proper scripted legendary/mythical dossier encounters, and late Champion
Circuit battles. Phase 9 is the final in-project validation, export,
documentation, build-readiness, and playtest-package phase.

## Project Goals

- All Generation 1-4 Pokemon obtainable in one save file.
- Approved later-generation direct evolutions and regional/new forms of Gen 1-4 families
  obtainable where implementation is clean.
- Improved Johto level progression.
- Stronger and more meaningful Kanto postgame.
- Modern quality-of-life features that fit an HGSS-style game.
- Stronger and more varied trainer rosters.
- Full 6-Pokemon parties for Gym Leaders and above.
- All Generation 1-4 legendary and mythical Pokemon obtainable through proper events.
- Additional low-rate random legendary surprise encounters.
- Gym rematches, Elite Four rematches, Champion battles, and superbosses.
- Static validation, Markdown documentation, and structured game-data exports
  for build/test audit readiness.
- Future separate web-app explorer can consume the structured exports, but it
  is not a current-project ROM hack deliverable.

## Global Design Restrictions

- Do not add Mega Evolution.
- Do not add Primal Reversion.
- Do not add Z-Moves.
- Do not add Dynamax or Gigantamax.
- Do not add Terastalization.
- Do not add similar later-generation battle gimmicks.
- Do not expose unrelated Generation 5+ Pokemon lines.
- Later-generation Pokemon/forms are allowed only when they are direct
  evolutions, regional forms, or new forms of Generation 1-4 Pokemon families,
  as recorded in the approved exception plan.
- Do not add later-generation legendary/mythical Pokemon unless they are forms
  of Generation 1-4 legendary/mythical Pokemon and are explicitly approved in a
  later phase.
- Do not restore consumed held items after trainer battles.
- Do not add an interactive web app, browser explorer, React/Next/Vite
  frontend, or `package.json` explorer project in this ROM hack phase.
- Preserve credits and attribution for open-source code, tools, data, and assets.
- Do not download ROMs, pre-patched ROMs, or copyrighted material.

## Phase Log

### Phase 1 - Repo Audit and Project Plan

Status: complete.

Scope:

- Audited `hg-engine-main/hg-engine-main`.
- Audited `pokeheartgold-master`.
- Inspected `../reference_roms`.
- Inspected `../pokeclassic-testing`.
- Read `../pokeclassic-testing/pokeclassic-testing/personalized_tweak.md`.
- Created this project ledger.
- Ran non-invasive validation checks where possible.

No gameplay implementation was performed.

### Phase 2 - Baseline Config Cleanup and Build Environment

Status: complete.

Scope:

- Read this ledger before making changes.
- Audited `hg-engine-main/hg-engine-main/include/config.h`.
- Audited `hg-engine-main/hg-engine-main/armips/include/config.s`.
- Disabled forbidden `MEGA_EVOLUTIONS`, `PRIMAL_REVERSION`, and
  `RESTORE_ITEMS_AT_BATTLE_END` config defines.
- Preserved already-enabled QOL config for reusable TMs, reusable Repels,
  capture EXP, critical captures, EV/IV viewer, expanded PC boxes, updated
  vitamin EV caps, and Hidden Abilities.
- Left `GEN_LATEST = 9` in place as engine compatibility/capacity.
- Documented the Gen 1-4 gameplay-content restriction policy.
- Documented reproducible build requirements for this machine.
- Ran available Python-only validations.

No Pokemon stats/types/abilities, learnsets, evolutions, encounters, trainers,
marts, scripts, maps, legendary events, random legendary systems, or web
explorer files were changed.

### Phase 3 - Approved Pokemon Scope and Core QOL Foundation

Status: complete.

Scope:

- Read this ledger before making changes.
- Replaced the strict Gen 1-4-only scope with a family-based approved exception
  policy for later-generation direct evolutions and forms.
- Audited local HG-Engine species, form, sprite/icon/overworld asset, text, and
  evolution data for the approved later-generation exception candidates.
- Documented later-generation exceptions that are in scope for future content
  phases.
- Documented unrelated Gen 5+ Pokemon lines and later battle gimmicks as still
  disallowed.
- Enabled `FAST_TEXT_PRINTING` in `armips/include/config.s`.
- Enabled `DELETABLE_HMS` in `include/config.h`, paired with already-enabled
  reusable TMs.
- Preserved existing QOL config for reusable TMs, reusable Repels, capture EXP,
  critical captures, EV/IV viewer with nature indicators, expanded PC boxes,
  updated vitamin EV caps, Hidden Abilities, and disabled overworld poison
  damage.

No Pokemon stats/types/abilities, learnsets, evolutions, encounters, trainers,
marts, scripts, maps, legendary events, random legendary systems, or web
explorer files were changed.

### Phase 4 - Pokemon Modernization, Evolutions, and Learnsets

Status: complete.

Scope:

- Read this ledger before making changes.
- Used `../pokeclassic-testing/pokeclassic-testing/personalized_tweak.md` for
  project direction while respecting the Phase 4 deferral list.
- Used local Polished Crystal data as the primary concrete reference for
  restrained Gen 1-2 type modernization.
- Used local Sacred Gold/Storm Silver evolution documentation as HGSS-compatible
  context.
- Used local Heart & Soul only for general Johto/HGSS compatibility context.
- Confirmed Renegade Platinum and Luminescent Platinum documentation was not
  present locally; used public documentation pages only as high-level Gen 3-4
  inspiration where Polished Crystal had no coverage.
- Applied selected semantic type changes to 38 approved-scope Pokemon.
- Did not change base stats, ability slots, hidden ability tables, move battle
  behavior, or the type chart in Phase 4.
- Removed trade-only evolution rows for approved-scope trade evolutions where a
  non-trade item method now exists.
- Converted approved-scope trade-with-item evolutions into direct item-use
  evolutions.
- Replaced awkward approved later-generation evolution methods for Stantler,
  Primeape, and Galarian Farfetch'd with known-move evolutions.
- Updated approved-scope level-up learnsets so evolved forms inherit earlier-form
  level-up moves, duplicate level-up move entries are removed, and non-legendary
  level 60+ moves are moved before level 60.

No encounters, trainers, marts, item prices, item placement, scripts, maps,
legendary events, random legendary systems, or web explorer files were changed.

### Phase 5 - Customization Economy, Max Candy, and Evolution Items

Status: complete.

Scope:

- Read this ledger before making changes.
- Used `../pokeclassic-testing/pokeclassic-testing/personalized_tweak.md` for
  item economy direction while preserving this project's forbidden-gimmick
  restrictions.
- Added `ITEM_MAX_CANDY` in the unused Gen 7 item slot 1058 without shifting
  item IDs.
- Added Max Candy item data, item text, and party-use behavior. Max Candy sets
  all six IVs to 31 and costs 8000 once unlocked.
- Enabled the six base IV stat candies as party-use items. Health, Mighty,
  Tough, Smart, Courage, and Quick Candy each set their matching IV to 31 and
  cost 2000.
- Reduced customization prices: mints, Ability Capsule, and Ability Patch cost
  1000; vitamins and Power items cost 3000; feathers cost 300; EV-reduction
  berries cost 200.
- Expanded standard Poké Mart badge-gated stock to introduce feathers, EV
  berries, mints, and Ability Capsule at 3 badges; vitamins and common
  evolution items at 4 badges; IV stat candies, Power items, and trade-item
  replacements at 5 badges; Ability Patch and broad modern evolution items at
  6 badges; and Max Candy at 12 badges.
- Made approved-scope evolution items, including the item-use methods used by
  Phase 4's Gen 1-4 family evolution work and approved later family exceptions,
  obtainable through the badge-gated standard mart.
- Did not implement held-item restoration, forbidden battle gimmicks, type-chart
  changes, custom abilities, or unrelated flavor hacks.

Files changed:

- `hg-engine-main/hg-engine-main/include/constants/item.h`
- `hg-engine-main/hg-engine-main/asm/include/items.inc`
- `hg-engine-main/hg-engine-main/data/itemdata/itemdata.c`
- `hg-engine-main/hg-engine-main/data/text/222.txt`
- `hg-engine-main/hg-engine-main/data/text/300.txt`
- `hg-engine-main/hg-engine-main/data/text/842.txt`
- `hg-engine-main/hg-engine-main/data/text/843.txt`
- `hg-engine-main/hg-engine-main/data/text/844.txt`
- `hg-engine-main/hg-engine-main/data/text/845.txt`
- `hg-engine-main/hg-engine-main/src/field/mart.c`
- `hg-engine-main/hg-engine-main/src/individual/PartyMenu_HandleUseItemOnMon.c`
- `FEATURES_AND_CHANGES.md`

### Phase 6 - Wild Encounters, Obtainability, Rare Layer, and Random Legendary Surprise

Status: complete, pending runtime build testing.

Scope:

- Read this ledger before making changes.
- Used `../pokeclassic-testing/pokeclassic-testing/personalized_tweak.md` for
  the random legendary overlay direction, but reduced the rate from the
  reference's 1% to a much rarer badge-gated range.
- Regenerated `data/Encounters.c` through
  `tools/perfect_johto/phase6_encounter_tools.py` so the large encounter pass is
  repeatable and statically validated.
- Added rare encounter placements to every meaningful non-Safari main encounter
  area where the table structure supports a below-5% rare slot.
- Used land slots 10 and 11 as 1% slots, surf slot 4 as a 1% slot, and changed
  fishing slot 4 to 4% so fishing can support true below-5% rare encounters.
- Raised Kanto route, cave, city-water, and postgame encounter levels so Kanto
  wild Pokemon are useful after the Johto League instead of vanilla low-level
  filler.
- Added late-game and postgame starter access through semantic wild placements,
  not early route clutter.
- Added or preserved one-save wild/Safari/Headbutt coverage for all
  non-legendary Gen 1-4 evolution-family components.
- Added approved regional-form placements only for Gen 1-4 families, including
  selected Alolan, Galarian, Hisuian, and Paldean Wooper forms.
- Added a badge-gated random legendary/mythical surprise overlay in
  `AddWildPartyPokemon`. It rolls after normal encounter generation has
  succeeded, excludes Safari/roamer/scripted special battle types, uses normal
  wild battles rather than roamer save state, and therefore respects Repel
  through the pre-existing normal encounter flow.
- Created `docs/phase6_obtainability_report.md` with rare placements,
  obtainability coverage, later-generation exclusion status, and validation
  notes.
- Did not add proper stationary legendary/mythical events in Phase 6; those
  remain a future System A event/script phase.

Files changed:

- `hg-engine-main/hg-engine-main/data/Encounters.c`
- `hg-engine-main/hg-engine-main/src/field/encounter_check.c`
- `hg-engine-main/hg-engine-main/src/field/enemy_party.c`
- `tools/perfect_johto/phase6_encounter_tools.py`
- `docs/phase6_obtainability_report.md`
- `FEATURES_AND_CHANGES.md`

### Phase 7 - Trainer Rosters, Boss Teams, and Level Curve

Status: complete, pending runtime build testing and playtest tuning.

Scope:

- Read this ledger before making changes.
- Used `../pokeclassic-testing/pokeclassic-testing/personalized_tweak.md` for
  broad difficulty/QOL direction.
- Used local Sacred Gold/Storm Silver trainer documentation as the primary
  concrete reference for expanded HGSS boss rosters and full serious teams.
- Used the local HG-Engine trainer table as the source of truth for trainer IDs,
  class records, text ownership, and data formatting.
- Added `tools/perfect_johto/phase7_trainer_tools.py` to make the trainer pass
  repeatable, statically validated, and guarded against accidental repeated
  level scaling once Phase 7 is already present.
- Rebuilt all Gym Leader, Elite Four, Champion, Red, major Silver, major Team
  Rocket Executive, and Giovanni/Rocket Boss records targeted by Phase 7.
- Confirmed every Gym Leader, Elite Four, Champion-class, and Red trainer record
  now has 6 Pokemon.
- Raised the first-clear Johto curve through Clair 46-50, the first League
  through Lance 58-60, Kanto Gym Leaders through Blue 78-82, Elite Four
  rematches to 78-88 overall, and Red to 88-100.
- Applied a controlled regular-trainer level pass and diversified obvious
  duplicate no-custom-move parties without turning every route trainer into a
  six-Pokemon boss.
- Kept trainer rosters within Gen 1-4 Pokemon. Phase 7 added no Gen 5+ regional
  or direct-evolution exceptions to trainer parties and found no unrelated
  later-generation trainer species.
- Created `docs/phase7_trainer_report.md` with boss roster tables, curve
  summary, six-Pokemon confirmation, exception usage, and validation notes.

Files changed:

- `hg-engine-main/hg-engine-main/data/Trainers.c`
- `tools/perfect_johto/phase7_trainer_tools.py`
- `docs/phase7_trainer_report.md`
- `FEATURES_AND_CHANGES.md`

### Phase 8 - Kanto Postgame, Legendary Events, Rematches, and Champions

Status: complete, pending script assembly, ROM build testing, and playtesting.

Scope:

- Read this ledger before making changes.
- Added `tools/perfect_johto/phase8_postgame_tools.py` to generate, validate,
  and document the Phase 8 postgame layer.
- Replaced the Saffron Fighting Dojo karate master script after all 16 badges
  with a postgame hub while preserving the existing visible 16 Gym Leader
  phone-rematch scripts in the same map.
- Added a Champion Circuit menu for repeatable Lance and Blue battles after 16
  badges. Red rematch, Steven, Wallace, Cynthia, and Arceus unlock only after
  the original Mt. Silver Red trainer flag is set.
- Added Champion Circuit trainer records for Steven, Wallace, and Cynthia as
  six-Pokemon level 90-98 battles using Gen 1-4 Pokemon only.
- Added one-time scripted/static Dojo dossier encounters for every Gen 1-4
  legendary/mythical that was not already cleanly covered by native roaming
  flow, plus higher-level dossier access for key Kanto/Johto legends.
- Kept Raikou and Entei as their native Burned Tower level-40 roamers.
- Used static encounter outcome `4` to set caught flags only on actual capture;
  failed, fainted, or fled dossier encounters remain retryable.
- Added named Phase 8 caught flags in the unused late flag range 2865-2887.
- Documented every legendary/mythical location, level, prerequisite, encounter
  type, and flag in `docs/phase8_postgame_report.md`.
- Added no unrelated Gen 5+ Pokemon, no later-generation legendary forms, and
  no forbidden battle gimmicks.

Files changed:

- `hg-engine-main/hg-engine-main/armips/include/flags.s`
- `hg-engine-main/hg-engine-main/armips/scr_seq/scr_seq_00832_phase8_dojo.s`
- `hg-engine-main/hg-engine-main/data/Trainers.c`
- `hg-engine-main/hg-engine-main/data/text/533.txt`
- `tools/perfect_johto/phase8_postgame_tools.py`
- `docs/phase8_postgame_report.md`
- `FEATURES_AND_CHANGES.md`

### Phase 9 - Final Game Validation, Build Readiness, Static Documentation, and Playtest Package

Status: complete for static validation and documentation; pending local build
tooling, `rom.nds`, script assembly, and runtime playtesting.

Scope:

- Read this ledger before making changes.
- Removed the interactive web-app explorer as a current ROM hack deliverable.
  It is now documented as a future separate project, not part of this ROM hack
  phase.
- Kept structured exports in this ROM hack project under
  `exports/perfect_johto/` so a future separate explorer can consume them.
- Added `tools/perfect_johto/validate_project.py` as the master Phase 9
  validation/export/documentation runner. By default it validates only; with
  `--write` it regenerates static exports and Markdown docs.
- Coordinated existing Phase 6 encounter validation, Phase 7 trainer
  validation, Phase 8 postgame validation, learnset JSON parsing, learnset
  generation into a temporary validation folder, trainer source validation,
  text archive validation, forbidden config/scope scans, mart/item checks,
  evolution-method checks, random legendary checks, Dojo script/flag checks,
  and build-readiness checks.
- Generated 22 structured JSON exports under `exports/perfect_johto/`,
  including availability, approved scope, evolutions, encounters, rare
  encounters, random legendary data, legendary events, trainer teams, boss
  battles, rematches, Champion Circuit, marts/items, Max Candy, level curve,
  Kanto postgame, and known risks.
- Added static Markdown documentation under `docs/`, including build/testing,
  project scope, QOL features, Pokemon availability, approved later
  exceptions, evolutions, wild/rare encounters, random legendary system,
  trainers, boss battles, legendaries, Champion Circuit, items/marts, Kanto
  postgame, playtest checklist, release checklist, and known limitations.
- Validated Phase 8 Dojo labels, generated script/text parity, text indexes,
  late caught-flag aliases in range 2865-2887, capture-only static encounter
  outcome `4`, retry behavior after non-captures, native Raikou/Entei
  separation, Latias/Latios separate dossier flags, Champion Circuit unlock
  rules, and Steven/Wallace/Cynthia six-Pokemon trainer records.
- Validated Phase 6 random legendary pool/rates/blocked battle types and
  confirmed it does not touch roamer save state.
- Validated item/mart/Max Candy definitions, prices, badge gates, UI count,
  party-use behavior, and forbidden-gimmick mart exclusion.
- Validated no approved-scope trade-only evolutions remain and that
  approved-scope item and known-move evolution methods have static access.
- Documented remaining release warnings: build environment incomplete,
  `rom.nds` missing, `armips` missing, Pokedex area data regeneration/derival
  unconfirmed, Dudunsparce Three-Segment and Ursaluna Bloodmoon special form
  access not implemented, and runtime playtesting still required.

Files changed:

- `tools/perfect_johto/validate_project.py`
- `exports/perfect_johto/*.json`
- `docs/README.md`
- `docs/BUILD_AND_TESTING.md`
- `docs/PROJECT_SCOPE.md`
- `docs/QOL_FEATURES.md`
- `docs/POKEMON_AVAILABILITY.md`
- `docs/APPROVED_LATER_EXCEPTIONS.md`
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
- `docs/PLAYTEST_CHECKLIST.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/KNOWN_LIMITATIONS.md`
- `FEATURES_AND_CHANGES.md`

## Project Structure Summary

- `hg-engine-main/hg-engine-main`: primary HG-Engine project to modify for this hack.
- `pokeheartgold-master`: base Pokemon HeartGold/SoulSilver disassembly/reference tree.
- `../reference_roms`: local reference material:
  - `Sacred Gold & Storm Silver V1.05`
  - `polishedcrystal-master`
  - `pokemonHnS-1.2`
- `../pokeclassic-testing`: local personalized reference project. The main preference file is
  `pokeclassic-testing/personalized_tweak.md`.

No `.git` directory is present in the current project root, HG-Engine directory, or
`pokeheartgold-master`; the `git` command is also not available from the current
PowerShell environment.

## HG-Engine Version and Config Audit

Version identity:

- Local source identifies itself as `hg-engine` from `BluRosie/hg-engine`.
- No tag, commit hash, release file, or git metadata is available locally.
- Treat the exact HG-Engine version as unknown until the project is restored as a git clone
  or an external provenance note is added.

Primary config files:

- `hg-engine-main/hg-engine-main/include/config.h`
- `hg-engine-main/hg-engine-main/armips/include/config.s`
- `hg-engine-main/hg-engine-main/Makefile`
- `hg-engine-main/hg-engine-main/narcs.mk`
- `hg-engine-main/hg-engine-main/data/codetables.mk`
- `hg-engine-main/hg-engine-main/data/itemdata/itemdata.mk`
- `hg-engine-main/hg-engine-main/hooks`
- `hg-engine-main/hg-engine-main/repoints`

Enabled or configured in `include/config.h`:

- `GEN_LATEST = 9` outside debug battle scenarios.
- `APPLY_ANTIPIRACY`
- `FAIRY_TYPE_IMPLEMENTED = 1`
- `TYPE_EFFECTIVENESS_GEN = GEN_LATEST`
- `ALLOW_SAVE_CHANGES`
- `EXPERIENCE_FORMULA_GEN = GEN_LATEST`
- `HIDDEN_ABILITIES`
- `ITEM_POCKET_EXPANSION`
- `IMPLEMENT_BDHCAM_ROUTINE`
- `IMPLEMENT_CAPTURE_EXPERIENCE`
- `IMPLEMENT_CRITICAL_CAPTURE`
- `IMPLEMENT_NEW_EV_IV_VIEWER`
- `UPDATE_OVERWORLD_POISON`
- `IMPLEMENT_SEASONS`
- `IMPLEMENT_DEXIT_FORMS_MECHANICS`
- `EXPAND_PC_BOXES`
- `FRIENDSHIP_EVOLUTION_THRESHOLD = 160`
- `FRIENDSHIP_EFFECTS`
- `AI_CAN_GRAB_ITEMS`
- `IMPLEMENT_REUSABLE_REPELS`
- `UPDATE_VITAMIN_EV_CAPS`
- `REUSABLE_TMS`
- `DELETABLE_HMS`
- `MART_EXPANSION`
- `STATIC_HP_BAR`
- `UPDATE_MACHINE_MOVE_LABELS`
- `BLOCK_LEARNING_UNIMPLEMENTED_MOVES`
- `VANILLA_PARADOX_BOOSTER_ENERGY_BEHAVIOUR`
- `VANILLA_MYTHICALS`
- `DISABLE_CRITICAL_HP_WARNING`

Disabled or commented in `include/config.h`:

- `MEGA_EVOLUTIONS` (disabled in Phase 2 by project restriction)
- `PRIMAL_REVERSION` (disabled in Phase 2 by project restriction)
- `RESTORE_ITEMS_AT_BATTLE_END` (disabled in Phase 2 by project restriction)
- `IMPLEMENT_TRANSPARENT_TEXTBOXES`
- `IMPLEMENT_WILD_DOUBLE_BATTLES`
- `IMPLEMENT_LEVEL_CAP`
- `DISABLE_ITEMS_IN_TRAINER_BATTLE`
- `POKEATHLON_SHOP_EXPANSION`
- terrain/weather special conversions for thunderstorm and fog.

Configured in `armips/include/config.s`:

- `DISALLOW_DEXIT_GEN = 0`
- `FAIRY_TYPE_IMPLEMENTED = 1`
- `SNOW_WARNING_GENERATION = GEN_LATEST`
- `SLEEP_TURNS_GENERATION = GEN_LATEST`
- `ALLOW_SAVE_CHANGES` is defined.
- `BATTLE_MODE_FORCE_SET = 0`
- `ALWAYS_HAVE_NATIONAL_DEX = 0`
- `ALWAYS_UNCAPPED_FRAME_RATE = 0`
- `BATTLES_UNCAPPED_FRAME_RATE = 0`
- `FAST_TEXT_PRINTING = 1`
- `NO_PARTNER_DOUBLE_BATTLES = 1`

Phase 2 config resolution:

- `MEGA_EVOLUTIONS` is disabled.
- `PRIMAL_REVERSION` is disabled.
- `RESTORE_ITEMS_AT_BATTLE_END` is disabled.
- No top-level `include/config.h` or `armips/include/config.s` switches were found for enabling
  Z-Moves, Dynamax/Gigantamax, or Terastalization. The engine still contains related constants
  and handler code as capacity, including system flag constants for Z-Moves, Dynamax, and
  Terastalization. Gameplay phases must not set those flags or expose related items, scripts,
  forms, trainers, encounters, or documentation.
- `GEN_LATEST = 9` remains in place for engine compatibility. Gameplay scope will be enforced by
  content policy and later validation, not by reducing the engine's internal generation constant.
- The engine includes many Gen 5+ species/forms, moves, abilities, items, and gimmick constants
  by default. Future gameplay phases must gate content to Gen 1-4 unless explicitly expanded.

## Data Location Map

Pokemon species data:

- `hg-engine-main/hg-engine-main/data/Species.c`
- `hg-engine-main/hg-engine-main/include/species_data.h`
- `hg-engine-main/hg-engine-main/include/constants/species.h`
- Built into personal data target `a/0/0/2` via `narcs.mk`.

Moves:

- `hg-engine-main/hg-engine-main/data/Moves.c`
- `hg-engine-main/hg-engine-main/include/move_data.h`
- `hg-engine-main/hg-engine-main/include/constants/moves.h`
- Move battle scripts: `hg-engine-main/hg-engine-main/data/battle_scripts`
- Move animation scripts: `hg-engine-main/hg-engine-main/armips/move`

Abilities:

- Ability constants: `hg-engine-main/hg-engine-main/include/constants/ability.h`
- Species ability slots: `hg-engine-main/hg-engine-main/data/Species.c`
- Hidden ability table: `hg-engine-main/hg-engine-main/data/HiddenAbilityTable.c`
- Battle implementation source: `hg-engine-main/hg-engine-main/src/battle`

Learnsets:

- Main generated/source JSON: `hg-engine-main/hg-engine-main/data/learnsets/learnsets.json`
- Base learnset imports: `hg-engine-main/hg-engine-main/data/learnsets/base/*.json`
- Generator: `hg-engine-main/hg-engine-main/scripts/build_learnsets.py`
- Generated build outputs: `build/learnset/*.c`
- Level-up target: `a/0/3/3`
- Egg target: `a/2/2/9`
- Machine/tutor codetable targets: `a028` codetable entries.

Evolutions:

- `hg-engine-main/hg-engine-main/data/Evolutions.c`
- Evolution structs/constants: `hg-engine-main/hg-engine-main/include/pokemon.h`
- Built into target `a/0/3/4`.

Items:

- `hg-engine-main/hg-engine-main/data/itemdata/itemdata.c`
- `hg-engine-main/hg-engine-main/include/constants/item.h`
- Item behavior code: `hg-engine-main/hg-engine-main/src/item.c`
- Item text archives: `hg-engine-main/hg-engine-main/data/text`
- Machine move update helper: `hg-engine-main/hg-engine-main/scripts/update_machine_moves.py`

Poke Marts and shops:

- HG-Engine mart source: `hg-engine-main/hg-engine-main/src/field/mart.c`
- Standard badge mart table: `sBadgeMart` in `src/field/mart.c`
- Named special mart arrays: `sCherrygroveCityMart`, department-store arrays, Kanto mart arrays,
  Indigo Plateau, etc. in `src/field/mart.c`
- Repoint mapping: `hg-engine-main/hg-engine-main/repoints`
- Common mart script flow: `hg-engine-main/hg-engine-main/armips/scr_seq/scr_seq_00003_commonscript.s`
- Base reference implementation: `pokeheartgold-master/src/scrcmd_mart.c`

Trainers:

- `hg-engine-main/hg-engine-main/data/Trainers.c`
- `hg-engine-main/hg-engine-main/include/trainer_data.h`
- `hg-engine-main/hg-engine-main/include/constants/trainerclass.h`
- Generator: `hg-engine-main/hg-engine-main/tools/source/trainerdatagen`
- Built into targets `a/0/5/5`, `a/0/5/6`, `a/0/5/7`, and `a/1/3/1`.

Wild encounters:

- Main wild encounters: `hg-engine-main/hg-engine-main/data/Encounters.c`
- Safari encounters: `hg-engine-main/hg-engine-main/data/SafariEncounters.c`
- Headbutt encounters: `hg-engine-main/hg-engine-main/data/Headbutt.c`
- Encounter constants: `hg-engine-main/hg-engine-main/include/constants/encounter_tables.h`
- Encounter structs: `hg-engine-main/hg-engine-main/include/encounter.h`

Maps:

- HG-Engine map constants: `hg-engine-main/hg-engine-main/include/constants/maps.h`
- Base map data/reference: `pokeheartgold-master/files/fielddata`
- Base map headers/code: `pokeheartgold-master/src/data/map_headers.h`,
  `pokeheartgold-master/src/map_header.c`, `pokeheartgold-master/src/map_matrix.c`
- Base map events: `pokeheartgold-master/files/fielddata/eventdata/zone_event`
- Base map matrices: `pokeheartgold-master/files/fielddata/mapmatrix/map_matrix`

Scripts and events:

- HG-Engine patched scripts: `hg-engine-main/hg-engine-main/armips/scr_seq`
- Common script: `armips/scr_seq/scr_seq_00003_commonscript.s`
- Trainer script: `armips/scr_seq/scr_seq_00953_trainerscript.s`
- Base scripts: `pokeheartgold-master/files/fielddata/script/scr_seq`
- Script macros/constants: `hg-engine-main/hg-engine-main/armips/include/scriptmacros.s`,
  `hg-engine-main/hg-engine-main/armips/include/flags.s`,
  `hg-engine-main/hg-engine-main/armips/include/vars.s`

Text:

- HG-Engine text patches/generated archives: `hg-engine-main/hg-engine-main/data/text/*.txt`
- Text build/validation: `narcs.mk`, `tools/msgenc`,
  `tools/source/dumptools/validate_text_archive.py`
- Base text reference: `pokeheartgold-master/files/msgdata/msg/*.gmm` and
  `pokeheartgold-master/files/msgdata/scenario/scr_msg.narc`

Build config:

- HG-Engine build: `hg-engine-main/hg-engine-main/Makefile`
- HG-Engine Docker path: `Dockerfile`, `docker-makerom.cmd`, `docker-login.cmd`
- HG-Engine requirements: `requirements.txt`
- Base disassembly build: `pokeheartgold-master/Makefile`, `config.mk`, `filesystem.mk`

Documentation/export/validation tools:

- `hg-engine-main/hg-engine-main/documentation`
- `hg-engine-main/hg-engine-main/scripts/build_learnsets.py`
- `hg-engine-main/hg-engine-main/scripts/build_tests.py`
- `hg-engine-main/hg-engine-main/scripts/run_tests.py`
- `hg-engine-main/hg-engine-main/scripts/run_tests.sh`
- `hg-engine-main/hg-engine-main/scripts/validate_trainers_s.py`
- `hg-engine-main/hg-engine-main/scripts/update_machine_moves.py`
- `hg-engine-main/hg-engine-main/scripts/msg_cat.py`
- `hg-engine-main/hg-engine-main/dump.mk`
- `pokeheartgold-master/tools/py_scripts`
- Project-specific validation/export/documentation runner:
  `tools/perfect_johto/validate_project.py`.
- Structured static exports: `exports/perfect_johto/*.json`.
- Static documentation: `docs/*.md`.
- No interactive web explorer exists in `perfect_johto`; any explorer is a
  future separate project.

## Name And Attribution

Project name: Pokemon Johto Reforged.

Primary foundations and project references:

- HG-Engine: primary engine and gameplay source tree used for this hack.
- `pokeheartgold-master`: base Pokemon HeartGold/SoulSilver disassembly and
  reference tree used for HGSS source structure, scripts, text, maps, and build
  context.
- Sacred Gold & Storm Silver: local HGSS ROM hack reference material used for
  roster, evolution, item, and event-design context.
- Polished Crystal: local ROM hack/reference material used for restrained
  Pokemon modernization context.
- Heart & Soul: local Johto/HGSS reference material used for general
  compatibility and structure context.

Learning-path acknowledgement: the author's first ROM hack practice was based
on PokeClassic and Pokemon Rekindled. Those projects did not directly supply
code or assets for Pokemon Johto Reforged, but they are credited as important
practice projects that helped make this work possible.

## Current Data Scale

Approximate source-entry counts from Phase 1:

- `data/Species.c`: 1476 species/form entries.
- `data/Moves.c`: 923 move entries.
- `data/Trainers.c`: 738 trainer entries.
- `data/Encounters.c`: 142 encounter tables.
- `data/SafariEncounters.c`: 12 Safari area entries.

The current HG-Engine dataset goes far beyond Gen 4. For this project, unrelated
later-generation data should be treated as engine capacity, not as approved gameplay content.
Only documented family-based exceptions may be exposed.

## Approved Pokemon Scope Policy

- Keep `GEN_LATEST = 9` unless a later build/test pass proves that lowering it is safe.
- Treat unrelated Gen 5+ Pokemon, unrelated Gen 5+ forms, later-generation gimmick forms, moves,
  abilities, and items as internal HG-Engine capacity only.
- Approved baseline scope:
  - All Generation 1-4 Pokemon.
  - Later-generation Pokemon only if they are direct evolutions of Gen 1-4 Pokemon/families.
  - Later-generation forms only if they are new forms or regional forms of Gen 1-4
    Pokemon/families.
  - Later evolutions connected to approved regional forms only when the family relationship is
    direct and the implementation is clean.
- Still disallowed:
  - Unrelated Gen 5+ Pokemon lines.
  - Later-generation legendary/mythical Pokemon unless they are a form of a Gen 1-4
    legendary/mythical and explicitly approved in a later phase.
  - Mega Evolution, Primal Reversion, Z-Moves, Dynamax/Gigantamax, Terastalization, and similar
    later-generation battle gimmicks.
  - Totem, Noble/Lord, Gigantamax, Mega, Primal, Terastal, and unrelated later-generation form
    families unless explicitly approved later.
- Hidden Abilities may remain enabled because that flag does not by itself expose unrelated Gen 5+
  Pokemon.
- Phase 9 validation allows approved cross-generation family exceptions while still blocking
  unrelated later-generation Pokemon/forms and forbidden-gimmick flags/items/moves in gameplay
  placement files.

## Approved Later-Generation Exception Plan

This began as documentation only in Phase 3. Later phases placed approved
exceptions in encounters/evolutions/items where intended, and Phase 9 exports
the approved scope for audit.

Approved direct later-generation evolutions with local species/text/sprite/icon/overworld assets:

- Eevee family: Sylveon. Current method: knows a Fairy-type move. Clean enough if Fairy move
  access is ensured later.
- Stantler family: Wyrdeer. Current method: `EVO_FORM_ARGUMENT`. Replace later with an intuitive
  level or known-move method.
- Scyther family: Kleavor. Current method: Black Augurite item. Clean if the item is obtainable
  later.
- Ursaring family: Ursaluna. Current method: Peat Block at night. Clean if the item is obtainable
  later.
- Primeape family: Annihilape. Current method: `EVO_FORM_ARGUMENT`. Replace later with an
  intuitive level or known-move method.
- Girafarig family: Farigiraf. Current method: knows Twin Beam. Clean if move access is ensured
  later.
- Dunsparce family: Dudunsparce, including Three-Segment form. Current method: knows Hyper Drill.
  Clean if move access/form handling is ensured later.
- Galarian Meowth family: Perrserker. Current method: level 28. Clean.
- Galarian Farfetch'd family: Sirfetch'd. Current method: three critical hits in battle. Replace
  later with an intuitive level, item, or known-move method.
- Galarian Mr. Mime family: Mr. Rime. Current method: level 42. Clean.
- Galarian Corsola family: Cursola. Current method: level 38. Clean.
- Galarian Zigzagoon family: Obstagoon. Current method: level 35. Clean, though later flavor may
  choose a night condition.
- Hisuian Sneasel family: Sneasler. Current method: Razor Claw during day. Clean if the item is
  obtainable later.
- Hisuian Qwilfish family: Overqwil. Current method: knows Barb Barrage. Clean if move access is
  ensured later.
- Paldean Wooper family: Clodsire. Current method: level 20. Clean.

Approved later regional/new forms with local species entries, form mappings, form table entries,
and sprite/icon/overworld assets:

- Alolan forms: Rattata, Raticate, Raichu, Sandshrew, Sandslash, Vulpix, Ninetales, Diglett,
  Dugtrio, Meowth, Persian, Geodude, Graveler, Golem, Grimer, Muk, Exeggutor, Marowak.
- Galarian forms: Meowth, Ponyta, Rapidash, Slowpoke, Slowbro, Farfetch'd, Weezing, Mr. Mime,
  Slowking, Corsola, Zigzagoon, Linoone.
- Hisuian forms: Growlithe, Arcanine, Voltorb, Electrode, Typhlosion, Qwilfish, Sneasel.
- Paldean forms: Wooper and Tauros Combat/Blaze/Aqua.
- New forms tied to approved families: Dudunsparce Three-Segment and Ursaluna Bloodmoon.

Not approved by this phase:

- Galarian Articuno, Zapdos, and Moltres. These are later forms of Gen 1 legendaries and require
  explicit later approval under the legendary/mythical rule.
- Dialga Origin and Palkia Origin. These are later forms of Gen 4 legendaries and require explicit
  later approval under the legendary/mythical rule.
- Galarian Darumaka/Darmanitan, Galarian Yamask/Runerigus, Galarian Stunfisk, Hisuian Samurott,
  Hisuian Lilligant, Hisuian Zorua/Zoroark, Hisuian Braviary, Hisuian Sliggoo/Goodra, Hisuian
  Avalugg, Hisuian Decidueye, Basculegion, and other unrelated Gen 5+ families.
- Any Mega, Primal, Gigantamax, Terastal, Totem, Noble/Lord, Z-Move, Dynamax, or similar
  gimmick-driven form.

## Core QOL Status

Implemented/enabled in Phase 3:

- Fast text printing from the start: enabled with `FAST_TEXT_PRINTING = 1`.
- Deletable HMs: enabled with `DELETABLE_HMS`, paired with reusable TMs so HMs are not consumed
  permanently.

Already present and preserved:

- Reusable TMs: `REUSABLE_TMS`.
- Reusable Repel prompt: `IMPLEMENT_REUSABLE_REPELS`.
- Capture EXP: `IMPLEMENT_CAPTURE_EXPERIENCE`.
- Critical captures: `IMPLEMENT_CRITICAL_CAPTURE`.
- EV/IV summary viewer: `IMPLEMENT_NEW_EV_IV_VIEWER`.
- Nature up/down stat indicators: included by the EV/IV viewer per local `CONFIG.md`.
- Expanded PC boxes / 30 boxes: `EXPAND_PC_BOXES`.
- Updated vitamin EV caps to 252: `UPDATE_VITAMIN_EV_CAPS`.
- Hidden Abilities support: `HIDDEN_ABILITIES`.
- Overworld poison damage disabled: `UPDATE_OVERWORLD_POISON`.

Deferred or unsupported by clean existing config:

- Toggle run/walk or AutoRun from the beginning: no existing HG-Engine config flag found in Phase
  3. Revisit as a small field/input hook or early-game script decision after build verification.
- Fast Surf: no existing HG-Engine config flag found in Phase 3. Revisit only after field movement
  code is traced and buildable.
- Field move usability without requiring the HM to be taught: current HG-Engine party-menu logic
  still derives field moves from known moves. Revisit as a dedicated field-move service rewrite,
  not as a config-only QOL change.
- Optional badge-based level cap: supported by `IMPLEMENT_LEVEL_CAP`, but not enabled yet because
  it needs a badge-to-variable policy and script integration.
- Optional QOL/settings NPC in New Bark Town or Goldenrod: deferred until script/map editing
  workflow is buildable and verified.

## Reference Files Discovered

Sacred Gold / Storm Silver:

- `../reference_roms/Sacred Gold & Storm Silver V1.05/Documents/SS_SG Trainer Pokemon by @JD48096761.txt`
- `../reference_roms/Sacred Gold & Storm Silver V1.05/Documents/Action Replay Codes.pdf`
- `../reference_roms/Sacred Gold & Storm Silver V1.05/Documents/Evolution Changes.pdf`
- `../reference_roms/Sacred Gold & Storm Silver V1.05/Documents/Important Item Locations.pdf`
- `../reference_roms/Sacred Gold & Storm Silver V1.05/Documents/Pokemon Changes.pdf`
- `../reference_roms/Sacred Gold & Storm Silver V1.05/Documents/Pokemon Locations.pdf`
- `../reference_roms/Sacred Gold & Storm Silver V1.05/Documents/Special Event Guide.pdf`
- `../reference_roms/Sacred Gold & Storm Silver V1.05/Patches/Instructions.txt`

Polished Crystal:

- `../reference_roms/polishedcrystal-master/FEATURES.md`
- `../reference_roms/polishedcrystal-master/CHANGELOG.md`
- `../reference_roms/polishedcrystal-master/CREDITS.md`
- `../reference_roms/polishedcrystal-master/FAQ.md`
- `../reference_roms/polishedcrystal-master/TODO.md`
- `../reference_roms/polishedcrystal-master/data`
- `../reference_roms/polishedcrystal-master/maps`
- `../reference_roms/polishedcrystal-master/engine`
- `../reference_roms/polishedcrystal-master/material`

Heart & Soul:

- `../reference_roms/pokemonHnS-1.2/pokemonHnS-1.2/README.md`
- `../reference_roms/pokemonHnS-1.2/pokemonHnS-1.2/data/maps`
- `../reference_roms/pokemonHnS-1.2/pokemonHnS-1.2/src/data/wild_encounters.json`
- `../reference_roms/pokemonHnS-1.2/pokemonHnS-1.2/prefabs.json`
- `../reference_roms/pokemonHnS-1.2/pokemonHnS-1.2/INSTALL.md`

Personalized project reference:

- `../pokeclassic-testing/pokeclassic-testing/personalized_tweak.md`
- `../pokeclassic-testing/pokeclassic-testing/postgame_changes.md`
- `../pokeclassic-testing/pokeclassic-testing/pokeclassic-explorer/README.md`

## Personalized Tweak Summary

The personalized tweak file should be treated as the main preference source for
balance/flavor. Key preferences:

- Rock should no longer be weak to Ground.
- Custom defensive ability direction:
  - `Immortal Shell`: super-effective incoming damage is treated as neutral unless ignored by
    Mold Breaker-style effects.
  - `Solid Rock`: standard 25 percent reduction to super-effective damage.
- Favor tasteful Polished Crystal-inspired type/stat/ability modernization.
- Preserve custom flavor for Tyranitar, Salamence, Aron/Aggron, Charizard, Dragonite, and
  special Starter Pikachu.
- Prefer compressed level-up learnsets so non-legendary late moves arrive before level 60.
- Evolved forms should not lose access to earlier-form level-up moves.
- Prefer stronger but smoother boss level curves over extreme grind curves.
- Kanto and postgame bosses should be materially stronger and include meaningful rematches.
- QOL shop upgrades should be gated by badge progression.
- Random legendary surprise encounters should be low-rate, respect Repel, avoid Safari Zone,
  and not overwrite roamer save state.
- Explorer expectations include linked Pokemon/move/item/trainer/location data and regenerated
  exports after stable gameplay data.

Do not blindly copy GBA-specific implementation details into HGSS. Use the preference file for
design direction, then implement natively in HG-Engine/HGSS.

## Proposed Implementation Phases

1. Baseline config cleanup and build environment. Complete as Phase 2.
   - Disable forbidden gimmicks and held-item restoration.
   - Decide save compatibility stance.
   - Establish a reproducible build command.
   - Add minimal local validation commands/scripts if needed.

2. Approved Pokemon scope and core QOL foundation. Complete as Phase 3.
   - Replace strict Gen 1-4-only policy with the approved family-exception policy.
   - Audit direct later evolutions and forms connected to Gen 1-4 families.
   - Enable clean foundational QOL config switches.

3. Species/form/evolution availability baseline.
   - Confirm all Gen 1-4 species constants, graphics, cries, forms, and dex text are present.
   - Confirm approved later-generation family exceptions are asset-complete enough to expose.
   - Replace impossible or awkward later evolution methods with HGSS-appropriate methods.
   - Keep unrelated Gen 5+ content unused/not obtainable.

4. Pokemon modernization pass.
   - Apply approved type/stat/ability preferences.
   - Include Rock/Ground chart preference only after battle-engine trace and test.
   - Add or adapt custom ability behavior only if compatible with HG-Engine architecture.

5. Evolution and learnset pass.
   - Make all Gen 1-4 evolutions obtainable without trading where appropriate.
   - Align level-up pacing and inherited move access.
   - Keep learnset changes coherent with HGSS move availability.

6. Item, TM/HM, tutor, and mart pass.
   - Tune reusable TM/HM policy.
   - Add badge-gated QOL mart stock.
   - Update item text, prices, and machine labels through existing tools.

7. Wild encounter availability pass.
   - Place all non-legendary Gen 1-4 species in Johto/Kanto/Safari/Headbutt/fishing/surfing.
   - Keep route identity and day/night flavor.
   - Update Pokedex area data.

8. Johto trainer and level curve pass.
   - Rebuild regular trainer parties and early-to-mid boss curve.
   - Use Sacred Gold/Storm Silver as a major roster reference while respecting Gen 1-4 scope.

9. Gym Leader, Elite Four, Champion, and rival pass.
   - Full 6-Pokemon teams for Gym Leaders and above.
   - Build first-run League and Champion progression.
   - Add held items, abilities, natures, and movesets where supported.

10. Kanto postgame pass.
   - Raise Kanto route/gym curve.
   - Make Kanto more structured and meaningful.
   - Add postgame gating and rewards.

11. Legendary and mythical event pass.
    - Implement proper events for all Gen 1-4 legendary/mythical Pokemon.
    - Use existing maps/scripts where possible before adding new areas.

12. Random legendary surprise encounter system.
    - Implement low-rate overlay after event-based legendaries are defined.
    - Respect Repel, Safari exclusions, level scaling, and save safety.

13. Rematches, Champion exhibitions, and superbosses.
    - Gym rematches.
    - Elite Four rematches.
    - Champion battles.
    - Red and additional superbosses.

14. Documentation and export tooling.
    - Add repeatable exports for Pokemon, moves, encounters, trainers, marts, items, and events.
    - Add validation checks for full availability and boss-team constraints.
    - Completed in Phase 9 as static JSON exports, Markdown docs, and
      `tools/perfect_johto/validate_project.py`.

15. Future separate web-app explorer.
    - Future separate project, not part of this ROM hack phase.
    - Use generated exports rather than hand-maintained web data if pursued later.
    - Do not add React, Next.js, Vite, frontend routes, CSS, browser-app files,
      or `package.json` for an explorer in this ROM hack project.

## Feature Ledger

Features added:

- None in Phase 1.
- None in Phase 2; config cleanup only.
- None in Phase 3 beyond QOL config switches and project-scope documentation.
- Phase 4 added approved-scope Pokemon data modernization, no-trade evolution
  replacements, and approved-scope learnset pacing cleanup.
- Phase 5 added a badge-gated customization economy, Max Candy support, usable
  IV stat candies, and repeatable mart access to approved item-use evolution
  items.
- Phase 6 added rare wild encounter infrastructure, main encounter
  obtainability coverage, raised Kanto wild levels, and the random legendary
  surprise overlay.
- Phase 7 added expanded trainer rosters, full boss teams, trainer rematch
  level updates, and trainer-data validation/report tooling.

QOL changes:

- None in Phase 1.
- Phase 2 preserved existing enabled QOL flags for reusable TMs, reusable Repels, capture EXP,
  critical captures, the EV/IV viewer, expanded PC boxes, updated vitamin EV caps, and Hidden
  Abilities.
- Phase 3 enabled fast text printing by setting `FAST_TEXT_PRINTING = 1` in
  `armips/include/config.s`.
- Phase 3 enabled deletable HMs by defining `DELETABLE_HMS` in `include/config.h`, paired with
  already-enabled reusable TMs.
- Phase 3 confirmed nature up/down stat indicators are part of the already-enabled EV/IV summary
  viewer according to local `CONFIG.md`.
- Phase 3 confirmed overworld poison damage remains disabled through `UPDATE_OVERWORLD_POISON`.
- Phase 5 made mints, Ability Capsule/Patch, EV training items, IV stat
  candies, and evolution items progressively buyable through the standard mart
  expansion.

Pokemon data changes:

- None in Phase 1.
- None in Phase 2.
- None in Phase 3. The approved later-generation exception list is scope documentation only.
- Phase 4 changed selected approved-scope Pokemon typings only. No base stats,
  ability slots, hidden abilities, catch rates, EV yields, held items, or growth
  data were changed.
- Phase 4 Polished Crystal-priority Gen 1-2 type changes:
  - Charizard: Fire / Flying -> Fire / Dragon.
  - Blastoise: Water -> Water / Steel.
  - Butterfree: Bug / Flying -> Bug / Psychic.
  - Golduck: Water -> Water / Psychic.
  - Rapidash: Fire -> Fire / Fairy.
  - Meganium: Grass -> Grass / Fairy.
  - Typhlosion: Fire -> Fire / Ground.
  - Feraligatr: Water -> Water / Dark.
  - Noctowl: Normal / Flying -> Ghost / Flying.
  - Ledian: Bug / Flying -> Bug / Fighting.
  - Ariados: Bug / Poison -> Bug / Dark.
  - Ampharos: Electric -> Electric / Dragon.
  - Bellossom: Grass -> Grass / Fairy.
  - Politoed: Water -> Water / Grass.
  - Sunflora: Grass -> Grass / Fire.
  - Dunsparce: Normal -> Normal / Ground.
  - Girafarig: Normal / Psychic -> Psychic / Dark.
  - Octillery: Water -> Water / Fire.
  - Stantler: Normal -> Normal / Psychic.
  - Ninetales: Fire -> Fire / Ghost.
- Phase 4 Renegade/Luminescent Platinum-inspired Gen 3-4 type changes:
  - Sceptile: Grass -> Grass / Dragon.
  - Masquerain: Bug / Flying -> Bug / Water.
  - Volbeat: Bug -> Bug / Electric.
  - Illumise: Bug -> Bug / Fairy.
  - Trapinch: Ground -> Bug / Ground.
  - Vibrava: Ground / Dragon -> Bug / Dragon.
  - Flygon: Ground / Dragon -> Bug / Dragon.
  - Swablu: Normal / Flying -> Fairy / Flying.
  - Altaria: Dragon / Flying -> Dragon / Fairy.
  - Seviper: Poison -> Poison / Dark.
  - Milotic: Water -> Water / Fairy.
  - Glalie: Ice -> Ice / Rock.
  - Luvdisc: Water -> Water / Fairy.
  - Misdreavus: Ghost -> Ghost / Fairy.
  - Mismagius: Ghost -> Ghost / Fairy.
  - Luxray: Electric -> Electric / Dark.
  - Lopunny: Normal -> Normal / Fighting.
  - Electivire: Electric -> Electric / Fighting.

Move/ability/type changes:

- None in Phase 1.
- None in Phase 2. Mega Evolution and Primal Reversion config support were disabled, but no
  Pokemon stats, types, abilities, moves, or learnsets were edited.
- None in Phase 3.
- Phase 4 changed Pokemon type data listed above.
- Phase 4 did not change move data, move battle behavior, ability data, or the
  type chart.
- Phase 4 deliberately deferred Rock no longer being weak to Ground, Immortal
  Shell, custom defensive ability work, personalized Tyranitar changes,
  personalized Salamence changes, personalized Dragonite changes, and other
  strict one-off flavor hacks.

Battle behavior/config changes:

- Phase 2 disabled `MEGA_EVOLUTIONS`.
- Phase 2 disabled `PRIMAL_REVERSION`.
- Phase 2 disabled `RESTORE_ITEMS_AT_BATTLE_END`.
- Z-Moves, Dynamax/Gigantamax, Terastalization, and similar later-generation battle gimmicks
  remain disallowed by project policy and must not be exposed through gameplay content.
- Phase 3 preserved the forbidden-gimmick restrictions.

Evolution changes:

- None in Phase 1.
- None in Phase 2.
- None in Phase 3. Future evolution work should replace awkward/impossible current methods for
  Wyrdeer, Annihilape, and Sirfetch'd before gameplay exposure.
- Phase 4 removed trade-only rows for Kadabra, Machoke, Graveler, Haunter, and
  Alolan Graveler. These now use the existing Linking Cord item-use evolution.
- Phase 4 converted trade-with-item evolutions into direct item-use evolutions:
  - Poliwhirl -> Politoed with King's Rock.
  - Slowpoke -> Slowking with King's Rock.
  - Onix -> Steelix with Metal Coat.
  - Seadra -> Kingdra with Dragon Scale.
  - Scyther -> Scizor with Metal Coat.
  - Porygon -> Porygon2 with Up-Grade.
  - Rhydon -> Rhyperior with Protector.
  - Electabuzz -> Electivire with Electirizer.
  - Magmar -> Magmortar with Magmarizer.
  - Porygon2 -> Porygon-Z with Dubious Disc.
  - Feebas -> Milotic with Prism Scale remains alongside beauty evolution.
  - Dusclops -> Dusknoir with Reaper Cloth.
  - Clamperl -> Huntail with Deep Sea Tooth.
  - Clamperl -> Gorebyss with Deep Sea Scale.
- Phase 4 replaced awkward approved later-generation direct evolution methods:
  - Stantler -> Wyrdeer now evolves by leveling while knowing Psyshield Bash.
  - Primeape -> Annihilape now evolves by leveling while knowing Rage Fist.
  - Galarian Farfetch'd -> Sirfetch'd now evolves by leveling while knowing Leaf
    Blade.
- Phase 4 left item-based approved later evolutions in place for Kleavor,
  Ursaluna, Sneasler, Galarian Slowbro, and Galarian Slowking. Item
  availability is intentionally left for Phase 5.
- Phase 5 did not change evolution methods. It made approved-scope evolution
  items obtainable through badge-gated standard Poké Marts.

Learnset changes:

- None in Phase 1.
- None in Phase 2.
- None in Phase 3.
- Phase 4 updated approved-scope level-up learnsets only. Machine, tutor, and
  egg move lists were not intentionally changed.
- Phase 4 changed Stantler's level 32 `Role Play` to `Psyshield Bash` so
  Wyrdeer has a reachable known-move evolution method.
- Phase 4 moved Galarian Farfetch'd's `Leaf Blade` from level 55 to level 35 so
  Sirfetch'd has a reachable known-move evolution method before late game.
- Phase 4 propagated earlier-form level-up moves into evolved forms across 267
  approved-scope evolution relationships. The pass added 229 missing move
  entries and lowered 988 evolved-form move levels where a previous form learned
  the same move earlier.
- Phase 4 removed 77 duplicate approved-scope level-up move entries after
  inheritance and prerequisite edits.
- Phase 4 compressed 84 approved-scope non-legendary level-up learnsets so all
  level 60+ moves now occur before level 60. Legendary and mythical learnsets
  were intentionally left unchanged by this compression rule.

Item and mart changes:

- None in Phase 1.
- None in Phase 2. No item data or mart stock was edited.
- None in Phase 3. Deletable HMs changed HM forgettability behavior through config only; no item
  data, prices, or mart stock were edited.
- None in Phase 4. Evolution item availability is intentionally deferred to
  Phase 5.
- Phase 5 added `ITEM_MAX_CANDY` at item ID 1058, replacing an unused
  `ITEM_UNKNOWN_1058` slot without shifting item IDs.
- Phase 5 made Max Candy a party-use medicine item that sets all six IVs to 31.
  It costs 8000 and appears in standard marts at 12 badges.
- Phase 5 made `ITEM_HEALTH_CANDY`, `ITEM_MIGHTY_CANDY`, `ITEM_TOUGH_CANDY`,
  `ITEM_SMART_CANDY`, `ITEM_COURAGE_CANDY`, and `ITEM_QUICK_CANDY` party-use
  medicine items that set HP, Attack, Defense, Sp. Atk, Sp. Def, and Speed IVs
  to 31 respectively. They cost 2000 and appear at 5 badges.
- Phase 5 set all available mints plus Ability Capsule and Ability Patch to
  1000. Mints and Ability Capsule appear at 3 badges; Ability Patch appears at
  6 badges.
- Phase 5 set EV vitamins and Power training items to 3000, feathers to 300,
  and EV-reduction berries to 200.
- Phase 5 expanded `sBadgeMart` to 104 entries, below the documented 203-item
  UI limit.
- Phase 5 badge-gated progression:
  - 0-2 badges: core balls, medicine, status heals, Escape Rope, and Repels.
  - 3 badges: EV feathers, EV-reduction berries, all available mints, and
    Ability Capsule.
  - 4 badges: EV vitamins, common stones, Oval Stone, and Linking Cord.
  - 5 badges: IV stat candies, Macho Brace, Power items, and trade-item
    replacements.
  - 6 badges: Ability Patch and broad modern evolution items, including
    Black Augurite, Peat Block, Galarica Cuff, and Galarica Wreath.
  - 12 badges: Max Candy.

Encounter changes:

- None in Phase 1.
- None in Phase 2.
- None in Phase 3.
- None in Phase 4.
- None in Phase 5.
- Phase 6 regenerated the main wild encounter archive with a repeatable
  project-local tool and added a rare encounter layer to 132/132 meaningful
  non-Safari main encounter areas.
- Phase 6 rare land encounters use slots 10 and/or 11, each 1%; rare surf
  encounters use surf slot 4 at 1%; rare fishing encounters use fishing slot 4,
  now 4% after the Phase 6 fishing slot-rate adjustment.
- Phase 6 added full non-legendary Gen 1-4 evolution-family coverage across
  main wild encounters plus existing Safari and Headbutt data. The generated
  report records 211/211 non-legendary family components covered.
- Phase 6 added late-game/postgame wild starter access: Johto starters are
  placed in late Johto/Kanto contexts, Hoenn and Sinnoh starters are placed in
  late Johto/postgame Kanto contexts, and no starter family was added as early
  route clutter.
- Phase 6 notable rare placements include Larvitar in Dark Cave Route 31
  entrance at 1%, Dratini/Bagon in dragon and sea-cave areas, Beldum/Gible/Bagon
  in mineral or rugged late caves, Feebas in limited water locations, Rotom near
  the Power Plant route context, and fossil lines in ruins/caves.
- Phase 6 added selected approved regional-form wild placements only for Gen
  1-4 families, such as Alolan Sandshrew/Vulpix/Diglett, Galarian Slowpoke,
  Galarian Farfetch'd, Galarian Corsola, Hisuian Voltorb/Qwilfish/Sneasel, and
  Paldean Wooper.
- Phase 6 validation found no unrelated later-generation species in
  `data/Encounters.c`, `data/SafariEncounters.c`, or `data/Headbutt.c`.

Trainer changes:

- None in Phase 1.
- None in Phase 2.
- None in Phase 3.
- None in Phase 4.
- None in Phase 5.
- None in Phase 6.
- Phase 7 rebuilt first-clear Johto Gym Leader rosters into six-Pokemon teams
  with type identity and coverage: Falkner 13-14, Bugsy 18-20, Whitney 23-25,
  Morty 29-31, Chuck 34-38, Jasmine 38-42, Pryce 40-43, and Clair 46-50.
- Phase 7 rebuilt the first Elite Four and Champion into full six-Pokemon
  teams: Will 50-54, Koga 52-56, Bruno 54-58, Karen 56-58, and Lance 58-60.
- Phase 7 rebuilt Kanto Gym Leaders into six-Pokemon teams and raised them into
  the post-League curve: Lt. Surge/Janine/Brock/Misty in the 58-66 range,
  Erika/Sabrina in the 65-72 range, Blaine 72-76, and Blue 78-82.
- Phase 7 raised Red to an 88-100 superboss team with his iconic six Pokemon.
- Phase 7 expanded major Silver fights from mid-game onward to six Pokemon
  where appropriate, including Pokemon League, post-League, and postgame
  special records.
- Phase 7 expanded major Rocket Executive and Rocket Boss records, including
  Ariana, Petrel, Archer, and Giovanni, into full serious teams where their
  story role and level band support it.
- Phase 7 applied a regular-trainer pass that raised non-boss trainer levels
  across the game and diversified obvious duplicate no-custom-move parties with
  semantic Gen 1-4 alternatives.

Level curve changes:

- None in Phase 1.
- None in Phase 2.
- Phase 6 raised Kanto wild route, cave, city-water, and postgame encounter
  levels into useful post-League ranges. Standard Kanto routes generally now use
  high-30s to low-40s land levels, Victory Road/Tohjo use low-to-high 40s,
  Mt. Silver uses low-to-high 50s, and Cerulean Cave reaches the mid-50s to
  mid-60s.
- Phase 7 raised trainer progression to match the new encounter and boss
  expectations. The final trainer curve is:
  - Johto Leaders: Falkner 13-14, Bugsy 18-20, Whitney 23-25, Morty 29-31,
    Chuck 34-38, Jasmine 38-42, Pryce 40-43, Clair 46-50.
  - First League: Will 50-54, Koga 52-56, Bruno 54-58, Karen 56-58, Lance
    58-60.
  - Kanto Leaders: early Kanto 58-66, mid Kanto 65-72, Blaine 72-76, Blue
    78-82.
  - Rematches/postgame: Elite Four rematches 78-84, Lance rematch 82-88, Gym
    Leader rematches 66-90, Red 88-100.
- Phase 8 added Champion Circuit exhibition battles for Steven and Wallace at
  90-96 and Cynthia at 92-98.

Legendary/mythical event changes:

- None in Phase 1.
- None in Phase 2.
- None in Phase 3.
- None in Phase 4.
- None in Phase 5.
- Phase 6 did not add proper stationary, scripted, roaming, gift, or puzzle
  legendary/mythical events; it only added the separate random surprise overlay.
- Phase 8 added the System A official legendary/mythical obtainability layer
  through the Saffron Fighting Dojo postgame dossier hub. It covers all Gen 1-4
  legendary/mythical Pokemon in one save when combined with the native Raikou
  and Entei Burned Tower roamers.
- Phase 8 dossier encounters are one-time static/scripted battles gated by
  badges and caught/prerequisite flags. Key chained prerequisites include the
  three Regis before Regigigas, Kyogre plus Groudon before Rayquaza, Cresselia
  before Darkrai, Manaphy before Phione, and Red plus the lake/creation trios
  before Arceus.

Random legendary surprise encounter system changes:

- None in Phase 1.
- None in Phase 2.
- None in Phase 3.
- None in Phase 4.
- None in Phase 5.
- Phase 6 implemented System B as a low-rate overlay in
  `src/field/enemy_party.c` inside `AddWildPartyPokemon`.
- The overlay runs only after normal wild encounter generation succeeds, so
  Repel filtering remains handled by the existing field encounter flow.
- The overlay excludes trainer battles, Safari, built-in roamer battles, Pal
  Park, catching demos, and Bug-Catching Contest battles.
- The overlay does not write to roamer save state and starts the selected
  Pokemon as a normal wild battle.
- Random surprise encounters are repeatable and not flag-limited.
- Random surprise rate by badge count:
  - 0-3 badges: disabled.
  - 4 badges: 1/4096.
  - 5 badges: 1/3072.
  - 6-7 badges: 1/2048.
  - 8-15 badges: 1/1536.
  - 16 badges: 1/1024.
- Random surprise pool by badge gate:
  - 4 badges: Articuno, Zapdos, Moltres, Raikou, Entei, Suicune.
  - 5 badges: Regirock, Regice, Registeel, Latias, Latios, Uxie, Mesprit,
    Azelf, Heatran, Cresselia.
  - 6 badges: Mewtwo, Lugia, Ho-Oh, Kyogre, Groudon, Rayquaza, Dialga, Palkia,
    Giratina, Regigigas.
  - 16 badges: Mew, Celebi, Jirachi, Deoxys, Phione, Manaphy, Darkrai, Shaymin,
    Arceus.
- Random surprise levels use the current map encounter level plus a small badge
  bonus, then clamp to badge-tier bounds: 25-32 at 4 badges, 32-38 at 5 badges,
  38-45 at 6-7 badges, 45-55 at 8-11 badges, 50-60 at 12-15 badges, and 55-70
  at 16 badges.

Kanto postgame changes:

- None in Phase 1.
- None in Phase 2.
- Phase 6 raised Kanto wild encounter levels so post-League routes and caves
  are no longer vanilla low-level filler.
- Phase 7 raised Kanto trainer progression. First-clear Kanto Gym Leaders now
  start in the high 50s/low 60s, Blue is 78-82, Gym Leader rematches reach
  66-90, Elite Four rematches reach 78-88 overall, and Red is 88-100.
- Phase 8 turns the Saffron Fighting Dojo into the post-16-badge Kanto
  postgame hub for Champion Circuit battles and legendary/mythical dossiers.
- Phase 8 adds higher-level Kanto legendary dossier battles for Seafoam
  Articuno, Power Plant Zapdos, Mt. Silver Moltres, and Cerulean Cave Mewtwo.

Rematch/champion/superboss content:

- None in Phase 1.
- None in Phase 2.
- Phase 7 updated Champion Lance's first-clear team to a six-Pokemon 58-60
  roster: Gyarados, Aerodactyl, Kingdra, Charizard, Aggron, and Dragonite.
- Phase 7 raised Lance's rematch Champion team to 82-88.
- Phase 7 raised Elite Four rematches to 78-84 and Gym Leader rematches to
  66-90, including a Blue rematch at 84-90.
- Phase 7 expanded special postgame Lance, Clair, and Silver records to
  six-Pokemon teams.
- Phase 7 raised Red to an 88-100 superboss team.
- Phase 8 added repeatable Champion Circuit battles in the Saffron Fighting
  Dojo: Lance, Blue, Red rematch, Steven, Wallace, and Cynthia.
- Phase 8 added Steven, Wallace, and Cynthia as six-Pokemon Champion-class
  trainer records. Red rematch and visiting champions require the original Mt.
  Silver Red defeat flag.

Documentation/export tooling changes:

- Created `FEATURES_AND_CHANGES.md`.
- Phase 2 updated `FEATURES_AND_CHANGES.md` with baseline config cleanup, the then-current Gen
  1-4 gameplay scope policy, build environment requirements, and validation status.
- Phase 3 updated `FEATURES_AND_CHANGES.md` with the approved Pokemon scope policy, approved
  later-generation exception plan, foundational QOL status, and validation/TODO updates.
- Phase 4 updated `FEATURES_AND_CHANGES.md` with Pokemon type changes, no-trade
  evolution replacements, known-move evolution replacements, learnset cleanup
  counts, deferred flavor work, and validation status.
- Phase 5 updated `FEATURES_AND_CHANGES.md` with the badge-gated item economy,
  Max Candy implementation, evolution-item availability, price changes, changed
  files, validation status, and remaining build limitation.
- Phase 6 added `tools/perfect_johto/phase6_encounter_tools.py` to regenerate
  the main encounter archive and emit obtainability/rare-layer validation.
- Phase 6 added `docs/phase6_obtainability_report.md` with coverage counts,
  notable rare placements, per-area rare placement notes, and validation notes.
- Phase 6 updated `FEATURES_AND_CHANGES.md` with encounter, rare-layer,
  obtainability, random legendary, validation, and remaining-risk status.
- Phase 7 added `tools/perfect_johto/phase7_trainer_tools.py` to rewrite,
  validate, and report trainer roster/curve changes.
- Phase 7 added `docs/phase7_trainer_report.md` with boss team tables,
  six-Pokemon confirmation, regular-trainer pass notes, level-curve summary,
  later-generation exception usage, and validation results.
- Phase 7 updated `FEATURES_AND_CHANGES.md` with trainer, boss, rematch,
  level-curve, validation, and remaining-risk status.
- Phase 8 added `tools/perfect_johto/phase8_postgame_tools.py` to generate
  the Dojo script patch, Dojo text archive replacement, Champion Circuit
  trainers, named caught flags, and the Phase 8 report.
- Phase 8 added `docs/phase8_postgame_report.md` with legendary/mythical
  location, level, prerequisite, encounter type, flag, rematch, champion, and
  scope-validation details.
- Phase 8 updated `FEATURES_AND_CHANGES.md` with Kanto postgame, proper
  legendary event, rematch, champion, validation, and remaining-risk status.
- Phase 9 added `tools/perfect_johto/validate_project.py` as the master
  validation/export/documentation runner.
- Phase 9 added structured static exports under `exports/perfect_johto/`.
- Phase 9 added static Markdown documentation under `docs/` for build/testing,
  project scope, QOL, availability, evolutions, encounters, random
  legendaries, trainers, boss battles, legendaries, Champion Circuit,
  items/marts, Kanto postgame, playtesting, release, and known limitations.
- Phase 9 explicitly moved the web-app explorer to a future separate project.

## Build and Test Status

Discovered intended HG-Engine commands:

- `make`
- `make -j$(nproc)`
- `make AUTO_TEST=Y -j$(nproc)`
- `scripts/run_tests.sh -c -j $(nproc)`
- Docker path: `docker build . -t hg-engine`, then `docker-makerom.cmd`

Discovered intended base disassembly commands:

- `make`
- `make soulsilver`
- `make compare`
- `make main`
- `make filesystem`

Local environment status:

- `python` and `python3`: available, Python 3.12.7.
- `git`: not available on PATH.
- `make`: not available on PATH.
- `cmake`: not available on PATH.
- `armips`: not available on PATH.
- `arm-none-eabi-gcc`: not available on PATH.
- `docker`: not available on PATH.
- `rom.nds`: missing from `hg-engine-main/hg-engine-main`.
- `baserom.nds`: missing from `pokeheartgold-master`.
- No full ROM build was possible in Phase 1, Phase 2, Phase 3, Phase 4, Phase
  5, Phase 6, Phase 7, Phase 8, or Phase 9 because the local build
  environment is incomplete.

Reproducible build requirements:

- Required local ROM input: a legally obtained US Pokemon HeartGold ROM named `rom.nds` placed in
  `hg-engine-main/hg-engine-main`. Do not commit or redistribute this file.
- Recommended route on this machine: Docker, once Docker Desktop is installed and available on
  PATH. Intended commands from `hg-engine-main/hg-engine-main` are `docker build . -t hg-engine`
  and then `docker-makerom.cmd`.
- Native route: install Git, GNU Make, CMake, Python 3, the ARM toolchain expected by HG-Engine,
  and any libraries/tools required by the Makefile. WSL or MSYS2 is likely cleaner than raw
  Windows PowerShell for the native route.
- Version control: install Git before large data passes. Prefer restoring this HG-Engine tree as
  a real git clone or initializing a repository before major edits so provenance, diffs, and
  build metadata are trackable.

Checks run in Phase 1:

- `python -c "import json; json.load(...data/learnsets/learnsets.json...)"`: passed.
- `tools/source/dumptools/validate_text_archive.py` over `data/text/*.txt`: passed.
- `PYTHONUTF8=1 python scripts/validate_trainers_s.py data/Trainers.c`: passed.
- `make -n`: not run successfully because `make` is not installed/available.

Checks run in Phase 2:

- Active forbidden config define scan for `MEGA_EVOLUTIONS`, `PRIMAL_REVERSION`, and
  `RESTORE_ITEMS_AT_BATTLE_END`: passed.
- `python -c "import json; json.load(...data/learnsets/learnsets.json...)"`: passed.
- `PYTHONUTF8=1 python scripts/validate_trainers_s.py data/Trainers.c`: passed.
- `python tools/source/dumptools/validate_text_archive.py charmap.txt data/text/*.txt`: passed.
- Gen 5+ species placement sanity scan across `data/Encounters.c`, `data/SafariEncounters.c`,
  `data/Headbutt.c`, `data/Trainers.c`, and `src/field/mart.c`: passed for the scanned files.
- Full ROM build: not run because `make`, `git`, Docker, ARM toolchain, and `rom.nds` are missing
  from the current environment.

Checks run in Phase 3:

- Phase 3 config scan for disabled forbidden features and enabled QOL flags: passed.
- `python -c "import json; json.load(...data/learnsets/learnsets.json...)"`: passed.
- `PYTHONUTF8=1 python scripts/validate_trainers_s.py data/Trainers.c`: passed.
- `python tools/source/dumptools/validate_text_archive.py charmap.txt data/text/*.txt`: passed.
- Approved later-generation exception audit for documented direct evolutions/forms: passed for
  species entries, form mappings where needed, form table entries where needed, and
  sprite/icon/overworld asset folders.
- Full ROM build: not run because `make`, `git`, CMake, Docker, ARM toolchain, and `rom.nds` are
  missing from the current environment.

Checks run in Phase 4:

- `python -c "import json; json.load(...data/learnsets/learnsets.json...)"`: passed.
- `python scripts/build_learnsets.py --learnsets data/learnsets/learnsets.json ...`: passed for
  level-up, egg, machine, and tutor learnset generation into a temporary validation directory.
- Custom approved-scope learnset validation: passed. No approved-scope non-legendary level-up
  moves remain at level 60 or higher, and no approved-scope duplicate level-up moves remain.
- Custom evolution reference validation for species, move, and item constants: passed.
- Targeted evolution method scan for Kadabra, Machoke, Graveler, Haunter, Alolan Graveler,
  Stantler, Primeape, and Galarian Farfetch'd: passed.
- Approved-scope gameplay placement scan across `data/Encounters.c`, `data/SafariEncounters.c`,
  `data/Headbutt.c`, `data/Trainers.c`, and `src/field/mart.c`: passed; no unrelated Gen 5+
  Pokemon were found in the scanned gameplay placement files.
- `PYTHONUTF8=1 python scripts/validate_trainers_s.py data/Trainers.c`: passed.
- `python tools/source/dumptools/validate_text_archive.py charmap.txt data/text/*.txt`: passed
  using PowerShell-expanded file paths.
- Full ROM build: not run because `make`, `git`, CMake, Docker, ARM toolchain, and `rom.nds` are
  missing from the current environment.

Checks run in Phase 5:

- `python -c "import json; json.load(...data/learnsets/learnsets.json...)"`: passed.
- `python tools/source/dumptools/validate_text_archive.py charmap.txt data/text/*.txt`: passed
  using PowerShell-expanded file paths from the HG-Engine directory.
- `PYTHONUTF8=1 python scripts/validate_trainers_s.py data/Trainers.c`: passed using
  PowerShell-compatible `$env:PYTHONUTF8='1'`.
- Custom Max Candy validation: passed. `ITEM_MAX_CANDY` is defined in both C and asm item
  constants, has itemdata and text entries, and is handled by the party item-use overlay.
- Custom Phase 5 approved-scope price/use/gate validation: passed. Mints and ability items are
  1000, IV stat candies are 2000, Max Candy is 8000, vitamins and Power items are 3000, feathers
  are 300, EV-reduction berries are 200, approved-scope evolution items are 2500, stat
  candies/Max Candy are party-use medicine items, unrelated later-family evolution items are not
  stocked, and key badge gates match the intended progression.
- Custom badge mart validation: passed. `sBadgeMart` has 104 entries, all referenced item
  constants have itemdata entries, all required customization items are present, and all 30
  approved-scope evolution items are present in the badge-gated standard mart.
- Incidental unrelated later-family item price restoration check: passed against upstream
  HG-Engine itemdata values for apples, pots, scrolls, armor items, Whipped Dream, and Sachet.
- Badge mart forbidden-gimmick exposure scan: passed. The badge mart does not expose Dynamax,
  Gigantamax, Mega, Primal, Tera/Terastal, or Z-Move/Z-Crystal items.
- `make -n`: not run successfully because `make` is not installed/available.
- Full ROM build: not run because `make`, `git`, CMake, Docker, ARM toolchain, and `rom.nds` are
  missing from the current environment.

Checks run in Phase 6:

- `python tools/perfect_johto/phase6_encounter_tools.py --write`: passed. The
  tool regenerated `data/Encounters.c`, emitted
  `docs/phase6_obtainability_report.md`, validated 132/132 meaningful
  non-Safari main encounter areas with rare placements, validated 211/211
  non-legendary Gen 1-4 family components covered across main/Safari/Headbutt
  encounter sources, and found no unrelated later-generation species in those
  encounter sources.
- Custom random legendary pool validation: passed. The implemented System B
  pool contains only Gen 1-4 legendary/mythical species and excludes later
  regional legendary forms.
- Custom rare-rate validation: passed. Land rare placements use 1% slots, surf
  rare placements use 1% slots, and fishing rare placements use the Phase 6 4%
  slot.
- Approved later-generation encounter placement validation: passed. Later-form
  placements are restricted to approved Gen 1-4 families.
- `make -n`: not run successfully because `make` is not installed/available.
- Full ROM build: not run because `make`, `git`, CMake, Docker, ARM toolchain,
  and `rom.nds` are missing from the current environment.

Checks run in Phase 7:

- `python tools/perfect_johto/phase7_trainer_tools.py --write`: passed. The
  tool updated `data/Trainers.c`, emitted `docs/phase7_trainer_report.md`,
  validated trainer species/move/item constants and trainer ability slots,
  validated mandatory six-Pokemon Gym Leader/Elite Four/Champion/Red records,
  validated major rival/Rocket boss team sizes, and found no unrelated
  later-generation trainer species.
- Post-write idempotency/validation guard:
  `python tools/perfect_johto/phase7_trainer_tools.py`: passed. The tool
  detected the Phase 7 sentinel trainer state and validated without reapplying
  trainer edits.
- Custom boss summary parse over `data/Trainers.c`: passed. All Gym Leader,
  Elite Four, Champion-class, and Red records have 6 Pokemon after Phase 7.
- Custom regular-trainer level distribution audit: passed for static sanity.
  Non-boss regular trainers now top out at level 73, leaving Blue, rematches,
  Lance, and Red as the intended late-game ceiling.
- `make -n`: not run successfully because `make` is not installed/available.
- Full ROM build: not run because `make`, `git`, CMake, Docker, ARM toolchain,
  and `rom.nds` are missing from the current environment.

Checks run in Phase 8:

- `python tools/perfect_johto/phase8_postgame_tools.py --write`: passed. The
  tool regenerated the Dojo script patch, Dojo text archive replacement,
  Champion Circuit trainers, named caught flags, and
  `docs/phase8_postgame_report.md`; it validated 35/35 Gen 1-4
  legendary/mythical coverage including native Raikou/Entei roamers.
- Post-write idempotency/validation guard:
  `python tools/perfect_johto/phase8_postgame_tools.py`: passed. The tool
  validated Phase 8 species, move, item, flag, text-index, script-label, and
  Gen 1-4 scope references.
- `PYTHONUTF8=1 python scripts/validate_trainers_s.py data/Trainers.c`:
  passed.
- `python tools/source/dumptools/validate_text_archive.py charmap.txt data/text/533.txt`:
  passed.
- Targeted Phase 8 Gen 5+/forbidden-form scan over the new Dojo script and
  Phase 8 generator: passed; no unrelated Gen 5+ species, Mega/Primal forms,
  or regional/form legendary exceptions were found.
- Generated Dojo script transformation scan: passed; no base disassembly
  CamelCase script macros remained in
  `armips/scr_seq/scr_seq_00832_phase8_dojo.s`.
- `armips`: not run because `armips` is not installed/available.
- `make -n`: not run successfully because `make` is not installed/available.
- Full ROM build: not run because `make`, `git`, CMake, Docker, ARM toolchain,
  `armips`, and `rom.nds` are missing from the current environment.

Checks run in Phase 9:

- `python tools/perfect_johto/validate_project.py`: passed with no failures and
  3 warnings.
- `python tools/perfect_johto/validate_project.py --write`: passed with no
  failures and regenerated static exports/docs.
- Learnset JSON parse: passed for `data/learnsets/learnsets.json`.
- Learnset generation into a temporary validation folder: passed for machine,
  level-up, egg, and tutor learnset outputs.
- Phase 6 encounter validation: passed; 132/132 meaningful non-Safari areas
  have rare placements.
- Phase 7 trainer validation: passed; mandatory leader, Elite Four, Champion,
  and Red records have six Pokemon.
- Phase 8 postgame validation: passed; 35 Gen 1-4 legendary/mythical entries
  validated, including native Raikou/Entei roamers.
- `PYTHONUTF8=1 python scripts/validate_trainers_s.py data/Trainers.c`:
  passed.
- Text archive validation over `data/text/*.txt`: passed for 46 archives.
- Forbidden config and approved-scope scan: passed; forbidden configs are
  disabled and gameplay placement files stay inside approved Pokemon scope.
- Random legendary validation: passed; 35 Gen 1-4 legendary/mythical pool
  entries, documented badge rates, level clamps, and exclusions are present.
- Dojo script and flag validation: passed; labels, capture-only outcome checks,
  and late flag aliases were validated.
- Item, mart, and Max Candy validation: passed; 104 badge-mart entries remain
  under the 203-item UI limit, with intended prices/gates.
- Evolution/form validation: warning only. No approved-scope trade-only
  evolutions remain and item/known-move methods validate, but Dudunsparce
  Three-Segment and Ursaluna Bloodmoon special access are not implemented.
- Pokedex area data status: warning. No Phase 9 regeneration hook was confirmed;
  release must confirm engine derivation or add area-data generation.
- Build readiness: warning. `git`, `make`, `cmake`, `armips`, Docker,
  `arm-none-eabi-gcc`, and `rom.nds` are missing, so no full ROM build,
  `armips` assembly run, Docker build, or `make -n` dry run could be completed.

## Known Limitations and Risks

- Exact HG-Engine version is unknown without git metadata or an external provenance note.
- Phase 2 resolved the direct config conflicts for Mega Evolution, Primal Reversion, and
  trainer-battle held-item restoration.
- HG-Engine still contains later-generation gimmick constants and handler code. Future content
  passes must avoid enabling or documenting those systems.
- Current engine data includes unrelated Gen 5+ species/forms, moves, abilities, items, and later
  battle gimmick constants; future phases must expose only approved family exceptions unless
  explicitly expanded later.
- Phase 4 resolved the awkward Wyrdeer, Annihilape, and Sirfetch'd evolution methods. Phase 5
  resolved repeatable mart access for item-use evolution constants currently referenced by
  `data/Evolutions.c`. Remaining approved later evolution/form risks are encounter, gift, NPC, and
  form access rules that belong to later availability passes.
- Phase 5 item behavior and mart progression are validated statically, but have not been
  runtime-tested in a built ROM because the local build environment is incomplete.
- Phase 6 encounter generation, rare-rate rules, family coverage, and later-generation
  exclusion were validated statically, but have not been runtime-tested in a built ROM
  because the local build environment is incomplete.
- Phase 6 random legendary surprise encounters use a clean post-normal-encounter hook and
  avoid roamer save state, but the hook has not been runtime-tested in a built ROM.
- Phase 7 trainer rosters, move/item constants, ability slots, six-Pokemon boss rules,
  approved-scope species usage, and regular-trainer level distribution were
  validated statically, but have not been runtime-tested in a built ROM.
- Phase 7 intentionally raises regular trainers broadly. Static distribution is
  sane, but route-by-route playtesting is still needed to catch any local
  difficulty spikes caused by map order, optional trainer density, or backtracking.
- Giovanni's optional Rocket Boss timing should be runtime-checked; Phase 7
  places that record at 58-64 as an optional post-League-scale fight.
- Phase 8's proper legendary/mythical layer is implemented as a Saffron Dojo
  dossier hub rather than bespoke object/event edits on every source map. This
  keeps the patch scoped and buildable through the existing script-NARC patch
  flow, but future polish can move individual dossiers into native map quests
  if desired.
- Phase 8 Latias/Latios dossier flags are separate from native roamer save
  state. This guarantees one-save non-event access to both Lati twins, but the
  native roamer/Enigma-style flow should be runtime-checked for possible
  duplicate access in edge-case save orders.
- Phase 8 script syntax and control flow were statically checked, but the Dojo
  script archive could not be assembled with `armips` in the current
  environment.
- Phase 9 master validation passed all static checks, but it does not replace a
  full ROM build, script assembly, or runtime playtest pass.
- Pokedex area data was not separately regenerated in Phase 6; confirm whether this
  HG-Engine build derives area data from encounter NARCs or needs a separate Pokedex-area
  update before release.
- Dudunsparce Three-Segment and Ursaluna Bloodmoon have local form data, but Phase 4 did not add a
  new random/form-selection rule for obtaining those specific forms.
- Some approved regional/form entries use placeholder text names in `Species.c` while relying on
  form tables/assets. Future display/runtime validation should confirm final names and Pokedex text
  before these forms are exposed in player-facing documentation.
- Fast text is currently a global forced setting, not an in-game option.
- Deletable HMs are enabled through config, but field moves still require known moves.
- Build environment is incomplete in the current PowerShell PATH.
- `git`, `make`, `cmake`, `armips`, Docker, and `arm-none-eabi-gcc` are not
  available on PATH in the current environment.
- Full build requires a legally obtained US HeartGold `rom.nds` in the HG-Engine directory.
- Base disassembly build requires proprietary toolchain components and base ROM inputs that are
  not present here.
- Future script/map editing needs careful coordination between HG-Engine patched scripts and the
  base `pokeheartgold-master/files/fielddata` data.
- Structured exports are available for a future separate web-app explorer, but
  that explorer is not part of this ROM hack project or Phase 9.

## TODO

- Add exact source provenance for the HG-Engine checkout.
- Install Git before future major data passes.
- Establish a reproducible local build environment, preferably Docker first on this machine,
  or install the native Git/Make/CMake/`armips`/ARM toolchain route.
- Add a legally obtained US HeartGold `rom.nds` locally for builds; do not commit it.
- Run `python tools/perfect_johto/validate_project.py` before release and after
  any future gameplay data changes.
- Keep `exports/perfect_johto/` and static `docs/` generated from the Phase 9
  runner when source data changes.
- Runtime-test approved regional/new form encounter display, form handling, and evolution
  behavior after a build works.
- Investigate AutoRun/toggle run, fast Surf, and field-move-without-HM-teaching as dedicated
  field/input tasks after a build works.
- Runtime-test the Phase 8 Dojo postgame hub, Champion Circuit unlocks,
  legendary/mythical caught flags, retry behavior after failed static battles,
  and prerequisite chains after builds are possible.
- Consider moving selected Phase 8 dossiers into bespoke native map quests
  after the script build/runtime loop is available.
- Add Pokedex area-data generation/update if the engine does not derive area data from the
  regenerated encounter archives.
- Runtime-test Phase 7 boss teams, Rocket Executive fights, Silver fights,
  Kanto trainers, rematches, and Red after builds are possible.
- Confirm Phase 7's regular-trainer curve in map order and tune any local
  difficulty spikes found during playtesting.
- Runtime-test random legendary surprise encounters after builds are possible, including Repel,
  Safari exclusion, built-in roamer coexistence, levels, and badge-gated pools.
- Treat any interactive web-app explorer as a future separate project that
  consumes the structured exports, not as part of this ROM hack release.
