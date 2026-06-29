# Wild Encounters

Wild encounters are generated from `data/Encounters.c` and summarized in `exports/perfect_johto/wild_encounters.json`.

Main land encounters use a shared daytime pool: the engine-facing morning and day arrays are kept identical, while night remains separate.

Static validation confirms Phase 6 encounter structure, approved-scope species use, late-Johto and Kanto level raises, Kanto/postgame starter rare access, separate six-species minimums for land/cave pools and surf/fishing pools, Gen 3-4 non-starter Johto-main base-form coverage, and rare-slot coverage. Non-rare low-rate land, surf, and rod filler slots duplicate normal common species so ordinary Pokemon do not appear as separate wiki rare finds. See `docs/phase6_obtainability_report.md` for the detailed area list.
