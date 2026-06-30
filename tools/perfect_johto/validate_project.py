#!/usr/bin/env python3
"""Phase 9 validation, export, and static documentation runner."""

from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict, deque
from typing import Any

import phase6_encounter_tools as phase6
import phase7_trainer_tools as phase7
import phase8_postgame_tools as phase8


ROOT = pathlib.Path(__file__).resolve().parents[2]
ENGINE = ROOT / "hg-engine-main" / "hg-engine-main"
DOCS = ROOT / "docs"
EXPORTS = ROOT / "exports" / "perfect_johto"
VALIDATION_TMP = ROOT / "build" / "perfect_johto_validation"
PROJECT_NAME = "Pokemon Johto Reforged"

GAMEPLAY_SPECIES_FILES = [
    ENGINE / "data" / "Encounters.c",
    ENGINE / "data" / "SafariEncounters.c",
    ENGINE / "data" / "Headbutt.c",
    ENGINE / "data" / "Trainers.c",
    ENGINE / "armips" / "scr_seq" / "scr_seq_00832_phase8_dojo.s",
]

FORBIDDEN_ACTIVE_CONFIGS = {
    "MEGA_EVOLUTIONS",
    "PRIMAL_REVERSION",
    "RESTORE_ITEMS_AT_BATTLE_END",
}

FORBIDDEN_GAMEPLAY_TOKENS = [
    "Z_CRYSTAL",
    "DYNAMAX",
    "GIGANTAMAX",
    "TERASTAL",
    "TERA_ORB",
    "TERA_SHARD",
    "MEGA_STONE",
    "MEGA_RING",
    "PRIMAL_REVERSION",
    "RED_ORB",
    "BLUE_ORB",
]

IV_CANDIES = [
    "ITEM_HEALTH_CANDY",
    "ITEM_MIGHTY_CANDY",
    "ITEM_TOUGH_CANDY",
    "ITEM_SMART_CANDY",
    "ITEM_COURAGE_CANDY",
    "ITEM_QUICK_CANDY",
]

MINTS = [
    "ITEM_LONELY_MINT",
    "ITEM_ADAMANT_MINT",
    "ITEM_NAUGHTY_MINT",
    "ITEM_BRAVE_MINT",
    "ITEM_BOLD_MINT",
    "ITEM_IMPISH_MINT",
    "ITEM_LAX_MINT",
    "ITEM_RELAXED_MINT",
    "ITEM_MODEST_MINT",
    "ITEM_MILD_MINT",
    "ITEM_RASH_MINT",
    "ITEM_QUIET_MINT",
    "ITEM_CALM_MINT",
    "ITEM_GENTLE_MINT",
    "ITEM_CAREFUL_MINT",
    "ITEM_SASSY_MINT",
    "ITEM_TIMID_MINT",
    "ITEM_HASTY_MINT",
    "ITEM_JOLLY_MINT",
    "ITEM_NAIVE_MINT",
    "ITEM_SERIOUS_MINT",
]

EV_ITEMS = [
    "ITEM_HP_UP",
    "ITEM_PROTEIN",
    "ITEM_IRON",
    "ITEM_CALCIUM",
    "ITEM_ZINC",
    "ITEM_CARBOS",
    "ITEM_HEALTH_FEATHER",
    "ITEM_MUSCLE_FEATHER",
    "ITEM_RESIST_FEATHER",
    "ITEM_GENIUS_FEATHER",
    "ITEM_CLEVER_FEATHER",
    "ITEM_SWIFT_FEATHER",
    "ITEM_POMEG_BERRY",
    "ITEM_KELPSY_BERRY",
    "ITEM_QUALOT_BERRY",
    "ITEM_HONDEW_BERRY",
    "ITEM_GREPA_BERRY",
    "ITEM_TAMATO_BERRY",
    "ITEM_MACHO_BRACE",
    "ITEM_POWER_WEIGHT",
    "ITEM_POWER_BRACER",
    "ITEM_POWER_BELT",
    "ITEM_POWER_LENS",
    "ITEM_POWER_BAND",
    "ITEM_POWER_ANKLET",
]

EXPECTED_RANDOM_LEGENDARY_RATES = [
    {"badges": "0-3 badges", "denominator": 0, "description": "disabled"},
    {
        "badges": "4+ badges",
        "tier": "weaker",
        "denominator": 2000,
        "description": "1/2000 aggregate unlocked weaker/mystical legendary pool roll",
    },
    {
        "badges": "6+ badges when true-tier species are unlocked",
        "tier": "true",
        "denominator": 4000,
        "description": "1/4000 aggregate unlocked stronger true/cover-story legendary pool roll",
    },
]

LATE_LEVEL_EXEMPT_SPECIES_ROOTS = {
    "ARTICUNO",
    "ZAPDOS",
    "MOLTRES",
    "MEWTWO",
    "MEW",
    "RAIKOU",
    "ENTEI",
    "SUICUNE",
    "LUGIA",
    "HO_OH",
    "CELEBI",
    "REGIROCK",
    "REGICE",
    "REGISTEEL",
    "LATIAS",
    "LATIOS",
    "KYOGRE",
    "GROUDON",
    "RAYQUAZA",
    "JIRACHI",
    "DEOXYS",
    "UXIE",
    "MESPRIT",
    "AZELF",
    "DIALGA",
    "PALKIA",
    "HEATRAN",
    "REGIGIGAS",
    "GIRATINA",
    "CRESSELIA",
    "PHIONE",
    "MANAPHY",
    "DARKRAI",
    "SHAYMIN",
    "ARCEUS",
    "VICTINI",
    "COBALION",
    "TERRAKION",
    "VIRIZION",
    "TORNADUS",
    "THUNDURUS",
    "RESHIRAM",
    "ZEKROM",
    "LANDORUS",
    "KYUREM",
    "KELDEO",
    "MELOETTA",
    "GENESECT",
    "XERNEAS",
    "YVELTAL",
    "ZYGARDE",
    "DIANCIE",
    "HOOPA",
    "VOLCANION",
    "TYPE_NULL",
    "SILVALLY",
    "TAPU_KOKO",
    "TAPU_LELE",
    "TAPU_BULU",
    "TAPU_FINI",
    "COSMOG",
    "COSMOEM",
    "SOLGALEO",
    "LUNALA",
    "NIHILEGO",
    "BUZZWOLE",
    "PHEROMOSA",
    "XURKITREE",
    "CELESTEELA",
    "KARTANA",
    "GUZZLORD",
    "NECROZMA",
    "MAGEARNA",
    "MARSHADOW",
    "POIPOLE",
    "NAGANADEL",
    "STAKATAKA",
    "BLACEPHALON",
    "ZERAORA",
    "MELTAN",
    "MELMETAL",
    "ZACIAN",
    "ZAMAZENTA",
    "ETERNATUS",
    "KUBFU",
    "URSHIFU",
    "ZARUDE",
    "REGIELEKI",
    "REGIDRAGO",
    "GLASTRIER",
    "SPECTRIER",
    "CALYREX",
    "ENAMORUS",
    "WO_CHIEN",
    "CHIEN_PAO",
    "TING_LU",
    "CHI_YU",
    "KORAIDON",
    "MIRAIDON",
    "OKIDOGI",
    "MUNKIDORI",
    "FEZANDIPITI",
    "OGERPON",
    "TERAPAGOS",
    "PECHARUNT",
}

LATE_LEVEL_EXEMPT_FORM_ROWS = {
    "SPECIES_496",
    "SPECIES_497",
    "SPECIES_498",
    "SPECIES_501",
    "SPECIES_502",
}


@dataclasses.dataclass
class CheckResult:
    name: str
    status: str
    details: str


def rel(path: pathlib.Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def symbol_name(symbol: str) -> str:
    return symbol.replace("SPECIES_", "").replace("ITEM_", "").replace("MOVE_", "").replace("_", " ").title()


def is_late_level_exempt_species(species: str) -> bool:
    if species in phase6.LEGENDARY_OR_MYTHICAL or species in LATE_LEVEL_EXEMPT_FORM_ROWS:
        return True
    for root in LATE_LEVEL_EXEMPT_SPECIES_ROOTS:
        base = f"SPECIES_{root}"
        if species == base or species.startswith(base + "_"):
            return True
    return False


def normalize_species_token(token: str) -> str:
    match = re.search(r"SPECIES_[A-Z0-9_]+", token)
    return match.group(0) if match else token.strip()


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


def split_top_level_csv(text: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    current: list[str] = []
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current).strip())
    return parts


def read_define_numbers(path: pathlib.Path, prefix: str) -> dict[str, int]:
    values: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(rf"#define\s+({prefix}_[A-Z0-9_]+)\s+(\d+)\b", line.strip())
        if match:
            values[match.group(1)] = int(match.group(2))
    return values


def read_equ_numbers(path: pathlib.Path, prefix: str) -> dict[str, int]:
    values: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        match = re.match(rf"({prefix}_[A-Z0-9_]+)\s+equ\s+(\d+)\b", stripped)
        if not match:
            match = re.match(rf"\.equ\s+({prefix}_[A-Z0-9_]+)\s*,\s*(\d+)\b", stripped)
        if match:
            values[match.group(1)] = int(match.group(2))
    return values


def read_species_numbers() -> dict[str, int]:
    return read_define_numbers(ENGINE / "include" / "constants" / "species.h", "SPECIES")


def read_item_numbers() -> dict[str, int]:
    return read_define_numbers(ENGINE / "include" / "constants" / "item.h", "ITEM")


def read_item_names() -> dict[str, str]:
    item_numbers = read_item_numbers()
    lines = (ENGINE / "data" / "text" / "222.txt").read_text(encoding="utf-8", errors="replace").splitlines()
    names: dict[str, str] = {}
    for item, number in item_numbers.items():
        if 0 <= number < len(lines):
            names[item] = lines[number]
    return names


def parse_item_prices() -> dict[str, int]:
    text = (ENGINE / "data" / "itemdata" / "itemdata.c").read_text(encoding="utf-8", errors="replace")
    prices: dict[str, int] = {}
    for match in re.finditer(r"\[(ITEM_[A-Z0-9_]+)\]\s*=\s*\{", text):
        item = match.group(1)
        block, _ = extract_braced(text, match.end() - 1)
        price_match = re.search(r"ITEM_PRICE\((\d+)\)", block)
        if price_match:
            prices[item] = int(price_match.group(1))
    return prices


def parse_badge_mart() -> list[dict[str, Any]]:
    text = (ENGINE / "src" / "field" / "mart.c").read_text(encoding="utf-8", errors="replace")
    marker = "const struct BadgeMartItems sBadgeMart[] ="
    start = text.index("{", text.index(marker))
    block, _ = extract_braced(text, start)
    prices = parse_item_prices()
    names = read_item_names()
    numbers = read_item_numbers()
    rows = []
    for item, badges in re.findall(r"\{\s*(ITEM_[A-Z0-9_]+)\s*,\s*(\d+)\s*\}", block):
        rows.append(
            {
                "item": item,
                "name": names.get(item, symbol_name(item)),
                "id": numbers.get(item),
                "required_badges": int(badges),
                "price": prices.get(item),
            }
        )
    return rows


def item_icon_path(item: str) -> pathlib.Path:
    return ENGINE / "data" / "graphics" / "item" / f"{item.removeprefix('ITEM_').lower()}.png"


def parse_evolutions() -> list[dict[str, Any]]:
    text = (ENGINE / "data" / "Evolutions.c").read_text(encoding="utf-8", errors="replace")
    rows: list[dict[str, Any]] = []
    for match in re.finditer(r"\[(SPECIES_[A-Z0-9_]+)\]\s*=\s*\{", text):
        parent = match.group(1)
        block, _ = extract_braced(text, match.end() - 1)
        for line in block.splitlines():
            stripped = line.strip().rstrip(",")
            if not stripped.startswith("{ EVO_"):
                continue
            inner = stripped.strip("{} ")
            parts = split_top_level_csv(inner)
            if len(parts) < 3:
                continue
            method = parts[0]
            parameter = parts[1]
            target_token = parts[2]
            target = normalize_species_token(target_token)
            if target == "SPECIES_NONE":
                continue
            form_match = re.search(r"MON_WITH_FORM\(\s*SPECIES_[A-Z0-9_]+\s*,\s*(\d+)\s*\)", target_token)
            rows.append(
                {
                    "from": parent,
                    "from_name": symbol_name(parent),
                    "method": method,
                    "parameter": parameter,
                    "target": target,
                    "target_name": symbol_name(target),
                    "target_form": int(form_match.group(1)) if form_match else None,
                }
            )
    return rows


def approved_later_species(species_numbers: dict[str, int], evolutions: list[dict[str, Any]]) -> set[str]:
    graph: dict[str, set[str]] = defaultdict(set)
    for evo in evolutions:
        parent = evo["from"]
        target = evo["target"]
        graph[parent].add(target)
        graph[target].add(parent)

    approved = set(phase7.APPROVED_LATER_SPECIES) | set(phase6.APPROVED_LATER_PLACEMENTS)
    seen: set[str] = set()
    for species, number in species_numbers.items():
        if species in seen or not (1 <= number <= 493):
            continue
        queue = deque([species])
        component: set[str] = set()
        seen.add(species)
        while queue:
            current = queue.popleft()
            component.add(current)
            for nxt in graph[current]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        for member in component:
            if species_numbers.get(member, 0) > 493:
                approved.add(member)
    return approved


def approved_species_set() -> set[str]:
    species_numbers = read_species_numbers()
    evolutions = parse_evolutions()
    approved = {species for species, number in species_numbers.items() if 1 <= number <= 493}
    approved.update(approved_later_species(species_numbers, evolutions))
    return approved


def species_sort_key(species: str, species_numbers: dict[str, int]) -> tuple[int, str]:
    return (species_numbers.get(species, 99999), species)


