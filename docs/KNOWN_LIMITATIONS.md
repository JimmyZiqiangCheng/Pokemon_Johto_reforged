# Known Limitations

## Build And Tooling

- Full ROM build is not confirmed in the current PowerShell environment because
  Git, Make, CMake, armips, Docker, and the ARM toolchain are missing on `PATH`.
- `hg-engine-main/hg-engine-main/rom.nds` is present locally, but must never be
  committed or redistributed.
- `pokeheartgold-master/baserom.nds` is missing.
- Dojo script assembly is static-validation-only when `armips` is unavailable.

## Runtime Testing

- Runtime behavior has not been fully playtested; use
  `docs/PLAYTEST_CHECKLIST.md`.
- Game mode rules need runtime testing across Oak intro, battles, item use,
  gifts, static encounters, save/reload, and Nuzlocke route claims.
- Trainer curve, boss teams, Rocket/Silver fights, rematches, Red, Champion
  Circuit unlocks, Dojo retries, and legendary/mythical caught flags need
  runtime testing.
- Random legendary surprise encounters need runtime testing for Repel behavior,
  Safari exclusion, native roamer coexistence, level scaling, and badge-gated
  pools.

## Data And Content

- Pokedex area data may need regeneration; this is a release blocker/TODO until
  engine behavior is confirmed.
- Latias/Latios dossier flags are separate from native roamer state and need
  duplicate-access edge-case testing.
- Approved regional/new form display text, naming, form handling, and evolution
  behavior need runtime and player-facing polish.

## Project Scope

- The web-app explorer remains a future separate project and is not part of this
  ROM hack phase.
- HG-Engine contains unused later-generation capacity; gameplay exposure must
  stay inside `docs/PROJECT_SCOPE.md`.
