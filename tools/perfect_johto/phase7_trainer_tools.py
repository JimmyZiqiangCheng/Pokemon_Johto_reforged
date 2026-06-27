#!/usr/bin/env python3
"""Phase 7 trainer roster and level-curve tooling for Pokemon Johto Reforged."""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import re
from collections import Counter, defaultdict


ROOT = pathlib.Path(__file__).resolve().parents[2]
ENGINE = ROOT / "hg-engine-main" / "hg-engine-main"
TRAINERS = ENGINE / "data" / "Trainers.c"
REPORT = ROOT / "docs" / "phase7_trainer_report.md"

TRAINER_TYPE_BOSS = "TRAINER_DATA_TYPE_MOVES | TRAINER_DATA_TYPE_ITEMS"
AI_EXPERT = "F_PRIORITIZE_SUPER_EFFECTIVE | F_EVALUATE_ATTACKS | F_EXPERT_ATTACKS"
AI_EXPERT_DAMAGE = AI_EXPERT + " | F_PRIORITIZE_DAMAGE"
AI_EXPERT_WEATHER = AI_EXPERT + " | F_USE_WEATHER"

APPROVED_LATER_SPECIES = {
    "SPECIES_RATTATA_ALOLAN",
    "SPECIES_RATICATE_ALOLAN",
    "SPECIES_RAICHU_ALOLAN",
    "SPECIES_SANDSHREW_ALOLAN",
    "SPECIES_SANDSLASH_ALOLAN",
    "SPECIES_VULPIX_ALOLAN",
    "SPECIES_NINETALES_ALOLAN",
    "SPECIES_DIGLETT_ALOLAN",
    "SPECIES_DUGTRIO_ALOLAN",
    "SPECIES_MEOWTH_ALOLAN",
    "SPECIES_PERSIAN_ALOLAN",
    "SPECIES_GEODUDE_ALOLAN",
    "SPECIES_GRAVELER_ALOLAN",
    "SPECIES_GOLEM_ALOLAN",
    "SPECIES_GRIMER_ALOLAN",
    "SPECIES_MUK_ALOLAN",
    "SPECIES_EXEGGUTOR_ALOLAN",
    "SPECIES_MAROWAK_ALOLAN",
    "SPECIES_MEOWTH_GALARIAN",
    "SPECIES_PERRSERKER",
    "SPECIES_PONYTA_GALARIAN",
    "SPECIES_RAPIDASH_GALARIAN",
    "SPECIES_SLOWPOKE_GALARIAN",
    "SPECIES_SLOWBRO_GALARIAN",
    "SPECIES_SLOWKING_GALARIAN",
    "SPECIES_FARFETCHD_GALARIAN",
    "SPECIES_SIRFETCHD",
    "SPECIES_WEEZING_GALARIAN",
    "SPECIES_MR_MIME_GALARIAN",
    "SPECIES_MR_RIME",
    "SPECIES_CORSOLA_GALARIAN",
    "SPECIES_CURSOLA",
    "SPECIES_ZIGZAGOON_GALARIAN",
    "SPECIES_LINOONE_GALARIAN",
    "SPECIES_OBSTAGOON",
    "SPECIES_GROWLITHE_HISUIAN",
    "SPECIES_ARCANINE_HISUIAN",
    "SPECIES_VOLTORB_HISUIAN",
    "SPECIES_ELECTRODE_HISUIAN",
    "SPECIES_QWILFISH_HISUIAN",
    "SPECIES_OVERQWIL",
    "SPECIES_SNEASEL_HISUIAN",
    "SPECIES_SNEASLER",
    "SPECIES_WOOPER_PALDEAN",
    "SPECIES_CLODSIRE",
    "SPECIES_WYRDEER",
    "SPECIES_KLEAVOR",
    "SPECIES_URSALUNA",
    "SPECIES_ANNIHILAPE",
    "SPECIES_FARIGIRAF",
    "SPECIES_DUDUNSPARCE",
}

DUPLICATE_ALT_SPECIES = {
    "SPECIES_CATERPIE": ["SPECIES_WURMPLE", "SPECIES_LEDYBA"],
    "SPECIES_WEEDLE": ["SPECIES_SPINARAK", "SPECIES_WURMPLE"],
    "SPECIES_GEODUDE": ["SPECIES_NOSEPASS", "SPECIES_ONIX"],
    "SPECIES_ZUBAT": ["SPECIES_SPINARAK", "SPECIES_MURKROW"],
    "SPECIES_RATTATA": ["SPECIES_SENTRET", "SPECIES_ZIGZAGOON"],
    "SPECIES_MAGIKARP": ["SPECIES_FEEBAS", "SPECIES_GOLDEEN"],
    "SPECIES_KOFFING": ["SPECIES_GRIMER", "SPECIES_ZUBAT"],
    "SPECIES_MAGNEMITE": ["SPECIES_VOLTORB", "SPECIES_ELECTRIKE"],
    "SPECIES_SEEL": ["SPECIES_SHELLDER", "SPECIES_SPHEAL"],
    "SPECIES_VOLTORB": ["SPECIES_MAGNEMITE", "SPECIES_ELECTRIKE"],
}


@dataclasses.dataclass(frozen=True)
class Mon:
    species: str
    level: int
    moves: tuple[str, str, str, str]
    item: str = "ITEM_NONE"
    ivs: int = 100
    ability_slot: str = "TRAINER_POKEMON_ABILITY_1"


@dataclasses.dataclass(frozen=True)
class TeamUpdate:
    note: str
    mons: tuple[Mon, ...]
    trainer_type: str = TRAINER_TYPE_BOSS
    items: tuple[str, str, str, str] = ("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE", "ITEM_NONE")
    ai_flags: str = AI_EXPERT


@dataclasses.dataclass
class Entry:
    trainer_id: int
    start: int
    end: int
    block: str
    name: str
    trainer_class: str
    trainer_type: str
    levels: list[int]
    species: list[str]


def m(
    species: str,
    level: int,
    moves: tuple[str, str, str, str],
    item: str = "ITEM_NONE",
    ivs: int = 100,
    ability_slot: str = "TRAINER_POKEMON_ABILITY_1",
) -> Mon:
    return Mon(f"SPECIES_{species}", level, tuple(f"MOVE_{move}" for move in moves), item, ivs, ability_slot)


def extract_braced(text: str, start: int) -> tuple[str, int]:
    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        ch = text[index]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1], index + 1
    raise ValueError("unterminated brace block")


def parse_entries(text: str) -> list[Entry]:
    entries: list[Entry] = []
    pos = 0
    while True:
        match = re.search(r"\[(\d+)\]\s*=\s*\{", text[pos:])
        if not match:
            break
        start = pos + match.start()
        brace_start = pos + match.end() - 1
        _, brace_end = extract_braced(text, brace_start)
        comma_end = brace_end + 1 if text[brace_end : brace_end + 1] == "," else brace_end
        block = text[start:comma_end]
        trainer_id = int(match.group(1))
        name_match = re.search(r'\.name\s*=\s*"([^"]*)"', block)
        class_match = re.search(r"\.trainerClass\s*=\s*(TRAINERCLASS_[A-Z0-9_]+)", block)
        type_match = re.search(r"\.trainerType\s*=\s*([^,\n]+)", block)
        levels = [int(value) for value in re.findall(r"\.level\s*=\s*(\d+)", block)]
        species = re.findall(r"\.species\s*=\s*(SPECIES_[A-Z0-9_]+)", block)
        entries.append(
            Entry(
                trainer_id=trainer_id,
                start=start,
                end=comma_end,
                block=block,
                name=name_match.group(1) if name_match else "",
                trainer_class=class_match.group(1) if class_match else "",
                trainer_type=type_match.group(1).strip() if type_match else "",
                levels=levels,
                species=species,
            )
        )
        pos = comma_end
    return entries


def replace_scalar(block: str, field: str, value: str) -> str:
    pattern = rf"(\.{field}\s*=\s*)[^,\n]+(,)"
    new_block, count = re.subn(pattern, rf"\g<1>{value}\2", block, count=1)
    if count != 1:
        raise ValueError(f"could not replace {field}")
    return new_block


def replace_items(block: str, items: tuple[str, str, str, str]) -> str:
    value = ".items = { " + ", ".join(items) + " },"
    new_block, count = re.subn(r"\.items\s*=\s*\{[^}]*\},", value, block, count=1)
    if count != 1:
        raise ValueError("could not replace items")
    return new_block


