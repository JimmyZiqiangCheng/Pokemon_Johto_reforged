#!/usr/bin/env python3
"""Phase 6 encounter regeneration and validation for Pokemon Johto Reforged."""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import re
from collections import defaultdict, deque


ROOT = pathlib.Path(__file__).resolve().parents[2]
ENGINE = ROOT / "hg-engine-main" / "hg-engine-main"
ENCOUNTERS = ENGINE / "data" / "Encounters.c"
REPORT = ROOT / "docs" / "phase6_obtainability_report.md"

LAND_RATES = [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1]
SURF_RATES = [60, 30, 5, 4, 1]
FISH_RATES_PHASE6 = [40, 30, 16, 10, 4]

LEGENDARY_OR_MYTHICAL = {
    "SPECIES_ARTICUNO",
    "SPECIES_ZAPDOS",
    "SPECIES_MOLTRES",
    "SPECIES_MEWTWO",
    "SPECIES_MEW",
    "SPECIES_RAIKOU",
    "SPECIES_ENTEI",
    "SPECIES_SUICUNE",
    "SPECIES_LUGIA",
    "SPECIES_HO_OH",
    "SPECIES_CELEBI",
    "SPECIES_REGIROCK",
    "SPECIES_REGICE",
    "SPECIES_REGISTEEL",
    "SPECIES_LATIAS",
    "SPECIES_LATIOS",
    "SPECIES_KYOGRE",
    "SPECIES_GROUDON",
    "SPECIES_RAYQUAZA",
    "SPECIES_JIRACHI",
    "SPECIES_DEOXYS",
    "SPECIES_UXIE",
    "SPECIES_MESPRIT",
    "SPECIES_AZELF",
    "SPECIES_DIALGA",
    "SPECIES_PALKIA",
    "SPECIES_HEATRAN",
    "SPECIES_REGIGIGAS",
    "SPECIES_GIRATINA",
    "SPECIES_CRESSELIA",
    "SPECIES_PHIONE",
    "SPECIES_MANAPHY",
    "SPECIES_DARKRAI",
    "SPECIES_SHAYMIN",
    "SPECIES_ARCEUS",
}

APPROVED_LATER_PLACEMENTS = {
    "SPECIES_RATTATA_ALOLAN",
    "SPECIES_SANDSHREW_ALOLAN",
    "SPECIES_VULPIX_ALOLAN",
    "SPECIES_DIGLETT_ALOLAN",
    "SPECIES_MEOWTH_ALOLAN",
    "SPECIES_GEODUDE_ALOLAN",
    "SPECIES_GRIMER_ALOLAN",
    "SPECIES_MEOWTH_GALARIAN",
    "SPECIES_PONYTA_GALARIAN",
    "SPECIES_SLOWPOKE_GALARIAN",
    "SPECIES_FARFETCHD_GALARIAN",
    "SPECIES_MR_MIME_GALARIAN",
    "SPECIES_CORSOLA_GALARIAN",
    "SPECIES_ZIGZAGOON_GALARIAN",
    "SPECIES_GROWLITHE_HISUIAN",
    "SPECIES_VOLTORB_HISUIAN",
    "SPECIES_QWILFISH_HISUIAN",
    "SPECIES_SNEASEL_HISUIAN",
    "SPECIES_WOOPER_PALDEAN",
}


@dataclasses.dataclass
class Slot:
    min_level: int
    max_level: int
    species: str


@dataclasses.dataclass
class Encounter:
    key: str
    rate_walk: int
    rate_surf: int
    rate_rock_smash: int
    rate_old_rod: int
    rate_good_rod: int
    rate_super_rod: int
    levels: list[int]
    morning: list[str]
    day: list[str]
    night: list[str]
    hoenn_sound: list[str]
    sinnoh_sound: list[str]
    surf: list[Slot]
    rock_smash: list[Slot]
    old_rod: list[Slot]
    good_rod: list[Slot]
    super_rod: list[Slot]
    land_swarm: str
    surf_swarm: str
    night_fish: str
    fish_swarm: str
    rare_notes: list[str] = dataclasses.field(default_factory=list)


def extract_braced(text: str, start: int) -> tuple[str, int]:
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
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
                return text[start : i + 1], i + 1
    raise ValueError("unterminated brace block")


def find_field_block(block: str, field: str) -> str:
    token = f".{field}"
    pos = block.find(token)
    if pos < 0:
        raise ValueError(f"missing field {field}")
    start = block.find("{", pos)
    sub, _ = extract_braced(block, start)
    return sub


def parse_int_field(block: str, field: str) -> int:
    m = re.search(rf"\.{field}\s*=\s*(\d+)", block)
    if not m:
        raise ValueError(f"missing int field {field}")
    return int(m.group(1))


def parse_species_field(block: str, field: str) -> str:
    m = re.search(rf"\.{field}\s*=\s*(SPECIES_[A-Z0-9_]+)", block)
    if not m:
        raise ValueError(f"missing species field {field}")
    return m.group(1)


def parse_int_array(block: str, field: str) -> list[int]:
    sub = find_field_block(block, field)
    return [int(x) for x in re.findall(r"\d+", sub)]


def parse_species_array(block: str, field: str) -> list[str]:
    sub = find_field_block(block, field)
    return re.findall(r"SPECIES_[A-Z0-9_]+", sub)


def parse_slot_array(block: str, field: str) -> list[Slot]:
    sub = find_field_block(block, field)
    slots = []
    for min_level, max_level, species in re.findall(
        r"\{\s*(\d+)\s*,\s*(\d+)\s*,\s*(SPECIES_[A-Z0-9_]+)\s*\}", sub
    ):
        slots.append(Slot(int(min_level), int(max_level), species))
    return slots


def parse_encounters(path: pathlib.Path) -> list[Encounter]:
    text = path.read_text(encoding="utf-8")
    entries: list[Encounter] = []
    for m in re.finditer(r"\[(ENCDATA_[A-Z0-9_]+)\]\s*=\s*\{", text):
        key = m.group(1)
        block, _ = extract_braced(text, m.end() - 1)
        land = find_field_block(block, "landSlots")
        entries.append(
            Encounter(
                key=key,
                rate_walk=parse_int_field(block, "rateWalk"),
                rate_surf=parse_int_field(block, "rateSurf"),
                rate_rock_smash=parse_int_field(block, "rateRockSmash"),
                rate_old_rod=parse_int_field(block, "rateOldRod"),
                rate_good_rod=parse_int_field(block, "rateGoodRod"),
                rate_super_rod=parse_int_field(block, "rateSuperRod"),
                levels=parse_int_array(land, "levels"),
                morning=parse_species_array(land, "speciesMorning"),
                day=parse_species_array(land, "speciesDay"),
                night=parse_species_array(land, "speciesNight"),
                hoenn_sound=parse_species_array(block, "hoennSoundSpecies"),
                sinnoh_sound=parse_species_array(block, "sinnohSoundSpecies"),
                surf=parse_slot_array(block, "surfSlots"),
                rock_smash=parse_slot_array(block, "rockSmashSlots"),
                old_rod=parse_slot_array(block, "oldRodSlots"),
                good_rod=parse_slot_array(block, "goodRodSlots"),
                super_rod=parse_slot_array(block, "superRodSlots"),
                land_swarm=parse_species_field(block, "landSwarm"),
                surf_swarm=parse_species_field(block, "surfSwarm"),
                night_fish=parse_species_field(block, "nightFish"),
                fish_swarm=parse_species_field(block, "fishSwarm"),
            )
        )
    return entries


