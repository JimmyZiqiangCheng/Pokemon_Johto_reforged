# Evolutions

Evolution data is exported from `hg-engine-main/hg-engine-main/data/Evolutions.c`.

## References

- Full export: `exports/perfect_johto/evolutions.json`.
- Trade replacement export:
  `exports/perfect_johto/trade_evolution_replacements.json`.
- Required item access: `docs/ITEMS_AND_MARTS.md`.
- Learnset prerequisites: `docs/TYPE_AND_LEARNSET_CHANGES.md` and
  `docs/LEARNSET_ACCESSIBILITY.md`.

## Design Rules

- All approved-scope Pokemon should be evolvable in one save file without
  trading.
- Existing item-use methods are preferred when they are clear and HGSS-friendly.
- Known-move methods are used when they better match the later official
  evolution identity.
- Required approved-scope evolution items are made repeatably available through
  the badge-gated standard mart.
- Unrelated later-generation families remain out of scope even if their
  evolution items or constants exist in HG-Engine.

## Trade-Only Replacements

These approved-scope trade-only lines use the Linking Cord item where the engine
already supports a non-trade replacement:

- Kadabra -> Alakazam.
- Machoke -> Machamp.
- Graveler -> Golem.
- Alolan Graveler -> Alolan Golem.
- Haunter -> Gengar.

## Trade-With-Item Replacements

These trade-with-item evolutions were converted into direct item-use evolutions:

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
- Feebas -> Milotic with Prism Scale, alongside beauty evolution.
- Dusclops -> Dusknoir with Reaper Cloth.
- Clamperl -> Huntail with Deep Sea Tooth.
- Clamperl -> Gorebyss with Deep Sea Scale.

## Known-Move Replacements

- Stantler -> Wyrdeer by leveling while knowing `Psyshield Bash`.
- Primeape -> Annihilape by leveling while knowing `Rage Fist`.
- Galarian Farfetch'd -> Sirfetch'd by leveling while knowing `Leaf Blade`.

## Special Form Access

- Dudunsparce Three-Segment evolves from Dudunsparce by level-up at 50.
- Ursaluna Bloodmoon evolves from Ursaluna by level-up at 55.

These are simple access methods for special forms already present in local data.
Runtime testing still needs to confirm form display, naming, and evolution
behavior.

## Validation

Static validation checks that no approved-scope trade-only evolutions remain,
that species/move/item constants resolve, that required evolution items are
available through the badge mart, and that known-move methods have reasonable
learnset access.
