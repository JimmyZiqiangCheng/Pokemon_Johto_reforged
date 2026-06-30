# Game Modes

Game modes are selected immediately after choosing New Game, before Professor Oak's speech. The selector uses two pages:

- Page 1: Normal, Challenge, More.
- Page 2: Hardcore, Nuzlocke, Back.

## References

- Implementation header: `hg-engine-main/hg-engine-main/include/perfect_johto_game_modes.h`.
- Implementation source: `hg-engine-main/hg-engine-main/src/perfect_johto_game_modes.c`.
- Oak intro integration: `hg-engine-main/hg-engine-main/src/field/script_commands.c`.
- Wild/gift/static encounter interaction: `docs/ENCOUNTER_SYSTEMS.md`.
- Playtest checklist: `docs/PLAYTEST_CHECKLIST.md`.

## Modes

| Mode | Rules |
| --- | --- |
| Normal | Current Pokemon Johto Reforged QOL and balance, with no enforced level caps. |
| Challenge | Normal plus dynamic level caps, forced Set battle style, and no player Bag item use in trainer battles. |
| Hardcore | Challenge plus fainted non-Egg party Pokemon are released/deleted after battle. The last non-Egg party Pokemon is never released by this rule. |
| Nuzlocke | Hardcore plus enforced first encounter/gift/static claim per map section. Optional rules, such as retiring Pokemon after a Gym run, are left to the player. |

## Level Caps

Level caps are enabled only in Challenge, Hardcore, and Nuzlocke. Pokemon at the cap no longer gain battle EXP, and Rare Candy level-up is also blocked by the cap.

| Progress | Cap |
| --- | ---: |
| Before Falkner | 16 |
| Before Bugsy | 22 |
| Before Whitney | 27 |
| Before Morty | 33 |
| Before all of Chuck/Jasmine/Pryce are cleared | 45 |
| Before Clair | 52 |
| After Clair, before first Elite Four clear | 62 |
| Kanto before Lt. Surge | 65 |
| Kanto before Brock | 66 |
| Kanto before Janine | 66 |
| Kanto before Misty | 68 |
| Kanto before Erika | 70 |
| Kanto before Sabrina | 74 |
| Kanto before Blaine | 78 |
| Kanto before Blue | 84 |
| After all 16 badges | 98 |

## Nuzlocke Enforcement

- Wild encounters claim the current map section when generated.
- Catch attempts are legal only for the currently claimed encounter area; illegal catches fail at the ball-shake stage.
- Gift and egg Pokemon claim the current map section before being awarded.
- Starter selection claims the starter's current map section but is never blocked.
- Static encounters are covered when they use the standard wild encounter or gift creation paths.

## Implementation Notes

- Game mode is stored in `VAR_PERFECT_JOHTO_GAME_MODE` (`0x416E`).
- Current legal Nuzlocke battle area is stored in `VAR_PERFECT_JOHTO_NUZLOCKE_LEGAL_AREA` (`0x416D`).
- Current level cap is mirrored in `VAR_PERFECT_JOHTO_LEVEL_CAP` (`0x416F`).
- Claimed Nuzlocke areas are stored as a bitset in `SAVE_MISC_DATA`.
- The Oak speech tutorial menu in overlay 53 is repurposed for mode selection.

## Playtest Focus

- Verify every mode can be selected from New Game and Oak's speech continues.
- Verify EXP and Rare Candy stop at cap in Challenge or harder modes.
- Verify Set mode is forced in Challenge or harder modes.
- Verify trainer-battle Bag items are blocked while wild battle capture remains possible.
- Verify Hardcore and Nuzlocke release fainted Pokemon after battle while preserving the last non-Egg party Pokemon.
- Verify Nuzlocke wild, gift, egg, starter, and static encounters claim areas as expected.