def has_real_land(entry: Encounter) -> bool:
    return entry.rate_walk > 0 and any(s != "SPECIES_NONE" for s in entry.morning + entry.day + entry.night)


def has_real_surf(entry: Encounter) -> bool:
    return entry.rate_surf > 0 and any(s.species != "SPECIES_NONE" for s in entry.surf)


def has_real_fish(entry: Encounter) -> bool:
    return (
        entry.rate_old_rod > 0
        or entry.rate_good_rod > 0
        or entry.rate_super_rod > 0
    ) and any(
        s.species != "SPECIES_NONE"
        for s in entry.old_rod + entry.good_rod + entry.super_rod
    )


def is_meaningful(entry: Encounter) -> bool:
    return "UNUSED" not in entry.key and (has_real_land(entry) or has_real_surf(entry) or has_real_fish(entry))


def average_land_level(entry: Encounter) -> int:
    levels = [level for level, species in zip(entry.levels, entry.day) if species != "SPECIES_NONE" and level > 0]
    if not levels:
        levels = [level for level in entry.levels if level > 0]
    if not levels:
        return 20
    return max(2, round(sum(levels) / len(levels)))


def set_land_rare(entry: Encounter, species: str, level: int | None = None, slots=(10, 11), note: str | None = None) -> None:
    if not has_real_land(entry):
        return
    if level is None:
        level = average_land_level(entry)
    for slot in slots:
        entry.levels[slot] = level
        entry.morning[slot] = species
        entry.day[slot] = species
        entry.night[slot] = species
    rate = sum(LAND_RATES[slot] for slot in slots)
    entry.rare_notes.append(f"land {species} {rate}% lv{level}" + (f" - {note}" if note else ""))


def set_time_land_rare(
    entry: Encounter,
    morning: str,
    day: str,
    night: str,
    level: int | None = None,
    slots=(10, 11),
    note: str | None = None,
) -> None:
    if not has_real_land(entry):
        return
    if level is None:
        level = average_land_level(entry)
    for slot in slots:
        entry.levels[slot] = level
        entry.morning[slot] = morning
        entry.day[slot] = day
        entry.night[slot] = night
    rate = sum(LAND_RATES[slot] for slot in slots)
    entry.rare_notes.append(f"land timed rare {rate}% lv{level}" + (f" - {note}" if note else ""))


def set_surf_rare(entry: Encounter, species: str, level: int | None = None, note: str | None = None) -> None:
    if not has_real_surf(entry):
        return
    if level is None:
        real = [s for s in entry.surf if s.species != "SPECIES_NONE"]
        level = round(sum((s.min_level + s.max_level) / 2 for s in real) / len(real))
    entry.surf[4] = Slot(max(1, level - 1), level + 1, species)
    entry.rare_notes.append(f"surf {species} 1% lv{max(1, level - 1)}-{level + 1}" + (f" - {note}" if note else ""))


def set_fish_rare(entry: Encounter, species: str, level: int | None = None, rod: str = "super", note: str | None = None) -> None:
    slots = {"old": entry.old_rod, "good": entry.good_rod, "super": entry.super_rod}[rod]
    if not slots or all(slot.species == "SPECIES_NONE" for slot in slots):
        return
    if level is None:
        real = [s for s in slots if s.species != "SPECIES_NONE"]
        level = round(sum((s.min_level + s.max_level) / 2 for s in real) / len(real))
    slots[4] = Slot(max(1, level - 1), level + 1, species)
    entry.rare_notes.append(f"{rod} rod {species} 4% lv{max(1, level - 1)}-{level + 1}" + (f" - {note}" if note else ""))


def scale_land(entry: Encounter, levels: list[int]) -> None:
    if has_real_land(entry):
        entry.levels = levels[:12]


def scale_slots(slots: list[Slot], target_min: int, target_max: int) -> None:
    real = [slot for slot in slots if slot.species != "SPECIES_NONE"]
    if not real:
        return
    pattern = [
        (target_min, target_min + 2),
        (target_min, target_min + 3),
        (target_min + 2, target_max - 2),
        (target_min + 3, target_max - 1),
        (target_max - 2, target_max),
    ]
    for slot, (lo, hi) in zip(slots, pattern):
        if slot.species != "SPECIES_NONE":
            slot.min_level = max(1, lo)
            slot.max_level = max(slot.min_level, hi)