def render_party(mons: tuple[Mon, ...]) -> str:
    lines = ["        .party = {"]
    for mon in mons:
        lines.extend(
            [
                "            {",
                f"                .ivs = {mon.ivs},",
                f"                .abilitySlot = {mon.ability_slot},",
                f"                .level = {mon.level},",
                f"                .species = {mon.species},",
                f"                .item = {mon.item},",
                "                .moves = { " + ", ".join(mon.moves) + " },",
                "                .ballSeal = 0,",
                "            },",
            ]
        )
    lines.extend(["        },"])
    return "\n".join(lines)


def replace_party(block: str, mons: tuple[Mon, ...]) -> str:
    match = re.search(r"(?m)^        \.party\s*=\s*\{", block)
    if not match:
        raise ValueError("missing party block")
    brace_start = block.find("{", match.start())
    _, brace_end = extract_braced(block, brace_start)
    end = brace_end + 1 if block[brace_end : brace_end + 1] == "," else brace_end
    return block[: match.start()] + render_party(mons) + block[end:]


def apply_team_update(block: str, update: TeamUpdate) -> str:
    block = replace_scalar(block, "trainerType", update.trainer_type)
    block = replace_items(block, update.items)
    block = replace_scalar(block, "aiFlags", update.ai_flags)
    block = replace_party(block, update.mons)
    return block


def replace_levels(block: str, levels: list[int]) -> str:
    index = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal index
        if index >= len(levels):
            raise ValueError("too many level fields")
        value = levels[index]
        index += 1
        return f"{match.group(1)}{value}"

    new_block, count = re.subn(r"(\.level\s*=\s*)\d+", repl, block)
    if count != len(levels):
        raise ValueError("level replacement count mismatch")
    return new_block


def is_boss_class(trainer_class: str) -> bool:
    return (
        trainer_class.startswith("TRAINERCLASS_LEADER_")
        or trainer_class.startswith("TRAINERCLASS_ELITE_FOUR_")
        or trainer_class in {
            "TRAINERCLASS_CHAMPION",
            "TRAINERCLASS_RIVAL",
            "TRAINERCLASS_PKMN_TRAINER_RED",
            "TRAINERCLASS_PKMN_TRAINER_LANCE",
            "TRAINERCLASS_ROCKET_BOSS",
            "TRAINERCLASS_EXECUTIVE_ARIANA",
            "TRAINERCLASS_EXECUTIVE_ARCHER",
            "TRAINERCLASS_EXECUTIVE_PROTON",
            "TRAINERCLASS_EXECUTIVE_PETREL",
        }
    )


INITIAL_PHASE7_REGULAR_SCALE_COUNT = 639
INITIAL_PHASE7_DUPLICATE_DIVERSIFY_COUNT = 39


def scale_regular_level_once(level: int) -> int:
    if level >= 70:
        return min(100, level + 2)
    if level >= 58:
        return min(78, level + 4)
    if level >= 40:
        return min(72, level + 6)
    if level >= 30:
        return min(46, level + 3)
    if level >= 20:
        return min(34, level + 2)
    if level >= 8:
        return min(24, level + 1)
    return level


def scale_regular_level(level: int) -> int:
    """Apply the final Phase 7 regular-trainer bump from a clean baseline."""
    return scale_regular_level_once(scale_regular_level_once(level))


def phase7_already_applied(entries: list[Entry]) -> bool:
    by_id = {entry.trainer_id: entry for entry in entries}
    falkner = by_id.get(20)
    lance = by_id.get(244)
    blue = by_id.get(261)
    if not falkner or not lance or not blue:
        return False
    return (
        falkner.species[:3] == ["SPECIES_DODUO", "SPECIES_FARFETCHD", "SPECIES_CHATOT"]
        and len(falkner.species) == 6
        and min(falkner.levels) == 13
        and max(falkner.levels) == 14
        and "SPECIES_AGGRON" in lance.species
        and min(lance.levels) == 58
        and max(lance.levels) == 60
        and len(blue.species) == 6
        and min(blue.levels) == 78
        and max(blue.levels) == 82
    )


def diversify_duplicates(block: str, defined_species: set[str]) -> tuple[str, list[str]]:
    if "TRAINER_DATA_TYPE_NOTHING" not in block:
        return block, []
    levels = [int(value) for value in re.findall(r"\.level\s*=\s*(\d+)", block)]
    if not levels or max(levels) < 8:
        return block, []

    matches = list(re.finditer(r"\.species\s*=\s*(SPECIES_[A-Z0-9_]+)", block))
    present = [match.group(1) for match in matches]
    counts: Counter[str] = Counter()
    replacements: list[tuple[int, int, str, str]] = []
    notes: list[str] = []
    current = set(present)

    for match in matches:
        species = match.group(1)
        counts[species] += 1
        if counts[species] == 1 or species not in DUPLICATE_ALT_SPECIES:
            continue
        for alt in DUPLICATE_ALT_SPECIES[species]:
            if alt in defined_species and alt not in current:
                replacements.append((match.start(1), match.end(1), species, alt))
                current.add(alt)
                notes.append(f"{species}->{alt}")
                break

    if not replacements:
        return block, []

    new_block = block
    for start, end, _old, new in reversed(replacements):
        new_block = new_block[:start] + new + new_block[end:]
    return new_block, notes


def silver_team(
    levels: tuple[int, int, int, int, int, int],
    starter_species: str,
    starter_moves: tuple[str, str, str, str],
    evolved: bool,
    starter_item: str = "ITEM_SITRUS_BERRY",
) -> tuple[Mon, ...]:
    first = "WEAVILE" if evolved else "SNEASEL"
    bat = "CROBAT" if evolved else "GOLBAT"
    magnet = "MAGNEZONE" if evolved else "MAGNETON"
    ghost = "GENGAR" if evolved else "HAUNTER"
    psychic = "ALAKAZAM" if evolved else "KADABRA"
    return (
        m(first, levels[0], ("QUICK_ATTACK", "ICE_PUNCH", "NIGHT_SLASH", "SHADOW_CLAW"), "ITEM_NONE", 200),
        m(bat, levels[1], ("POISON_FANG", "BITE", "CONFUSE_RAY", "AIR_CUTTER"), "ITEM_NONE", 200),
        m(magnet, levels[2], ("DISCHARGE", "FLASH_CANNON", "THUNDER_WAVE", "MAGNET_BOMB"), "ITEM_NONE", 200),
        m(ghost, levels[3], ("MEAN_LOOK", "CURSE", "SHADOW_BALL", "CONFUSE_RAY"), "ITEM_NONE", 200),
        m(psychic, levels[4], ("DISABLE", "RECOVER", "REFLECT", "PSYCHIC"), "ITEM_NONE", 200),
        m(starter_species, levels[5], starter_moves, starter_item, 220),
    )


