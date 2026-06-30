# Type And Learnset Changes

This doc covers type modernization, level-up attacking STAB support, and
project-wide learnset cleanup rules. For the broader Pokemon-data overview, see
`docs/POKEMON_DATA.md`.

## Type Modernization Policy

- Type changes are restrained and species-identity driven.
- No type chart change has been made.
- Type changes do not by themselves change base stats, evolution methods,
  encounter scope, catch rates, EV yields, held items, or growth data.
- Custom or modernized typings are audited so project-added secondary types have
  reasonable level-up attacking move access.

## Type Change List

Phase 4 Polished Crystal-priority Gen 1-2 changes:

| Pokemon | Old type | New type |
| --- | --- | --- |
| Charizard | Fire/Flying | Fire/Dragon |
| Blastoise | Water | Water/Steel |
| Butterfree | Bug/Flying | Bug/Psychic |
| Golduck | Water | Water/Psychic |
| Rapidash | Fire | Fire/Fairy |
| Meganium | Grass | Grass/Fairy |
| Typhlosion | Fire | Fire/Ground |
| Feraligatr | Water | Water/Dark |
| Noctowl | Normal/Flying | Ghost/Flying |
| Ledian | Bug/Flying | Bug/Fighting |
| Ariados | Bug/Poison | Bug/Dark |
| Ampharos | Electric | Electric/Dragon |
| Bellossom | Grass | Grass/Fairy |
| Politoed | Water | Water/Grass |
| Sunflora | Grass | Grass/Fire |
| Dunsparce | Normal | Normal/Ground |
| Girafarig | Normal/Psychic | Psychic/Dark |
| Octillery | Water | Water/Fire |
| Stantler | Normal | Normal/Psychic |
| Ninetales | Fire | Fire/Ghost |

Phase 4 Gen 3-4 inspired changes:

| Pokemon | Old type | New type |
| --- | --- | --- |
| Sceptile | Grass | Grass/Dragon |
| Masquerain | Bug/Flying | Bug/Water |
| Volbeat | Bug | Bug/Electric |
| Illumise | Bug | Bug/Fairy |
| Trapinch | Ground | Bug/Ground |
| Vibrava | Ground/Dragon | Bug/Dragon |
| Flygon | Ground/Dragon | Bug/Dragon |
| Swablu | Normal/Flying | Fairy/Flying |
| Altaria | Dragon/Flying | Dragon/Fairy |
| Seviper | Poison | Poison/Dark |
| Milotic | Water | Water/Fairy |
| Glalie | Ice | Ice/Rock |
| Luvdisc | Water | Water/Fairy |
| Misdreavus | Ghost | Ghost/Fairy |
| Mismagius | Ghost | Ghost/Fairy |
| Luxray | Electric | Electric/Dark |
| Lopunny | Normal | Normal/Fighting |
| Electivire | Electric | Electric/Fighting |

Later Gen 3-4 semantic additions:

| Pokemon | New type |
| --- | --- |
| Chingling and Chimecho | Psychic/Fairy |
| Huntail | Water/Dark |
| Gorebyss | Water/Psychic |
| Cranidos and Rampardos | Rock/Dragon |
| Carnivine | Grass/Dark |
| Finneon and Lumineon | Water/Fairy |

## Level-Up STAB Support

The following lines now have direct level-up attack support for an added or
previously unsupported type:

- Fairy support: Meganium, Rapidash, Azurill, Misdreavus, Mismagius, Chingling,
  Chimecho, Togetic, Finneon, and Lumineon.
- Dragon support: Sceptile, Cranidos, and Rampardos.
- Bug support: Surskit, Nincada, Shedinja, and Trapinch.
- Electric support: Volbeat.
- Rock support: Glalie.
- Ground support: Typhlosion, Gligar, and Gliscor.
- Steel support: Probopass.
- Ghost support: Ninetales and Noctowl.
- Grass support: Politoed.
- Fire support: Sunflora and Octillery.
- Ice support: Delibird.

Huntail, Gorebyss, and Carnivine already had appropriate Dark/Psychic/Dark
level-up attacks after their type changes and did not need extra moves.

Remaining no-level-up attacking STAB cases are canonical or status-oriented
exceptions such as the Bulbasaur, Gastly, and Budew poison lines, plus Beldum's
one-move identity. No project-added custom secondary type is intentionally left
without a level-up attacking move.

## Learnset Rules

- Phase 4 updated approved-scope level-up learnsets only. Machine, tutor, and
  egg move lists were not intentionally changed in that pass.
- Evolved forms inherit earlier-form level-up moves more consistently.
- Duplicate level-up move entries are removed, keeping the earliest occurrence.
- Non-legendary level-up moves are compressed below level 60.
- Legendary, mythical, Ultra Beast, and comparable special one-off Pokemon keep
  their late signature pacing.
- Egg moves are also level-up accessible for every Pokemon that has egg moves.

## Notable Learnset Access Changes

- Stantler learns `Psyshield Bash` at level 32 so Wyrdeer has a reachable
  known-move evolution method.
- Galarian Farfetch'd learns `Leaf Blade` at level 35 so Sirfetch'd has a
  reachable known-move evolution method before late game.
- Missing Luminescent Platinum 3.0 level-up moves are appended at their
  Luminescent levels while preserving local extras.
- Luminescent move IDs are resolved through Luminescent move-name text before
  mapping to local `MOVE_*` constants.

## Validation

`tools/perfect_johto/validate_project.py` validates learnset JSON parsing,
learnset generation, no duplicate level-up moves after cleanup, no
non-legendary level 60+ moves after compression, and egg-move coverage through
level-up learnsets.