def scale_kanto_and_late(entries: list[Encounter]) -> None:
    levels_36_43 = [36, 36, 37, 37, 38, 38, 39, 39, 40, 40, 41, 43]
    levels_38_46 = [38, 38, 39, 39, 40, 40, 42, 42, 44, 44, 45, 46]
    levels_42_50 = [42, 42, 43, 43, 44, 44, 46, 46, 48, 48, 49, 50]
    levels_50_58 = [50, 50, 51, 51, 52, 52, 54, 54, 56, 56, 57, 58]
    levels_55_64 = [55, 55, 56, 56, 58, 58, 60, 60, 62, 62, 63, 64]
    for entry in entries:
        key = entry.key
        if key in {"ENCDATA_R26_ROUTE_26", "ENCDATA_R27_ROUTE_27", "ENCDATA_D43R0101_VICTORY_ROAD_1F", "ENCDATA_D43R0102_VICTORY_ROAD_2F", "ENCDATA_D43R0103_VICTORY_ROAD_3F", "ENCDATA_D45R0101_TOHJO_FALLS"}:
            scale_land(entry, levels_42_50)
        elif any(tag in key for tag in ["CERULEAN_CAVE"]):
            scale_land(entry, levels_55_64)
        elif any(tag in key for tag in ["MT_SILVER", "R28_ROUTE_28"]):
            scale_land(entry, levels_50_58)
        elif any(tag in key for tag in ["SEAFOAM", "ROCK_TUNNEL", "DIGLETTS_CAVE", "MT_MOON"]):
            scale_land(entry, levels_42_50)
        elif re.search(r"ENCDATA_(R0[1-9]|R1[0-8]|R22|R24|R25|R02R0101|D46R0101)", key):
            scale_land(entry, levels_36_43)
        elif key in {
            "ENCDATA_T01_PALLET_TOWN",
            "ENCDATA_T02_VIRIDIAN_CITY",
            "ENCDATA_T04_CERULEAN_CITY",
            "ENCDATA_T06_VERMILION_CITY",
            "ENCDATA_T07_CELADON_CITY",
            "ENCDATA_T08_FUCHSIA_CITY",
            "ENCDATA_T09_CINNABAR_ISLAND",
            "ENCDATA_W19_ROUTE_19",
            "ENCDATA_W20_ROUTE_20",
            "ENCDATA_W21_ROUTE_21",
            "ENCDATA_R12_ROUTE_12",
        }:
            scale_land(entry, levels_38_46)

        if any(tag in key for tag in ["CERULEAN_CAVE", "MT_SILVER"]):
            for slots in [entry.surf, entry.good_rod, entry.super_rod]:
                scale_slots(slots, 50, 60)
        elif (
            re.search(r"ENCDATA_(R0[1-9]|R1[0-8]|R22|R24|R25|R02R0101|D46R0101)", key)
            or key.startswith("ENCDATA_T0")
            or key in {"ENCDATA_W19_ROUTE_19", "ENCDATA_W20_ROUTE_20", "ENCDATA_W21_ROUTE_21", "ENCDATA_R12_ROUTE_12"}
        ):
            for slots in [entry.surf, entry.good_rod, entry.super_rod]:
                scale_slots(slots, 35, 45)
        elif key in {"ENCDATA_R26_ROUTE_26", "ENCDATA_R27_ROUTE_27", "ENCDATA_D45R0101_TOHJO_FALLS"}:
            for slots in [entry.surf, entry.good_rod, entry.super_rod]:
                scale_slots(slots, 40, 48)


def entry_by_key(entries: list[Encounter]) -> dict[str, Encounter]:
    return {entry.key: entry for entry in entries}


