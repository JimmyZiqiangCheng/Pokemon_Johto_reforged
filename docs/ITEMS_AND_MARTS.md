# Items And Marts

This doc covers the badge-gated mart economy, customization items, IV candies,
Max Candy, and evolution-item access.

## References

- Badge mart export: `exports/perfect_johto/items_and_marts.json`.
- Customization export: `exports/perfect_johto/customization_items.json`.
- Max Candy export: `exports/perfect_johto/max_candy.json`.
- Evolution methods: `docs/EVOLUTIONS.md`.
- QOL summary: `docs/QOL_FEATURES.md`.

## Source Files

- Badge mart source: `hg-engine-main/hg-engine-main/src/field/mart.c`.
- Item data: `hg-engine-main/hg-engine-main/data/itemdata/itemdata.c`.
- Item constants: `hg-engine-main/hg-engine-main/include/constants/item.h`.
- Party-use behavior:
  `hg-engine-main/hg-engine-main/src/individual/PartyMenu_HandleUseItemOnMon.c`.
- Item text archives: `hg-engine-main/hg-engine-main/data/text/222.txt` and
  related text archives.

## Badge Mart Summary

- Badge mart entries: 104 / 203 UI limit.
- 0-2 badges: core balls, medicine, status heals, Escape Rope, and Repels.
- 3 badges: EV feathers, EV-reduction berries, all available mints, and Ability
  Capsule.
- 4 badges: EV vitamins, common stones, Oval Stone, and Linking Cord.
- 5 badges: IV stat candies, Macho Brace, Power items, and trade-item
  replacements.
- 6 badges: Ability Patch and broad modern evolution items, including Black
  Augurite, Peat Block, Galarica Cuff, and Galarica Wreath.
- 12 badges: Max Candy.

## Prices And Effects

- Max Candy costs 8000, unlocks at 12 badges, and sets all six IVs to 31.
- Health, Mighty, Tough, Smart, Courage, and Quick Candy cost 2000, unlock at 5
  badges, and set one matching IV to 31.
- Mints and Ability Capsule/Patch cost 1000 with their intended badge gates.
- Vitamins and Power items cost 3000.
- Feathers cost 300.
- EV-reduction berries cost 200.
- Approved-scope evolution items are stocked through the badge mart.

## Restrictions

- Forbidden gimmick items are not stocked in the badge mart.
- Unrelated later-family evolution items are not exposed unless needed by an
  approved Gen 1-4 family exception.
- Trainer-battle held-item restoration remains out of scope.
