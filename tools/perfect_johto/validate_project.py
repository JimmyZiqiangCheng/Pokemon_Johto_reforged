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
    {"badges": "0-3", "denominator": 0, "description": "disabled"},
    {"badges": "4+", "denominator": 100, "description": "1/100 aggregate unlocked-pool roll"},
]


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
    return [
        {
            "species": species,
            "name": symbol_name(species),
            "species_id": species_numbers.get(species),
            "min_badges": int(badges),
        }
        for species, badges in re.findall(r"\{\s*(SPECIES_[A-Z0-9_]+)\s*,\s*(\d+)\s*\}", block)
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
        "return 100;",
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
    return CheckResult("Random legendary validation", "PASS", f"{len(pool)} Gen 1-4 legendary/mythical pool entries; aggregate 1% roll, flee move, and exclusions present")


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
            {"area": entry.key, "rare_notes": entry.rare_notes}
            for entry in entries
            if phase6.is_meaningful(entry) and entry.rare_notes
        ],
        "random_legendary_surprise.json": {
            "pool": random_pool,
            "rates": EXPECTED_RANDOM_LEGENDARY_RATES,
            "roll_model": "One 1/100 overlay roll is made after a normal eligible wild encounter succeeds, then one species is selected from the unlocked pool.",
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
        {"risk": "Full ROM build not confirmed locally", "status": "blocked until build tools and legal rom.nds are present"},
        {"risk": "Dojo script not assembled locally if armips is missing", "status": "static script validation only"},
        {"risk": "Runtime behavior not playtested", "status": "use docs/PLAYTEST_CHECKLIST.md"},
        {"risk": "Pokedex area data may need regeneration", "status": "release blocker/TODO until engine behavior is confirmed"},
        {"risk": "Latias/Latios dossier flags are separate from native roamer state", "status": "manual duplicate-access edge-case testing required"},
        {"risk": "Dudunsparce Three-Segment and Ursaluna Bloodmoon special form access", "status": "not implemented; documented limitation"},
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

    docs["README.md"] = f"""
# {PROJECT_NAME} Documentation

This folder contains static documentation for {PROJECT_NAME}. The interactive web-app explorer is intentionally not part of this phase; structured exports live in `exports/perfect_johto/` for any future separate explorer project.

## Core Docs

- `PROJECT_SCOPE.md`
- `BUILD_AND_TESTING.md`
- `PLAYTEST_CHECKLIST.md`
- `RELEASE_CHECKLIST.md`
- `KNOWN_LIMITATIONS.md`

## Generated Data Summaries

- `POKEMON_AVAILABILITY.md`
- `WILD_ENCOUNTERS.md`
- `RARE_ENCOUNTERS.md`
- `TRAINER_TEAMS.md`
- `BOSS_BATTLES.md`
- `LEGENDARIES.md`
- `CHAMPION_CIRCUIT.md`
- `ITEMS_AND_MARTS.md`
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

## In Scope

{markdown_list(scope['rules'])}

## Out Of Scope

- Rock type no longer weak to Ground.
- Immortal Shell.
- Custom defensive ability behavior.
- Personalized Tyranitar, Salamence, or Dragonite changes.
- Mega Evolution, Primal Reversion, Z-Moves, Dynamax/Gigantamax, and Terastalization.
- Restoring consumed held items after trainer battles.
- Interactive web app or browser explorer.

The web-app explorer is a future separate project, not part of this ROM hack phase. This project provides structured data exports in `exports/perfect_johto/` that a later separate explorer can consume.
"""

    docs["QOL_FEATURES.md"] = """
# QOL Features

- Fast text is enabled globally through `FAST_TEXT_PRINTING`.
- HMs are deletable through `DELETABLE_HMS`.
- TMs are reusable through existing HG-Engine configuration.
- EV/IV viewer and nature indicators are enabled.
- Reusable Repels, capture EXP, critical captures, expanded PC boxes, updated vitamin EV caps, Hidden Abilities, and overworld poison-damage disablement are preserved.
- Max Candy and IV stat candies are party-use convenience items added by Phase 5.

Runtime playtesting is still required for each QOL feature in a built ROM.
"""

    docs["POKEMON_AVAILABILITY.md"] = f"""
# Pokemon Availability

All Gen 1-4 Pokemon are intended to be obtainable in one save file. Phase 6 static validation reports non-legendary Gen 1-4 evolution-family coverage as complete across main, Safari, and Headbutt encounter sources. Phase 8 covers Gen 1-4 legendary/mythical availability through native roamers and the Saffron Fighting Dojo dossier system.

- Availability export: `exports/perfect_johto/pokemon_availability.json`
- Encounter report: `docs/phase6_obtainability_report.md`
- Legendary report: `docs/phase8_postgame_report.md`

Release blocker/TODO: confirm whether Pokedex area data is derived from encounter tables or needs a separate regeneration step.
"""

    docs["APPROVED_LATER_EXCEPTIONS.md"] = f"""
# Approved Later Exceptions

Approved later exceptions are limited to direct evolutions, regional forms, and new forms of Gen 1-4 Pokemon families.

- Export: `exports/perfect_johto/approved_later_exceptions.json`
- Count: {len(later)}

No unrelated Gen 5+ Pokemon are intentionally exposed by encounter, trainer, mart, or Phase 8 Dojo gameplay files.
"""

    docs["EVOLUTIONS.md"] = """
# Evolutions

Evolution data is exported from `data/Evolutions.c`.

- Export: `exports/perfect_johto/evolutions.json`
- Trade replacement export: `exports/perfect_johto/trade_evolution_replacements.json`
- No approved-scope trade-only evolutions remain in static validation.
- Required approved-scope evolution items are checked against the badge-gated mart.
- Known-move evolutions are checked against level-up learnsets for reasonable access.

Known limitation: Dudunsparce Three-Segment and Ursaluna Bloodmoon special form access are not implemented yet.
"""

    docs["WILD_ENCOUNTERS.md"] = f"""
# Wild Encounters

Wild encounters are generated from `data/Encounters.c` and summarized in `exports/perfect_johto/wild_encounters.json`.

Main land encounters use a shared daytime pool: the engine-facing morning and day arrays are kept identical, while night remains separate.

Static validation confirms Phase 6 encounter structure, approved-scope species use, late-Johto and Kanto level raises, starter late/postgame access, six-species minimum area variety, Gen 3-4 Johto-main base-form coverage, and rare-slot coverage. See `docs/phase6_obtainability_report.md` for the detailed area list.
"""

    docs["RARE_ENCOUNTERS.md"] = f"""
# Rare Encounters

- Export: `exports/perfect_johto/rare_encounters.json`
- Meaningful non-Safari areas with rare notes: {len(rare)}
- Land rare slots use the 4% slot 8.
- Surf rare slots use the 4% slot 3.
- Fishing rare slots use the Phase 6 4% slot 4.
- Every meaningful non-Safari encounter area has 1-3 rare species.
- Rare species are reserved for strong current forms, lines whose final form reaches 500+ BST, or approved regional forms.

Rare pseudo-legendary initial forms are intentionally sparse and semantically placed, including Larvitar, Bagon, Gible, Beldum, and Riolu in cave, mountain, dragon, or expert-training contexts.
"""

    docs["RANDOM_LEGENDARY_SYSTEM.md"] = f"""
# Random Legendary System

The random legendary surprise overlay is implemented in `src/field/enemy_party.c` from `AddWildPartyPokemon` after normal wild encounter generation succeeds.

## Rates

{markdown_list([f"{row['badges']} badges: {row['description']}" for row in random_legendary['rates']])}

The 1/100 rate is an aggregate overlay roll, not one independent roll per legendary. After the roll succeeds, one species is selected from the currently unlocked pool.

Surprise legendaries receive Teleport in move slot 4, giving the wild AI a move-based chance to flee each turn.

## Exclusions

{markdown_list(random_legendary['blocked_battle_types'])}

The system uses normal wild battles, does not write to roamer save state, and respects Repel through the pre-existing normal encounter flow. Runtime testing is still required.
"""

    docs["TRAINER_TEAMS.md"] = """
# Trainer Teams

Trainer teams are exported from `data/Trainers.c`.

- Full export: `exports/perfect_johto/trainer_teams.json`
- Phase 7 report: `docs/phase7_trainer_report.md`

Static validation checks trainer species, moves, items, ability slots, approved Pokemon scope, regular-trainer Gen 3-4 variety, major rival/Rocket sizes, and mandatory six-Pokemon boss rules.
"""

    docs["BOSS_BATTLES.md"] = f"""
# Boss Battles

- Export: `exports/perfect_johto/boss_battles.json`
- Boss records exported: {len(boss)}

Gym Leaders, Elite Four members, Champions, Red, Champion Circuit trainers, and major late rival/Rocket records are validated for intended team sizes. Route/order playtesting is still needed for local difficulty spikes.
"""

    docs["LEGENDARIES.md"] = f"""
# Legendaries

Phase 8 provides native roamer documentation plus Saffron Fighting Dojo dossier encounters.

- Export: `exports/perfect_johto/proper_legendary_events.json`
- Native entries: {len(legends['native'])}
- Dojo dossier entries: {len(legends['dojo_dossiers'])}

Static encounter outcome `4` is used so caught flags are set only on capture; failed, fled, or fainted dossier battles remain retryable by script logic. Raikou and Entei remain native Burned Tower roamers.
"""

    docs["CHAMPION_CIRCUIT.md"] = """
# Champion Circuit

The Saffron Fighting Dojo Champion Circuit exposes repeatable postgame battles.

- Lance and Blue unlock after 16 badges.
- Red rematch, Steven, Wallace, Cynthia, and Arceus unlock after the original Mt. Silver Red defeat flag.
- Steven, Wallace, and Cynthia are valid six-Pokemon Champion-class records.

Export: `exports/perfect_johto/champion_circuit.json`
"""

    docs["ITEMS_AND_MARTS.md"] = f"""
# Items And Marts

- Badge mart export: `exports/perfect_johto/items_and_marts.json`
- Customization export: `exports/perfect_johto/customization_items.json`
- Max Candy export: `exports/perfect_johto/max_candy.json`
- Badge mart entries: {mart['badge_mart_count']} / {mart['badge_mart_ui_limit']} UI limit.

Max Candy costs 8000 and unlocks at 12 badges. IV stat candies cost 2000 and unlock at 5 badges. Mints and Ability Capsule/Patch cost 1000 with their intended badge gates. No forbidden gimmick items are stocked in the badge mart.
"""

    docs["KANTO_POSTGAME.md"] = """
# Kanto Postgame

Phase 8 repurposes the Saffron Fighting Dojo karate master into a postgame hub after all 16 badges while preserving visible Gym Leader rematch scripts.

The hub contains Champion Circuit battles and legendary/mythical dossiers. Latias and Latios use Phase 8 dossier flags separate from native roamer state; runtime testing must check duplicate-access edge cases.
"""

    docs["PLAYTEST_CHECKLIST.md"] = """
# Playtest Checklist

- New game start.
- Fast text behavior.
- Deletable HMs.
- Reusable TMs.
- EV/IV viewer and nature indicators.
- Badge-gated mart unlocks.
- Max Candy and IV stat candies.
- Evolution item access.
- No-trade evolutions.
- Approved later-generation forms/evolutions.
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
- Saffron Fighting Dojo hub.
- Champion Circuit Lance/Blue after 16 badges.
- Champion Circuit Red/Steven/Wallace/Cynthia after Red.
- Legendary dossier prerequisites.
- Legendary caught flags.
- Retry behavior after fleeing/fainting from dossier encounters.
- Latias/Latios duplicate-access edge cases.
- Native Raikou/Entei roamer coexistence.
- Random legendary surprise encounters at each badge tier.
- Repel behavior with random legendary surprise encounters.
- Safari exclusion from random legendary surprise encounters.
- Rare encounter verification.
- Kanto wild level balance.
- Pokedex completion path.
- Final one-save obtainability.
"""

    docs["RELEASE_CHECKLIST.md"] = """
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
"""

    docs["KNOWN_LIMITATIONS.md"] = f"""
# Known Limitations

{markdown_list([f"{item['risk']}: {item['status']}" for item in risks])}

Static validation is strong enough for audit readiness, but the ROM has not been proven buildable or runtime-stable on this machine while required tools and `rom.nds` are missing.
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
