# Legendaries

This doc covers proper Gen 1-4 legendary and mythical access. The separate
repeatable random legendary surprise system is documented in
`docs/RANDOM_LEGENDARY_SYSTEM.md`.

## References

- Proper event export: `exports/perfect_johto/proper_legendary_events.json`.
- Phase 8 report: `docs/phase8_postgame_report.md`.
- Kanto postgame hub: `docs/KANTO_POSTGAME.md`.
- Champion Circuit: `docs/CHAMPION_CIRCUIT.md`.

## Access Layers

- Raikou and Entei remain native Burned Tower roamers.
- All other Gen 1-4 legendary/mythical access is handled through Saffron
  Fighting Dojo dossier encounters unless already covered by native flow.
- Dossier battles are scripted/static encounters.
- Static encounter outcome `4` is used so caught flags are set only on capture.
- Failed, fled, or fainted dossier battles remain retryable by script logic.
- Latias and Latios use Phase 8 dossier flags separate from native roamer state.

## Current Audit

- Native entries: 2.
- Dojo dossier entries: 33.
- Phase 8 validates 35/35 Gen 1-4 legendary/mythical coverage including native
  Raikou and Entei.

## Major Prerequisite Chains

- Regirock, Regice, and Registeel before Regigigas.
- Kyogre and Groudon before Rayquaza.
- Cresselia before Darkrai.
- Manaphy before Phione.
- Red defeated, lake trio caught, and creation trio caught before Arceus.

## Runtime Focus

Runtime testing should verify Dojo menus, caught flags, retry behavior,
Latias/Latios duplicate-access edge cases, native roamer coexistence, and
prerequisite chains.
