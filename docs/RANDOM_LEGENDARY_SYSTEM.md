# Random Legendary System

The random legendary surprise overlay is a repeatable low-rate wild encounter system. It is separate from proper legendary/mythical access through native roamers and Saffron Fighting Dojo dossiers.

## References

- Export: `exports/perfect_johto/random_legendary_surprise.json`.
- Proper legendary access: `docs/LEGENDARIES.md`.
- Encounter system overview: `docs/ENCOUNTER_SYSTEMS.md`.
- Implementation hook: `hg-engine-main/hg-engine-main/src/field/enemy_party.c`.

## Trigger Flow

- The overlay runs from `AddWildPartyPokemon` after normal wild encounter generation succeeds.
- Because it runs after the normal encounter flow, Repel behavior is preserved by the existing encounter system.
- The selected legendary/mythical is started as a normal wild battle.
- The system does not write to roamer save state.
- Surprise legendaries receive Teleport in move slot 4, giving the wild AI a move-based chance to flee each turn.

## Rates

- 0-3 badges: disabled.
- 4+ badges: 1/2000 aggregate unlocked weaker/mystical legendary pool roll.
- 6+ badges when true-tier species are unlocked: 1/4000 aggregate unlocked stronger true/cover-story legendary pool roll.

These rates are aggregate tier rolls, not independent rolls per legendary. After a tier roll succeeds, one species is selected from the currently unlocked matching tier.

## Exclusions

- `BATTLE_TYPE_TRAINER`.
- `BATTLE_TYPE_SAFARI`.
- `BATTLE_TYPE_ROAMER`.
- `BATTLE_TYPE_PAL_PARK`.
- `BATTLE_TYPE_CATCHING_DEMO`.
- `BATTLE_TYPE_BUG_CONTEST`.

## Validation And Testing

Static validation checks the pool, rates, badge gates, excluded battle types, and approved Gen 1-4 legendary/mythical scope. Runtime testing is still required for Repel behavior, Safari exclusion, native roamer coexistence, level scaling, and badge-gated pools.