def parse_random_legendary_pool() -> list[dict[str, Any]]:
    text = (ENGINE / "src" / "field" / "enemy_party.c").read_text(encoding="utf-8", errors="replace")
    marker = "sPerfectJohtoRandomLegendaryPool[]"
    start = text.index("{", text.index(marker))
    block, _ = extract_braced(text, start)
    species_numbers = read_species_numbers()
    tier_names = {
        "PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER": "weaker",
        "PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_TRUE": "true",
    }
    return [
        {
            "species": species,
            "name": symbol_name(species),
            "species_id": species_numbers.get(species),
            "min_badges": int(badges),
            "tier": tier_names.get(tier, tier),
            "rate_denominator": 4000 if tier.endswith("_TRUE") else 2000,
        }
        for species, badges, tier in re.findall(
            r"\{\s*(SPECIES_[A-Z0-9_]+)\s*,\s*(\d+)\s*,\s*(PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_[A-Z]+)\s*\}",
            block,
        )
    ]


def trainer_party(entry: phase7.Entry) -> list[dict[str, Any]]:
    party_match = re.search(r"(?ms)^        \.party\s*=\s*\{(.+?)^        \},", entry.block)
    if not party_match:
        return []
    mons = []
    for mon_block in re.findall(r"(?ms)^            \{\n(.+?)^            \},", party_match.group(1)):
        species = re.search(r"\.species\s*=\s*(SPECIES_[A-Z0-9_]+)", mon_block)
        level = re.search(r"\.level\s*=\s*(\d+)", mon_block)
        item = re.search(r"\.item\s*=\s*(ITEM_[A-Z0-9_]+)", mon_block)
        moves_match = re.search(r"\.moves\s*=\s*\{([^}]*)\}", mon_block)
        moves = re.findall(r"MOVE_[A-Z0-9_]+", moves_match.group(1)) if moves_match else []
        mons.append(
            {
                "species": species.group(1) if species else None,
                "name": symbol_name(species.group(1)) if species else None,
                "level": int(level.group(1)) if level else None,
                "item": item.group(1) if item else "ITEM_NONE",
                "moves": moves,
            }
        )
    return mons


def trainer_to_dict(entry: phase7.Entry) -> dict[str, Any]:
    return {
        "id": entry.trainer_id,
        "name": entry.name,
        "trainer_class": entry.trainer_class,
        "trainer_type": entry.trainer_type,
        "party_size": len(entry.species),
        "min_level": min(entry.levels) if entry.levels else None,
        "max_level": max(entry.levels) if entry.levels else None,
        "species": entry.species,
        "party": trainer_party(entry),
    }


def encounter_slot_dict(slot: phase6.Slot, rate: int | None = None) -> dict[str, Any]:
    return {
        "min_level": slot.min_level,
        "max_level": slot.max_level,
        "species": slot.species,
        "name": symbol_name(slot.species) if slot.species != "SPECIES_NONE" else "None",
        "rate_percent": rate,
    }


def encounter_to_dict(entry: phase6.Encounter) -> dict[str, Any]:
    return {
        "area": entry.key,
        "rates": {
            "walk": entry.rate_walk,
            "surf": entry.rate_surf,
            "rock_smash": entry.rate_rock_smash,
            "old_rod": entry.rate_old_rod,
            "good_rod": entry.rate_good_rod,
            "super_rod": entry.rate_super_rod,
        },
        "land": [
            {
                "slot": index,
                "level": entry.levels[index],
                "morning": entry.morning[index],
                "day": entry.day[index],
                "night": entry.night[index],
                "rate_percent": phase6.LAND_RATES[index],
            }
            for index in range(len(entry.levels))
        ],
        "surf": [encounter_slot_dict(slot, phase6.SURF_RATES[index]) for index, slot in enumerate(entry.surf)],
        "rock_smash": [encounter_slot_dict(slot, [80, 20][index] if index < 2 else None) for index, slot in enumerate(entry.rock_smash)],
        "old_rod": [encounter_slot_dict(slot, phase6.FISH_RATES_PHASE6[index]) for index, slot in enumerate(entry.old_rod)],
        "good_rod": [encounter_slot_dict(slot, phase6.FISH_RATES_PHASE6[index]) for index, slot in enumerate(entry.good_rod)],
        "super_rod": [encounter_slot_dict(slot, phase6.FISH_RATES_PHASE6[index]) for index, slot in enumerate(entry.super_rod)],
        "rare_notes": entry.rare_notes,
        "common_notes": entry.common_notes,
    }


def run_command(command: list[str], cwd: pathlib.Path, timeout: int = 120) -> CheckResult:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            env={**os.environ, "PYTHONUTF8": "1"},
        )
    except FileNotFoundError:
        return CheckResult(" ".join(command), "SKIP", f"{command[0]} is not available on PATH")
    except subprocess.TimeoutExpired:
        return CheckResult(" ".join(command), "FAIL", f"timed out after {timeout}s")
    output = completed.stdout.strip()
    if completed.returncode == 0:
        detail = output.splitlines()[-1] if output else "completed"
        return CheckResult(" ".join(command), "PASS", detail)
    return CheckResult(" ".join(command), "FAIL", output[-1200:] if output else f"exit code {completed.returncode}")


