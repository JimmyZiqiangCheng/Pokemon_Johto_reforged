# Random Legendary System

The random legendary surprise overlay is implemented in `src/field/enemy_party.c` from `AddWildPartyPokemon` after normal wild encounter generation succeeds.

## Rates

- 0-3 badges: disabled
- 4+ badges: 1/100 aggregate unlocked-pool roll

The 1/100 rate is an aggregate overlay roll, not one independent roll per legendary. After the roll succeeds, one species is selected from the currently unlocked pool.

Surprise legendaries receive Teleport in move slot 4, giving the wild AI a move-based chance to flee each turn.

## Exclusions

- BATTLE_TYPE_TRAINER
- BATTLE_TYPE_SAFARI
- BATTLE_TYPE_ROAMER
- BATTLE_TYPE_PAL_PARK
- BATTLE_TYPE_CATCHING_DEMO
- BATTLE_TYPE_BUG_CONTEST

The system uses normal wild battles, does not write to roamer save state, and respects Repel through the pre-existing normal encounter flow. Runtime testing is still required.
