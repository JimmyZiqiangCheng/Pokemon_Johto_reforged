# Kanto Postgame

The Kanto postgame is centered on the Saffron Fighting Dojo after all 16 badges. The hub provides Champion Circuit battles and legendary/mythical dossier encounters while preserving visible Gym Leader rematch scripts.

## References

- Phase 8 report: `docs/phase8_postgame_report.md`.
- Legendary access: `docs/LEGENDARIES.md`.
- Champion Circuit: `docs/CHAMPION_CIRCUIT.md`.
- Boss battles: `docs/BOSS_BATTLES.md`.
- Kanto postgame export: `exports/perfect_johto/kanto_postgame.json`.

## Hub Behavior

- The Dojo karate master becomes the postgame hub after all 16 badges.
- Existing 16 Gym Leader phone-rematch scripts remain intact and still use the visible leader NPCs.
- Lance and Blue are repeatable from the Champion Circuit after 16 badges.
- Red rematch, Steven, Wallace, Cynthia, and Arceus unlock after the original Mt. Silver Red defeat flag.
- Latias and Latios use Phase 8 dossier flags separate from native roamer state.

## Related Progression

- Kanto wild levels were raised so post-League routes and caves are no longer vanilla low-level filler.
- Kanto Gym Leaders were raised into the post-League trainer curve, with Blue at 78-82.
- Gym Leader rematches, Elite Four rematches, Red, and Champion Circuit battles form the late-postgame challenge path.

## Runtime Focus

Runtime testing must check Dojo menu flow, Champion Circuit unlocks, legendary prerequisites, caught flags, retry behavior, Latias/Latios duplicate-access edge cases, and visible rematch NPC preservation.
