# QOL Features

This doc tracks quality-of-life features that are enabled, added, or explicitly
deferred.

## Implemented Or Preserved

- Running from the beginning: Mom gives the Running Shoes in the initial home
  conversation.
- Cherrygrove Guide Gent skip: if the player already has Running Shoes, the
  Guide skips the forced walking tour while preserving the later Map Card
  callback.
- Fast text is enabled globally through `FAST_TEXT_PRINTING`.
- HMs are deletable through `DELETABLE_HMS`.
- TMs are reusable through existing HG-Engine configuration.
- Reusable Repels are preserved.
- Capture EXP and critical captures are preserved.
- EV/IV viewer and nature indicators are enabled.
- Expanded PC boxes are preserved.
- Updated vitamin EV caps are preserved.
- Hidden Abilities are enabled.
- Overworld poison damage is disabled.
- Max Candy and IV stat candies are party-use convenience items.
- Mints, Ability Capsule, Ability Patch, EV training items, IV stat candies, and
  evolution items are progressively available through the standard badge mart.

## Deferred

- AutoRun/toggle-run as an input-mode feature. Running from the start is handled
  through early Running Shoes, but automatic running remains separate.
- Fast Surf.
- Field moves without teaching the HM move.
- Optional QOL/settings NPC.

## References

- Game mode rules: `docs/GAME_MODES.md`.
- Item and mart economy: `docs/ITEMS_AND_MARTS.md`.
- Release/runtime status: `docs/KNOWN_LIMITATIONS.md`.

Runtime playtesting is still required for each QOL feature in a built ROM.