def add_explicit_placements(entries: list[Encounter]) -> None:
    e = entry_by_key(entries)
    land = [
        ("ENCDATA_R29_ROUTE_29", "SPECIES_SHINX", 4, (10, 11), "early electric variety without starter clutter"),
        ("ENCDATA_R30_ROUTE_30", "SPECIES_LEDYBA", 4, (10, 11), "morning Johto bug line access"),
        ("ENCDATA_R31_ROUTE_31", "SPECIES_WEEDLE", 5, (10, 11), "version-independent forest bug access"),
        ("ENCDATA_D15R0102_SPROUT_TOWER_2F", "SPECIES_CHINGLING", 6, (10, 11), "quiet tower rare"),
        ("ENCDATA_D15R0103_SPROUT_TOWER_3F", "SPECIES_TOGEPI", 7, (10,), "sacred tower surprise"),
        ("ENCDATA_R32_ROUTE_32", "SPECIES_WOOPER_PALDEAN", 8, (10, 11), "approved Wooper-family regional form"),
        ("ENCDATA_D24R0101_RUINS_OF_ALPH_OUTSIDE", "SPECIES_NATU", 12, (10, 11), "mystic ruins flavor"),
        ("ENCDATA_D24R0205_RUINS_OF_ALPH_INSIDE_MAIN_ROOM", "SPECIES_SPIRITOMB", 16, (10,), "ancient sealed-spirit rare"),
        ("ENCDATA_D25R0101_UNION_CAVE_1F", "SPECIES_ARON", 9, (10, 11), "mineral cave line"),
        ("ENCDATA_D25R0102_UNION_CAVE_B1F", "SPECIES_MAWILE", 10, (10, 11), "cave steel/fairy-line access"),
        ("ENCDATA_D25R0103_UNION_CAVE_B2F", "SPECIES_LILEEP", 22, (10,), "deep fossil-adjacent rare"),
        ("ENCDATA_R33_ROUTE_33", "SPECIES_GULPIN", 11, (10, 11), "wet lowland Hoenn line"),
        ("ENCDATA_D26R0102_SLOWPOKE_WELL_1F", "SPECIES_SLOWPOKE_GALARIAN", 12, (10, 11), "approved Slowpoke-family regional form"),
        ("ENCDATA_D26R0103_SLOWPOKE_WELL_B2F", "SPECIES_SHELLDER", 15, (10, 11), "Slowpoke ecosystem pairing"),
        ("ENCDATA_D36R0101_ILEX_FOREST", "SPECIES_NINCADA", 14, (10, 11), "hidden forest molt line"),
        ("ENCDATA_R34_ROUTE_34", "SPECIES_SKITTY", 15, (10, 11), "Goldenrod-adjacent domestic rare"),
        ("ENCDATA_R35_ROUTE_35", "SPECIES_EEVEE", 16, (10,), "desirable but restrained city-edge rare"),
        ("ENCDATA_D22R0101_NATIONAL_PARK", "SPECIES_SCYTHER", 16, (10,), "classic park rare"),
        ("ENCDATA_D22R0102_NATIONAL_PARK_BUG_CATCHING_CONTEST", "SPECIES_PINSIR", 16, (10,), "contest counterpart rare"),
        ("ENCDATA_R36_ROUTE_36", "SPECIES_BONSLY", 17, (10, 11), "Sudowoodo-route family access"),
        ("ENCDATA_R37_ROUTE_37", "SPECIES_VULPIX", 18, (10, 11), "Ecruteak fox-fire flavor"),
        ("ENCDATA_D18R0101_BURNED_TOWER_1F", "SPECIES_HOUNDOUR", 18, (10, 11), "burned ruins dark/fire rare"),
        ("ENCDATA_D18R0102_BURNED_TOWER_B1F", "SPECIES_DUSKULL", 19, (10, 11), "haunted basement rare"),
        ("ENCDATA_D17R0102_BELL_TOWER_2F", "SPECIES_TOGEPI", 22, (10,), "sacred tower line"),
        ("ENCDATA_D17R0103_BELL_TOWER_3F", "SPECIES_CHIMECHO", 23, (10, 11), "bell-themed rare"),
        ("ENCDATA_D17R0104_BELL_TOWER_4F", "SPECIES_DRIFLOON", 24, (10, 11), "windborne tower rare"),
        ("ENCDATA_D17R0105_BELL_TOWER_5F", "SPECIES_ABSOL", 25, (10, 11), "omens near a sacred tower"),
        ("ENCDATA_D17R0106_BELL_TOWER_6F", "SPECIES_PONYTA_GALARIAN", 26, (10,), "approved mystical regional form"),
        ("ENCDATA_D17R0107_BELL_TOWER_7F", "SPECIES_KECLEON", 27, (10, 11), "hidden tower trickster"),
        ("ENCDATA_D17R0108_BELL_TOWER_8F", "SPECIES_CASTFORM", 28, (10, 11), "weather-sensitive tower rare"),
        ("ENCDATA_D17R0109_BELL_TOWER_9F", "SPECIES_CHERUBI", 29, (10, 11), "sunlit tower crown"),
        ("ENCDATA_D17R0112_BELL_TOWER_10F", "SPECIES_CHIKORITA", 32, (10,), "late Johto starter access"),
        ("ENCDATA_D17R0112_BELL_TOWER_10F", "SPECIES_CYNDAQUIL", 32, (11,), "late Johto starter access"),
        ("ENCDATA_R38_ROUTE_38", "SPECIES_MEOWTH_GALARIAN", 18, (10, 11), "approved Meowth-family regional form"),
        ("ENCDATA_R39_ROUTE_39", "SPECIES_FARFETCHD_GALARIAN", 19, (10, 11), "farm-route regional Farfetch'd"),
        ("ENCDATA_D40R0101_WHIRL_ISLANDS_1F", "SPECIES_BAGON", 25, (10,), "rugged sea-cave dragon rare"),
        ("ENCDATA_D40R0102_WHIRL_ISLANDS_B1F", "SPECIES_QWILFISH_HISUIAN", 26, (10, 11), "approved Qwilfish regional form"),
        ("ENCDATA_D40R0104_WHIRL_ISLANDS_B2F", "SPECIES_CORSOLA_GALARIAN", 28, (10,), "deep ghostly coral form"),
        ("ENCDATA_D40R0106_WHIRL_ISLANDS_B3F_LEDGE_OVERLOOKING_LUGIA_ROOM", "SPECIES_DRATINI", 30, (10,), "dragon-water pilgrimage rare"),
        ("ENCDATA_R42_ROUTE_42", "SPECIES_TEDDIURSA", 22, (10, 11), "mountain-edge bear line"),
        ("ENCDATA_D38R0101_MT_MORTAR_WATERFALL_ROOM", "SPECIES_TYROGUE", 25, (10, 11), "Mt. Mortar fighting-line access"),
        ("ENCDATA_D38R0102_MT_MORTAR_CENTRAL_ROOM", "SPECIES_BELDUM", 27, (10,), "mineral/steel pseudo rare"),
        ("ENCDATA_D38R0103_MT_MORTAR_ROOM_ABOVE_WATERFALL", "SPECIES_CRANIDOS", 28, (10,), "rugged fossil-line rare"),
        ("ENCDATA_D38R0104_MT_MORTAR_B1F", "SPECIES_SHIELDON", 28, (10,), "deep fossil-line counterpart"),
        ("ENCDATA_R43_ROUTE_43", "SPECIES_CASTFORM", 24, (10, 11), "Lake of Rage weather route"),
        ("ENCDATA_R44_ROUTE_44", "SPECIES_KECLEON", 26, (10, 11), "concealed roadside rare"),
        ("ENCDATA_D39R0101_ICE_PATH_1F", "SPECIES_SNORUNT", 28, (10, 11), "cold-cave Hoenn ice line"),
        ("ENCDATA_D39R0102_ICE_PATH_B1F", "SPECIES_SANDSHREW_ALOLAN", 29, (10, 11), "approved cold regional form"),
        ("ENCDATA_D39R0103_ICE_PATH_B2F", "SPECIES_VULPIX_ALOLAN", 30, (10,), "stronger cold regional rare"),
        ("ENCDATA_D39R0104_ICE_PATH_B3F", "SPECIES_SNOVER", 31, (10, 11), "deep ice forest line"),
        ("ENCDATA_D44R0102_DRAGONS_DEN", "SPECIES_DRATINI", 35, (10,), "Johto dragon identity"),
        ("ENCDATA_R45_ROUTE_45", "SPECIES_SKARMORY", 33, (10, 11), "cliffside steel bird"),
        ("ENCDATA_R46_ROUTE_46", "SPECIES_TRAPINCH", 10, (10, 11), "dry cliff rare without early power spike"),
        ("ENCDATA_D42R0102_DARK_CAVE_ROUTE_31_ENTRANCE", "SPECIES_LARVITAR", 7, (10,), "Sacred Gold-style early pseudo at 1%"),
        ("ENCDATA_D42R0101_DARK_CAVE_ROUTE_45_ENTRANCE", "SPECIES_GIBLE", 32, (10,), "deep rocky tunnel pseudo rare"),
        ("ENCDATA_R47_ROUTE_47", "SPECIES_TURTWIG", 35, (10,), "late Johto starter access"),
        ("ENCDATA_R48_ROUTE_48", "SPECIES_TREECKO", 35, (10,), "Safari-frontier Hoenn starter access"),
        ("ENCDATA_D50R0101_CLIFF_CAVE", "SPECIES_ANORITH", 35, (10,), "cliff fossil-line rare"),
        ("ENCDATA_D02R0103_MT_MOON_OUTSIDE_AREA", "SPECIES_CLEFFA", 38, (10, 11), "Mt. Moon moonlight rare"),
        ("ENCDATA_D02R0104_MT_MOON_OUTSIDE_CLEFAIRY_ACTIVE", "SPECIES_CLEFAIRY", 40, (10, 11), "active moonlight table"),
        ("ENCDATA_D02R0101_MT_MOON_1F", "SPECIES_CHARMANDER", 39, (10,), "postgame Kanto starter access"),
        ("ENCDATA_D02R0102_MT_MOON_2F", "SPECIES_AERODACTYL", 44, (10,), "ancient mountain fossil rare"),
        ("ENCDATA_D11R0101_SEAFOAM_ISLANDS_1F", "SPECIES_PIPLUP", 41, (10,), "postgame cold-water starter access"),
        ("ENCDATA_D11R0102_SEAFOAM_ISLANDS_B1F", "SPECIES_MR_MIME_GALARIAN", 43, (10, 11), "approved cold regional form"),
        ("ENCDATA_D11R0103_SEAFOAM_ISLANDS_B2F", "SPECIES_DELIBIRD", 44, (10, 11), "deep ice cave rare"),
        ("ENCDATA_D11R0104_SEAFOAM_ISLANDS_B3F", "SPECIES_SNORUNT", 45, (10, 11), "deep ice family reinforcement"),
        ("ENCDATA_D11R0105_SEAFOAM_ISLANDS_B4F", "SPECIES_VULPIX_ALOLAN", 46, (10,), "deep cold regional rare"),
        ("ENCDATA_D41R0105_MT_SILVER_MOLTRES_ROOM", "SPECIES_CHIMCHAR", 55, (10,), "postgame fire starter access"),
        ("ENCDATA_D41R0106_MT_SILVER_3F", "SPECIES_BAGON", 56, (10,), "high mountain dragon rare"),
        ("ENCDATA_D41R0107_MT_SILVER_4F", "SPECIES_SNEASEL_HISUIAN", 57, (10, 11), "approved high-cliff regional form"),
        ("ENCDATA_D41R0101_MT_SILVER_1F", "SPECIES_TORCHIC", 53, (10,), "postgame fire starter access"),
        ("ENCDATA_D41R0103_MT_SILVER_MOUNTAINSIDE", "SPECIES_GROWLITHE_HISUIAN", 55, (10, 11), "approved volcanic mountain regional form"),
        ("ENCDATA_D41R0104_MT_SILVER_EXPERT_BELT_ROOM", "SPECIES_RIOLU", 55, (10,), "expert training chamber rare"),
        ("ENCDATA_D41R0102_MT_SILVER_TOP_SNOWY_AREA", "SPECIES_SNEASEL_HISUIAN", 58, (10, 11), "snowy summit form"),
        ("ENCDATA_R26_ROUTE_26", "SPECIES_MUDKIP", 43, (10,), "late pre-League starter access"),
        ("ENCDATA_R27_ROUTE_27", "SPECIES_PORYGON", 43, (10,), "Tohjo technical rare"),
        ("ENCDATA_R28_ROUTE_28", "SPECIES_SNORLAX", 55, (10,), "postgame mountain-gate rare"),
        ("ENCDATA_D05R0101_ROCK_TUNNEL_1F", "SPECIES_OMANYTE", 42, (10,), "ancient damp cave fossil"),
        ("ENCDATA_D05R0102_ROCK_TUNNEL_B1F", "SPECIES_KABUTO", 43, (10,), "ancient damp cave counterpart"),
        ("ENCDATA_D43R0101_VICTORY_ROAD_1F", "SPECIES_BAGON", 45, (10,), "late rugged dragon rare"),
        ("ENCDATA_D43R0102_VICTORY_ROAD_2F", "SPECIES_GIBLE", 46, (10,), "late tunnel pseudo rare"),
        ("ENCDATA_D43R0103_VICTORY_ROAD_3F", "SPECIES_BELDUM", 47, (10,), "late mineral pseudo rare"),
        ("ENCDATA_R01_ROUTE_1", "SPECIES_BULBASAUR", 37, (10,), "postgame Kanto starter access"),
        ("ENCDATA_R02_ROUTE_2_SOUTH_BELOW_VIRIDIAN_FOREST", "SPECIES_WEEDLE", 37, (10, 11), "Kanto forest bug version parity"),
        ("ENCDATA_R02R0101_ROUTE_2_NORTH_ABOVE_VIRIDIAN_FOREST", "SPECIES_BULBASAUR", 38, (10,), "postgame forest starter access"),
        ("ENCDATA_D46R0101_VIRIDIAN_FOREST", "SPECIES_CHIKORITA", 39, (10,), "postgame forest starter access"),
        ("ENCDATA_R03_ROUTE_3", "SPECIES_CHARMANDER", 39, (10,), "postgame rocky Kanto starter access"),
        ("ENCDATA_R04_ROUTE_4", "SPECIES_EEVEE", 39, (10,), "Cerulean-edge rare"),
        ("ENCDATA_R05_ROUTE_5", "SPECIES_MEOWTH", 38, (10, 11), "Kanto urban-cat family access"),
        ("ENCDATA_R06_ROUTE_6", "SPECIES_GLAMEOW", 38, (10, 11), "urban Sinnoh cat counterpart"),
        ("ENCDATA_R07_ROUTE_7", "SPECIES_PORYGON", 39, (10,), "Celadon technical rare"),
        ("ENCDATA_R08_ROUTE_8", "SPECIES_STUNKY", 39, (10, 11), "urban poison/dark Sinnoh line"),
        ("ENCDATA_R09_ROUTE_9", "SPECIES_VOLTORB_HISUIAN", 40, (10, 11), "Power Plant-adjacent regional form"),
        ("ENCDATA_R10_ROUTE_10", "SPECIES_ROTOM", 40, (10,), "Power Plant-adjacent ghost/electric rare"),
        ("ENCDATA_R11_ROUTE_11", "SPECIES_MUNCHLAX", 40, (10,), "Snorlax-route family access"),
        ("ENCDATA_R12_ROUTE_12", "SPECIES_TOTODILE", 40, (10,), "postgame water starter access"),
        ("ENCDATA_R13_ROUTE_13", "SPECIES_CARNIVINE", 39, (10, 11), "marsh-edge Sinnoh rare"),
        ("ENCDATA_R14_ROUTE_14", "SPECIES_TROPIUS", 40, (10, 11), "warm southern Kanto rare"),
        ("ENCDATA_R15_ROUTE_15", "SPECIES_BURMY", 39, (10, 11), "tree-lined route Sinnoh line"),
        ("ENCDATA_R16R0301_ROUTE_16", "SPECIES_RATTATA_ALOLAN", 40, (10, 11), "urban night-leaning regional family"),
        ("ENCDATA_R17_ROUTE_17", "SPECIES_TAUROS", 40, (10, 11), "wide-open Cycling Road plains"),
        ("ENCDATA_R18_ROUTE_18", "SPECIES_PONYTA", 40, (10, 11), "plains fire-horse family"),
        ("ENCDATA_R22_ROUTE_22", "SPECIES_TREECKO", 38, (10,), "postgame starter echo near Victory Road"),
        ("ENCDATA_R24_ROUTE_24", "SPECIES_SQUIRTLE", 38, (10,), "postgame water starter access"),
        ("ENCDATA_R25_ROUTE_25", "SPECIES_SHELLOS", 39, (10, 11), "coastal Sinnoh water line"),
        ("ENCDATA_D45R0101_TOHJO_FALLS", "SPECIES_FEEBAS", 42, (10,), "waterfall beauty line rare"),
        ("ENCDATA_D01R0101_DIGLETTS_CAVE", "SPECIES_DIGLETT_ALOLAN", 42, (10, 11), "approved Diglett regional form"),
        ("ENCDATA_D03R0101_CERULEAN_CAVE_1F", "SPECIES_DITTO", 58, (10, 11), "identity-shifting cave rare"),
        ("ENCDATA_D03R0102_CERULEAN_CAVE_B1F", "SPECIES_BELDUM", 60, (10,), "deep artificial/mineral pseudo"),
        ("ENCDATA_D03R0103_CERULEAN_CAVE_B2F", "SPECIES_ROTOM", 60, (10,), "deep strange-energy rare"),
    ]
    for key, species, level, slots, note in land:
        if key in e:
            set_land_rare(e[key], species, level, slots, note)

    timed = [
        ("ENCDATA_R37_ROUTE_37", "SPECIES_VULPIX", "SPECIES_VULPIX", "SPECIES_MISDREAVUS", 18, "day fox-fire, night ghost flavor"),
        ("ENCDATA_R38_ROUTE_38", "SPECIES_MEOWTH_GALARIAN", "SPECIES_MEOWTH_GALARIAN", "SPECIES_MEOWTH_ALOLAN", 18, "Meowth-family regional split by time"),
        ("ENCDATA_R16R0301_ROUTE_16", "SPECIES_RATTATA_ALOLAN", "SPECIES_RATTATA_ALOLAN", "SPECIES_GRIMER_ALOLAN", 40, "urban regional dark/poison forms"),
    ]
    for key, morning, day, night, level, note in timed:
        if key in e:
            set_time_land_rare(e[key], morning, day, night, level, (10, 11), note)

    surf = [
        ("ENCDATA_T20_NEW_BARK_TOWN", "SPECIES_SHELLDER", 18, "coastal Johto rare"),
        ("ENCDATA_T21_CHERRYGROVE_CITY", "SPECIES_STARYU", 18, "night-fish identity made always reachable"),
        ("ENCDATA_R30_ROUTE_30", "SPECIES_SURSKIT", 16, "pond bug/water rare"),
        ("ENCDATA_R31_ROUTE_31", "SPECIES_SURSKIT", 16, "pond bug/water rare"),
        ("ENCDATA_T22_VIOLET_CITY", "SPECIES_POLIWAG", 18, "city pond baseline rare"),
        ("ENCDATA_R32_ROUTE_32", "SPECIES_FEEBAS", 12, "very early but weak 1% water rare"),
        ("ENCDATA_R34_ROUTE_34", "SPECIES_CLAMPERL", 22, "coastal pearl rare"),
        ("ENCDATA_T26_OLIVINE_CITY", "SPECIES_WAILMER", 30, "port-city whale line"),
        ("ENCDATA_W40_ROUTE_40", "SPECIES_FINNEON", 28, "open-sea Sinnoh fish"),
        ("ENCDATA_W41_ROUTE_41", "SPECIES_CARVANHA", 30, "rough ocean predator"),
        ("ENCDATA_T24_CIANWOOD_CITY", "SPECIES_CLAMPERL", 30, "island pearl rare"),
        ("ENCDATA_T29_LAKE_OF_RAGE", "SPECIES_FEEBAS", 28, "lake beauty-line rare"),
        ("ENCDATA_T30_BLACKTHORN_CITY", "SPECIES_DRATINI", 35, "dragon-city water rare"),
        ("ENCDATA_R47_ROUTE_47", "SPECIES_SHELLOS", 35, "cliffside coastal Sinnoh line"),
        ("ENCDATA_T31_MT_SILVER_OUTSIDE_POKEMON_CENTER", "SPECIES_DRATINI", 50, "remote mountain water rare"),
        ("ENCDATA_R12_ROUTE_12", "SPECIES_TOTODILE", 40, "postgame water starter access"),
        ("ENCDATA_T01_PALLET_TOWN", "SPECIES_SQUIRTLE", 36, "postgame starter coastal access"),
        ("ENCDATA_T04_CERULEAN_CITY", "SPECIES_SQUIRTLE", 38, "postgame water-starter city access"),
        ("ENCDATA_T06_VERMILION_CITY", "SPECIES_WAILMER", 40, "major-port whale line"),
        ("ENCDATA_T08_FUCHSIA_CITY", "SPECIES_FINNEON", 40, "southern water-route fish"),
        ("ENCDATA_T09_CINNABAR_ISLAND", "SPECIES_CLAMPERL", 42, "island shellfish rare"),
        ("ENCDATA_W19_ROUTE_19", "SPECIES_PIPLUP", 40, "cold sea starter access"),
        ("ENCDATA_W20_ROUTE_20", "SPECIES_CARVANHA", 41, "rough current predator"),
        ("ENCDATA_W21_ROUTE_21", "SPECIES_WAILMER", 40, "deep ocean-route whale line"),
        ("ENCDATA_R24_ROUTE_24", "SPECIES_SQUIRTLE", 38, "Cerulean cape water starter"),
        ("ENCDATA_R25_ROUTE_25", "SPECIES_SHELLOS", 39, "coastal Sinnoh water line"),
        ("ENCDATA_D45R0101_TOHJO_FALLS", "SPECIES_FEEBAS", 43, "waterfall beauty-line rare"),
    ]
    for key, species, level, note in surf:
        if key in e:
            set_surf_rare(e[key], species, level, note)

    fish = [
        ("ENCDATA_W40_ROUTE_40", "SPECIES_LUVDISC", 30, "warm-water uncommon fish"),
        ("ENCDATA_W41_ROUTE_41", "SPECIES_RELICANTH", 42, "ancient deep-sea rare"),
        ("ENCDATA_T29_LAKE_OF_RAGE", "SPECIES_FEEBAS", 30, "lake beauty-line rare"),
        ("ENCDATA_D44R0102_DRAGONS_DEN", "SPECIES_DRATINI", 35, "dragon shrine fishing rare"),
        ("ENCDATA_T09_CINNABAR_ISLAND", "SPECIES_CLAMPERL", 42, "island shellfish rare"),
        ("ENCDATA_W19_ROUTE_19", "SPECIES_FINNEON", 40, "southern sea Sinnoh fish"),
        ("ENCDATA_W20_ROUTE_20", "SPECIES_CARVANHA", 41, "rough current predator"),
        ("ENCDATA_W21_ROUTE_21", "SPECIES_WAILMER", 40, "open sea whale line"),
        ("ENCDATA_D03R0101_CERULEAN_CAVE_1F", "SPECIES_FEEBAS", 55, "deep cave water rare"),
        ("ENCDATA_D03R0102_CERULEAN_CAVE_B1F", "SPECIES_RELICANTH", 58, "ancient cave-pool rare"),
        ("ENCDATA_D03R0103_CERULEAN_CAVE_B2F", "SPECIES_DRATINI", 58, "deep cave dragon-water rare"),
    ]
    for key, species, level, note in fish:
        if key in e:
            set_fish_rare(e[key], species, level, "super", note)


