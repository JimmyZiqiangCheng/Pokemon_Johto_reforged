# Trainer Teams

Trainer teams are exported from `hg-engine-main/hg-engine-main/data/Trainers.c`.

## References

- Full export: `exports/perfect_johto/trainer_teams.json`.
- Boss export: `exports/perfect_johto/boss_battles.json`.
- Level curve export: `exports/perfect_johto/level_curve.json`.
- Phase 7 report: `docs/phase7_trainer_report.md`.
- Boss battle summary: `docs/BOSS_BATTLES.md`.
- Champion Circuit: `docs/CHAMPION_CIRCUIT.md`.

## Source Files

- Trainer source: `hg-engine-main/hg-engine-main/data/Trainers.c`.
- Trainer generation/validation tool:
  `tools/perfect_johto/phase7_trainer_tools.py`.
- Master validation/export runner:
  `tools/perfect_johto/validate_project.py`.

## Change Summary

- Gym Leaders, Elite Four, Champions, Red, and other major bosses use full
  six-Pokemon teams.
- First-clear Johto leaders progress from Falkner 13-14 through Clair 46-50.
- First Elite Four and Champion progress from Will 50-54 through Lance 58-60.
- Kanto leaders were raised into the post-League curve, ending with Blue 78-82.
- Gym Leader rematches, Elite Four rematches, Lance rematches, Red, and
  Champion Circuit battles were raised for late-postgame play.
- Major Silver, Team Rocket Executive, and Giovanni/Rocket Boss records were
  expanded where their story role and level band support it.
- Regular trainers received a controlled level pass and semantic Gen 3-4 variety
  replacements without turning every route trainer into a boss.

## Regular Trainer Rules

- Regular trainer party sizes are not broadly inflated.
- The variety pass replaces one to two ordinary species on no-custom-move
  non-boss trainers with semantic Gen 3-4 alternatives.
- The pass covers roadside trainers, gym non-leaders, Team Rocket grunts,
  swimmers, hikers, psychics, and similar regular classes.
- Non-boss regular trainers are intentionally below the late boss/rematch
  ceiling.

## Scope And Validation

Static validation checks trainer species, moves, items, ability slots, approved
Pokemon scope, regular-trainer Gen 3-4 variety, major rival/Rocket sizes, and
mandatory six-Pokemon boss rules.

The Phase 7 curve was re-audited after the regular-trainer variety pass. Boss
and route bands still progress smoothly from early Johto through Red; no
additional trainer-level raise was needed for the latest encounter/type/learnset
update.
