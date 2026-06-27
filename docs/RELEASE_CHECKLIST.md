# Release Checklist

## Static Validations

- Run `python tools/perfect_johto/validate_project.py`.
- Confirm Phase 6, Phase 7, and Phase 8 validators pass.
- Confirm trainer source validation passes.
- Confirm text archive validation passes.
- Confirm forbidden config/gimmick and approved-scope scans pass.

## Build Commands

- Place a legally obtained US HeartGold ROM at `hg-engine-main/hg-engine-main/rom.nds`.
- Docker route: `docker build . -t hg-engine`, then `docker-makerom.cmd`.
- Native route: install Git, GNU Make, CMake, `armips`, and the ARM toolchain, then run `make -n` and the normal HG-Engine build.

## Manual Runtime Tests

- Complete the milestones in `PLAYTEST_CHECKLIST.md`.
- Confirm Dojo script assembly and in-game Dojo menus.
- Confirm random legendary rates/exclusions by controlled test saves where possible.
- Confirm Pokedex area behavior or regenerate area data.

## Must Not Commit Or Redistribute

- `rom.nds`
- `baserom.nds`
- Pre-patched ROMs
- Copyrighted ROM data

Preserve credits and attribution. The web-app explorer is a future separate project, not part of this ROM hack release.