TEAM_UPDATES: dict[int, TeamUpdate] = {
    20: TeamUpdate(
        "Falkner first badge: six early flying Pokemon at lv13-14.",
        (
            m("DODUO", 13, ("AERIAL_ACE", "ROOST", "QUICK_ATTACK", "GROWL"), ivs=50),
            m("FARFETCHD", 13, ("AERIAL_ACE", "ROOST", "FURY_ATTACK", "SAND_ATTACK"), ivs=50),
            m("CHATOT", 13, ("CHATTER", "UPROAR", "ROOST", "GROWL"), ivs=50),
            m("MURKROW", 14, ("WING_ATTACK", "FEINT_ATTACK", "HAZE", "ROOST"), "ITEM_ORAN_BERRY", 60),
            m("SWABLU", 14, ("AERIAL_ACE", "SING", "SAFEGUARD", "ROOST"), ivs=60),
            m("PIDGEOTTO", 14, ("GUST", "ROOST", "TACKLE", "SAND_ATTACK"), "ITEM_ORAN_BERRY", 70),
        ),
        items=("ITEM_SUPER_POTION", "ITEM_NONE", "ITEM_NONE", "ITEM_NONE"),
    ),
    21: TeamUpdate(
        "Bugsy first badge: full bug squad with Scyther ace at lv20.",
        (
            m("BUTTERFREE", 18, ("CONFUSION", "SLEEP_POWDER", "GUST", "BUG_BITE"), ivs=70),
            m("YANMA", 18, ("QUICK_ATTACK", "SONIC_BOOM", "U_TURN", "DETECT"), ivs=70),
            m("BEEDRILL", 18, ("POISON_JAB", "FOCUS_ENERGY", "TWINEEDLE", "PURSUIT"), ivs=70),
            m("HERACROSS", 19, ("BRICK_BREAK", "AERIAL_ACE", "FURY_ATTACK", "LEER"), ivs=80),
            m("PINSIR", 19, ("X_SCISSOR", "BRICK_BREAK", "BIND", "SEISMIC_TOSS"), ivs=80),
            m("SCYTHER", 20, ("QUICK_ATTACK", "WING_ATTACK", "U_TURN", "FOCUS_ENERGY"), "ITEM_SITRUS_BERRY", 90),
        ),
        items=("ITEM_SUPER_POTION", "ITEM_SUPER_POTION", "ITEM_NONE", "ITEM_NONE"),
    ),
    30: TeamUpdate(
        "Whitney first badge: expanded normal team, Miltank still the ace.",
        (
            m("LICKITUNG", 23, ("STOMP", "ROLLOUT", "DEFENSE_CURL", "DISABLE"), ivs=90),
            m("LOPUNNY", 23, ("QUICK_ATTACK", "JUMP_KICK", "DIZZY_PUNCH", "ATTRACT"), ivs=90),
            m("STANTLER", 24, ("STOMP", "HYPNOSIS", "CONFUSE_RAY", "TAKE_DOWN"), ivs=100),
            m("WIGGLYTUFF", 24, ("BODY_SLAM", "SING", "DOUBLE_SLAP", "DISABLE"), ivs=100),
            m("CLEFABLE", 24, ("METRONOME", "DRAIN_PUNCH", "MOONLIGHT", "DOUBLE_SLAP"), ivs=100),
            m("MILTANK", 25, ("STOMP", "ROLLOUT", "ATTRACT", "MILK_DRINK"), "ITEM_SITRUS_BERRY", 120),
        ),
        items=("ITEM_SUPER_POTION", "ITEM_SUPER_POTION", "ITEM_NONE", "ITEM_NONE"),
    ),
    31: TeamUpdate(
        "Morty first badge: full ghost/dark-leaning roster at lv29-31.",
        (
            m("DUSKULL", 29, ("SHADOW_SNEAK", "WILL_O_WISP", "CONFUSE_RAY", "PAYBACK"), ivs=110),
            m("SHUPPET", 29, ("SHADOW_SNEAK", "SCREECH", "FEINT_ATTACK", "WILL_O_WISP"), ivs=110),
            m("HAUNTER", 30, ("SHADOW_BALL", "HYPNOSIS", "DREAM_EATER", "CONFUSE_RAY"), ivs=120),
            m("MISDREAVUS", 30, ("SHADOW_BALL", "POWER_GEM", "WILL_O_WISP", "MEAN_LOOK"), ivs=120),
            m("SABLEYE", 30, ("SUCKER_PUNCH", "SHADOW_CLAW", "DETECT", "FEINT_ATTACK"), ivs=120),
            m("GENGAR", 31, ("SHADOW_BALL", "HYPNOSIS", "DREAM_EATER", "SUCKER_PUNCH"), "ITEM_SITRUS_BERRY", 140),
        ),
        items=("ITEM_HYPER_POTION", "ITEM_HYPER_POTION", "ITEM_NONE", "ITEM_NONE"),
    ),
    34: TeamUpdate(
        "Chuck first badge: six fighting Pokemon at lv34-38.",
        (
            m("PRIMEAPE", 34, ("KARATE_CHOP", "ROCK_SLIDE", "FOCUS_ENERGY", "U_TURN"), ivs=130),
            m("BRELOOM", 35, ("MACH_PUNCH", "BULLET_SEED", "STUN_SPORE", "DRAIN_PUNCH"), ivs=130),
            m("HARIYAMA", 35, ("FAKE_OUT", "VITAL_THROW", "KNOCK_OFF", "BULLET_PUNCH"), ivs=130),
            m("HITMONLEE", 36, ("BRICK_BREAK", "BLAZE_KICK", "ROCK_SLIDE", "FOCUS_ENERGY"), ivs=140),
            m("HITMONCHAN", 36, ("DRAIN_PUNCH", "FIRE_PUNCH", "ICE_PUNCH", "THUNDER_PUNCH"), ivs=140),
            m("POLIWRATH", 38, ("SURF", "HYPNOSIS", "DRAIN_PUNCH", "ROCK_SLIDE"), "ITEM_SITRUS_BERRY", 160),
        ),
        items=("ITEM_HYPER_POTION", "ITEM_HYPER_POTION", "ITEM_NONE", "ITEM_NONE"),
        ai_flags=AI_EXPERT_DAMAGE,
    ),
    33: TeamUpdate(
        "Jasmine first badge: steel identity broadened before the ace Steelix.",
        (
            m("METANG", 38, ("METAL_CLAW", "ZEN_HEADBUTT", "ROCK_SLIDE", "IRON_DEFENSE"), ivs=150),
            m("FORRETRESS", 39, ("SPIKES", "GYRO_BALL", "PROTECT", "EXPLOSION"), ivs=150),
            m("BRONZONG", 39, ("REFLECT", "LIGHT_SCREEN", "GYRO_BALL", "PSYCHIC"), ivs=150),
            m("MAGNETON", 40, ("THUNDERBOLT", "FLASH_CANNON", "THUNDER_WAVE", "SUPERSONIC"), ivs=160),
            m("SKARMORY", 40, ("AIR_SLASH", "STEEL_WING", "ROOST", "SPIKES"), ivs=160),
            m("STEELIX", 42, ("IRON_TAIL", "EARTHQUAKE", "ROCK_SLIDE", "SANDSTORM"), "ITEM_SITRUS_BERRY", 180),
        ),
        items=("ITEM_HYPER_POTION", "ITEM_HYPER_POTION", "ITEM_NONE", "ITEM_NONE"),
    ),
    32: TeamUpdate(
        "Pryce first badge: late-Johto ice team at lv40-43.",
        (
            m("ABOMASNOW", 40, ("ICE_SHARD", "RAZOR_LEAF", "HAIL", "GIGA_DRAIN"), ivs=150),
            m("FROSLASS", 41, ("ICE_BEAM", "SHADOW_BALL", "HAIL", "CONFUSE_RAY"), ivs=160),
            m("GLALIE", 41, ("ICE_BEAM", "CRUNCH", "HAIL", "PROTECT"), ivs=160),
            m("DEWGONG", 42, ("SURF", "ICE_BEAM", "REST", "SLEEP_TALK"), ivs=170),
            m("LAPRAS", 42, ("SURF", "ICE_BEAM", "BODY_SLAM", "SING"), ivs=170),
            m("MAMOSWINE", 43, ("EARTHQUAKE", "ICE_SHARD", "ANCIENT_POWER", "HAIL"), "ITEM_SITRUS_BERRY", 190),
        ),
        items=("ITEM_HYPER_POTION", "ITEM_HYPER_POTION", "ITEM_NONE", "ITEM_NONE"),
        ai_flags=AI_EXPERT_WEATHER,
    ),
    35: TeamUpdate(
        "Clair first badge: six dragons/dragon-adjacent Pokemon at lv46-50.",
        (
            m("GYARADOS", 46, ("WATERFALL", "ICE_FANG", "DRAGON_DANCE", "CRUNCH"), ivs=180),
            m("DRAGONAIR", 47, ("DRAGON_PULSE", "THUNDER_WAVE", "AQUA_TAIL", "SAFEGUARD"), ivs=180),
            m("ALTARIA", 48, ("DRAGON_PULSE", "AIR_SLASH", "ROOST", "SING"), ivs=190),
            m("FLYGON", 48, ("EARTHQUAKE", "DRAGON_CLAW", "ROCK_SLIDE", "U_TURN"), ivs=190),
            m("KINGDRA", 49, ("SURF", "DRAGON_PULSE", "ICE_BEAM", "YAWN"), ivs=200),
            m("DRAGONITE", 50, ("DRAGON_RUSH", "FIRE_PUNCH", "THUNDER_PUNCH", "ROOST"), "ITEM_SITRUS_BERRY", 220),
        ),
        items=("ITEM_HYPER_POTION", "ITEM_HYPER_POTION", "ITEM_HYPER_POTION", "ITEM_NONE"),
    ),
    245: TeamUpdate(
        "First-clear Will: six psychic-themed Pokemon at lv50-54.",
        (
            m("JYNX", 50, ("ICE_PUNCH", "PSYCHIC", "LOVELY_KISS", "FAKE_TEARS"), ivs=220),
            m("LUNATONE", 51, ("PSYCHIC", "ROCK_SLIDE", "HYPNOSIS", "LIGHT_SCREEN"), ivs=220),
            m("SOLROCK", 51, ("PSYCHIC", "ROCK_SLIDE", "WILL_O_WISP", "REFLECT"), ivs=220),
            m("SLOWBRO", 52, ("SURF", "PSYCHIC", "AMNESIA", "BODY_SLAM"), ivs=230),
            m("GARDEVOIR", 53, ("PSYCHIC", "THUNDERBOLT", "CALM_MIND", "FOCUS_BLAST"), ivs=230),
            m("XATU", 54, ("PSYCHIC", "AIR_SLASH", "SHADOW_BALL", "CONFUSE_RAY"), "ITEM_SITRUS_BERRY", 240),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE", "ITEM_NONE"),
    ),
    247: TeamUpdate(
        "First-clear Koga: poison team expanded to six at lv52-56.",
        (
            m("VENOMOTH", 52, ("PSYCHIC", "SILVER_WIND", "TOXIC", "DOUBLE_TEAM"), ivs=220),
            m("WEEZING", 52, ("SLUDGE_BOMB", "THUNDERBOLT", "WILL_O_WISP", "EXPLOSION"), ivs=220),
            m("TOXICROAK", 53, ("POISON_JAB", "CROSS_CHOP", "SUCKER_PUNCH", "X_SCISSOR"), ivs=230),
            m("TENTACRUEL", 54, ("SURF", "SLUDGE_BOMB", "ICE_BEAM", "TOXIC_SPIKES"), ivs=230),
            m("MUK", 55, ("GUNK_SHOT", "MINIMIZE", "SCREECH", "TOXIC"), "ITEM_BLACK_SLUDGE", 240),
            m("CROBAT", 56, ("CROSS_POISON", "AIR_SLASH", "TOXIC", "CONFUSE_RAY"), "ITEM_SITRUS_BERRY", 250),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE", "ITEM_NONE"),
    ),
    418: TeamUpdate(
        "First-clear Bruno: six fighting Pokemon at lv54-58.",
        (
            m("HITMONTOP", 54, ("FAKE_OUT", "CLOSE_COMBAT", "EARTHQUAKE", "QUICK_ATTACK"), ivs=220),
            m("HITMONLEE", 54, ("CLOSE_COMBAT", "BLAZE_KICK", "ROCK_SLIDE", "FOCUS_ENERGY"), ivs=220),
            m("HITMONCHAN", 54, ("DRAIN_PUNCH", "FIRE_PUNCH", "ICE_PUNCH", "THUNDER_PUNCH"), ivs=220),
            m("LUCARIO", 56, ("AURA_SPHERE", "EXTREME_SPEED", "IRON_TAIL", "DARK_PULSE"), ivs=230),
            m("HARIYAMA", 57, ("FAKE_OUT", "BULK_UP", "PAYBACK", "CLOSE_COMBAT"), "ITEM_SITRUS_BERRY", 240),
            m("MACHAMP", 58, ("DYNAMIC_PUNCH", "STONE_EDGE", "PAYBACK", "BULK_UP"), "ITEM_BLACK_BELT", 250),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE", "ITEM_NONE"),
        ai_flags=AI_EXPERT_DAMAGE,
    ),
    246: TeamUpdate(
        "First-clear Karen: six dark-themed Pokemon at lv56-58.",
        (
            m("UMBREON", 56, ("PAYBACK", "CONFUSE_RAY", "MOONLIGHT", "TOXIC"), ivs=230),
            m("SPIRITOMB", 56, ("DARK_PULSE", "SHADOW_BALL", "NASTY_PLOT", "WILL_O_WISP"), ivs=230),
            m("ABSOL", 57, ("NIGHT_SLASH", "PSYCHO_CUT", "SWORDS_DANCE", "SUCKER_PUNCH"), ivs=240),
            m("HONCHKROW", 57, ("DRILL_PECK", "SUCKER_PUNCH", "DARK_PULSE", "THUNDER_WAVE"), ivs=240),
            m("WEAVILE", 58, ("NIGHT_SLASH", "ICE_PUNCH", "LOW_KICK", "QUICK_ATTACK"), ivs=250),
            m("HOUNDOOM", 58, ("NASTY_PLOT", "DARK_PULSE", "FLAMETHROWER", "SLUDGE_BOMB"), "ITEM_SITRUS_BERRY", 250),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE", "ITEM_NONE"),
    ),
    244: TeamUpdate(
        "First-clear Lance: iconic Champion team, one Dragonite ace at lv60.",
        (
            m("GYARADOS", 58, ("WATERFALL", "ICE_FANG", "DRAGON_DANCE", "CRUNCH"), ivs=250),
            m("AERODACTYL", 58, ("AERIAL_ACE", "ROCK_SLIDE", "CRUNCH", "THUNDER_FANG"), ivs=250),
            m("KINGDRA", 59, ("SURF", "DRAGON_PULSE", "ICE_BEAM", "YAWN"), ivs=250),
            m("CHARIZARD", 59, ("FLAMETHROWER", "AIR_SLASH", "DRAGON_CLAW", "SHADOW_CLAW"), ivs=250),
            m("AGGRON", 59, ("IRON_HEAD", "DRAGON_CLAW", "EARTHQUAKE", "STONE_EDGE"), ivs=250),
            m("DRAGONITE", 60, ("DRAGON_RUSH", "FIRE_BLAST", "SAFEGUARD", "HYPER_BEAM"), "ITEM_SITRUS_BERRY", 250),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE"),
    ),
    253: TeamUpdate(
        "Kanto Brock first clear: six rock Pokemon at lv60-64.",
        (
            m("GOLEM", 60, ("EARTHQUAKE", "ROCK_SLIDE", "SANDSTORM", "DEFENSE_CURL"), ivs=220),
            m("OMASTAR", 61, ("SURF", "ANCIENT_POWER", "PROTECT", "SPIKES"), ivs=220),
            m("KABUTOPS", 61, ("AQUA_JET", "ROCK_SLIDE", "X_SCISSOR", "GIGA_DRAIN"), ivs=220),
            m("SUDOWOODO", 62, ("WOOD_HAMMER", "ROCK_SLIDE", "SUCKER_PUNCH", "LOW_KICK"), ivs=230),
            m("RHYPERIOR", 63, ("EARTHQUAKE", "STONE_EDGE", "MEGAHORN", "SANDSTORM"), ivs=240),
            m("STEELIX", 64, ("IRON_TAIL", "EARTHQUAKE", "ROCK_SLIDE", "SANDSTORM"), "ITEM_SITRUS_BERRY", 250),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE"),
    ),
    254: TeamUpdate(
        "Kanto Misty first clear: six water Pokemon at lv62-66.",
        (
            m("POLITOED", 62, ("SURF", "HYPNOSIS", "ICE_BEAM", "PERISH_SONG"), ivs=220),
            m("QUAGSIRE", 62, ("SURF", "EARTHQUAKE", "AMNESIA", "RAIN_DANCE"), ivs=220),
            m("LAPRAS", 63, ("SURF", "ICE_BEAM", "BODY_SLAM", "SING"), ivs=230),
            m("VAPOREON", 64, ("SURF", "ICE_BEAM", "AQUA_RING", "QUICK_ATTACK"), ivs=230),
            m("MILOTIC", 65, ("SURF", "RECOVER", "ICE_BEAM", "AQUA_TAIL"), ivs=240),
            m("STARMIE", 66, ("SURF", "PSYCHIC", "RECOVER", "THUNDERBOLT"), "ITEM_SITRUS_BERRY", 250),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE"),
        ai_flags=AI_EXPERT_WEATHER,
    ),
    255: TeamUpdate(
        "Kanto Lt. Surge first clear: six electric Pokemon at lv58-63.",
        (
            m("RAICHU", 58, ("THUNDERBOLT", "QUICK_ATTACK", "THUNDER_WAVE", "DOUBLE_TEAM"), ivs=220),
            m("ELECTRODE", 58, ("THUNDERBOLT", "LIGHT_SCREEN", "THUNDER_WAVE", "EXPLOSION"), ivs=220),
            m("MAGNEZONE", 60, ("DISCHARGE", "FLASH_CANNON", "THUNDER_WAVE", "MIRROR_SHOT"), ivs=230),
            m("AMPHAROS", 61, ("THUNDERBOLT", "SIGNAL_BEAM", "POWER_GEM", "LIGHT_SCREEN"), ivs=230),
            m("JOLTEON", 62, ("THUNDERBOLT", "SHADOW_BALL", "DOUBLE_TEAM", "QUICK_ATTACK"), ivs=240),
            m("ELECTIVIRE", 63, ("THUNDER_PUNCH", "LOW_KICK", "ICE_PUNCH", "LIGHT_SCREEN"), "ITEM_SITRUS_BERRY", 250),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE"),
    ),
    256: TeamUpdate(
        "Kanto Erika first clear: six grass Pokemon at lv65-68.",
        (
            m("JUMPLUFF", 65, ("U_TURN", "LEECH_SEED", "SLEEP_POWDER", "GIGA_DRAIN"), ivs=220),
            m("VICTREEBEL", 65, ("LEAF_STORM", "SLUDGE_BOMB", "SLEEP_POWDER", "SYNTHESIS"), ivs=220),
            m("BELLOSSOM", 66, ("GIGA_DRAIN", "SOLAR_BEAM", "SUNNY_DAY", "SYNTHESIS"), ivs=230),
            m("LEAFEON", 66, ("LEAF_BLADE", "X_SCISSOR", "QUICK_ATTACK", "SWORDS_DANCE"), ivs=230),
            m("TANGROWTH", 67, ("POWER_WHIP", "ANCIENT_POWER", "SLEEP_POWDER", "GIGA_DRAIN"), ivs=240),
            m("ROSERADE", 68, ("ENERGY_BALL", "SLUDGE_BOMB", "STUN_SPORE", "SHADOW_BALL"), "ITEM_SITRUS_BERRY", 250),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE"),
        ai_flags=AI_EXPERT_WEATHER,
    ),
    257: TeamUpdate(
        "Kanto Janine first clear: six poison Pokemon at lv58-64.",
        (
            m("CROBAT", 58, ("CROSS_POISON", "AIR_SLASH", "CONFUSE_RAY", "TOXIC"), ivs=220),
            m("WEEZING", 59, ("SLUDGE_BOMB", "THUNDERBOLT", "WILL_O_WISP", "EXPLOSION"), ivs=220),
            m("ARIADOS", 60, ("POISON_JAB", "SPIDER_WEB", "SUCKER_PUNCH", "PSYCHIC"), ivs=230),
            m("VENOMOTH", 61, ("SLUDGE_BOMB", "PSYCHIC", "SILVER_WIND", "DOUBLE_TEAM"), ivs=230),
            m("TOXICROAK", 62, ("POISON_JAB", "CROSS_CHOP", "SUCKER_PUNCH", "X_SCISSOR"), ivs=240),
            m("DRAPION", 64, ("CROSS_POISON", "CRUNCH", "X_SCISSOR", "TOXIC_SPIKES"), "ITEM_SITRUS_BERRY", 250),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE"),
    ),
    258: TeamUpdate(
        "Kanto Sabrina first clear: six psychic Pokemon at lv68-72.",
        (
            m("ALAKAZAM", 68, ("PSYCHIC", "FOCUS_BLAST", "RECOVER", "CALM_MIND"), ivs=230),
            m("ESPEON", 68, ("PSYCHIC", "SHADOW_BALL", "CALM_MIND", "QUICK_ATTACK"), ivs=230),
            m("MR_MIME", 69, ("PSYCHIC", "REFLECT", "LIGHT_SCREEN", "THUNDERBOLT"), ivs=230),
            m("JYNX", 70, ("PSYCHIC", "ICE_BEAM", "LOVELY_KISS", "FAKE_TEARS"), ivs=240),
            m("BRONZONG", 70, ("PSYCHIC", "GYRO_BALL", "REFLECT", "LIGHT_SCREEN"), ivs=240),
            m("GALLADE", 72, ("PSYCHO_CUT", "DRAIN_PUNCH", "NIGHT_SLASH", "SWORDS_DANCE"), "ITEM_SITRUS_BERRY", 250),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE"),
    ),
    259: TeamUpdate(
        "Kanto Blaine first clear: six fire Pokemon at lv72-76.",
        (
            m("NINETALES", 72, ("FLAMETHROWER", "WILL_O_WISP", "NASTY_PLOT", "CONFUSE_RAY"), ivs=230),
            m("RAPIDASH", 72, ("FLARE_BLITZ", "MEGAHORN", "BOUNCE", "QUICK_ATTACK"), ivs=230),
            m("CAMERUPT", 73, ("FLAMETHROWER", "EARTH_POWER", "ROCK_SLIDE", "AMNESIA"), ivs=240),
            m("HOUNDOOM", 74, ("NASTY_PLOT", "DARK_PULSE", "FLAMETHROWER", "SLUDGE_BOMB"), ivs=240),
            m("ARCANINE", 75, ("FLARE_BLITZ", "CRUNCH", "EXTREME_SPEED", "THUNDER_FANG"), ivs=250),
            m("MAGMORTAR", 76, ("FLAMETHROWER", "THUNDERBOLT", "FOCUS_BLAST", "WILL_O_WISP"), "ITEM_SITRUS_BERRY", 250),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE"),
    ),
    261: TeamUpdate(
        "Blue first clear: six mixed final-form Pokemon at lv78-82.",
        (
            m("PIDGEOT", 78, ("RETURN", "AIR_SLASH", "ROOST", "MIRROR_MOVE"), ivs=250),
            m("ALAKAZAM", 78, ("PSYCHIC", "FOCUS_BLAST", "RECOVER", "CALM_MIND"), ivs=250),
            m("RHYPERIOR", 80, ("EARTHQUAKE", "STONE_EDGE", "MEGAHORN", "SANDSTORM"), ivs=250),
            m("EXEGGUTOR", 80, ("PSYCHIC", "LEAF_STORM", "HYPNOSIS", "REFLECT"), ivs=250),
            m("ARCANINE", 80, ("FLARE_BLITZ", "CRUNCH", "EXTREME_SPEED", "THUNDER_FANG"), ivs=250),
            m("TYRANITAR", 82, ("STONE_EDGE", "CRUNCH", "EARTHQUAKE", "FIRE_PUNCH"), "ITEM_SITRUS_BERRY", 250),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE"),
    ),
    260: TeamUpdate(
        "Red superboss: iconic party at lv88-100.",
        (
            m("PIKACHU", 100, ("VOLT_TACKLE", "IRON_TAIL", "QUICK_ATTACK", "THUNDERBOLT"), "ITEM_LIGHT_BALL", 250),
            m("LAPRAS", 88, ("SURF", "BLIZZARD", "BODY_SLAM", "REST"), "ITEM_LEFTOVERS", 250),
            m("SNORLAX", 90, ("BODY_SLAM", "CRUNCH", "REST", "SLEEP_TALK"), "ITEM_LEFTOVERS", 250),
            m("VENUSAUR", 92, ("FRENZY_PLANT", "SLUDGE_BOMB", "SLEEP_POWDER", "GIGA_DRAIN"), "ITEM_MIRACLE_SEED", 250),
            m("CHARIZARD", 94, ("BLAST_BURN", "AIR_SLASH", "DRAGON_CLAW", "FLAMETHROWER"), "ITEM_CHARCOAL", 250),
            m("BLASTOISE", 94, ("HYDRO_CANNON", "SURF", "ICE_BEAM", "FOCUS_BLAST"), "ITEM_MYSTIC_WATER", 250),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE"),
    ),
    271: TeamUpdate(
        "Mid-game Silver: six Pokemon once his team identity is established.",
        silver_team((32, 32, 32, 34, 34, 36), "FERALIGATR", ("ICE_FANG", "WATERFALL", "CRUNCH", "SLASH"), False),
        items=("ITEM_NONE", "ITEM_NONE", "ITEM_NONE", "ITEM_NONE"),
    ),
    288: TeamUpdate(
        "Mid-game Silver: six Pokemon once his team identity is established.",
        silver_team((32, 32, 32, 34, 34, 36), "MEGANIUM", ("REFLECT", "SYNTHESIS", "POISON_POWDER", "PETAL_DANCE"), False),
        items=("ITEM_NONE", "ITEM_NONE", "ITEM_NONE", "ITEM_NONE"),
    ),
    289: TeamUpdate(
        "Mid-game Silver: six Pokemon once his team identity is established.",
        silver_team((32, 32, 32, 34, 34, 36), "QUILAVA", ("SMOKESCREEN", "SWIFT", "QUICK_ATTACK", "FLAME_WHEEL"), False),
        items=("ITEM_NONE", "ITEM_NONE", "ITEM_NONE", "ITEM_NONE"),
    ),
    285: TeamUpdate(
        "Pokemon League Silver: six Pokemon at lv48-52.",
        silver_team((48, 49, 48, 50, 50, 52), "MEGANIUM", ("PETAL_DANCE", "POISON_POWDER", "SYNTHESIS", "LIGHT_SCREEN"), False),
        items=("ITEM_FULL_RESTORE", "ITEM_NONE", "ITEM_NONE", "ITEM_NONE"),
    ),
    286: TeamUpdate(
        "Pokemon League Silver: six Pokemon at lv48-52.",
        silver_team((48, 49, 48, 50, 50, 52), "TYPHLOSION", ("FLAMETHROWER", "QUICK_ATTACK", "FLAME_WHEEL", "SWIFT"), False),
        items=("ITEM_FULL_RESTORE", "ITEM_NONE", "ITEM_NONE", "ITEM_NONE"),
    ),
    287: TeamUpdate(
        "Pokemon League Silver: six Pokemon at lv48-52.",
        silver_team((48, 49, 48, 50, 50, 52), "FERALIGATR", ("WATERFALL", "ICE_FANG", "CRUNCH", "SLASH"), False),
        items=("ITEM_FULL_RESTORE", "ITEM_NONE", "ITEM_NONE", "ITEM_NONE"),
    ),
    489: TeamUpdate(
        "Post-League Silver: evolved six-Pokemon team at lv68-74.",
        silver_team((68, 69, 69, 70, 70, 74), "MEGANIUM", ("PETAL_DANCE", "BODY_SLAM", "LIGHT_SCREEN", "SYNTHESIS"), True),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE", "ITEM_NONE"),
    ),
    490: TeamUpdate(
        "Post-League Silver: evolved six-Pokemon team at lv68-74.",
        silver_team((68, 69, 69, 70, 70, 74), "TYPHLOSION", ("FLAMETHROWER", "FOCUS_BLAST", "WILL_O_WISP", "SWIFT"), True),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE", "ITEM_NONE"),
    ),
    491: TeamUpdate(
        "Post-League Silver: evolved six-Pokemon team at lv68-74.",
        silver_team((68, 69, 69, 70, 70, 74), "FERALIGATR", ("WATERFALL", "ICE_FANG", "CRUNCH", "AQUA_TAIL"), True),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE", "ITEM_NONE"),
    ),
    478: TeamUpdate(
        "Radio Tower Ariana: full serious Executive team.",
        (
            m("ARBOK", 45, ("POISON_JAB", "CRUNCH", "GLARE", "AQUA_TAIL"), ivs=180),
            m("JYNX", 45, ("ICE_BEAM", "PSYCHIC", "LOVELY_KISS", "FAKE_TEARS"), ivs=180),
            m("VILEPLUME", 45, ("GIGA_DRAIN", "SLUDGE_BOMB", "SLEEP_POWDER", "MOONLIGHT"), ivs=180),
            m("PURUGLY", 46, ("FAKE_OUT", "BODY_SLAM", "HYPNOSIS", "SHADOW_CLAW"), ivs=190),
            m("MILOTIC", 46, ("SURF", "RECOVER", "ICE_BEAM", "AQUA_TAIL"), ivs=190),
            m("HONCHKROW", 47, ("DRILL_PECK", "SUCKER_PUNCH", "DARK_PULSE", "THUNDER_WAVE"), "ITEM_SITRUS_BERRY", 200),
        ),
        items=("ITEM_HYPER_POTION", "ITEM_HYPER_POTION", "ITEM_NONE", "ITEM_NONE"),
    ),
    487: TeamUpdate(
        "Radio Tower Petrel: full Executive team without six Koffing filler.",
        (
            m("RATICATE", 42, ("SUPER_FANG", "CRUNCH", "SUCKER_PUNCH", "QUICK_ATTACK"), ivs=160),
            m("SKUNTANK", 42, ("NIGHT_SLASH", "POISON_JAB", "SMOKESCREEN", "EXPLOSION"), ivs=160),
            m("TANGROWTH", 43, ("POWER_WHIP", "ANCIENT_POWER", "SLEEP_POWDER", "GIGA_DRAIN"), ivs=170),
            m("TOXICROAK", 43, ("POISON_JAB", "CROSS_CHOP", "SUCKER_PUNCH", "X_SCISSOR"), ivs=170),
            m("HYPNO", 44, ("PSYCHIC", "HYPNOSIS", "DREAM_EATER", "NASTY_PLOT"), ivs=180),
            m("WEEZING", 45, ("SLUDGE_BOMB", "THUNDERBOLT", "WILL_O_WISP", "EXPLOSION"), "ITEM_SITRUS_BERRY", 190),
        ),
        items=("ITEM_HYPER_POTION", "ITEM_HYPER_POTION", "ITEM_NONE", "ITEM_NONE"),
    ),
    485: TeamUpdate(
        "Radio Tower Archer: final Rocket Executive fight at lv46-48.",
        (
            m("ZANGOOSE", 46, ("CRUSH_CLAW", "X_SCISSOR", "SHADOW_CLAW", "SWORDS_DANCE"), ivs=190),
            m("DRAPION", 46, ("CROSS_POISON", "CRUNCH", "X_SCISSOR", "TOXIC_SPIKES"), ivs=190),
            m("SCIZOR", 46, ("X_SCISSOR", "IRON_HEAD", "QUICK_ATTACK", "SWORDS_DANCE"), ivs=190),
            m("MACHAMP", 47, ("DYNAMIC_PUNCH", "STONE_EDGE", "PAYBACK", "BULK_UP"), ivs=200),
            m("GYARADOS", 47, ("WATERFALL", "ICE_FANG", "DRAGON_DANCE", "CRUNCH"), ivs=200),
            m("HOUNDOOM", 48, ("NASTY_PLOT", "DARK_PULSE", "FLAMETHROWER", "SLUDGE_BOMB"), "ITEM_SITRUS_BERRY", 220),
        ),
        items=("ITEM_HYPER_POTION", "ITEM_HYPER_POTION", "ITEM_NONE", "ITEM_NONE"),
    ),
    700: TeamUpdate(
        "Giovanni optional Rocket boss: six Pokemon at lv58-64.",
        (
            m("NIDOKING", 58, ("EARTH_POWER", "POISON_JAB", "MEGAHORN", "SHADOW_CLAW"), ivs=220),
            m("KANGASKHAN", 59, ("DIZZY_PUNCH", "SUCKER_PUNCH", "OUTRAGE", "EARTHQUAKE"), ivs=220),
            m("HONCHKROW", 60, ("DARK_PULSE", "NASTY_PLOT", "DRILL_PECK", "SHADOW_BALL"), ivs=230),
            m("RHYPERIOR", 61, ("EARTHQUAKE", "STONE_EDGE", "MEGAHORN", "SANDSTORM"), ivs=230),
            m("PERSIAN", 62, ("FAKE_OUT", "SLASH", "HYPNOSIS", "POWER_GEM"), ivs=240),
            m("NIDOQUEEN", 64, ("EARTH_POWER", "SUPERPOWER", "CRUNCH", "SLUDGE_BOMB"), "ITEM_SITRUS_BERRY", 250),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE", "ITEM_NONE"),
    ),
    733: TeamUpdate(
        "Postgame Lance special: Champion-class record expanded to six.",
        (
            m("GYARADOS", 82, ("WATERFALL", "ICE_FANG", "DRAGON_DANCE", "CRUNCH"), ivs=250),
            m("AERODACTYL", 82, ("AERIAL_ACE", "ROCK_SLIDE", "CRUNCH", "THUNDER_FANG"), ivs=250),
            m("KINGDRA", 84, ("SURF", "DRAGON_PULSE", "ICE_BEAM", "YAWN"), ivs=250),
            m("CHARIZARD", 84, ("FLAMETHROWER", "AIR_SLASH", "DRAGON_CLAW", "HYPER_BEAM"), ivs=250),
            m("AGGRON", 86, ("IRON_HEAD", "DRAGON_CLAW", "EARTHQUAKE", "STONE_EDGE"), ivs=250),
            m("DRAGONITE", 88, ("FIRE_PUNCH", "SAFEGUARD", "DRACO_METEOR", "HYPER_BEAM"), "ITEM_SITRUS_BERRY", 250),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE"),
    ),
    734: TeamUpdate(
        "Postgame Clair special: Leader-class record expanded to six.",
        (
            m("GYARADOS", 76, ("WATERFALL", "ICE_FANG", "DRAGON_DANCE", "CRUNCH"), ivs=230),
            m("DRAGONAIR", 76, ("THUNDER_WAVE", "DRAGON_RUSH", "THUNDERBOLT", "FLAMETHROWER"), ivs=230),
            m("ALTARIA", 78, ("DRAGON_PULSE", "AIR_SLASH", "ROOST", "SING"), ivs=240),
            m("KINGDRA", 80, ("HYDRO_PUMP", "ICE_BEAM", "DRAGON_PULSE", "YAWN"), ivs=240),
            m("CHARIZARD", 82, ("FLAMETHROWER", "AIR_SLASH", "DRAGON_CLAW", "HYPER_BEAM"), ivs=250),
            m("DRAGONITE", 84, ("THUNDER", "PROTECT", "DRAGON_RUSH", "HYPER_BEAM"), "ITEM_SITRUS_BERRY", 250),
        ),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE"),
    ),
    735: TeamUpdate(
        "Postgame Silver special: full evolved team at lv78-82.",
        silver_team((78, 78, 79, 80, 80, 82), "MEGANIUM", ("PETAL_DANCE", "BODY_SLAM", "LIGHT_SCREEN", "SYNTHESIS"), True),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE", "ITEM_NONE"),
    ),
    736: TeamUpdate(
        "Postgame Silver special: full evolved team at lv78-82.",
        silver_team((78, 78, 79, 80, 80, 82), "TYPHLOSION", ("FLAMETHROWER", "FOCUS_BLAST", "WILL_O_WISP", "SWIFT"), True),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE", "ITEM_NONE"),
    ),
    737: TeamUpdate(
        "Postgame Silver special: full evolved team at lv78-82.",
        silver_team((78, 78, 79, 80, 80, 82), "FERALIGATR", ("WATERFALL", "ICE_FANG", "CRUNCH", "AQUA_TAIL"), True),
        items=("ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE", "ITEM_NONE", "ITEM_NONE"),
    ),
}


LEVEL_ONLY_UPDATES: dict[int, list[int]] = {
    264: [38, 40, 39, 39, 39, 42],
    268: [38, 40, 39, 39, 39, 42],
    272: [38, 40, 39, 39, 39, 42],
    701: [84, 82, 84, 84, 84, 88],
    702: [78, 80, 78, 80, 82, 84],
    703: [78, 80, 78, 80, 82, 84],
    704: [78, 78, 78, 80, 82, 84],
    705: [78, 78, 80, 82, 82, 84],
    712: [68, 66, 68, 70, 70, 72],
    713: [70, 68, 68, 69, 70, 72],
    714: [71, 69, 69, 70, 72, 73],
    715: [72, 68, 70, 70, 72, 74],
    716: [72, 72, 72, 74, 74, 76],
    717: [72, 74, 70, 72, 76, 78],
    718: [73, 70, 70, 72, 73, 75],
    719: [72, 72, 74, 76, 76, 78],
    720: [74, 72, 74, 76, 76, 78],
    721: [76, 72, 74, 74, 76, 78],
    722: [76, 74, 76, 76, 78, 80],
    723: [76, 74, 76, 78, 78, 80],
    724: [74, 72, 74, 76, 76, 78],
    725: [78, 76, 76, 76, 78, 80],
    726: [80, 78, 78, 78, 80, 82],
    727: [84, 84, 86, 86, 88, 90],
}


def read_defined_symbols(path: pathlib.Path) -> set[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r"#define\s+([A-Z][A-Z0-9_]+)\b", text))


def read_species_numbers(path: pathlib.Path) -> dict[str, int | None]:
    numbers: dict[str, int | None] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"#define\s+(SPECIES_[A-Z0-9_]+)\s+(.+)", line)
        if not match:
            continue
        value = match.group(2).split("//", 1)[0].strip()
        number = int(value) if re.fullmatch(r"\d+", value) else None
        numbers[match.group(1)] = number
    return numbers


def validate(text: str) -> list[str]:
    errors: list[str] = []
    defined_species = read_defined_symbols(ENGINE / "include" / "constants" / "species.h")
    defined_moves = read_defined_symbols(ENGINE / "include" / "constants" / "moves.h")
    defined_items = read_defined_symbols(ENGINE / "include" / "constants" / "item.h")
    species_numbers = read_species_numbers(ENGINE / "include" / "constants" / "species.h")

    used_species = set(re.findall(r"\.species\s*=\s*(SPECIES_[A-Z0-9_]+)", text))
    used_moves = set(re.findall(r"MOVE_[A-Z0-9_]+", text))
    used_items = set(re.findall(r"ITEM_[A-Z0-9_]+", text))
    used_ability_slots = set(re.findall(r"\.abilitySlot\s*=\s*(TRAINER_POKEMON_ABILITY_[A-Z0-9_]+)", text))

    missing_species = sorted(used_species - defined_species)
    missing_moves = sorted(used_moves - defined_moves)
    missing_items = sorted(used_items - defined_items)
    if missing_species:
        errors.append("missing species constants: " + ", ".join(missing_species))
    if missing_moves:
        errors.append("missing move constants: " + ", ".join(missing_moves))
    if missing_items:
        errors.append("missing item constants: " + ", ".join(missing_items))
    bad_ability_slots = sorted(
        used_ability_slots
        - {
            "TRAINER_POKEMON_ABILITY_1",
            "TRAINER_POKEMON_ABILITY_2",
            "TRAINER_POKEMON_ABILITY_HIDDEN",
        }
    )
    if bad_ability_slots:
        errors.append("invalid trainer ability slots: " + ", ".join(bad_ability_slots))

    forbidden_species: list[str] = []
    for species in sorted(used_species):
        number = species_numbers.get(species)
        if number is not None and number <= 493:
            continue
        if number is None and species not in APPROVED_LATER_SPECIES:
            forbidden_species.append(species)
        elif number is not None and number > 493 and species not in APPROVED_LATER_SPECIES:
            forbidden_species.append(species)
    if forbidden_species:
        errors.append("forbidden later-generation trainer species: " + ", ".join(forbidden_species))

    for entry in parse_entries(text):
        size = len(entry.species)
        max_level = max(entry.levels) if entry.levels else 0
        is_mandatory_six = (
            entry.trainer_class.startswith("TRAINERCLASS_LEADER_")
            or entry.trainer_class.startswith("TRAINERCLASS_ELITE_FOUR_")
            or entry.trainer_class in {"TRAINERCLASS_CHAMPION", "TRAINERCLASS_PKMN_TRAINER_RED"}
        )
        if is_mandatory_six and size != 6:
            errors.append(
                f"trainer {entry.trainer_id} {entry.name} {entry.trainer_class} has {size} Pokemon, expected 6"
            )
        if entry.trainer_class == "TRAINERCLASS_RIVAL" and max_level >= 28 and size != 6:
            errors.append(f"major rival trainer {entry.trainer_id} has {size} Pokemon, expected 6")
        if entry.trainer_class.startswith("TRAINERCLASS_EXECUTIVE_") and max_level >= 35 and size != 6:
            errors.append(f"major Rocket executive {entry.trainer_id} has {size} Pokemon, expected 6")
        if entry.trainer_class == "TRAINERCLASS_ROCKET_BOSS" and size != 6:
            errors.append(f"Rocket Boss trainer {entry.trainer_id} has {size} Pokemon, expected 6")

        if "TRAINER_DATA_TYPE_MOVES" in entry.trainer_type:
            party_block = re.search(r"(?ms)^        \.party\s*=\s*\{(.+?)^        \},", entry.block)
            if party_block:
                mon_blocks = re.findall(r"(?ms)^            \{\n(.+?)^            \},", party_block.group(1))
                for mon_index, mon_block in enumerate(mon_blocks, 1):
                    move_count = len(re.findall(r"MOVE_[A-Z0-9_]+", mon_block))
                    if move_count != 4:
                        errors.append(f"trainer {entry.trainer_id} mon {mon_index} has {move_count} moves")
        if "TRAINER_DATA_TYPE_ITEMS" in entry.trainer_type:
            party_block = re.search(r"(?ms)^        \.party\s*=\s*\{(.+?)^        \},", entry.block)
            if party_block:
                mon_blocks = re.findall(r"(?ms)^            \{\n(.+?)^            \},", party_block.group(1))
                for mon_index, mon_block in enumerate(mon_blocks, 1):
                    if ".item =" not in mon_block:
                        errors.append(f"trainer {entry.trainer_id} mon {mon_index} missing item")

    return errors


def entry_summary(entry: Entry) -> str:
    levels = f"{min(entry.levels)}-{max(entry.levels)}" if entry.levels else "none"
    species = ", ".join(mon.replace("SPECIES_", "") for mon in entry.species)
    return f"| {entry.trainer_id} | {entry.name} | {entry.trainer_class.replace('TRAINERCLASS_', '')} | {len(entry.species)} | {levels} | {species} |"


def write_report(
    before_text: str,
    after_text: str,
    team_updates: dict[int, TeamUpdate],
    level_only: dict[int, list[int]],
    scaled_regulars: list[tuple[int, str, str, int, int]],
    diversified: list[tuple[int, str, list[str]]],
    errors: list[str],
    already_applied: bool = False,
) -> None:
    before = {entry.trainer_id: entry for entry in parse_entries(before_text)}
    after = {entry.trainer_id: entry for entry in parse_entries(after_text)}
    later_species = sorted(
        species
        for species in set(re.findall(r"\.species\s*=\s*(SPECIES_[A-Z0-9_]+)", after_text))
        if species in APPROVED_LATER_SPECIES
    )
    gen4_family_completion = sorted(
        {
            species
            for species in re.findall(r"\.species\s*=\s*(SPECIES_[A-Z0-9_]+)", after_text)
            if species
            in {
                "SPECIES_ROSERADE",
                "SPECIES_AMBIPOM",
                "SPECIES_MISMAGIUS",
                "SPECIES_HONCHKROW",
                "SPECIES_WEAVILE",
                "SPECIES_MAGNEZONE",
                "SPECIES_LICKILICKY",
                "SPECIES_RHYPERIOR",
                "SPECIES_TANGROWTH",
                "SPECIES_ELECTIVIRE",
                "SPECIES_MAGMORTAR",
                "SPECIES_TOGEKISS",
                "SPECIES_YANMEGA",
                "SPECIES_LEAFEON",
                "SPECIES_GLACEON",
                "SPECIES_GLISCOR",
                "SPECIES_MAMOSWINE",
                "SPECIES_PORYGON_Z",
                "SPECIES_GALLADE",
                "SPECIES_PROBOPASS",
                "SPECIES_DUSKNOIR",
                "SPECIES_FROSLASS",
            }
        }
    )

    scale_counts = Counter()
    for _trainer_id, _name, _cls, old_max, new_max in scaled_regulars:
        scale_counts[f"{old_max}->{new_max}"] += 1

    lines = [
        "# Phase 7 Trainer Report",
        "",
        "## Boss roster changes",
        "",
        "| ID | Name | Class | Size | Levels | Species |",
        "| - | - | - | - | - | - |",
    ]
    for trainer_id in sorted(team_updates):
        lines.append(entry_summary(after[trainer_id]))

    if already_applied:
        lines.extend(
            [
                "",
                "## Level-only boss/rematch final levels",
                "",
                "| ID | Name | Class | Final |",
                "| - | - | - | - |",
            ]
        )
        for trainer_id in sorted(level_only):
            new = after[trainer_id]
            lines.append(
                f"| {trainer_id} | {new.name} | {new.trainer_class.replace('TRAINERCLASS_', '')} | "
                f"{min(new.levels)}-{max(new.levels)} |"
            )
    else:
        lines.extend(
            [
                "",
                "## Level-only boss/rematch changes",
                "",
                "| ID | Name | Class | Before | After |",
                "| - | - | - | - | - |",
            ]
        )
        for trainer_id in sorted(level_only):
            old = before[trainer_id]
            new = after[trainer_id]
            lines.append(
                f"| {trainer_id} | {new.name} | {new.trainer_class.replace('TRAINERCLASS_', '')} | "
                f"{min(old.levels)}-{max(old.levels)} | {min(new.levels)}-{max(new.levels)} |"
            )

    lines.extend(
        [
            "",
            "## Regular trainer pass",
            "",
            (
                f"- Non-boss trainers level-scaled: already applied; initial Phase 7 pass touched "
                f"{INITIAL_PHASE7_REGULAR_SCALE_COUNT}"
                if already_applied
                else f"- Non-boss trainers level-scaled: {len(scaled_regulars)}"
            ),
            (
                f"- Duplicate no-custom-move parties diversified: already applied; initial Phase 7 pass touched "
                f"{INITIAL_PHASE7_DUPLICATE_DIVERSIFY_COUNT}"
                if already_applied
                else f"- Duplicate no-custom-move parties diversified: {len(diversified)}"
            ),
        ]
    )
    if diversified:
        lines.append("- Duplicate replacements:")
        for trainer_id, name, notes in diversified[:80]:
            lines.append(f"  - {trainer_id} {name}: {', '.join(notes)}")
        if len(diversified) > 80:
            lines.append(f"  - ...and {len(diversified) - 80} more.")

    lines.extend(
        [
            "",
            "## Six-Pokemon boss confirmation",
            "",
            "- Gym Leaders: all leader-class records have 6 Pokemon.",
            "- Elite Four: all Elite Four records have 6 Pokemon.",
            "- Champions/Red: all Champion-class and Red records have 6 Pokemon.",
            "- Major rival fights from mid-game onward have 6 Pokemon.",
            "- Major Rocket Executive/Rocket Boss records at level 35+ have 6 Pokemon.",
            "",
            "## Level curve summary",
            "",
            "- Johto leaders: Falkner 13-14, Bugsy 18-20, Whitney 23-25, Morty 29-31, Chuck 34-38, Jasmine 38-42, Pryce 40-43, Clair 46-50.",
            "- First League: Will 50-54, Koga 52-56, Bruno 54-58, Karen 56-58, Lance 58-60.",
            "- Kanto leaders: early Kanto 58-66, mid Kanto 65-72, Blaine 72-76, Blue 78-82.",
            "- Rematches/postgame: Elite Four rematches 78-84, Lance rematch 82-88, Gym Leader rematches 66-90, Red 88-100.",
            "",
            "## Later-generation exception usage",
            "",
            "- No unrelated Gen 5+ Pokemon are used in trainer rosters.",
            "- No Gen 5+ family exceptions were added to trainer rosters in Phase 7.",
            "- Gen 4 family completions used where thematic: " + (", ".join(s.replace("SPECIES_", "") for s in gen4_family_completion) or "None"),
            "- Approved later regional/direct exceptions found in trainer data: " + (", ".join(s.replace("SPECIES_", "") for s in later_species) or "None"),
            "",
            "## Validation",
            "",
        ]
    )
    if errors:
        lines.append("- FAILED:")
        lines.extend(f"  - {error}" for error in errors)
    else:
        lines.extend(
            [
                "- Constant validation passed for trainer species, moves, and items.",
                "- Trainer ability-slot validation passed.",
                "- Six-Pokemon mandatory boss validation passed.",
                "- Major rival/Rocket size validation passed.",
                "- Approved Pokemon scope validation passed; no unrelated later-generation species found.",
            ]
        )

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(write: bool) -> None:
    before_text = TRAINERS.read_text(encoding="utf-8", errors="replace")
    entries = parse_entries(before_text)
    defined_species = read_defined_symbols(ENGINE / "include" / "constants" / "species.h")

    if phase7_already_applied(entries):
        errors = validate(before_text)
        write_report(before_text, before_text, TEAM_UPDATES, LEVEL_ONLY_UPDATES, [], [], errors, already_applied=True)
        if errors:
            raise SystemExit("\n".join(errors))
        print("Phase 7 trainer data is already applied; validation passed.")
        print(f"Wrote {REPORT}")
        return

    replacements: dict[int, str] = {}
    scaled_regulars: list[tuple[int, str, str, int, int]] = []
    diversified: list[tuple[int, str, list[str]]] = []

    for entry in entries:
        block = entry.block
        if entry.trainer_id in TEAM_UPDATES:
            block = apply_team_update(block, TEAM_UPDATES[entry.trainer_id])
        elif entry.trainer_id in LEVEL_ONLY_UPDATES:
            block = replace_levels(block, LEVEL_ONLY_UPDATES[entry.trainer_id])
        elif entry.levels and not is_boss_class(entry.trainer_class):
            new_levels = [scale_regular_level(level) for level in entry.levels]
            if new_levels != entry.levels:
                scaled_regulars.append(
                    (entry.trainer_id, entry.name, entry.trainer_class, max(entry.levels), max(new_levels))
                )
                block = replace_levels(block, new_levels)
            block, notes = diversify_duplicates(block, defined_species)
            if notes:
                diversified.append((entry.trainer_id, entry.name, notes))
        if block != entry.block:
            replacements[entry.trainer_id] = block

    after_parts: list[str] = []
    cursor = 0
    for entry in entries:
        after_parts.append(before_text[cursor : entry.start])
        after_parts.append(replacements.get(entry.trainer_id, entry.block))
        cursor = entry.end
    after_parts.append(before_text[cursor:])
    after_text = "".join(after_parts)

    errors = validate(after_text)
    write_report(before_text, after_text, TEAM_UPDATES, LEVEL_ONLY_UPDATES, scaled_regulars, diversified, errors)
    if errors:
        raise SystemExit("\n".join(errors))

    if write:
        TRAINERS.write_text(after_text, encoding="utf-8")
        print(f"Updated {TRAINERS}")
        print(f"Wrote {REPORT}")
    else:
        print("Validation passed. Re-run with --write to update Trainers.c.")
        print(f"Wrote {REPORT}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="rewrite data/Trainers.c")
    args = parser.parse_args()
    run(write=args.write)


if __name__ == "__main__":
    main()
