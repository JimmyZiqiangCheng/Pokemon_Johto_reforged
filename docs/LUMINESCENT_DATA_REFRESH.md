# Luminescent Data Refresh

Last updated: 2026-06-29

This note documents the Luminescent Platinum data pass for Gen 1-4 Pokemon
identity data.

## Source Priority

- Primary source: Luminescent Platinum 3.0 game data.
- Secondary design references: Renegade Platinum and Polished Crystal. These
  inform the broader philosophy of stronger identity, expanded viable roles,
  and modern mechanics, but they do not override Luminescent values in this
  pass.

## Source Files

- Luminescent personal data:
  https://raw.githubusercontent.com/TeamLumi/luminescent-team/main/__3.0gamedata/PersonalTable.json
- Luminescent level-up learnsets:
  https://raw.githubusercontent.com/TeamLumi/luminescent-team/main/__3.0gamedata/WazaOboeTable.json
- Luminescent move-name text:
  https://raw.githubusercontent.com/TeamLumi/luminescent-team/main/__3.0gamedata/english_ss_wazaname.json

## Scope

- Updated 493 base species rows from Bulbasaur through Arceus.
- Updated 18 relevant native Gen 3-4 form rows: Deoxys Attack/Defense/Speed,
  Wormadam Sandy/Trash, Giratina Origin, Shaymin Sky, Rotom Heat/Wash/Frost/Fan/Mow,
  Castform Sunny/Rainy/Snowy, Cherrim Sunshine, Shellos East Sea, and Gastrodon
  East Sea.
- Updated base stats only: HP, Attack, Defense, Special Attack, Special Defense,
  and Speed.
- Appended missing Luminescent level-up moves only. Existing local level-up
  extras are intentionally preserved.
- Created seven missing form learnset rows so the target form scope is complete:
  `SPECIES_500`, `SPECIES_CASTFORM_SUNNY`, `SPECIES_CASTFORM_RAINY`,
  `SPECIES_CASTFORM_SNOWY`, `SPECIES_CHERRIM_SUNSHINE`,
  `SPECIES_SHELLOS_EAST_SEA`, and `SPECIES_GASTRODON_EAST_SEA`.

## Mapping Rules

- Form rows use each Luminescent base row's `form_index` and form offset.
- Luminescent `WazaOboeTable` level-up data is read as `[level, move_id]` pairs.
- Level `0` entries are kept as level `0` because this engine already supports
  them for evolution/reminder-style moves.
- Luminescent move IDs are not mapped directly to local numeric constants after
  Gen 4. Instead, each Luminescent move ID is resolved through
  `english_ss_wazaname.json`, normalized to a local `MOVE_*` name, and then
  checked against `include/constants/moves.h`.
- The only spelling alias required in the target set is Luminescent "Vise Grip"
  to local `MOVE_VICE_GRIP`.

## Audit Results

- Stat targets: 511.
- Stat mismatches after update: 0.
- Learnset targets: 511.
- Missing Luminescent level-up moves after update: 0.
- Missing local move constants for target Luminescent learnsets: 0.
- Example sanity check: Butterfree now has `60/45/45/110/100/90` base stats,
  for a 450 base stat total.

## Not Changed

- TM, tutor, item, catch rate, EV yield, type, encounter, and evolution data
  were not changed by this pass unless already handled elsewhere. Egg moves
  are mirrored into level-up learnsets by the separate learnset accessibility
  pass documented in `docs/LEARNSET_ACCESSIBILITY.md`.
- Later-generation Pokemon outside the approved project scope were not imported.
