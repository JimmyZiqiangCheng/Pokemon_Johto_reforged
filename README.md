# Pokemon Johto Reforged

Pokemon Johto Reforged is a Pokemon HeartGold-based ROM hack project built on
HG-Engine. The goal is a fuller Johto/HGSS experience with all Generation 1-4
Pokemon obtainable in one save file, approved later-generation family
evolutions/forms where they fit cleanly, stronger trainer progression, a more
meaningful Kanto postgame, and HGSS-style quality-of-life improvements.

No ROMs, pre-patched ROMs, or copyrighted ROM data are included in this
repository. Building requires a legally obtained US Pokemon HeartGold ROM named
`rom.nds` placed at `hg-engine-main/hg-engine-main/rom.nds`.

## Current Status

- Static validation and generated documentation are complete.
- Full ROM build, script assembly, and runtime playtesting are still blocked on
  missing local build tooling and the required local ROM input.
- Known release risks are tracked in `docs/KNOWN_LIMITATIONS.md`.

## Project Layout

- `hg-engine-main/hg-engine-main/`: primary HG-Engine source tree modified for
  Pokemon Johto Reforged.
- `pokeheartgold-master/`: Pokemon HeartGold/SoulSilver disassembly/reference
  tree used for base HGSS structure and context.
- `tools/perfect_johto/`: project-specific validation, encounter, trainer, and
  postgame generation tools. The folder name is historical/internal tooling and
  does not change the public project name.
- `exports/perfect_johto/`: generated JSON exports for auditability and future
  explorer tooling.
- `docs/`: generated project documentation, release checklists, and gameplay
  summaries.
- `FEATURES_AND_CHANGES.md`: detailed project ledger.

## Major Features

- One-save obtainability plan for all Generation 1-4 Pokemon.
- Approved later direct evolutions, regional forms, and new forms for Gen 1-4
  families only.
- No Mega Evolution, Primal Reversion, Z-Moves, Dynamax/Gigantamax,
  Terastalization, or unrelated Gen 5+ Pokemon exposure.
- Reusable TMs, deletable HMs, fast text, reusable Repels, EV/IV viewing, Hidden
  Abilities, expanded PC boxes, and updated vitamin EV caps.
- Badge-gated mart upgrades, IV stat candies, and Max Candy.
- Rebuilt wild encounters, rare encounters, starter access, and Kanto wild
  levels.
- Expanded trainer rosters, six-Pokemon boss teams, rematches, and a stronger
  level curve.
- Saffron Fighting Dojo postgame hub with Champion Circuit battles and
  legendary/mythical dossier encounters.
- Aggregate 1% random legendary surprise encounters with badge-gated pools.

## Validation

Run static validation from the repository root:

```powershell
python tools/perfect_johto/validate_project.py
```

Regenerate static exports and generated docs:

```powershell
python tools/perfect_johto/validate_project.py --write
```

## Build Notes

The intended HG-Engine build route is from `hg-engine-main/hg-engine-main/`.
Once Docker and the local ROM input are available:

```powershell
docker build . -t hg-engine
.\docker-makerom.cmd
```

Native builds require Git, GNU Make, CMake, Python 3, `armips`, the expected ARM
toolchain, and any HG-Engine Makefile dependencies. WSL or MSYS2 is likely
cleaner than raw PowerShell for native Makefile work.

## Credits And Acknowledgements

Pokemon Johto Reforged depends on and/or was developed with reference to:

- HG-Engine, the primary engine and ROM-hacking source base for this project.
- The Pokemon HeartGold/SoulSilver disassembly/reference work represented here
  by `pokeheartgold-master`.
- Sacred Gold & Storm Silver, used as local HGSS ROM hack reference material for
  roster, evolution, item, and event-design context.
- Polished Crystal, used as local reference material for restrained Pokemon
  modernization ideas.
- Heart & Soul, used as local Johto/HGSS compatibility and structure reference
  material.

Additional acknowledgement: my first ROM hack practice was based on PokeClassic
and Pokemon Rekindled. They did not directly contribute code or assets to
Pokemon Johto Reforged, but I would not be here without practicing on them.

Pokemon is owned by Nintendo, Game Freak, and The Pokemon Company. This is an
unofficial fan project and does not include or distribute commercial ROM data.
