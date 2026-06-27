# Random Legendary System

The random legendary surprise overlay is implemented in `src/field/enemy_party.c` from `AddWildPartyPokemon` after normal wild encounter generation succeeds.

## Rates

- 0-3 badges: disabled
- 4 badges: 1/4096
- 5 badges: 1/3072
- 6-7 badges: 1/2048
- 8-15 badges: 1/1536
- 16 badges: 1/1024

## Exclusions

- BATTLE_TYPE_TRAINER
- BATTLE_TYPE_SAFARI
- BATTLE_TYPE_ROAMER
- BATTLE_TYPE_PAL_PARK
- BATTLE_TYPE_CATCHING_DEMO
- BATTLE_TYPE_BUG_CONTEST

The system uses normal wild battles, does not write to roamer save state, and respects Repel through the pre-existing normal encounter flow. Runtime testing is still required.