def validate_text_archives() -> CheckResult:
    module_path = ENGINE / "tools" / "source" / "dumptools" / "validate_text_archive.py"
    spec = importlib.util.spec_from_file_location("validate_text_archive", module_path)
    if spec is None or spec.loader is None:
        return CheckResult("text archive validation", "FAIL", "could not import validate_text_archive.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    valid_chars, valid_commands = module.load_charmap(ENGINE / "charmap.txt")
    errors: list[str] = []
    for path in sorted((ENGINE / "data" / "text").glob("*.txt")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if not module.validate_text(text, valid_chars, valid_commands, str(path)):
            errors.append(rel(path))
    if errors:
        return CheckResult("text archive validation", "FAIL", "invalid text archives: " + ", ".join(errors[:20]))
    return CheckResult("text archive validation", "PASS", f"{len(list((ENGINE / 'data' / 'text').glob('*.txt')))} archives passed")


def validate_learnsets_generation() -> CheckResult:
    with tempfile.TemporaryDirectory(prefix="perfect_johto_learnsets_") as tmp:
        tmp_path = pathlib.Path(tmp)
        result = run_command(
            [
                sys.executable,
                "scripts/build_learnsets.py",
                "--learnsets",
                "data/learnsets/learnsets.json",
                "--machineout",
                str(tmp_path / "MachineMoveLearnsets.c"),
                "--levelupout",
                str(tmp_path / "LevelupLearnsets.c"),
                "--eggout",
                str(tmp_path / "EggLearnsets.c"),
                "--tutorout",
                str(tmp_path / "TutorMoveLearnsets.c"),
            ],
            ENGINE,
        )
        return dataclasses.replace(result, name="Learnset generation")


def validate_learnset_accessibility() -> CheckResult:
    learnsets = json.loads((ENGINE / "data" / "learnsets" / "learnsets.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    rows_with_egg_moves = 0
    total_egg_moves = 0
    legendary_late_entries = 0

    for species, learnset in learnsets.items():
        level_moves = learnset.get("LevelMoves", [])
        egg_moves = learnset.get("EggMoves", [])
        level_move_names = [entry.get("Move") for entry in level_moves]
        level_move_set = set(level_move_names)

        if egg_moves:
            rows_with_egg_moves += 1
            total_egg_moves += len(egg_moves)
            missing_egg_moves = [move for move in egg_moves if move not in level_move_set]
            if missing_egg_moves:
                errors.append(f"{species} egg moves missing from level-up: {', '.join(missing_egg_moves[:8])}")

        duplicates = [move for move, count in Counter(level_move_names).items() if count > 1]
        if duplicates:
            errors.append(f"{species} duplicate level-up moves: {', '.join(duplicates[:8])}")

        late_moves = [entry for entry in level_moves if int(entry.get("Level", 0)) >= 60]
        if is_late_level_exempt_species(species):
            legendary_late_entries += len(late_moves)
        elif late_moves:
            formatted = ", ".join(f"{entry.get('Move')}@{entry.get('Level')}" for entry in late_moves[:8])
            errors.append(f"{species} non-legendary level 60+ moves: {formatted}")

    if errors:
        return CheckResult("Learnset accessibility validation", "FAIL", "; ".join(errors[:20]))
    return CheckResult(
        "Learnset accessibility validation",
        "PASS",
        f"{rows_with_egg_moves} egg-move rows/{total_egg_moves} egg moves are level-up accessible; non-legendary moves stay below 60; {legendary_late_entries} legendary late moves preserved",
    )


def validate_phase6() -> CheckResult:
    entries = phase6.parse_encounters(phase6.ENCOUNTERS)
    phase6.apply_phase6(entries)
    errors = phase6.validate(entries)
    if errors:
        return CheckResult("Phase 6 encounter validation", "FAIL", "; ".join(errors[:20]))
    meaningful = [entry for entry in entries if phase6.is_meaningful(entry)]
    with_rares = [entry for entry in meaningful if entry.rare_notes]
    return CheckResult("Phase 6 encounter validation", "PASS", f"{len(with_rares)}/{len(meaningful)} meaningful areas have rare placements")


def validate_phase7() -> CheckResult:
    text = phase7.TRAINERS.read_text(encoding="utf-8", errors="replace")
    errors = phase7.validate(text)
    if errors:
        return CheckResult("Phase 7 trainer validation", "FAIL", "; ".join(errors[:20]))
    entries = phase7.parse_entries(text)
    six_bosses = [
        entry
        for entry in entries
        if (
            entry.trainer_class.startswith("TRAINERCLASS_LEADER_")
            or entry.trainer_class.startswith("TRAINERCLASS_ELITE_FOUR_")
            or entry.trainer_class in {"TRAINERCLASS_CHAMPION", "TRAINERCLASS_PKMN_TRAINER_RED"}
        )
        and len(entry.species) == 6
    ]
    return CheckResult("Phase 7 trainer validation", "PASS", f"{len(six_bosses)} mandatory leader/E4/champion/Red records have six Pokemon")


def validate_phase8() -> CheckResult:
    errors = phase8.validate_outputs()
    script_path = phase8.DOJO_SCRIPT
    text_path = phase8.DOJO_TEXT
    if not script_path.exists():
        errors.append(f"missing Dojo script {rel(script_path)}")
    elif script_path.read_text(encoding="utf-8", errors="replace") != phase8.generate_dojo_script():
        errors.append("Dojo script does not match Phase 8 generator output")
    if not text_path.exists():
        errors.append(f"missing Dojo text {rel(text_path)}")
    elif text_path.read_text(encoding="utf-8", errors="replace").splitlines() != phase8.DOJO_TEXT_LINES:
        errors.append("Dojo text does not match Phase 8 generator output")
    if errors:
        return CheckResult("Phase 8 postgame validation", "FAIL", "; ".join(errors[:20]))
    return CheckResult("Phase 8 postgame validation", "PASS", f"{len(phase8.LEGENDARIES) + len(phase8.NATIVE_EVENTS)} legendary/mythical entries validated")


def validate_forbidden_config_and_scope() -> CheckResult:
    errors: list[str] = []
    for path in [ENGINE / "include" / "config.h", ENGINE / "armips" / "include" / "config.s"]:
        text = path.read_text(encoding="utf-8", errors="replace")
        for config in FORBIDDEN_ACTIVE_CONFIGS:
            if re.search(rf"^\s*#\s*define\s+{config}\b", text, flags=re.MULTILINE) or re.search(rf"^\s*{config}\s*=\s*1\b", text, flags=re.MULTILINE):
                errors.append(f"{config} is active in {rel(path)}")

    species_numbers = read_species_numbers()
    approved = approved_species_set()
    forbidden_species: list[str] = []
    token_hits: list[str] = []
    for path in GAMEPLAY_SPECIES_FILES + [ENGINE / "src" / "field" / "mart.c"]:
        text = path.read_text(encoding="utf-8", errors="replace")
        for species in set(re.findall(r"SPECIES_[A-Z0-9_]+", text)):
            number = species_numbers.get(species)
            if species == "SPECIES_NONE":
                continue
            if (number is None or number > 493) and species not in approved:
                forbidden_species.append(f"{rel(path)}:{species}")
        for token in FORBIDDEN_GAMEPLAY_TOKENS:
            if token in text:
                token_hits.append(f"{rel(path)}:{token}")
    if forbidden_species:
        errors.append("unapproved later species in gameplay files: " + ", ".join(sorted(forbidden_species)[:20]))
    if token_hits:
        errors.append("forbidden gimmick tokens in gameplay files: " + ", ".join(sorted(token_hits)[:20]))
    if errors:
        return CheckResult("Forbidden config and scope scan", "FAIL", "; ".join(errors))
    return CheckResult("Forbidden config and scope scan", "PASS", "forbidden configs disabled; gameplay placement files stay inside approved species scope")


def validate_random_legendary() -> CheckResult:
    errors: list[str] = []
    pool = parse_random_legendary_pool()
    species_numbers = read_species_numbers()
    for entry in pool:
        species = entry["species"]
        if species not in phase6.LEGENDARY_OR_MYTHICAL:
            errors.append(f"{species} is not in the Gen 1-4 legendary/mythical set")
        if species_numbers.get(species, 9999) > 493:
            errors.append(f"{species} is later than Gen 4")
    text = (ENGINE / "src" / "field" / "enemy_party.c").read_text(encoding="utf-8", errors="replace")
    required_fragments = [
        "if (badgeCount < 4)",
        "PERFECT_JOHTO_RANDOM_LEGENDARY_ROLL_DENOMINATOR 4000",
        "PERFECT_JOHTO_RANDOM_LEGENDARY_WEAKER_HITS 2",
        "PERFECT_JOHTO_RANDOM_LEGENDARY_TRUE_HITS 1",
        "PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER",
        "PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_TRUE",
        "MOVE_TELEPORT",
        "PerfectJohto_SetRandomLegendaryFleeMove(encounterPartyPokemon);",
        "BATTLE_TYPE_SAFARI",
        "BATTLE_TYPE_ROAMER",
        "BATTLE_TYPE_PAL_PARK",
        "BATTLE_TYPE_CATCHING_DEMO",
        "BATTLE_TYPE_BUG_CONTEST",
        "PerfectJohto_TryRandomLegendary(encounterInfo, encounterPartyPokemon, encounterBattleParam);",
    ]
    for fragment in required_fragments:
        if fragment not in text:
            errors.append(f"missing random legendary fragment: {fragment}")
    if "Save_Roamer" in text or "roamer save" in text.lower():
        errors.append("random legendary source appears to touch roamer save state")
    if errors:
        return CheckResult("Random legendary validation", "FAIL", "; ".join(errors))
    weaker_count = sum(1 for entry in pool if entry.get("tier") == "weaker")
    true_count = sum(1 for entry in pool if entry.get("tier") == "true")
    return CheckResult(
        "Random legendary validation",
        "PASS",
        f"{len(pool)} Gen 1-4 legendary/mythical pool entries; {weaker_count} weaker/mystical at 1/2000 and {true_count} stronger true-tier at 1/4000; flee move and exclusions present",
    )


def validate_dojo_flags_and_script() -> CheckResult:
    errors: list[str] = []
    flag_values = read_equ_numbers(ENGINE / "armips" / "include" / "flags.s", "FLAG")
    for flag, value in phase8.PHASE8_FLAGS.items():
        if flag_values.get(flag) != value:
            errors.append(f"{flag} expected {value}, found {flag_values.get(flag)}")
    reverse: dict[int, list[str]] = defaultdict(list)
    for flag, value in flag_values.items():
        reverse[value].append(flag)
    for value in range(2865, 2888):
        meaningful = [flag for flag in reverse.get(value, []) if not flag.startswith("FLAG_UNK_") and not flag.startswith("FLAG_PHASE8_")]
        if meaningful:
            errors.append(f"Phase 8 flag value {value} collides with {', '.join(meaningful)}")
    script = phase8.DOJO_SCRIPT.read_text(encoding="utf-8", errors="replace")
    for event in phase8.LEGENDARIES:
        label = "_p8_" + event.name.lower().replace("-", "_")
        label_start = script.find(label + ":")
        if label_start < 0:
            errors.append(f"missing label {label}")
            continue
        next_label = re.search(r"\n_[A-Za-z0-9_]+:", script[label_start + 1 :])
        block = script[label_start : label_start + 1 + next_label.start()] if next_label else script[label_start:]
        expected = [
            f"goto_if_set {event.flag}, _p8_already_caught",
            "wild_battle",
            "get_static_encounter_outcome VAR_TEMP_x4002",
            "compare VAR_TEMP_x4002, 4",
            "goto_if_ne _p8_not_caught",
            f"setflag {event.flag}",
        ]
        for fragment in expected:
            if fragment not in block:
                errors.append(f"{event.name} block missing {fragment}")
    if errors:
        return CheckResult("Dojo script and flag validation", "FAIL", "; ".join(errors[:20]))
    return CheckResult("Dojo script and flag validation", "PASS", "Dojo labels, capture-only outcome checks, and late flag aliases validated")


def validate_marts_and_items() -> CheckResult:
    errors: list[str] = []
    mart = parse_badge_mart()
    mart_by_item = {row["item"]: row for row in mart}
    prices = parse_item_prices()
    c_items = read_item_numbers()
    asm_items = read_equ_numbers(ENGINE / "asm" / "include" / "items.inc", "ITEM")
    if c_items.get("ITEM_MAX_CANDY") != 1058:
        errors.append("ITEM_MAX_CANDY missing or wrong in C item constants")
    if asm_items.get("ITEM_MAX_CANDY") != 1058:
        errors.append("ITEM_MAX_CANDY missing or wrong in asm item constants")
    if prices.get("ITEM_MAX_CANDY") != 8000:
        errors.append("Max Candy price is not 8000")
    if mart_by_item.get("ITEM_MAX_CANDY", {}).get("required_badges") != 12:
        errors.append("Max Candy does not unlock at 12 badges")
    for item in IV_CANDIES:
        if prices.get(item) != 2000:
            errors.append(f"{item} price is not 2000")
        if mart_by_item.get(item, {}).get("required_badges") != 5:
            errors.append(f"{item} does not unlock at 5 badges")
    for item in MINTS + ["ITEM_ABILITY_CAPSULE"]:
        if prices.get(item) != 1000:
            errors.append(f"{item} price is not 1000")
        if mart_by_item.get(item, {}).get("required_badges") != 3:
            errors.append(f"{item} does not unlock at 3 badges")
    if prices.get("ITEM_ABILITY_PATCH") != 1000:
        errors.append("ITEM_ABILITY_PATCH price is not 1000")
    if mart_by_item.get("ITEM_ABILITY_PATCH", {}).get("required_badges") != 6:
        errors.append("ITEM_ABILITY_PATCH does not unlock at 6 badges")
    party_text = (ENGINE / "src" / "individual" / "PartyMenu_HandleUseItemOnMon.c").read_text(encoding="utf-8", errors="replace")
    if "if (itemId == ITEM_MAX_CANDY)" not in party_text or "MON_DATA_HP_IV; i <= MON_DATA_SPDEF_IV; i++" not in party_text:
        errors.append("Max Candy six-IV loop was not found")
    if len(mart) > 203:
        errors.append(f"badge mart has {len(mart)} entries, over UI limit 203")
    forbidden_stock = [row["item"] for row in mart if any(token in row["item"] for token in ["Z_", "DYNAMAX", "GIGANTAMAX", "TERA", "MEGA", "PRIMAL"])]
    if forbidden_stock:
        errors.append("forbidden gimmick items stocked: " + ", ".join(forbidden_stock))
    if errors:
        return CheckResult("Item, mart, and Max Candy validation", "FAIL", "; ".join(errors))
    return CheckResult("Item, mart, and Max Candy validation", "PASS", f"{len(mart)} badge-mart entries; Max Candy/IV candy/customization gates validated")


def validate_badge_mart_item_icons() -> CheckResult:
    errors: list[str] = []
    placeholder = ENGINE / "data" / "graphics" / "item" / "unknown_7a.png"
    placeholder_bytes = placeholder.read_bytes() if placeholder.exists() else b""
    for row in parse_badge_mart():
        item = row["item"]
        icon_path = item_icon_path(item)
        if not icon_path.exists():
            errors.append(f"{item} missing icon {rel(icon_path)}")
            continue
        if placeholder_bytes and icon_path.read_bytes() == placeholder_bytes:
            errors.append(f"{item} still uses placeholder icon {rel(icon_path)}")
    if errors:
        return CheckResult("Badge mart item icon validation", "FAIL", "; ".join(errors[:20]))
    return CheckResult("Badge mart item icon validation", "PASS", f"{len(parse_badge_mart())} badge-mart item icons exist and are not placeholders")


def validate_evolutions_and_forms() -> CheckResult:
    errors: list[str] = []
    warnings: list[str] = []
    species_numbers = read_species_numbers()
    evolutions = parse_evolutions()
    approved = approved_species_set()
    mart_items = {row["item"] for row in parse_badge_mart()}
    learnsets = json.loads((ENGINE / "data" / "learnsets" / "learnsets.json").read_text(encoding="utf-8"))
    for evo in evolutions:
        if evo["from"] not in approved and evo["target"] not in approved:
            continue
        if evo["method"] == "EVO_TRADE":
            errors.append(f"trade-only evolution remains: {evo['from']} -> {evo['target']}")
        if evo["method"].startswith("EVO_ITEM") or evo["method"] == "EVO_STONE":
            item = evo["parameter"]
            if item.startswith("ITEM_") and item not in mart_items:
                errors.append(f"approved-scope evolution item not in badge mart: {item} for {evo['from']} -> {evo['target']}")
        if evo["method"] in {"EVO_HAS_MOVE", "EVO_HAS_MOVE_TYPE"} and evo["parameter"].startswith("MOVE_"):
            move = evo["parameter"]
            level_moves = learnsets.get(evo["from"], {}).get("LevelMoves", [])
            levels = [entry.get("Level") for entry in level_moves if entry.get("Move") == move]
            if not levels:
                errors.append(f"known-move evolution move missing from learnset: {evo['from']} needs {move}")
            elif min(levels) > 60:
                errors.append(f"known-move evolution move too late: {evo['from']} learns {move} at {min(levels)}")
    if not any(evo["target"] == "SPECIES_DUDUNSPARCE_THREE_SEGMENT" for evo in evolutions):
        warnings.append("Dudunsparce Three-Segment special access is not implemented")
    if not any(evo["target"] == "SPECIES_URSALUNA_BLOODMOON" for evo in evolutions):
        warnings.append("Ursaluna Bloodmoon special access is not implemented")
    if errors:
        return CheckResult("Evolution and form validation", "FAIL", "; ".join(errors[:30]))
    detail = "no trade-only approved-scope evolutions; evolution items and known-move methods validated"
    if warnings:
        return CheckResult("Evolution and form validation", "WARN", detail + "; " + "; ".join(warnings))
    return CheckResult("Evolution and form validation", "PASS", detail)


def validate_game_modes() -> CheckResult:
    required_tokens = {
        ENGINE / "include" / "perfect_johto_game_modes.h": [
            "PERFECT_JOHTO_MODE_NORMAL",
            "PERFECT_JOHTO_MODE_CHALLENGE",
            "PERFECT_JOHTO_MODE_HARDCORE",
            "PERFECT_JOHTO_MODE_NUZLOCKE",
            "VAR_PERFECT_JOHTO_NUZLOCKE_LEGAL_AREA 0x416D",
            "VAR_PERFECT_JOHTO_GAME_MODE           0x416E",
            "VAR_PERFECT_JOHTO_LEVEL_CAP           0x416F",
        ],
        ENGINE / "include" / "config.h": [
            "#define IMPLEMENT_LEVEL_CAP",
            "#define LEVEL_CAP_VARIABLE 0x416F",
        ],
        ENGINE / "include" / "save.h": [
            "perfectJohtoNuzlockeAreas",
        ],
        ENGINE / "hooks": [
            "0053 PerfectJohto_OakModeMenuPrintHook 021E716C 0",
            "0053 PerfectJohto_OakModeMenuInputHook 021E7188 0",
            "arm9 PerfectJohto_BattleSystem_GetBattleStyle 0202AD90 1",
            "0012 ImplementLevelCap_hook 02245A28 3",
        ],
        ENGINE / "asm" / "battle" / "battle_hooks.s": [
            "bl PerfectJohto_ReleaseFaintedBattleParty",
        ],
        ENGINE / "src" / "perfect_johto_game_modes.c": [
            "PerfectJohto_OakModeMenuApplySelection",
            "PerfectJohto_GetLevelCap",
            "PerfectJohto_NuzlockePrepareBattleArea",
            "PerfectJohto_NuzlockeTryClaimGift",
            "PerfectJohto_ReleaseFaintedBattleParty",
        ],
        ENGINE / "src" / "battle" / "battle_controller_player.c": [
            "PerfectJohto_ModeDisablesBattleItems",
        ],
        ENGINE / "src" / "individual" / "CalculateBallShakes.c": [
            "PerfectJohto_NuzlockeCanCatchCurrentBattle",
        ],
        ENGINE / "data" / "text" / "219.txt": [
            "Choose a game mode.",
            "NORMAL",
            "CHALLENGE",
            "HARDCORE",
            "NUZLOCKE",
        ],
        DOCS / "GAME_MODES.md": [
            "# Game Modes",
            "The last non-Egg party Pokemon is never released",
            "Level caps are enabled only in Challenge, Hardcore, and Nuzlocke",
        ],
    }

    errors: list[str] = []
    for path, tokens in required_tokens.items():
        if not path.exists():
            errors.append(f"missing {rel(path)}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                errors.append(f"{rel(path)} missing {token!r}")
    config_text = (ENGINE / "include" / "config.h").read_text(encoding="utf-8", errors="replace")
    if re.search(r"^\s*#define\s+UNCAP_CANDIES_FROM_LEVEL_CAP\b", config_text, flags=re.MULTILINE):
        errors.append("UNCAP_CANDIES_FROM_LEVEL_CAP must stay disabled so Rare Candy respects level caps")
    if errors:
        return CheckResult("Game mode validation", "FAIL", "; ".join(errors[:20]))
    return CheckResult("Game mode validation", "PASS", "mode selector, cap, battle item, death release, and Nuzlocke hooks documented")


def validate_pokedex_area_status() -> CheckResult:
    candidates = [
        ENGINE / "data" / "ZukanArea.c",
        ENGINE / "data" / "PokedexArea.c",
        ROOT / "pokeheartgold-master" / "files" / "application" / "zukanlist" / "zukan_area.narc",
    ]
    if any(path.exists() for path in candidates):
        return CheckResult("Pokedex area data status", "WARN", "encounter tables changed; no Phase 9 regeneration hook confirmed for Pokedex area data")
    return CheckResult("Pokedex area data status", "WARN", "no separate Pokedex area-data source/regeneration step was identified; confirm engine derivation before release")


def validate_build_readiness() -> tuple[CheckResult, dict[str, Any]]:
    tools = {
        "git": shutil.which("git"),
        "make": shutil.which("make"),
        "cmake": shutil.which("cmake"),
        "armips": shutil.which("armips"),
        "docker": shutil.which("docker"),
        "arm-none-eabi-gcc": shutil.which("arm-none-eabi-gcc"),
        "python": sys.executable,
    }
    rom_nds = ENGINE / "rom.nds"
    baserom_nds = ROOT / "pokeheartgold-master" / "baserom.nds"
    details = {
        "tools": {name: {"available": bool(path), "path": path} for name, path in tools.items()},
        "rom_nds": {"exists": rom_nds.exists(), "path": rel(rom_nds)},
        "baserom_nds": {"exists": baserom_nds.exists(), "path": rel(baserom_nds)},
        "make_dry_run": None,
        "armips_dojo_assembly": None,
        "docker_route": "available" if tools["docker"] else "docker missing",
    }
    if tools["make"]:
        result = run_command(["make", "-n"], ENGINE, timeout=60)
        details["make_dry_run"] = dataclasses.asdict(result)
    else:
        details["make_dry_run"] = {"status": "SKIP", "details": "make is not available on PATH"}
    if tools["armips"]:
        (ENGINE / "build" / "a012").mkdir(parents=True, exist_ok=True)
        result = run_command(["armips", "armips/scr_seq/scr_seq_00832_phase8_dojo.s"], ENGINE, timeout=60)
        details["armips_dojo_assembly"] = dataclasses.asdict(result)
    else:
        details["armips_dojo_assembly"] = {"status": "SKIP", "details": "armips is not available on PATH"}
    missing = [name for name, path in tools.items() if name != "python" and not path]
    if not rom_nds.exists():
        missing.append("rom.nds")
    if missing:
        return CheckResult("Build readiness", "WARN", "missing requirements: " + ", ".join(missing)), details
    return CheckResult("Build readiness", "PASS", "required tools and rom.nds found; see build details for dry-run status"), details


def run_validations() -> tuple[list[CheckResult], dict[str, Any]]:
    results: list[CheckResult] = []
    build_details: dict[str, Any] = {}
    try:
        json.loads((ENGINE / "data" / "learnsets" / "learnsets.json").read_text(encoding="utf-8"))
        results.append(CheckResult("Learnset JSON parse", "PASS", "data/learnsets/learnsets.json parsed"))
    except Exception as exc:  # noqa: BLE001
        results.append(CheckResult("Learnset JSON parse", "FAIL", str(exc)))
    results.append(validate_learnsets_generation())
    results.append(validate_learnset_accessibility())
    results.append(validate_phase6())
    results.append(validate_phase7())
    results.append(validate_phase8())
    results.append(run_command([sys.executable, "scripts/validate_trainers_s.py", "data/Trainers.c"], ENGINE))
    results.append(validate_text_archives())
    results.append(validate_forbidden_config_and_scope())
    results.append(validate_random_legendary())
    results.append(validate_dojo_flags_and_script())
    results.append(validate_marts_and_items())
    results.append(validate_badge_mart_item_icons())
    results.append(validate_evolutions_and_forms())
    results.append(validate_game_modes())
    results.append(validate_pokedex_area_status())
    build_result, build_details = validate_build_readiness()
    results.append(build_result)
    return results, build_details


def build_exports(build_details: dict[str, Any], results: list[CheckResult]) -> dict[str, Any]:
    species_numbers = read_species_numbers()
    item_numbers = read_item_numbers()
    item_names = read_item_names()
    item_prices = parse_item_prices()
    evolutions = parse_evolutions()
    approved_later = approved_later_species(species_numbers, evolutions)
    approved_all = approved_species_set()

    entries = phase6.parse_encounters(phase6.ENCOUNTERS)
    phase6.apply_phase6(entries)
    trainer_entries = phase7.parse_entries(phase7.TRAINERS.read_text(encoding="utf-8", errors="replace"))
    trainers = [trainer_to_dict(entry) for entry in trainer_entries]
    boss_trainers = [
        trainer
        for trainer in trainers
        if trainer["trainer_class"].startswith("TRAINERCLASS_LEADER_")
        or trainer["trainer_class"].startswith("TRAINERCLASS_ELITE_FOUR_")
        or trainer["trainer_class"]
        in {
            "TRAINERCLASS_CHAMPION",
            "TRAINERCLASS_PKMN_TRAINER_RED",
            "TRAINERCLASS_PKMN_TRAINER_LANCE",
            "TRAINERCLASS_RIVAL",
            "TRAINERCLASS_ROCKET_BOSS",
            "TRAINERCLASS_EXECUTIVE_ARIANA",
            "TRAINERCLASS_EXECUTIVE_ARCHER",
            "TRAINERCLASS_EXECUTIVE_PROTON",
            "TRAINERCLASS_EXECUTIVE_PETREL",
        }
    ]
    mart = parse_badge_mart()
    mart_by_item = {row["item"]: row for row in mart}
    random_pool = parse_random_legendary_pool()

    proper_legends = [
        {
            "name": event.name,
            "species": event.species,
            "level": event.level,
            "flag": event.flag,
            "category": event.category,
            "location": event.location,
            "prerequisites": event.prerequisites,
            "encounter_type": event.encounter_type,
            "hide_flags": list(event.hide_flags),
        }
        for event in phase8.LEGENDARIES
    ]
    native_legends = [
        {"name": name, "encounter_type": kind, "level": level, "location": location, "prerequisites": prereq}
        for name, kind, level, location, prereq in phase8.NATIVE_EVENTS
    ]

    approved_evolutions = [evo for evo in evolutions if evo["from"] in approved_all or evo["target"] in approved_all]
    trade_replacements = [
        evo
        for evo in approved_evolutions
        if evo["method"] in {"EVO_STONE", "EVO_ITEM_DAY", "EVO_ITEM_NIGHT", "EVO_HAS_MOVE", "EVO_HAS_MOVE_TYPE"}
        and (
            evo["parameter"].startswith("ITEM_")
            or evo["parameter"] in {"MOVE_RAGE_FIST", "MOVE_PSYSHIELD_BASH", "MOVE_LEAF_BLADE", "MOVE_HYPER_DRILL"}
        )
    ]

    level_values = [level for trainer in trainers for level in [trainer["min_level"], trainer["max_level"]] if level is not None]
    level_curve = {
        "summary": {
            "min_trainer_level": min(level_values) if level_values else None,
            "max_trainer_level": max(level_values) if level_values else None,
            "johto_leaders": "Falkner 13-14 through Clair 46-50",
            "first_league": "Will 50-54 through Lance 58-60",
            "kanto_leaders": "early Kanto 58-66 through Blue 78-82",
            "postgame": "Elite Four rematches 78-84, legacy Lance rematch 82-88, Gym rematches 66-90, Champion Circuit trainers 92-96",
        },
        "bosses": boss_trainers,
    }

    customization_items = [
        mart_by_item[item]
        for item in [*MINTS, "ITEM_ABILITY_CAPSULE", "ITEM_ABILITY_PATCH", *IV_CANDIES, *EV_ITEMS]
        if item in mart_by_item
    ]

    exports = {
        "pokemon_availability.json": {
            "summary": {
                "gen1_4_species_count": 493,
                "approved_later_exception_count": len(approved_later),
                "meaningful_areas_with_rare_layer": sum(1 for entry in entries if phase6.is_meaningful(entry) and entry.rare_notes),
                "proper_legendary_entries": len(proper_legends) + len(native_legends),
                "pokedex_area_status": "needs release confirmation",
            },
            "sources": [
                "data/Encounters.c",
                "data/SafariEncounters.c",
                "data/Headbutt.c",
                "armips/scr_seq/scr_seq_00832_phase8_dojo.s",
                "docs/phase6_obtainability_report.md",
                "docs/phase8_postgame_report.md",
            ],
        },
        "approved_scope.json": {
            "rules": [
                "All Gen 1-4 Pokemon are in scope.",
                "Later direct evolutions of Gen 1-4 families are in scope.",
                "Later regional/new forms of Gen 1-4 families are in scope.",
                "Unrelated Gen 5+ Pokemon and forbidden battle gimmicks are out of scope.",
            ],
            "gen1_4_range": {"min": 1, "max": 493},
            "approved_later_exceptions": sorted(approved_later, key=lambda s: species_sort_key(s, species_numbers)),
        },
        "approved_later_exceptions.json": [
            {"species": species, "species_id": species_numbers.get(species), "name": symbol_name(species)}
            for species in sorted(approved_later, key=lambda s: species_sort_key(s, species_numbers))
        ],
        "evolutions.json": approved_evolutions,
        "trade_evolution_replacements.json": trade_replacements,
        "wild_encounters.json": [encounter_to_dict(entry) for entry in entries],
        "rare_encounters.json": [
            {"area": entry.key, "notes": entry.rare_notes}
            for entry in entries
            if phase6.is_meaningful(entry) and entry.rare_notes
        ],
        "random_legendary_surprise.json": {
            "pool": random_pool,
            "rates": EXPECTED_RANDOM_LEGENDARY_RATES,
            "roll_model": "One tier roll is made after a normal eligible wild encounter succeeds: weaker/mystical-tier species have two hits in 4000 (1/2000 aggregate), stronger true/cover-story species have one hit in 4000 (1/4000 aggregate), then one species is selected from the matching unlocked tier.",
            "flee_behavior": "Generated surprise legendaries receive Teleport in move slot 4, giving wild AI a move-based chance to flee each turn.",
            "blocked_battle_types": [
                "BATTLE_TYPE_TRAINER",
                "BATTLE_TYPE_SAFARI",
                "BATTLE_TYPE_ROAMER",
                "BATTLE_TYPE_PAL_PARK",
                "BATTLE_TYPE_CATCHING_DEMO",
                "BATTLE_TYPE_BUG_CONTEST",
            ],
            "level_clamps": [
                {"badges": "4", "min_level": 25, "max_level": 32},
                {"badges": "5", "min_level": 32, "max_level": 38},
                {"badges": "6-7", "min_level": 38, "max_level": 45},
                {"badges": "8-11", "min_level": 45, "max_level": 55},
                {"badges": "12-15", "min_level": 50, "max_level": 60},
                {"badges": "16", "min_level": 55, "max_level": 70},
            ],
        },
        "proper_legendary_events.json": {"native": native_legends, "dojo_dossiers": proper_legends},
        "static_and_gift_pokemon.json": {
            "static": native_legends + proper_legends,
            "gift_export_status": "Phase 9 exports the Phase 8 static/dossier layer; pre-existing gifts are not exhaustively changed by Phases 6-8.",
        },
        "trainer_teams.json": trainers,
        "boss_battles.json": boss_trainers,
        "gym_leaders.json": [trainer for trainer in trainers if trainer["trainer_class"].startswith("TRAINERCLASS_LEADER_")],
        "elite_four_champions.json": [
            trainer
            for trainer in trainers
            if trainer["trainer_class"].startswith("TRAINERCLASS_ELITE_FOUR_")
            or trainer["trainer_class"] in {"TRAINERCLASS_CHAMPION", "TRAINERCLASS_PKMN_TRAINER_RED", "TRAINERCLASS_PKMN_TRAINER_LANCE"}
        ],
        "rematches.json": [
            trainer
            for trainer in trainers
            if trainer["id"] in set(range(701, 728)) | {733, 734, 735, 736, 737}
        ],
        "champion_circuit.json": {
            "unlock_rules": [
                "Lance and Blue unlock after 16 badges.",
                "Red rematch, Steven, Wallace, Cynthia, and Arceus require original Mt. Silver Red defeat.",
            ],
            "trainers": [
                trainer
                for trainer in trainers
                if trainer["id"] in {733, 727, 260, 738, 739, 740}
            ],
        },
        "items_and_marts.json": {
            "badge_mart_count": len(mart),
            "badge_mart_ui_limit": 203,
            "badge_mart": mart,
        },
        "customization_items.json": customization_items,
        "max_candy.json": {
            "item": "ITEM_MAX_CANDY",
            "id": item_numbers.get("ITEM_MAX_CANDY"),
            "name": item_names.get("ITEM_MAX_CANDY", "Max Candy"),
            "price": item_prices.get("ITEM_MAX_CANDY"),
            "required_badges": mart_by_item.get("ITEM_MAX_CANDY", {}).get("required_badges"),
            "effect": "Sets all six IVs to 31 if at least one IV can change.",
        },
        "level_curve.json": level_curve,
        "kanto_postgame.json": {
            "dojo_hub": "Saffron Fighting Dojo postgame hub after 16 badges.",
            "champion_circuit": exports_champion_placeholder(),
            "legendary_dossiers": proper_legends,
        },
        "known_risks.json": {
            "validation_status": [dataclasses.asdict(result) for result in results],
            "build_readiness": build_details,
            "risks": known_risks(),
        },
    }
    exports["kanto_postgame.json"]["champion_circuit"] = exports["champion_circuit.json"]
    return exports


def exports_champion_placeholder() -> dict[str, Any]:
    return {}


def known_risks() -> list[dict[str, str]]:
    return [
        {"risk": "Full ROM build not confirmed in current PowerShell environment", "status": "blocked until build tools are available on PATH; ROM input status is tracked in docs/BUILD_AND_TESTING.md"},
        {"risk": "Dojo script not assembled locally if armips is missing", "status": "static script validation only"},
        {"risk": "Runtime behavior not playtested", "status": "use docs/PLAYTEST_CHECKLIST.md"},
        {"risk": "Game mode runtime behavior", "status": "needs Oak intro, battle, item, gift/static, save/reload, and Nuzlocke route playtesting"},
        {"risk": "Pokedex area data may need regeneration", "status": "release blocker/TODO until engine behavior is confirmed"},
        {"risk": "Latias/Latios dossier flags are separate from native roamer state", "status": "manual duplicate-access edge-case testing required"},
        {"risk": "Approved regional/new form display text", "status": "needs runtime and player-facing polish pass"},
        {"risk": "Web-app explorer", "status": "future separate project; not part of this ROM hack phase"},
    ]


def write_json_exports(exports: dict[str, Any]) -> None:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    for filename, data in exports.items():
        (EXPORTS / filename).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def result_table(results: list[CheckResult]) -> str:
    lines = ["| Check | Status | Details |", "| --- | --- | --- |"]
    for result in results:
        details = result.details.replace("|", "\\|")
        lines.append(f"| {result.name} | {result.status} | {details} |")
    return "\n".join(lines)


def write_doc(path: str, text: str) -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / path).write_text(text.strip() + "\n", encoding="utf-8", newline="\n")


def markdown_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def generate_docs(exports: dict[str, Any], results: list[CheckResult], build_details: dict[str, Any]) -> dict[str, str]:
    scope = exports["approved_scope.json"]
    later = exports["approved_later_exceptions.json"]
    mart = exports["items_and_marts.json"]
    rare = exports["rare_encounters.json"]
    random_legendary = exports["random_legendary_surprise.json"]
    legends = exports["proper_legendary_events.json"]
    boss = exports["boss_battles.json"]
    level_curve = exports["level_curve.json"]
    risks = exports["known_risks.json"]["risks"]
    missing_tools = [
        name
        for name, info in build_details.get("tools", {}).items()
        if name != "python" and not info.get("available")
    ]
    docs: dict[str, str] = {}
    learnsets = json.loads((ENGINE / "data" / "learnsets" / "learnsets.json").read_text(encoding="utf-8"))
    egg_move_rows = sum(1 for learnset in learnsets.values() if learnset.get("EggMoves"))
    egg_move_count = sum(len(learnset.get("EggMoves", [])) for learnset in learnsets.values())
    legendary_late_count = sum(
        1
        for species, learnset in learnsets.items()
        if is_late_level_exempt_species(species)
        for move in learnset.get("LevelMoves", [])
        if int(move.get("Level", 0)) >= 60
    )

    docs["README.md"] = f"""
# {PROJECT_NAME} Documentation

This folder contains the project-facing documentation for {PROJECT_NAME}. Use `FEATURES_AND_CHANGES.md` at the repository root for the general feature index, then use the category docs here for implementation and future modification reference.

The interactive web-app explorer is intentionally not part of this ROM hack phase. Structured exports live in `exports/perfect_johto/` so a future separate project can consume them.

## Start Here

- `PROJECT_SCOPE.md`: allowed content, forbidden content, and scope policy.
- `POKEMON_DATA.md`: Pokemon stats, abilities, typings, learnsets, and evolution references.
- `ENCOUNTER_SYSTEMS.md`: wild tables, rare finds, random legendary surprises, proper legendary access, and Nuzlocke encounter claims.
- `TRAINER_TEAMS.md`: trainer roster, level curve, boss, rematch, and validation references.
- `GAME_MODES.md`: Normal, Challenge, Hardcore, and Nuzlocke rules.
- `BUILD_AND_TESTING.md`: validation commands, build readiness, and required local inputs.

## Feature Categories

Pokemon data and availability:

- `POKEMON_DATA.md`
- `POKEMON_AVAILABILITY.md`
- `APPROVED_LATER_EXCEPTIONS.md`
- `LUMINESCENT_DATA_REFRESH.md`
- `TYPE_AND_LEARNSET_CHANGES.md`
- `LEARNSET_ACCESSIBILITY.md`
- `EVOLUTIONS.md`

Encounters and postgame access:

- `ENCOUNTER_SYSTEMS.md`
- `WILD_ENCOUNTERS.md`
- `RARE_ENCOUNTERS.md`
- `RANDOM_LEGENDARY_SYSTEM.md`
- `LEGENDARIES.md`
- `KANTO_POSTGAME.md`
- `CHAMPION_CIRCUIT.md`

Trainers, battles, and progression:

- `TRAINER_TEAMS.md`
- `BOSS_BATTLES.md`
- `phase7_trainer_report.md`
- `phase8_postgame_report.md`

Systems and economy:

- `GAME_MODES.md`
- `QOL_FEATURES.md`
- `ITEMS_AND_MARTS.md`

Build, release, and audit:

- `BUILD_AND_TESTING.md`
- `PLAYTEST_CHECKLIST.md`
- `RELEASE_CHECKLIST.md`
- `KNOWN_LIMITATIONS.md`
- `phase6_obtainability_report.md`
- `history/FEATURES_AND_CHANGES_v2026-06-27.md`

## Generated Data

Most structured data lives in `exports/perfect_johto/`. The key exports are:

- `trainer_teams.json`
- `boss_battles.json`
- `wild_encounters.json`
- `rare_encounters.json`
- `random_legendary_surprise.json`
- `proper_legendary_events.json`
- `evolutions.json`
- `items_and_marts.json`
- `approved_scope.json`
- `approved_later_exceptions.json`

Run `python tools/perfect_johto/validate_project.py --write` after gameplay data changes to regenerate exports and generated docs.
"""

    docs["BUILD_AND_TESTING.md"] = f"""
# Build And Testing

## Static Validation

Run from the repository root:

```powershell
python tools/perfect_johto/validate_project.py
```

To regenerate static exports and documentation:

```powershell
python tools/perfect_johto/validate_project.py --write
```

## Current Build Readiness

{result_table([result for result in results if result.name in {"Build readiness", "text archive validation", "Learnset JSON parse"}])}

## Tool Availability

{markdown_list([f"`{name}`: {'available at ' + info['path'] if info.get('available') else 'missing on PATH'}" for name, info in build_details.get('tools', {}).items()])}

## ROM Inputs

- `hg-engine-main/hg-engine-main/rom.nds`: {'present' if build_details.get('rom_nds', {}).get('exists') else 'missing'}.
- `pokeheartgold-master/baserom.nds`: {'present' if build_details.get('baserom_nds', {}).get('exists') else 'missing'}.

Do not commit or redistribute `rom.nds`, `baserom.nds`, pre-patched ROMs, or copyrighted ROM data.

## Recommended Build Routes

- Docker route: install Docker Desktop, then run `docker build . -t hg-engine` from `hg-engine-main/hg-engine-main`, followed by `docker-makerom.cmd`.
- Native route: install Git, GNU Make, CMake, Python 3, `armips`, and the ARM toolchain expected by HG-Engine. WSL or MSYS2 is recommended over raw PowerShell for native Makefile use.
- `make -n` status: {build_details.get('make_dry_run', {}).get('details')}.
- Dojo `armips` assembly status: {build_details.get('armips_dojo_assembly', {}).get('details')}.
"""

    docs["PROJECT_SCOPE.md"] = f"""
# Project Scope

This doc defines what Pokemon Johto Reforged may expose through gameplay data, scripts, trainers, marts, encounters, and documentation.

## In Scope

- All Generation 1-4 Pokemon.
- Later direct evolutions of Generation 1-4 families.
- Later regional forms and new forms of Generation 1-4 families.
- Later evolutions connected to approved regional forms when the family relationship is direct and the implementation is clean.
- HGSS-style quality-of-life improvements that do not introduce forbidden battle gimmicks.
- Static JSON exports and Markdown docs for auditability and future external tools.

## Out Of Scope

- Unrelated Generation 5+ Pokemon lines.
- Later-generation legendary/mythical Pokemon unless they are forms of Generation 1-4 legendary/mythical Pokemon and explicitly approved later.
- Mega Evolution, Primal Reversion, Z-Moves, Dynamax/Gigantamax, Terastalization, and similar battle gimmicks.
- Totem, Noble/Lord, Gigantamax, Mega, Primal, Terastal, and unrelated later-generation form families unless explicitly approved later.
- Rock type no longer weak to Ground.
- Immortal Shell.
- Custom defensive ability behavior.
- Personalized Tyranitar, Salamence, or Dragonite changes.
- Restoring consumed held items after trainer battles.
- Interactive web app or browser explorer inside this ROM hack project.

## Engine Capacity Caveat

HG-Engine contains many later-generation species, forms, moves, abilities, items, and mechanic constants. This repository treats that data as engine capacity only. Gameplay exposure is controlled by project scope, validation, and the generated documentation/exports.

## Reference Docs

- Approved exceptions: `docs/APPROVED_LATER_EXCEPTIONS.md`.
- Pokemon-data policy: `docs/POKEMON_DATA.md`.
- Encounter exposure: `docs/ENCOUNTER_SYSTEMS.md`.
- Trainer exposure: `docs/TRAINER_TEAMS.md`.
- Forbidden-gimmick and release checks: `docs/RELEASE_CHECKLIST.md`.

The web-app explorer is a future separate project, not part of this ROM hack phase. This project provides structured data exports in `exports/perfect_johto/` that a later separate explorer can consume.
"""

    docs["GAME_MODES.md"] = """
# Game Modes

Game modes are selected immediately after choosing New Game, before Professor Oak's speech. The selector uses two pages:

- Page 1: Normal, Challenge, More.
- Page 2: Hardcore, Nuzlocke, Back.

## References

- Implementation header: `hg-engine-main/hg-engine-main/include/perfect_johto_game_modes.h`.
- Implementation source: `hg-engine-main/hg-engine-main/src/perfect_johto_game_modes.c`.
- Oak intro integration: `hg-engine-main/hg-engine-main/src/field/script_commands.c`.
- Wild/gift/static encounter interaction: `docs/ENCOUNTER_SYSTEMS.md`.
- Playtest checklist: `docs/PLAYTEST_CHECKLIST.md`.

## Modes

| Mode | Rules |
| --- | --- |
| Normal | Current Pokemon Johto Reforged QOL and balance, with no enforced level caps. |
| Challenge | Normal plus dynamic level caps, forced Set battle style, and no player Bag item use in trainer battles. |
| Hardcore | Challenge plus fainted non-Egg party Pokemon are released/deleted after battle. The last non-Egg party Pokemon is never released by this rule. |
| Nuzlocke | Hardcore plus enforced first encounter/gift/static claim per map section. Optional rules, such as retiring Pokemon after a Gym run, are left to the player. |

## Level Caps

Level caps are enabled only in Challenge, Hardcore, and Nuzlocke. Pokemon at the cap no longer gain battle EXP, and Rare Candy level-up is also blocked by the cap.

| Progress | Cap |
| --- | ---: |
| Before Falkner | 16 |
| Before Bugsy | 22 |
| Before Whitney | 27 |
| Before Morty | 33 |
| Before all of Chuck/Jasmine/Pryce are cleared | 45 |
| Before Clair | 52 |
| After Clair, before first Elite Four clear | 62 |
| Kanto before Lt. Surge | 65 |
| Kanto before Brock | 66 |
| Kanto before Janine | 66 |
| Kanto before Misty | 68 |
| Kanto before Erika | 70 |
| Kanto before Sabrina | 74 |
| Kanto before Blaine | 78 |
| Kanto before Blue | 84 |
| After all 16 badges | 98 |

## Nuzlocke Enforcement

- Wild encounters claim the current map section when generated.
- Catch attempts are legal only for the currently claimed encounter area; illegal catches fail at the ball-shake stage.
- Gift and egg Pokemon claim the current map section before being awarded.
- Starter selection claims the starter's current map section but is never blocked.
- Static encounters are covered when they use the standard wild encounter or gift creation paths.

## Implementation Notes

- Game mode is stored in `VAR_PERFECT_JOHTO_GAME_MODE` (`0x416E`).
- Current legal Nuzlocke battle area is stored in `VAR_PERFECT_JOHTO_NUZLOCKE_LEGAL_AREA` (`0x416D`).
- Current level cap is mirrored in `VAR_PERFECT_JOHTO_LEVEL_CAP` (`0x416F`).
- Claimed Nuzlocke areas are stored as a bitset in `SAVE_MISC_DATA`.
- The Oak speech tutorial menu in overlay 53 is repurposed for mode selection.

## Playtest Focus

- Verify every mode can be selected from New Game and Oak's speech continues.
- Verify EXP and Rare Candy stop at cap in Challenge or harder modes.
- Verify Set mode is forced in Challenge or harder modes.
- Verify trainer-battle Bag items are blocked while wild battle capture remains possible.
- Verify Hardcore and Nuzlocke release fainted Pokemon after battle while preserving the last non-Egg party Pokemon.
- Verify Nuzlocke wild, gift, egg, starter, and static encounters claim areas as expected.
"""

    docs["QOL_FEATURES.md"] = """
# QOL Features

This doc tracks quality-of-life features that are enabled, added, or explicitly deferred.

## Implemented Or Preserved

- Running from the beginning: Mom gives the Running Shoes in the initial home conversation.
- Cherrygrove Guide Gent skip: if the player already has Running Shoes, the Guide skips the forced walking tour while preserving the later Map Card callback.
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
- Mints, Ability Capsule, Ability Patch, EV training items, IV stat candies, and evolution items are progressively available through the standard badge mart.

## Deferred

- AutoRun/toggle-run as an input-mode feature. Running from the start is handled through early Running Shoes, but automatic running remains separate.
- Fast Surf.
- Field moves without teaching the HM move.
- Optional QOL/settings NPC.

## References

- Game mode rules: `docs/GAME_MODES.md`.
- Item and mart economy: `docs/ITEMS_AND_MARTS.md`.
- Release/runtime status: `docs/KNOWN_LIMITATIONS.md`.

Runtime playtesting is still required for each QOL feature in a built ROM.
"""

    docs["POKEMON_AVAILABILITY.md"] = f"""
# Pokemon Availability

All Generation 1-4 Pokemon are intended to be obtainable in one save file.

## References

- Availability export: `exports/perfect_johto/pokemon_availability.json`.
- Encounter system overview: `docs/ENCOUNTER_SYSTEMS.md`.
- Encounter report: `docs/phase6_obtainability_report.md`.
- Legendary report: `docs/phase8_postgame_report.md`.
- Approved later exceptions: `docs/APPROVED_LATER_EXCEPTIONS.md`.

## Non-Legendary Coverage

- Phase 6 static validation reports non-legendary Gen 1-4 evolution-family coverage as complete across main wild, Safari, and Headbutt encounter sources.
- The generated Phase 6 report records 211/211 non-legendary Gen 1-4 evolution-family components covered.
- Every non-legendary, non-starter Gen 3-4 base/pre-evolution species is represented in Johto main encounters.
- Approved later regional forms and direct family exceptions are placed only where they belong to Gen 1-4 families.
- No unrelated Gen 5+ Pokemon are intentionally exposed through encounters, trainers, marts, or Phase 8 Dojo gameplay files.

## Starter Access

Starter families are not used as early-route clutter. Starter access is pushed into late-game and postgame contexts, including late Johto, Kanto, and postgame Kanto wild placements.

## Legendary And Mythical Coverage

- Native Raikou and Entei remain Burned Tower roamers.
- Phase 8 Saffron Fighting Dojo dossiers provide proper scripted access for the remaining Gen 1-4 legendary/mythical roster.
- The random legendary surprise overlay is separate from proper access. It is a repeatable low-rate wild overlay and does not write roamer save state.

## Known Follow-Up

Release blocker/TODO: confirm whether Pokedex area data is derived from encounter tables or needs a separate regeneration step.
"""

    docs["POKEMON_DATA.md"] = """
# Pokemon Data Changes

This is the reference entry point for Pokemon-specific data changes: base stats, abilities, typings, learnsets, moves, and evolution access. Use the narrower docs linked below when you need the full rule detail for a specific subsystem.

## Quick Reference

| Topic | Primary reference |
| --- | --- |
| Scope and allowed species/forms | `docs/PROJECT_SCOPE.md`, `docs/APPROVED_LATER_EXCEPTIONS.md` |
| Base stats, ability slots, and Luminescent source pass | `docs/LUMINESCENT_DATA_REFRESH.md` |
| Type modernization and STAB support | `docs/TYPE_AND_LEARNSET_CHANGES.md` |
| Egg move and late-level learnset rules | `docs/LEARNSET_ACCESSIBILITY.md` |
| Evolution method changes | `docs/EVOLUTIONS.md` |
| One-save obtainability | `docs/POKEMON_AVAILABILITY.md`, `docs/ENCOUNTER_SYSTEMS.md` |

## Source Files

- Species personal data: `hg-engine-main/hg-engine-main/data/Species.c`.
- Hidden ability data: `hg-engine-main/hg-engine-main/data/HiddenAbilityTable.c`.
- Level-up, egg, machine, and tutor learnset source: `hg-engine-main/hg-engine-main/data/learnsets/learnsets.json`.
- Learnset build helper: `hg-engine-main/hg-engine-main/scripts/build_learnsets.py`.
- Evolution data: `hg-engine-main/hg-engine-main/data/Evolutions.c`.
- Ability item behavior: `hg-engine-main/hg-engine-main/src/individual/PartyMenu_HandleUseItemOnMon.c`.
- Natural wild ability rolling: `hg-engine-main/hg-engine-main/src/field/enemy_party.c`.

## Scope Rules

- All Generation 1-4 Pokemon are in scope.
- Later-generation direct evolutions, regional forms, and new forms are allowed only when they belong to Generation 1-4 families and are listed in `docs/APPROVED_LATER_EXCEPTIONS.md`.
- Unrelated Generation 5+ Pokemon, unrelated later forms, Mega Evolution, Primal Reversion, Z-Moves, Dynamax/Gigantamax, Terastalization, and similar battle gimmicks remain out of scope.
- The engine still contains later-generation species, moves, abilities, items, and mechanics as internal capacity. Gameplay exposure is restricted by validation, docs, encounters, trainers, marts, scripts, and events.

## Stats And Abilities

- Generation 1-4 base species rows and relevant native Generation 3-4 form rows were refreshed against Luminescent Platinum 3.0 as the primary data standard.
- The Luminescent pass covers base stats and ability slots for the target species/form set. Renegade Platinum and Polished Crystal remain secondary design references, not overrides.
- Ability modernization is allowed when it supports Pokemon identity, role variety, and Johto replayability.
- Hidden ability slots are natural wild encounter variety. Wild Pokemon now roll across non-empty ability slot 1, ability slot 2, and hidden ability slots, preserving duplicate Luminescent slots as intentional weighting.
- Ability Capsule and Ability Patch are part of the badge-gated customization economy. Ability Capsule unlocks at 3 badges; Ability Patch unlocks at 6 badges.
- Custom defensive ability behavior, Immortal Shell, and one-off personalized pseudo-legendary ability changes remain out of scope.

## Typing

Typing modernization is restrained and species-identity driven. The complete type-change list and STAB support audit live in `docs/TYPE_AND_LEARNSET_CHANGES.md`.

Important constraints:

- No type chart change has been made.
- Rock no longer being weak to Ground remains out of scope.
- Type changes do not by themselves change base stats, evolution methods, encounter scope, catch rates, EV yields, held items, or growth data.
- Project-added secondary types are audited for reasonable level-up attacking move access.

## Moves And Learnsets

- Move battle behavior and move data are not a project feature area right now; no custom move-behavior pass is documented.
- Level-up learnsets preserve local extras and append missing Luminescent Platinum 3.0 level-up moves at their Luminescent levels.
- Luminescent move IDs are resolved through Luminescent move names before being mapped to local `MOVE_*` constants, because post-Gen 4 numeric IDs do not fully match this engine.
- Egg moves are also level-up accessible for every Pokemon with egg moves.
- Non-legendary level-up moves are compressed below level 60. Legendary, mythical, Ultra Beast, and comparable one-off Pokemon keep late signature pacing.
- Evolved forms inherit earlier-form level-up moves more consistently.

## Evolutions

Evolution changes are documented in `docs/EVOLUTIONS.md`.

The major rules are:

- Approved-scope trade-only evolutions are replaced with item-use or other non-trade methods where appropriate.
- Trade-with-item evolutions use direct item-use methods.
- Known-move evolutions are used for Wyrdeer, Annihilape, and Sirfetch'd.
- Dudunsparce Three-Segment and Ursaluna Bloodmoon have simple level-up access through their standard final forms.
- Required evolution items are made available through badge-gated marts.

## Validation

Run the master validation before changing Pokemon data:

```powershell
python tools/perfect_johto/validate_project.py
```

Validation covers approved scope, learnset parsing/generation, learnset accessibility, evolution access, item/mart gates, encounter exposure, trainer species use, and forbidden gimmick exposure.
"""

    docs["TYPE_AND_LEARNSET_CHANGES.md"] = """
# Type And Learnset Changes

This doc covers type modernization, level-up attacking STAB support, and project-wide learnset cleanup rules. For the broader Pokemon-data overview, see `docs/POKEMON_DATA.md`.

## Type Modernization Policy

- Type changes are restrained and species-identity driven.
- No type chart change has been made.
- Type changes do not by themselves change base stats, evolution methods, encounter scope, catch rates, EV yields, held items, or growth data.
- Custom or modernized typings are audited so project-added secondary types have reasonable level-up attacking move access.

## Type Change List

Phase 4 Polished Crystal-priority Gen 1-2 changes:

| Pokemon | Old type | New type |
| --- | --- | --- |
| Charizard | Fire/Flying | Fire/Dragon |
| Blastoise | Water | Water/Steel |
| Butterfree | Bug/Flying | Bug/Psychic |
| Golduck | Water | Water/Psychic |
| Rapidash | Fire | Fire/Fairy |
| Meganium | Grass | Grass/Fairy |
| Typhlosion | Fire | Fire/Ground |
| Feraligatr | Water | Water/Dark |
| Noctowl | Normal/Flying | Ghost/Flying |
| Ledian | Bug/Flying | Bug/Fighting |
| Ariados | Bug/Poison | Bug/Dark |
| Ampharos | Electric | Electric/Dragon |
| Bellossom | Grass | Grass/Fairy |
| Politoed | Water | Water/Grass |
| Sunflora | Grass | Grass/Fire |
| Dunsparce | Normal | Normal/Ground |
| Girafarig | Normal/Psychic | Psychic/Dark |
| Octillery | Water | Water/Fire |
| Stantler | Normal | Normal/Psychic |
| Ninetales | Fire | Fire/Ghost |

Phase 4 Gen 3-4 inspired changes:

| Pokemon | Old type | New type |
| --- | --- | --- |
| Sceptile | Grass | Grass/Dragon |
| Masquerain | Bug/Flying | Bug/Water |
| Volbeat | Bug | Bug/Electric |
| Illumise | Bug | Bug/Fairy |
| Trapinch | Ground | Bug/Ground |
| Vibrava | Ground/Dragon | Bug/Dragon |
| Flygon | Ground/Dragon | Bug/Dragon |
| Swablu | Normal/Flying | Fairy/Flying |
| Altaria | Dragon/Flying | Dragon/Fairy |
| Seviper | Poison | Poison/Dark |
| Milotic | Water | Water/Fairy |
| Glalie | Ice | Ice/Rock |
| Luvdisc | Water | Water/Fairy |
| Misdreavus | Ghost | Ghost/Fairy |
| Mismagius | Ghost | Ghost/Fairy |
| Luxray | Electric | Electric/Dark |
| Lopunny | Normal | Normal/Fighting |
| Electivire | Electric | Electric/Fighting |

Later Gen 3-4 semantic additions:

| Pokemon | New type |
| --- | --- |
| Chingling and Chimecho | Psychic/Fairy |
| Huntail | Water/Dark |
| Gorebyss | Water/Psychic |
| Cranidos and Rampardos | Rock/Dragon |
| Carnivine | Grass/Dark |
| Finneon and Lumineon | Water/Fairy |

## Level-Up STAB Support

The following lines now have direct level-up attack support for an added or previously unsupported type:

- Fairy support: Meganium, Rapidash, Azurill, Misdreavus, Mismagius, Chingling, Chimecho, Togetic, Finneon, and Lumineon.
- Dragon support: Sceptile, Cranidos, and Rampardos.
- Bug support: Surskit, Nincada, Shedinja, and Trapinch.
- Electric support: Volbeat.
- Rock support: Glalie.
- Ground support: Typhlosion, Gligar, and Gliscor.
- Steel support: Probopass.
- Ghost support: Ninetales and Noctowl.
- Grass support: Politoed.
- Fire support: Sunflora and Octillery.
- Ice support: Delibird.

Huntail, Gorebyss, and Carnivine already had appropriate Dark/Psychic/Dark level-up attacks after their type changes and did not need extra moves.

Remaining no-level-up attacking STAB cases are canonical or status-oriented exceptions such as the Bulbasaur, Gastly, and Budew poison lines, plus Beldum's one-move identity. No project-added custom secondary type is intentionally left without a level-up attacking move.

## Learnset Rules

- Phase 4 updated approved-scope level-up learnsets only. Machine, tutor, and egg move lists were not intentionally changed in that pass.
- Evolved forms inherit earlier-form level-up moves more consistently.
- Duplicate level-up move entries are removed, keeping the earliest occurrence.
- Non-legendary level-up moves are compressed below level 60.
- Legendary, mythical, Ultra Beast, and comparable special one-off Pokemon keep their late signature pacing.
- Egg moves are also level-up accessible for every Pokemon that has egg moves.

## Notable Learnset Access Changes

- Stantler learns `Psyshield Bash` at level 32 so Wyrdeer has a reachable known-move evolution method.
- Galarian Farfetch'd learns `Leaf Blade` at level 35 so Sirfetch'd has a reachable known-move evolution method before late game.
- Missing Luminescent Platinum 3.0 level-up moves are appended at their Luminescent levels while preserving local extras.
- Luminescent move IDs are resolved through Luminescent move-name text before mapping to local `MOVE_*` constants.

## Validation

`tools/perfect_johto/validate_project.py` validates learnset JSON parsing, learnset generation, no duplicate level-up moves after cleanup, no non-legendary level 60+ moves after compression, and egg-move coverage through level-up learnsets.
"""

    docs["LEARNSET_ACCESSIBILITY.md"] = f"""
# Learnset Accessibility

The active learnset source is `hg-engine-main/hg-engine-main/data/learnsets/learnsets.json`.

This doc covers project-wide learnset accessibility rules. Type-specific move support is documented in `docs/TYPE_AND_LEARNSET_CHANGES.md`, and the Luminescent import behavior is documented in `docs/LUMINESCENT_DATA_REFRESH.md`.

## Rules

- Every egg move listed for a Pokemon must also be learnable through that Pokemon's level-up learnset.
- Missing egg moves are inserted across levels 5-55 in egg-list order, keeping inherited moves naturally accessible without putting every inherited move at level 1.
- Non-legendary level-up moves must occur before level 60.
- Legendary, mythical, Ultra Beast, and comparable special one-off Pokemon are exempt from the pre-60 compression rule so their late signature pacing can remain intact.
- Duplicate level-up move names are removed, keeping the earliest occurrence.

## Current Audit

- Learnset rows with egg moves: {egg_move_rows}.
- Egg move entries covered by level-up learnsets: {egg_move_count}.
- Non-legendary level 60+ moves after compression: 0.
- Duplicate level-up move names after cleanup: 0.
- Legendary/special level 60+ entries intentionally preserved: {legendary_late_count}.

`tools/perfect_johto/validate_project.py` enforces these rules through the Learnset accessibility validation check.

## Edit Notes

- Regenerate learnset outputs with the HG-Engine learnset builder after changing `learnsets.json`.
- Do not add duplicate level-up move names to solve access problems; move the earliest useful instance instead.
- Keep late legendary and mythical signature pacing unless the species is no longer treated as a special one-off.
"""

    docs["APPROVED_LATER_EXCEPTIONS.md"] = f"""
# Approved Later Exceptions

Approved later exceptions are limited to direct evolutions, regional forms, and new forms of Generation 1-4 Pokemon families.

## References

- Export: `exports/perfect_johto/approved_later_exceptions.json`.
- Scope policy: `docs/PROJECT_SCOPE.md`.
- Pokemon data overview: `docs/POKEMON_DATA.md`.
- Evolution methods: `docs/EVOLUTIONS.md`.

## Current Count

- Approved exception species/forms: {len(later)}.

## Allowed Categories

- Direct later-generation evolutions of Gen 1-4 families, such as Sylveon, Wyrdeer, Kleavor, Ursaluna, Annihilape, Farigiraf, Dudunsparce, Sneasler, Overqwil, Clodsire, and similar family continuations.
- Regional forms of Gen 1-4 families, including selected Alolan, Galarian, Hisuian, and Paldean forms.
- New forms tied to approved Gen 1-4 families, such as Dudunsparce Three-Segment and Ursaluna Bloodmoon.

## Restrictions

- No unrelated Gen 5+ Pokemon are intentionally exposed by encounter, trainer, mart, or Phase 8 Dojo gameplay files.
- Later-generation legendary/mythical forms require explicit separate approval.
- Forbidden battle gimmick forms remain out of scope.
"""

    docs["EVOLUTIONS.md"] = """
# Evolutions

Evolution data is exported from `hg-engine-main/hg-engine-main/data/Evolutions.c`.

## References

- Full export: `exports/perfect_johto/evolutions.json`.
- Trade replacement export: `exports/perfect_johto/trade_evolution_replacements.json`.
- Required item access: `docs/ITEMS_AND_MARTS.md`.
- Learnset prerequisites: `docs/TYPE_AND_LEARNSET_CHANGES.md` and `docs/LEARNSET_ACCESSIBILITY.md`.

## Design Rules

- All approved-scope Pokemon should be evolvable in one save file without trading.
- Existing item-use methods are preferred when they are clear and HGSS-friendly.
- Known-move methods are used when they better match the later official evolution identity.
- Required approved-scope evolution items are made repeatably available through the badge-gated standard mart.
- Unrelated later-generation families remain out of scope even if their evolution items or constants exist in HG-Engine.

## Trade-Only Replacements

These approved-scope trade-only lines use the Linking Cord item where the engine already supports a non-trade replacement:

- Kadabra -> Alakazam.
- Machoke -> Machamp.
- Graveler -> Golem.
- Alolan Graveler -> Alolan Golem.
- Haunter -> Gengar.

## Trade-With-Item Replacements

These trade-with-item evolutions were converted into direct item-use evolutions:

- Poliwhirl -> Politoed with King's Rock.
- Slowpoke -> Slowking with King's Rock.
- Onix -> Steelix with Metal Coat.
- Seadra -> Kingdra with Dragon Scale.
- Scyther -> Scizor with Metal Coat.
- Porygon -> Porygon2 with Up-Grade.
- Rhydon -> Rhyperior with Protector.
- Electabuzz -> Electivire with Electirizer.
- Magmar -> Magmortar with Magmarizer.
- Porygon2 -> Porygon-Z with Dubious Disc.
- Feebas -> Milotic with Prism Scale, alongside beauty evolution.
- Dusclops -> Dusknoir with Reaper Cloth.
- Clamperl -> Huntail with Deep Sea Tooth.
- Clamperl -> Gorebyss with Deep Sea Scale.

## Known-Move Replacements

- Stantler -> Wyrdeer by leveling while knowing `Psyshield Bash`.
- Primeape -> Annihilape by leveling while knowing `Rage Fist`.
- Galarian Farfetch'd -> Sirfetch'd by leveling while knowing `Leaf Blade`.

## Special Form Access

- Dudunsparce Three-Segment evolves from Dudunsparce by level-up at 50.
- Ursaluna Bloodmoon evolves from Ursaluna by level-up at 55.

These are simple access methods for special forms already present in local data. Runtime testing still needs to confirm form display, naming, and evolution behavior.

## Validation

Static validation checks that no approved-scope trade-only evolutions remain, that species/move/item constants resolve, that required evolution items are available through the badge mart, and that known-move methods have reasonable learnset access.
"""

    docs["WILD_ENCOUNTERS.md"] = f"""
# Wild Encounters

Wild encounters are the main one-save obtainability layer for ordinary Pokemon. For the full encounter-system map, see `docs/ENCOUNTER_SYSTEMS.md`.

## References

- Main export: `exports/perfect_johto/wild_encounters.json`.
- Phase 6 audit report: `docs/phase6_obtainability_report.md`.
- Rare layer: `docs/RARE_ENCOUNTERS.md`.
- Random legendary overlay: `docs/RANDOM_LEGENDARY_SYSTEM.md`.

## Source Files

- Main encounter source: `hg-engine-main/hg-engine-main/data/Encounters.c`.
- Safari source: `hg-engine-main/hg-engine-main/data/SafariEncounters.c`.
- Headbutt source: `hg-engine-main/hg-engine-main/data/Headbutt.c`.
- Generation/audit tool: `tools/perfect_johto/phase6_encounter_tools.py`.

## Main Rules

- Main land encounters use a shared daytime pool: the engine-facing morning and day arrays are kept identical, while night remains separate.
- Meaningful land/cave pools and surf/fishing pools are validated separately. Each meaningful mode must have at least six species when that mode exists.
- Late-Johto, Kanto, and postgame encounter levels were raised to match the stronger trainer curve.
- Gen 3-4 Pokemon are used as normal Johto ecology where slot space allows, not only as rare prizes.
- Starter families are placed in late-game or postgame contexts, not as early route clutter.
- Non-rare low-rate land, surf, and rod filler slots duplicate common species so ordinary Pokemon do not appear as separate rare finds.

## Coverage

- Meaningful non-Safari encounter areas with at least six encounter species: 132 / 132.
- Meaningful land/cave encounter pools with at least six species: 108 / 108.
- Meaningful surf/fishing encounter pools with at least six species: 71 / 71.
- Non-legendary Gen 1-4 evolution-family components with wild encounter coverage: 211 / 211.
- Non-legendary non-starter Gen 3-4 base/pre-evolution species covered in Johto main encounters: 95 / 95.
- Unrelated later-generation species found in encounter tables: none.

## Edit Notes

- Prefer editing `tools/perfect_johto/phase6_encounter_tools.py` and regenerating rather than hand-editing the large encounter source.
- Keep rare species in the rare layer and ordinary ecology in common slots.
- Keep Safari and Headbutt coverage in mind when validating full one-save availability.
- Confirm Pokedex area-data behavior before release.
"""

    docs["ENCOUNTER_SYSTEMS.md"] = """
# Encounter Systems

This is the reference entry point for all encounter mechanisms: ordinary wild tables, rare finds, Safari/Headbutt support, random legendary surprises, native roamers, Dojo dossier encounters, and Nuzlocke encounter claims.

## Quick Reference

| Mechanism | Primary reference |
| --- | --- |
| Main wild tables and level curve | `docs/WILD_ENCOUNTERS.md` |
| Per-area Phase 6 audit | `docs/phase6_obtainability_report.md` |
| Rare-find layer | `docs/RARE_ENCOUNTERS.md` |
| Random legendary surprise overlay | `docs/RANDOM_LEGENDARY_SYSTEM.md` |
| Proper legendary/mythical access | `docs/LEGENDARIES.md`, `docs/phase8_postgame_report.md` |
| Kanto Dojo postgame hub | `docs/KANTO_POSTGAME.md` |
| Nuzlocke area claims | `docs/GAME_MODES.md` |

## Source Files

- Main wild encounters: `hg-engine-main/hg-engine-main/data/Encounters.c`.
- Safari encounters: `hg-engine-main/hg-engine-main/data/SafariEncounters.c`.
- Headbutt encounters: `hg-engine-main/hg-engine-main/data/Headbutt.c`.
- Encounter generation hook: `hg-engine-main/hg-engine-main/src/field/enemy_party.c`.
- Encounter generation/audit tool: `tools/perfect_johto/phase6_encounter_tools.py`.
- Master validation/export runner: `tools/perfect_johto/validate_project.py`.

## Main Wild Encounters

- Main encounters were rebuilt for broad Generation 1-4 one-save obtainability.
- Morning and day land arrays are intentionally kept identical as a shared daytime pool; night remains separate for night-specific flavor.
- Land/cave pools and surf/fishing pools are validated separately. Meaningful pools are expected to have at least six species when that encounter mode exists.
- Johto routes and dungeons include Generation 3-4 Pokemon as normal ecology, not only as rare prizes.
- Kanto and late-Johto wild levels were raised so wild Pokemon remain useful alongside the stronger trainer curve.
- Starter access is delayed into late-game and postgame contexts rather than crowding early Johto routes.

## Rare Finds

- Every meaningful non-Safari main encounter area has one to three rare species.
- Primary land rares use slot 8 at 4%; curated secondary land rares may use slot 9 at 4%.
- Surf rares use slot 3 at 4%.
- Fishing rares use slot 4, changed by Phase 6 to a 4% slot.
- Non-rare low-rate filler duplicates common species so ordinary Pokemon are not accidentally treated as rare finds by future tools or wiki views.
- Rare species are reserved for strong current forms, lines whose final form reaches 500+ BST, or approved regional forms.
- Rock Smash is not used for the rare layer because its slot structure is only 80%/20%.

## Legendary And Mythical Access

Two systems intentionally coexist:

- Proper access: native Raikou/Entei roamers plus Saffron Fighting Dojo dossier encounters for the rest of the Generation 1-4 legendary/mythical roster.
- Surprise access: a low-rate random legendary overlay that can replace a normal wild encounter after the normal encounter flow succeeds.

The proper access system sets caught flags only on successful capture, so fled or fainted dossier battles remain retryable. The surprise overlay is repeatable, does not write roamer save state, and respects Repel through the existing normal encounter flow.

## Nuzlocke Claims

Nuzlocke mode uses the encounter/gift/static creation paths to claim map sections. Wild encounters claim the current map section when generated, gift and egg Pokemon claim before being awarded, and illegal catch attempts fail during ball shake resolution. See `docs/GAME_MODES.md` for the full rules.

## Known Follow-Up

Pokedex area data still needs release confirmation. If HG-Engine does not derive area data from the regenerated encounter archives, add or document the regeneration step before release.
"""

    docs["RARE_ENCOUNTERS.md"] = f"""
# Rare Encounters

Rare encounters are a curated low-rate layer on top of the main wild tables. They are intended for rare finds, approved regional forms, strong current forms, and sparse pseudo-legendary access.

## References

- Export: `exports/perfect_johto/rare_encounters.json`.
- Encounter system overview: `docs/ENCOUNTER_SYSTEMS.md`.
- Full per-area report: `docs/phase6_obtainability_report.md`.
- Main wild tables: `docs/WILD_ENCOUNTERS.md`.

## Slot Rules

- Primary land rare slots use HGSS slot 8 at 4%.
- Curated secondary land rares may use slot 9 at 4%.
- Surf rare slots use slot 3 at 4%.
- Fishing rare slots use slot 4, changed by Phase 6 to 4%.
- Rock Smash is not used for rare placement because it only has 80%/20% slots.
- Legacy non-rare land/surf filler slots and non-rare rod filler slots duplicate common species and are not treated as rare finds.

## Placement Rules

- Every meaningful non-Safari encounter area has 1-3 rare species.
- Rare species are reserved for strong current forms, lines whose final form reaches 500+ BST, or approved regional forms.
- Rare Finds explicitly include Alolan Geodude, Galarian Zigzagoon, Paldean Wooper, Lapras, Kangaskhan, Tauros, early Teddiursa, early Houndour, early Hisuian Sneasel, early Ponyta, and pre-League Ice Path Sneasel.
- Rare pseudo-legendary initial forms are intentionally sparse and semantically placed, including Larvitar, Bagon, Gible, Beldum, and Riolu in cave, mountain, dragon, or expert-training contexts.
- Starter rare access is pushed into Kanto and postgame Kanto contexts.

## Current Audit

- Meaningful non-Safari areas with rare notes: {len(rare)}.
- Meaningful non-Safari areas with 1-3 rare species: 132 / 132.
- Rare placements are validated to stay in the intended low-rate band.
- Approved later-form placements are restricted to approved Gen 1-4 families.
"""

    docs["RANDOM_LEGENDARY_SYSTEM.md"] = f"""
# Random Legendary System

The random legendary surprise overlay is a repeatable low-rate wild encounter system. It is separate from proper legendary/mythical access through native roamers and Saffron Fighting Dojo dossiers.

## References

- Export: `exports/perfect_johto/random_legendary_surprise.json`.
- Proper legendary access: `docs/LEGENDARIES.md`.
- Encounter system overview: `docs/ENCOUNTER_SYSTEMS.md`.
- Implementation hook: `hg-engine-main/hg-engine-main/src/field/enemy_party.c`.

## Trigger Flow

- The overlay runs from `AddWildPartyPokemon` after normal wild encounter generation succeeds.
- Because it runs after the normal encounter flow, Repel behavior is preserved by the existing encounter system.
- The selected legendary/mythical is started as a normal wild battle.
- The system does not write to roamer save state.
- Surprise legendaries receive Teleport in move slot 4, giving the wild AI a move-based chance to flee each turn.

## Rates

{markdown_list([f"{row['badges']}: {row['description']}." for row in random_legendary['rates']])}

These rates are aggregate tier rolls, not independent rolls per legendary. After a tier roll succeeds, one species is selected from the currently unlocked matching tier.

## Exclusions

{markdown_list([f"`{battle_type}`." for battle_type in random_legendary['blocked_battle_types']])}

## Validation And Testing

Static validation checks the pool, rates, badge gates, excluded battle types, and approved Gen 1-4 legendary/mythical scope. Runtime testing is still required for Repel behavior, Safari exclusion, native roamer coexistence, level scaling, and badge-gated pools.
"""

    docs["TRAINER_TEAMS.md"] = """
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
- Trainer generation/validation tool: `tools/perfect_johto/phase7_trainer_tools.py`.
- Master validation/export runner: `tools/perfect_johto/validate_project.py`.

## Change Summary

- Gym Leaders, Elite Four, Champions, Red, and other major bosses use full six-Pokemon teams.
- First-clear Johto leaders progress from Falkner 13-14 through Clair 46-50.
- First Elite Four and Champion progress from Will 50-54 through Lance 58-60.
- Kanto leaders were raised into the post-League curve, ending with Blue 78-82.
- Gym Leader rematches, Elite Four rematches, Lance rematches, Red, and Champion Circuit battles were raised for late-postgame play.
- Major Silver, Team Rocket Executive, and Giovanni/Rocket Boss records were expanded where their story role and level band support it.
- Regular trainers received a controlled level pass and semantic Gen 3-4 variety replacements without turning every route trainer into a boss.

## Regular Trainer Rules

- Regular trainer party sizes are not broadly inflated.
- The variety pass replaces one to two ordinary species on no-custom-move non-boss trainers with semantic Gen 3-4 alternatives.
- The pass covers roadside trainers, gym non-leaders, Team Rocket grunts, swimmers, hikers, psychics, and similar regular classes.
- Non-boss regular trainers are intentionally below the late boss/rematch ceiling.

## Scope And Validation

Static validation checks trainer species, moves, items, ability slots, approved Pokemon scope, regular-trainer Gen 3-4 variety, major rival/Rocket sizes, and mandatory six-Pokemon boss rules.

The Phase 7 curve was re-audited after the regular-trainer variety pass. Boss and route bands still progress smoothly from early Johto through Red; no additional trainer-level raise was needed for the latest encounter/type/learnset update.
"""

    docs["BOSS_BATTLES.md"] = f"""
# Boss Battles

Boss battles are the curated high-importance trainer records: Gym Leaders, Elite Four, Champions, Red, Champion Circuit trainers, major rivals, and major Team Rocket leaders.

## References

- Boss export: `exports/perfect_johto/boss_battles.json`.
- Full trainer export: `exports/perfect_johto/trainer_teams.json`.
- Phase 7 report: `docs/phase7_trainer_report.md`.
- Trainer overview: `docs/TRAINER_TEAMS.md`.
- Champion Circuit: `docs/CHAMPION_CIRCUIT.md`.

## Current Audit

- Boss records exported: {len(boss)}.
- Gym Leaders: all leader-class records have six Pokemon.
- Elite Four: all Elite Four records have six Pokemon.
- Champions/Red: all Champion-class and Red records have six Pokemon.
- Major rival fights from mid-game onward have six Pokemon where appropriate.
- Major Rocket Executive/Rocket Boss records at level 35+ have six Pokemon.

## Level Bands

- Johto leaders: Falkner 13-14, Bugsy 18-20, Whitney 23-25, Morty 29-31, Chuck 34-38, Jasmine 38-42, Pryce 40-43, Clair 46-50.
- First League: Will 50-54, Koga 52-56, Bruno 54-58, Karen 56-58, Lance 58-60.
- Kanto leaders: early Kanto 58-66, mid Kanto 65-72, Blaine 72-76, Blue 78-82.
- Rematches/postgame: Elite Four rematches 78-84, legacy Lance rematch 82-88, Gym Leader rematches 66-90, Champion Circuit trainers 92-96.

## Remaining Risk

Route/order playtesting is still needed for local difficulty spikes, especially optional trainer density, Rocket/Silver pacing, rematches, Red, and Champion Circuit unlock timing.
"""

    docs["LEGENDARIES.md"] = f"""
# Legendaries

This doc covers proper Gen 1-4 legendary and mythical access. The separate repeatable random legendary surprise system is documented in `docs/RANDOM_LEGENDARY_SYSTEM.md`.

## References

- Proper event export: `exports/perfect_johto/proper_legendary_events.json`.
- Phase 8 report: `docs/phase8_postgame_report.md`.
- Kanto postgame hub: `docs/KANTO_POSTGAME.md`.
- Champion Circuit: `docs/CHAMPION_CIRCUIT.md`.

## Access Layers

- Raikou and Entei remain native Burned Tower roamers.
- All other Gen 1-4 legendary/mythical access is handled through Saffron Fighting Dojo dossier encounters unless already covered by native flow.
- Dossier battles are scripted/static encounters.
- Static encounter outcome `4` is used so caught flags are set only on capture.
- Failed, fled, or fainted dossier battles remain retryable by script logic.
- Latias and Latios use Phase 8 dossier flags separate from native roamer state.

## Current Audit

- Native entries: {len(legends['native'])}.
- Dojo dossier entries: {len(legends['dojo_dossiers'])}.
- Phase 8 validates 35/35 Gen 1-4 legendary/mythical coverage including native Raikou and Entei.

## Major Prerequisite Chains

- Regirock, Regice, and Registeel before Regigigas.
- Kyogre and Groudon before Rayquaza.
- Cresselia before Darkrai.
- Manaphy before Phione.
- Red defeated, lake trio caught, and creation trio caught before Arceus.

## Runtime Focus

Runtime testing should verify Dojo menus, caught flags, retry behavior, Latias/Latios duplicate-access edge cases, native roamer coexistence, and prerequisite chains.
"""

    docs["CHAMPION_CIRCUIT.md"] = """
# Champion Circuit

The Saffron Fighting Dojo Champion Circuit exposes repeatable late-postgame battles.

## References

- Export: `exports/perfect_johto/champion_circuit.json`.
- Phase 8 report: `docs/phase8_postgame_report.md`.
- Boss battle summary: `docs/BOSS_BATTLES.md`.
- Kanto postgame hub: `docs/KANTO_POSTGAME.md`.

## Unlocks

- Lance and Blue unlock after 16 badges.
- Red rematch, Steven, Wallace, Cynthia, and Arceus unlock after the original Mt. Silver Red defeat flag.
- Steven, Wallace, and Cynthia are valid six-Pokemon Champion-class records.

## Level Band

Champion Circuit trainers sit at 92-96, matching Red's late-postgame superboss band.

## Runtime Focus

Runtime testing should verify unlock gates, repeatability, party data, Dojo menu flow, and interactions with the original Mt. Silver Red defeat flag.
"""

    docs["ITEMS_AND_MARTS.md"] = f"""
# Items And Marts

This doc covers the badge-gated mart economy, customization items, IV candies, Max Candy, and evolution-item access.

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
- Party-use behavior: `hg-engine-main/hg-engine-main/src/individual/PartyMenu_HandleUseItemOnMon.c`.
- Item text archives: `hg-engine-main/hg-engine-main/data/text/222.txt` and related text archives.

## Badge Mart Summary

- Badge mart entries: {mart['badge_mart_count']} / {mart['badge_mart_ui_limit']} UI limit.
- 0-2 badges: core balls, medicine, status heals, Escape Rope, and Repels.
- 3 badges: EV feathers, EV-reduction berries, all available mints, and Ability Capsule.
- 4 badges: EV vitamins, common stones, Oval Stone, and Linking Cord.
- 5 badges: IV stat candies, Macho Brace, Power items, and trade-item replacements.
- 6 badges: Ability Patch and broad modern evolution items, including Black Augurite, Peat Block, Galarica Cuff, and Galarica Wreath.
- 12 badges: Max Candy.

## Prices And Effects

- Max Candy costs 8000, unlocks at 12 badges, and sets all six IVs to 31.
- Health, Mighty, Tough, Smart, Courage, and Quick Candy cost 2000, unlock at 5 badges, and set one matching IV to 31.
- Mints and Ability Capsule/Patch cost 1000 with their intended badge gates.
- Vitamins and Power items cost 3000.
- Feathers cost 300.
- EV-reduction berries cost 200.
- Approved-scope evolution items are stocked through the badge mart.

## Restrictions

- Forbidden gimmick items are not stocked in the badge mart.
- Unrelated later-family evolution items are not exposed unless needed by an approved Gen 1-4 family exception.
- Trainer-battle held-item restoration remains out of scope.
"""

    docs["KANTO_POSTGAME.md"] = """
# Kanto Postgame

The Kanto postgame is centered on the Saffron Fighting Dojo after all 16 badges. The hub provides Champion Circuit battles and legendary/mythical dossier encounters while preserving visible Gym Leader rematch scripts.

## References

- Phase 8 report: `docs/phase8_postgame_report.md`.
- Legendary access: `docs/LEGENDARIES.md`.
- Champion Circuit: `docs/CHAMPION_CIRCUIT.md`.
- Boss battles: `docs/BOSS_BATTLES.md`.
- Kanto postgame export: `exports/perfect_johto/kanto_postgame.json`.

## Hub Behavior

- The Dojo karate master becomes the postgame hub after all 16 badges.
- Existing 16 Gym Leader phone-rematch scripts remain intact and still use the visible leader NPCs.
- Lance and Blue are repeatable from the Champion Circuit after 16 badges.
- Red rematch, Steven, Wallace, Cynthia, and Arceus unlock after the original Mt. Silver Red defeat flag.
- Latias and Latios use Phase 8 dossier flags separate from native roamer state.

## Related Progression

- Kanto wild levels were raised so post-League routes and caves are no longer vanilla low-level filler.
- Kanto Gym Leaders were raised into the post-League trainer curve, with Blue at 78-82.
- Gym Leader rematches, Elite Four rematches, Red, and Champion Circuit battles form the late-postgame challenge path.

## Runtime Focus

Runtime testing must check Dojo menu flow, Champion Circuit unlocks, legendary prerequisites, caught flags, retry behavior, Latias/Latios duplicate-access edge cases, and visible rematch NPC preservation.
"""

    docs["PLAYTEST_CHECKLIST.md"] = """
# Playtest Checklist

## New Game And Modes

- New game start.
- New Game mode selector before Oak's speech.
- Normal mode starts without level caps.
- Challenge mode level caps, Set battle style, and trainer-battle item block.
- Hardcore fainted-Pokemon release while preserving the last non-Egg party Pokemon.
- Nuzlocke first encounter/gift/static map-section claims.

## QOL And Economy

- Fast text behavior.
- Early Running Shoes from Mom.
- Cherrygrove Guide skip when Running Shoes are already owned.
- Deletable HMs.
- Reusable TMs.
- EV/IV viewer and nature indicators.
- Badge-gated mart unlocks.
- Max Candy and IV stat candies.
- Evolution item access.

## Pokemon Data

- No-trade evolutions.
- Known-move evolutions.
- Special-form evolutions for Dudunsparce Three-Segment and Ursaluna Bloodmoon.
- Approved later-generation forms/evolutions.
- Level-up move access for changed typings.
- Hidden ability wild rolls and Ability Patch behavior.

## Encounters

- Rare encounter verification.
- Kanto wild level balance.
- Starter late-game/postgame access.
- Random legendary surprise encounters at each badge tier.
- Repel behavior with random legendary surprise encounters.
- Safari exclusion from random legendary surprise encounters.
- Native Raikou/Entei roamer coexistence.
- Pokedex completion path.
- Final one-save obtainability.

## Trainers And Progression

- Early Johto level curve.
- Each Johto Gym Leader.
- Rival fights.
- Team Rocket events.
- Flexible Chuck/Jasmine/Pryce order.
- Clair.
- First Elite Four and Lance.
- Kanto route progression.
- Each Kanto Gym Leader.
- Blue.
- Gym rematches.
- Elite Four rematches.
- Red.

## Postgame And Legendaries

- Saffron Fighting Dojo hub.
- Champion Circuit Lance/Blue after 16 badges.
- Champion Circuit Red/Steven/Wallace/Cynthia after Red.
- Legendary dossier prerequisites.
- Legendary caught flags.
- Retry behavior after fleeing/fainting from dossier encounters.
- Latias/Latios duplicate-access edge cases.
"""

    docs["RELEASE_CHECKLIST.md"] = """
# Release Checklist

## Static Validations

- Run `python tools/perfect_johto/validate_project.py`.
- Confirm Phase 6, Phase 7, and Phase 8 validators pass.
- Confirm learnset JSON parsing and learnset generation pass.
- Confirm trainer source validation passes.
- Confirm text archive validation passes.
- Confirm forbidden config/gimmick and approved-scope scans pass.
- Confirm item, mart, evolution, random legendary, Dojo flag, and game-mode validations pass.

## Generated Artifacts

- Regenerate with `python tools/perfect_johto/validate_project.py --write` after gameplay data changes.
- Review changed files in `exports/perfect_johto/`.
- Review changed generated docs in `docs/`.
- Keep phase reports as audit appendices and category docs as front-door references.

## Build Commands

- Place a legally obtained US HeartGold ROM at `hg-engine-main/hg-engine-main/rom.nds`.
- Docker route: `docker build . -t hg-engine`, then `docker-makerom.cmd`.
- Native route: install Git, GNU Make, CMake, `armips`, and the ARM toolchain, then run `make -n` and the normal HG-Engine build.

## Manual Runtime Tests

- Complete the milestones in `docs/PLAYTEST_CHECKLIST.md`.
- Confirm Dojo script assembly and in-game Dojo menus.
- Confirm random legendary rates/exclusions by controlled test saves where possible.
- Confirm Pokedex area behavior or regenerate area data.
- Confirm game-mode behavior across Oak intro, battle rules, item use, gifts, static encounters, Nuzlocke claims, and save/reload.

## Must Not Commit Or Redistribute

- `rom.nds`.
- `baserom.nds`.
- Pre-patched ROMs.
- Copyrighted ROM data.

Preserve credits and attribution. The web-app explorer is a future separate project, not part of this ROM hack release.
"""

    docs["KNOWN_LIMITATIONS.md"] = f"""
# Known Limitations

## Build And Tooling

- Full ROM build is not confirmed in the current PowerShell environment because Git, Make, CMake, armips, Docker, and the ARM toolchain are missing on `PATH`.
- `hg-engine-main/hg-engine-main/rom.nds` is {'present' if build_details.get('rom_nds', {}).get('exists') else 'missing'} locally, but must never be committed or redistributed.
- `pokeheartgold-master/baserom.nds` is {'present' if build_details.get('baserom_nds', {}).get('exists') else 'missing'}.
- Dojo script assembly is static-validation-only when `armips` is unavailable.

## Runtime Testing

- Runtime behavior has not been fully playtested; use `docs/PLAYTEST_CHECKLIST.md`.
- Game mode rules need runtime testing across Oak intro, battles, item use, gifts, static encounters, save/reload, and Nuzlocke route claims.
- Trainer curve, boss teams, Rocket/Silver fights, rematches, Red, Champion Circuit unlocks, Dojo retries, and legendary/mythical caught flags need runtime testing.
- Random legendary surprise encounters need runtime testing for Repel behavior, Safari exclusion, native roamer coexistence, level scaling, and badge-gated pools.

## Data And Content

- Pokedex area data may need regeneration; this is a release blocker/TODO until engine behavior is confirmed.
- Latias/Latios dossier flags are separate from native roamer state and need duplicate-access edge-case testing.
- Approved regional/new form display text, naming, form handling, and evolution behavior need runtime and player-facing polish.

## Project Scope

- The web-app explorer remains a future separate project and is not part of this ROM hack phase.
- HG-Engine contains unused later-generation capacity; gameplay exposure must stay inside `docs/PROJECT_SCOPE.md`.
"""

    return docs


def write_docs(docs: dict[str, str]) -> None:
    for filename, text in docs.items():
        write_doc(filename, text)


def print_summary(results: list[CheckResult], wrote: bool) -> int:
    for result in results:
        print(f"{result.status:4} {result.name}: {result.details}")
    failures = [result for result in results if result.status == "FAIL"]
    warnings = [result for result in results if result.status == "WARN"]
    if wrote:
        print(f"Wrote exports to {rel(EXPORTS)}")
        print(f"Wrote static docs to {rel(DOCS)}")
    print(f"Summary: {len(failures)} failed, {len(warnings)} warnings, {len(results)} checks")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write exports and static docs")
    args = parser.parse_args(argv)
    results, build_details = run_validations()
    exports = build_exports(build_details, results)
    docs = generate_docs(exports, results, build_details)
    if args.write:
        write_json_exports(exports)
        write_docs(docs)
    return print_summary(results, args.write)


if __name__ == "__main__":
    raise SystemExit(main())