def default_rares(entries: list[Encounter]) -> None:
    route_cycle = [
        "SPECIES_RALTS",
        "SPECIES_SWABLU",
        "SPECIES_BUDEW",
        "SPECIES_SHROOMISH",
        "SPECIES_SPOINK",
        "SPECIES_MEDITITE",
        "SPECIES_COMBEE",
        "SPECIES_CHERUBI",
    ]
    cave_cycle = [
        "SPECIES_NOSEPASS",
        "SPECIES_MAWILE",
        "SPECIES_ARON",
        "SPECIES_BALTOY",
        "SPECIES_BRONZOR",
        "SPECIES_ABSOL",
    ]
    forest_cycle = ["SPECIES_COMBEE", "SPECIES_CHERUBI", "SPECIES_SHROOMISH", "SPECIES_NINCADA"]
    water_cycle = ["SPECIES_CLAMPERL", "SPECIES_FINNEON", "SPECIES_SHELLDER", "SPECIES_STARYU"]

    for idx, entry in enumerate(entries):
        if not is_meaningful(entry) or entry.rare_notes:
            continue
        key = entry.key
        if has_real_land(entry):
            if any(tag in key for tag in ["FOREST", "PARK"]):
                set_land_rare(entry, forest_cycle[idx % len(forest_cycle)], None, (10, 11), "default forest rare layer")
            elif any(tag in key for tag in ["CAVE", "TUNNEL", "MORTAR", "ROAD", "MOON", "RUINS", "TOWER", "DEN", "PATH"]):
                set_land_rare(entry, cave_cycle[idx % len(cave_cycle)], None, (10, 11), "default cave/dungeon rare layer")
            else:
                set_land_rare(entry, route_cycle[idx % len(route_cycle)], None, (10, 11), "default route rare layer")
        if not entry.rare_notes and has_real_surf(entry):
            set_surf_rare(entry, water_cycle[idx % len(water_cycle)], None, "default surf rare layer")
        if not entry.rare_notes and has_real_fish(entry):
            set_fish_rare(entry, water_cycle[idx % len(water_cycle)], None, "super", "default fishing rare layer")


