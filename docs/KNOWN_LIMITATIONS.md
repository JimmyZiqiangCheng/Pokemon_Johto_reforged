# Known Limitations

- Full ROM build not confirmed locally: blocked until build tools and legal rom.nds are present
- Dojo script not assembled locally if armips is missing: static script validation only
- Runtime behavior not playtested: use docs/PLAYTEST_CHECKLIST.md
- Game mode rules are statically wired but still need runtime playtesting across Oak intro, battles, item use, gifts, static encounters, and save/reload.
- Pokedex area data may need regeneration: release blocker/TODO until engine behavior is confirmed
- Latias/Latios dossier flags are separate from native roamer state: manual duplicate-access edge-case testing required
- Dudunsparce Three-Segment and Ursaluna Bloodmoon special form access: not implemented; documented limitation
- Approved regional/new form display text: needs runtime and player-facing polish pass
- Web-app explorer: future separate project; not part of this ROM hack phase

Static validation is strong enough for audit readiness, but the ROM has not been proven buildable or runtime-stable on this machine while required tools and `rom.nds` are missing.
