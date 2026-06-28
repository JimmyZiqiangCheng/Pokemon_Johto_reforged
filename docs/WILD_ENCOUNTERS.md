# Wild Encounters

Wild encounters are generated from `data/Encounters.c` and summarized in `exports/perfect_johto/wild_encounters.json`.

Main land encounters use a shared daytime pool: the engine-facing morning and day arrays are kept identical, while night remains separate.

Static validation confirms Phase 6 encounter structure, approved-scope species use, late-Johto and Kanto level raises, starter late/postgame access, six-species minimum area variety, Gen 3-4 Johto-main base-form coverage, and rare-slot coverage. See `docs/phase6_obtainability_report.md` for the detailed area list.