def apply_phase6(entries: list[Encounter]) -> None:
    scale_kanto_and_late(entries)
    add_explicit_placements(entries)
    default_rares(entries)


def fmt_species_array(values: list[str], indent: str) -> str:
    return "\n".join(f"{indent}{value}," for value in values)


def fmt_int_array(values: list[int], indent: str) -> str:
    return "\n".join(f"{indent}{value}," for value in values)


def fmt_slots(values: list[Slot], indent: str) -> str:
    return "\n".join(f"{indent}{{ {slot.min_level}, {slot.max_level}, {slot.species} }}," for slot in values)


def render_encounters(entries: list[Encounter]) -> str:
    out = [
        '#include "../include/constants/encounter_tables.h"',
        '#include "../include/constants/species.h"',
        '#include "../include/encounter.h"',
        "",
        "u32 __size = sizeof(EncounterData);",
        "",
        "const EncounterData __data[] =",
        "{",
    ]
    for entry in entries:
        out.extend(
            [
                f"    [{entry.key}] = {{",
                f"        .rateWalk = {entry.rate_walk},",
                f"        .rateSurf = {entry.rate_surf},",
                f"        .rateRockSmash = {entry.rate_rock_smash},",
                f"        .rateOldRod = {entry.rate_old_rod},",
                f"        .rateGoodRod = {entry.rate_good_rod},",
                f"        .rateSuperRod = {entry.rate_super_rod},",
                "        .landSlots = {",
                "            .levels = {",
                fmt_int_array(entry.levels, "                "),
                "            },",
                "            .speciesMorning = {",
                fmt_species_array(entry.morning, "                "),
                "            },",
                "            .speciesDay = {",
                fmt_species_array(entry.day, "                "),
                "            },",
                "            .speciesNight = {",
                fmt_species_array(entry.night, "                "),
                "            },",
                "        },",
                "        .hoennSoundSpecies = {",
                fmt_species_array(entry.hoenn_sound, "            "),
                "        },",
                "        .sinnohSoundSpecies = {",
                fmt_species_array(entry.sinnoh_sound, "            "),
                "        },",
                "        .surfSlots = {",
                fmt_slots(entry.surf, "            "),
                "        },",
                "        .rockSmashSlots = {",
                fmt_slots(entry.rock_smash, "            "),
                "        },",
                "        .oldRodSlots = {",
                fmt_slots(entry.old_rod, "            "),
                "        },",
                "        .goodRodSlots = {",
                fmt_slots(entry.good_rod, "            "),
                "        },",
                "        .superRodSlots = {",
                fmt_slots(entry.super_rod, "            "),
                "        },",
                f"        .landSwarm = {entry.land_swarm},",
                f"        .surfSwarm = {entry.surf_swarm},",
                f"        .nightFish = {entry.night_fish},",
                f"        .fishSwarm = {entry.fish_swarm},",
                "    },",
                "",
            ]
        )
    out.append("};")
    return "\n".join(out) + "\n"


def species_constants() -> tuple[dict[str, int], dict[int, str]]:
    text = (ENGINE / "include" / "constants" / "species.h").read_text(encoding="utf-8", errors="ignore")
    name_to_num: dict[str, int] = {}
    for line in text.splitlines():
        m = re.match(r"#define\s+(SPECIES_[A-Z0-9_]+)\s+(\d+)$", line.strip())
        if m:
            name_to_num[m.group(1)] = int(m.group(2))
    return name_to_num, {v: k for k, v in name_to_num.items()}


def evolution_components(name_to_num: dict[str, int]) -> list[set[str]]:
    text = (ENGINE / "data" / "Evolutions.c").read_text(encoding="utf-8", errors="ignore")
    graph: dict[str, set[str]] = defaultdict(set)
    parent: str | None = None
    for line in text.splitlines():
        m = re.match(r"\s*\[(SPECIES_[A-Z0-9_]+)\]\s*=\s*\{", line)
        if m:
            parent = m.group(1)
            continue
        if parent:
            for target in re.findall(r"(?:MON_WITH_FORM\()?\s*(SPECIES_[A-Z0-9_]+)", line):
                if target != "SPECIES_NONE" and target != parent and target in name_to_num:
                    graph[parent].add(target)
                    graph[target].add(parent)

    seen: set[str] = set()
    comps: list[set[str]] = []
    for species, num in sorted(name_to_num.items(), key=lambda item: item[1]):
        if not 1 <= num <= 493 or species in seen:
            continue
        queue = deque([species])
        seen.add(species)
        comp: set[str] = set()
        while queue:
            cur = queue.popleft()
            comp.add(cur)
            for nxt in graph[cur]:
                if nxt not in seen and nxt in name_to_num:
                    seen.add(nxt)
                    queue.append(nxt)
        comps.append(comp)
    return comps


def placed_species(entries: list[Encounter]) -> set[str]:
    placed: set[str] = set()
    for entry in entries:
        placed.update(entry.morning + entry.day + entry.night)
        placed.update(entry.hoenn_sound + entry.sinnoh_sound)
        for slots in [entry.surf, entry.rock_smash, entry.old_rod, entry.good_rod, entry.super_rod]:
            placed.update(slot.species for slot in slots)
        placed.update([entry.land_swarm, entry.surf_swarm, entry.night_fish, entry.fish_swarm])
    placed.discard("SPECIES_NONE")
    return placed


def placed_species_all_sources(entries: list[Encounter]) -> set[str]:
    placed = placed_species(entries)
    for rel in ["data/SafariEncounters.c", "data/Headbutt.c"]:
        text = (ENGINE / rel).read_text(encoding="utf-8", errors="ignore")
        placed.update(re.findall(r"SPECIES_[A-Z0-9_]+", text))
    placed.discard("SPECIES_NONE")
    return placed


def encounter_species_forbidden(placed: set[str], name_to_num: dict[str, int]) -> list[str]:
    forbidden = []
    for species in sorted(placed, key=lambda value: name_to_num.get(value, 99999)):
        num = name_to_num.get(species)
        if num is None:
            if species not in APPROVED_LATER_PLACEMENTS:
                forbidden.append(species)
        elif num > 493 and species not in APPROVED_LATER_PLACEMENTS:
            forbidden.append(species)
    return forbidden


def validate(entries: list[Encounter]) -> list[str]:
    errors: list[str] = []
    for entry in entries:
        if len(entry.levels) != 12 or len(entry.morning) != 12 or len(entry.day) != 12 or len(entry.night) != 12:
            errors.append(f"{entry.key}: land slot length mismatch")
        for field_name in ["surf", "old_rod", "good_rod", "super_rod"]:
            if len(getattr(entry, field_name)) != 5:
                errors.append(f"{entry.key}: {field_name} slot length mismatch")
        if len(entry.rock_smash) != 2:
            errors.append(f"{entry.key}: rock smash slot length mismatch")
        if is_meaningful(entry) and not entry.rare_notes:
            errors.append(f"{entry.key}: no rare layer placement")

    name_to_num, _ = species_constants()
    forbidden = encounter_species_forbidden(placed_species_all_sources(entries), name_to_num)
    if forbidden:
        errors.append("forbidden later-generation encounter species: " + ", ".join(forbidden))

    for entry in entries:
        for note in entry.rare_notes:
            m = re.search(r" (\d+)% ", note)
            if m and int(m.group(1)) >= 5:
                errors.append(f"{entry.key}: rare placement is not below 5%: {note}")
    return errors


def make_report(entries: list[Encounter]) -> str:
    name_to_num, _ = species_constants()
    comps = evolution_components(name_to_num)
    placed = placed_species_all_sources(entries)
    wild_missing = []
    wild_covered = []
    for comp in comps:
        if comp & LEGENDARY_OR_MYTHICAL:
            continue
        if comp & placed:
            wild_covered.append(comp)
        else:
            wild_missing.append(comp)

    forbidden = encounter_species_forbidden(placed, name_to_num)
    meaningful = [entry for entry in entries if is_meaningful(entry)]
    with_rares = [entry for entry in meaningful if entry.rare_notes]
    rare_lines = []
    for entry in meaningful:
        notes = "; ".join(entry.rare_notes)
        rare_lines.append(f"- `{entry.key}`: {notes}")

    notable = [
        "- Dark Cave Route 31 entrance: Larvitar at 1%, level 7.",
        "- Dragon's Den and Whirl Islands: Dratini/Bagon access in dragon- and water-themed spaces.",
        "- Mt. Mortar, Victory Road, Cerulean Cave, and Mt. Silver: Beldum, Gible, Bagon, and Riolu as late cave/mountain rares.",
        "- Ice Path and Seafoam Islands: Snorunt, Snover, Alolan Sandshrew, Alolan Vulpix, Galarian Mr. Mime, and Delibird.",
        "- Ruins of Alph: Natu and Spiritomb as ancient/mystic rares.",
        "- Kanto routes and caves: levels raised into the high 30s through 60s, with Hoenn/Sinnoh families and late starter access.",
        "- Power Plant-adjacent Route 9/10: Hisuian Voltorb and Rotom.",
    ]

    missing_text = "None." if not wild_missing else ", ".join(
        sorted(
            min(comp, key=lambda s: name_to_num.get(s, 99999)).replace("SPECIES_", "")
            for comp in wild_missing
        )
    )
    forbidden_text = "None." if not forbidden else ", ".join(forbidden)

    return "\n".join(
        [
            "# Phase 6 Obtainability and Rare Encounter Report",
            "",
            "Generated by `tools/perfect_johto/phase6_encounter_tools.py`.",
            "",
            "## Coverage Summary",
            "",
            f"- Meaningful non-Safari encounter areas with rare layer placements: {len(with_rares)} / {len(meaningful)}.",
            f"- Non-legendary Gen 1-4 evolution-family components with wild encounter coverage: {len(wild_covered)} / {len(wild_covered) + len(wild_missing)}.",
            f"- Non-legendary Gen 1-4 family components still missing from wild tables: {missing_text}",
            f"- Unrelated later-generation species found in encounter tables: {forbidden_text}",
            "- Gen 1-4 non-mythical legendaries are covered by the random surprise overlay beginning at 4 badges and expanding through 8 badges.",
            "- Gen 1-4 mythicals are included only in the 16-badge surprise pool, following the personalized tweak file's permissive direction while preserving proper events as future official encounters.",
            "",
            "## Notable Rare Placements",
            "",
            *notable,
            "",
            "## Rare Layer By Area",
            "",
            *rare_lines,
            "",
            "## Validation Notes",
            "",
            "- Land rare slots use HGSS slots 10 and/or 11, each 1%.",
            "- Surf rare slots use slot 4, 1%.",
            "- Fishing rare slots use slot 4, which Phase 6 changes from 5% to 4%.",
            "- Rock Smash has only 80%/20% slots and is not used for below-5% rare placement.",
            "- Safari Zone tables already contain broad Gen 1-4 variety and are excluded from the random legendary overlay.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write regenerated Encounters.c and report")
    args = parser.parse_args()

    entries = parse_encounters(ENCOUNTERS)
    apply_phase6(entries)
    errors = validate(entries)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    report = make_report(entries)
    if args.write:
        ENCOUNTERS.write_text(render_encounters(entries), encoding="utf-8", newline="\n")
        REPORT.write_text(report, encoding="utf-8", newline="\n")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
