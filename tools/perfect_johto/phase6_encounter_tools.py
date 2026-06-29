#!/usr/bin/env python3
"""Phase 6 encounter regeneration and validation for Pokemon Johto Reforged."""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import re
from collections import Counter, defaultdict, deque
from functools import lru_cache


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

FORCED_COMMON_SPECIES = {
    "SPECIES_PIDGEY",
    "SPECIES_RATTATA",
    "SPECIES_SENTRET",
    "SPECIES_HOOTHOOT",
    "SPECIES_POOCHYENA",
    "SPECIES_ZIGZAGOON",
    "SPECIES_WURMPLE",
    "SPECIES_TAILLOW",
    "SPECIES_WINGULL",
    "SPECIES_LOTAD",
    "SPECIES_SEEDOT",
    "SPECIES_SURSKIT",
    "SPECIES_SHROOMISH",
    "SPECIES_SLAKOTH",
    "SPECIES_WHISMUR",
    "SPECIES_MAKUHITA",
    "SPECIES_SKITTY",
    "SPECIES_PLUSLE",
    "SPECIES_MINUN",
    "SPECIES_VOLBEAT",
    "SPECIES_ILLUMISE",
    "SPECIES_BUDEW",
    "SPECIES_GULPIN",
    "SPECIES_NUMEL",
    "SPECIES_TORKOAL",
    "SPECIES_SPOINK",
    "SPECIES_SPINDA",
    "SPECIES_CACNEA",
    "SPECIES_ZANGOOSE",
    "SPECIES_SEVIPER",
    "SPECIES_BARBOACH",
    "SPECIES_CORPHISH",
    "SPECIES_CASTFORM",
    "SPECIES_KECLEON",
    "SPECIES_TROPIUS",
    "SPECIES_CHINGLING",
    "SPECIES_SNORUNT",
    "SPECIES_SPHEAL",
    "SPECIES_LUVDISC",
    "SPECIES_STARLY",
    "SPECIES_BIDOOF",
    "SPECIES_KRICKETOT",
    "SPECIES_BURMY",
    "SPECIES_COMBEE",
    "SPECIES_PACHIRISU",
    "SPECIES_CHERUBI",
    "SPECIES_BUNEARY",
    "SPECIES_GLAMEOW",
    "SPECIES_STUNKY",
    "SPECIES_CHATOT",
    "SPECIES_SKORUPI",
    "SPECIES_CARNIVINE",
    "SPECIES_ELECTRIKE",
    "SPECIES_CROAGUNK",
    "SPECIES_SHINX",
    "SPECIES_SHELLOS",
    "SPECIES_BUIZEL",
    "SPECIES_FINNEON",
    "SPECIES_MANTYKE",
    "SPECIES_HIPPOPOTAS",
    "SPECIES_AZURILL",
    "SPECIES_MIME_JR",
    "SPECIES_IGGLYBUFF",
    "SPECIES_WYNAUT",
    "SPECIES_NINCADA",
    "SPECIES_ROTOM",
}

STRONG_CURRENT_RARES = {
    "SPECIES_ABSOL",
    "SPECIES_AERODACTYL",
    "SPECIES_HERACROSS",
    "SPECIES_KANGASKHAN",
    "SPECIES_LAPRAS",
    "SPECIES_MILTANK",
    "SPECIES_PINSIR",
    "SPECIES_RELICANTH",
    "SPECIES_SCYTHER",
    "SPECIES_SNORLAX",
    "SPECIES_SPIRITOMB",
    "SPECIES_TAUROS",
}

FEATURED_COMMON_LAND_PLACEMENTS = {
    "ENCDATA_R29_ROUTE_29": ["SPECIES_ZIGZAGOON", "SPECIES_STARLY", "SPECIES_BIDOOF"],
    "ENCDATA_R30_ROUTE_30": ["SPECIES_TAILLOW", "SPECIES_WURMPLE", "SPECIES_POOCHYENA"],
    "ENCDATA_R31_ROUTE_31": ["SPECIES_LOTAD", "SPECIES_SEEDOT", "SPECIES_WURMPLE"],
    "ENCDATA_R32_ROUTE_32": ["SPECIES_ELECTRIKE", "SPECIES_WINGULL"],
    "ENCDATA_R33_ROUTE_33": ["SPECIES_CROAGUNK", "SPECIES_SEEDOT"],
    "ENCDATA_D15R0102_SPROUT_TOWER_2F": ["SPECIES_CHINGLING", "SPECIES_NATU", "SPECIES_HOOTHOOT"],
    "ENCDATA_D15R0103_SPROUT_TOWER_3F": ["SPECIES_CHINGLING", "SPECIES_NATU", "SPECIES_MISDREAVUS"],
    "ENCDATA_D24R0205_RUINS_OF_ALPH_INSIDE_MAIN_ROOM": ["SPECIES_BALTOY", "SPECIES_CHINGLING", "SPECIES_LUNATONE", "SPECIES_SOLROCK", "SPECIES_BRONZOR", "SPECIES_NATU"],
    "ENCDATA_D24R0217_RUINS_OF_ALPH_INSIDE_LADDER_ROOM": ["SPECIES_BALTOY", "SPECIES_CHINGLING", "SPECIES_LUNATONE", "SPECIES_SOLROCK", "SPECIES_BRONZOR", "SPECIES_NATU"],
    "ENCDATA_D25R0101_UNION_CAVE_1F": ["SPECIES_WHISMUR", "SPECIES_MAKUHITA"],
    "ENCDATA_D25R0102_UNION_CAVE_B1F": ["SPECIES_NOSEPASS", "SPECIES_SABLEYE"],
    "ENCDATA_D25R0103_UNION_CAVE_B2F": ["SPECIES_LILEEP", "SPECIES_WHISMUR"],
    "ENCDATA_D26R0102_SLOWPOKE_WELL_1F": ["SPECIES_GULPIN", "SPECIES_BARBOACH"],
    "ENCDATA_D26R0103_SLOWPOKE_WELL_B2F": ["SPECIES_GULPIN", "SPECIES_BARBOACH"],
    "ENCDATA_D36R0101_ILEX_FOREST": ["SPECIES_NINCADA", "SPECIES_BUDEW", "SPECIES_SHROOMISH", "SPECIES_SLAKOTH", "SPECIES_LOTAD", "SPECIES_SEEDOT"],
    "ENCDATA_R34_ROUTE_34": ["SPECIES_SKITTY", "SPECIES_PLUSLE", "SPECIES_MINUN", "SPECIES_BUNEARY", "SPECIES_MIME_JR", "SPECIES_IGGLYBUFF", "SPECIES_WYNAUT"],
    "ENCDATA_R35_ROUTE_35": ["SPECIES_PACHIRISU", "SPECIES_BUNEARY", "SPECIES_BUDEW", "SPECIES_KRICKETOT"],
    "ENCDATA_D22R0101_NATIONAL_PARK": ["SPECIES_WURMPLE", "SPECIES_KRICKETOT", "SPECIES_COMBEE", "SPECIES_BURMY", "SPECIES_CHERUBI"],
    "ENCDATA_D22R0102_NATIONAL_PARK_BUG_CATCHING_CONTEST": ["SPECIES_WURMPLE", "SPECIES_KRICKETOT", "SPECIES_COMBEE", "SPECIES_BURMY", "SPECIES_CHERUBI", "SPECIES_VOLBEAT", "SPECIES_ILLUMISE"],
    "ENCDATA_D18R0101_BURNED_TOWER_1F": ["SPECIES_SHUPPET", "SPECIES_NUMEL", "SPECIES_ROTOM"],
    "ENCDATA_D18R0102_BURNED_TOWER_B1F": ["SPECIES_SHUPPET", "SPECIES_NUMEL", "SPECIES_ROTOM"],
    "ENCDATA_D17R0102_BELL_TOWER_2F": ["SPECIES_CHINGLING", "SPECIES_NATU", "SPECIES_HOOTHOOT"],
    "ENCDATA_D17R0103_BELL_TOWER_3F": ["SPECIES_NATU", "SPECIES_SWABLU", "SPECIES_TOGEPI"],
    "ENCDATA_D17R0104_BELL_TOWER_4F": ["SPECIES_NATU", "SPECIES_SWABLU", "SPECIES_TOGEPI"],
    "ENCDATA_D17R0105_BELL_TOWER_5F": ["SPECIES_NATU", "SPECIES_SWABLU", "SPECIES_TOGEPI"],
    "ENCDATA_D17R0106_BELL_TOWER_6F": ["SPECIES_NATU", "SPECIES_SWABLU", "SPECIES_TOGEPI"],
    "ENCDATA_D17R0107_BELL_TOWER_7F": ["SPECIES_NATU", "SPECIES_DRIFLOON", "SPECIES_CHINGLING"],
    "ENCDATA_D17R0108_BELL_TOWER_8F": ["SPECIES_NATU", "SPECIES_DRIFLOON", "SPECIES_CHINGLING"],
    "ENCDATA_D17R0109_BELL_TOWER_9F": ["SPECIES_NATU", "SPECIES_DRIFLOON", "SPECIES_CHINGLING"],
    "ENCDATA_D17R0112_BELL_TOWER_10F": ["SPECIES_NATU", "SPECIES_DRIFLOON", "SPECIES_CHINGLING"],
    "ENCDATA_R38_ROUTE_38": ["SPECIES_SKITTY", "SPECIES_GLAMEOW", "SPECIES_BUNEARY"],
    "ENCDATA_R39_ROUTE_39": ["SPECIES_SKITTY", "SPECIES_GLAMEOW", "SPECIES_BUNEARY"],
    "ENCDATA_D40R0101_WHIRL_ISLANDS_1F": ["SPECIES_SPHEAL", "SPECIES_CLAMPERL"],
    "ENCDATA_D40R0102_WHIRL_ISLANDS_B1F": ["SPECIES_SPHEAL", "SPECIES_CLAMPERL"],
    "ENCDATA_D40R0104_WHIRL_ISLANDS_B2F": ["SPECIES_SPHEAL", "SPECIES_CLAMPERL"],
    "ENCDATA_D40R0106_WHIRL_ISLANDS_B3F_LEDGE_OVERLOOKING_LUGIA_ROOM": ["SPECIES_SPHEAL", "SPECIES_CLAMPERL"],
    "ENCDATA_R42_ROUTE_42": ["SPECIES_NUMEL", "SPECIES_TORKOAL", "SPECIES_SPOINK"],
    "ENCDATA_D38R0101_MT_MORTAR_WATERFALL_ROOM": ["SPECIES_MAKUHITA", "SPECIES_WHISMUR", "SPECIES_NOSEPASS"],
    "ENCDATA_D38R0102_MT_MORTAR_CENTRAL_ROOM": ["SPECIES_MAKUHITA", "SPECIES_WHISMUR", "SPECIES_NOSEPASS"],
    "ENCDATA_D38R0103_MT_MORTAR_ROOM_ABOVE_WATERFALL": ["SPECIES_MAKUHITA", "SPECIES_WHISMUR", "SPECIES_NOSEPASS"],
    "ENCDATA_D38R0104_MT_MORTAR_B1F": ["SPECIES_MAKUHITA", "SPECIES_WHISMUR", "SPECIES_NOSEPASS"],
    "ENCDATA_R43_ROUTE_43": ["SPECIES_CASTFORM", "SPECIES_BARBOACH", "SPECIES_CORPHISH", "SPECIES_SPOINK", "SPECIES_SPINDA"],
    "ENCDATA_R44_ROUTE_44": ["SPECIES_KECLEON", "SPECIES_CHERUBI", "SPECIES_PACHIRISU"],
    "ENCDATA_D39R0101_ICE_PATH_1F": ["SPECIES_SNORUNT", "SPECIES_SPHEAL", "SPECIES_CHINGLING"],
    "ENCDATA_D39R0102_ICE_PATH_B1F": ["SPECIES_SNORUNT", "SPECIES_SPHEAL", "SPECIES_CHINGLING"],
    "ENCDATA_D39R0103_ICE_PATH_B2F": ["SPECIES_SNORUNT", "SPECIES_SPHEAL", "SPECIES_CHINGLING"],
    "ENCDATA_D39R0104_ICE_PATH_B3F": ["SPECIES_SNORUNT", "SPECIES_SPHEAL", "SPECIES_CHINGLING"],
    "ENCDATA_R45_ROUTE_45": ["SPECIES_CACNEA", "SPECIES_ZANGOOSE", "SPECIES_SEVIPER", "SPECIES_HIPPOPOTAS", "SPECIES_SKORUPI"],
    "ENCDATA_R46_ROUTE_46": ["SPECIES_CACNEA", "SPECIES_ZANGOOSE", "SPECIES_SEVIPER"],
    "ENCDATA_D42R0101_DARK_CAVE_ROUTE_45_ENTRANCE": ["SPECIES_CACNEA", "SPECIES_ZANGOOSE", "SPECIES_SEVIPER", "SPECIES_SKORUPI"],
    "ENCDATA_R47_ROUTE_47": ["SPECIES_PACHIRISU", "SPECIES_CHERUBI", "SPECIES_GLAMEOW", "SPECIES_STUNKY"],
    "ENCDATA_D50R0101_CLIFF_CAVE": ["SPECIES_ANORITH", "SPECIES_SHELLOS", "SPECIES_BUIZEL", "SPECIES_SKORUPI"],
    "ENCDATA_R48_ROUTE_48": ["SPECIES_CARNIVINE", "SPECIES_PACHIRISU", "SPECIES_CHERUBI", "SPECIES_TROPIUS", "SPECIES_STUNKY"],
}

FEATURED_COMMON_SURF_PLACEMENTS = {
    "ENCDATA_T20_NEW_BARK_TOWN": ["SPECIES_AZURILL"],
    "ENCDATA_T21_CHERRYGROVE_CITY": ["SPECIES_AZURILL", "SPECIES_WINGULL"],
    "ENCDATA_T27_ECRUTEAK_CITY": ["SPECIES_LOTAD", "SPECIES_BARBOACH", "SPECIES_AZURILL"],
    "ENCDATA_W40_ROUTE_40": ["SPECIES_WINGULL", "SPECIES_LUVDISC", "SPECIES_MANTYKE"],
    "ENCDATA_W41_ROUTE_41": ["SPECIES_WINGULL", "SPECIES_LUVDISC", "SPECIES_MANTYKE"],
    "ENCDATA_T24_CIANWOOD_CITY": ["SPECIES_WINGULL", "SPECIES_LUVDISC", "SPECIES_MANTYKE"],
    "ENCDATA_T29_LAKE_OF_RAGE": ["SPECIES_BARBOACH", "SPECIES_CORPHISH", "SPECIES_AZURILL"],
    "ENCDATA_T30_BLACKTHORN_CITY": ["SPECIES_BARBOACH", "SPECIES_CORPHISH"],
    "ENCDATA_D44R0102_DRAGONS_DEN": ["SPECIES_BARBOACH", "SPECIES_CORPHISH"],
    "ENCDATA_D48R0101_CLIFF_EDGE_GATE": ["SPECIES_SHELLOS", "SPECIES_BUIZEL"],
}

MIN_VARIETY_FILLERS = {
    "forest": ["SPECIES_WURMPLE", "SPECIES_KRICKETOT", "SPECIES_COMBEE", "SPECIES_BURMY", "SPECIES_CHERUBI", "SPECIES_BUDEW"],
    "cave": ["SPECIES_WHISMUR", "SPECIES_MAKUHITA", "SPECIES_NOSEPASS", "SPECIES_SABLEYE", "SPECIES_CHINGLING", "SPECIES_BRONZOR"],
    "water": ["SPECIES_AZURILL", "SPECIES_WINGULL", "SPECIES_BARBOACH", "SPECIES_CORPHISH", "SPECIES_LUVDISC", "SPECIES_FINNEON"],
    "cold": ["SPECIES_SNORUNT", "SPECIES_SPHEAL", "SPECIES_CHINGLING", "SPECIES_SWINUB", "SPECIES_DELIBIRD", "SPECIES_SNEASEL"],
    "tower": ["SPECIES_CHINGLING", "SPECIES_NATU", "SPECIES_HOOTHOOT", "SPECIES_SWABLU", "SPECIES_DRIFLOON", "SPECIES_TOGEPI"],
    "route": ["SPECIES_ZIGZAGOON", "SPECIES_TAILLOW", "SPECIES_STARLY", "SPECIES_BIDOOF", "SPECIES_POOCHYENA", "SPECIES_BUNEARY"],
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
    common_notes: list[str] = dataclasses.field(default_factory=list)


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


def copy_land_slot(entry: Encounter, source: int, target: int) -> None:
    entry.levels[target] = entry.levels[source]
    entry.morning[target] = entry.morning[source]
    entry.day[target] = entry.day[source]
    entry.night[target] = entry.night[source]


def land_slots_match(entry: Encounter, slots: tuple[int, ...], level: int, morning: str, day: str, night: str) -> bool:
    return all(
        entry.levels[slot] == level
        and entry.morning[slot] == morning
        and entry.day[slot] == day
        and entry.night[slot] == night
        for slot in slots
    )


def preserve_land_common_slots(entry: Encounter, rare_slots: tuple[int, ...], level: int, morning: str, day: str, night: str) -> None:
    if land_slots_match(entry, rare_slots, level, morning, day, night):
        return
    copy_land_slot(entry, 8, 10)
    copy_land_slot(entry, 9, 11)


def merged_daytime_slots_match(entry: Encounter, slots: tuple[int, ...], _level: int, morning: str, day: str, night: str) -> bool:
    daytime = set(entry.morning + entry.day)
    return (
        morning in daytime
        and day in daytime
        and all(entry.night[slot] == night for slot in slots)
    )


def normalized_land_rare_slots(slots: tuple[int, ...]) -> tuple[int, ...]:
    if slots in {(10,), (10, 11)}:
        return (8,)
    if slots == (11,):
        return (9,)
    return slots


def species_in_common_land_slot(entry: Encounter, species: str) -> bool:
    return any(entry.day[slot] == species or entry.morning[slot] == species or entry.night[slot] == species for slot in range(8))


def choose_common_land_slot(entry: Encounter, preferred_slots: tuple[int, ...] = (2, 3, 4, 5, 0, 1, 6, 7)) -> int:
    counts = Counter(entry.day[:8] + entry.morning[:8] + entry.night[:8])
    for slot in preferred_slots:
        if entry.day[slot] == "SPECIES_NONE":
            return slot
    return max(preferred_slots, key=lambda slot: (counts[entry.day[slot]], LAND_RATES[slot], -slot))


def append_common_note(entry: Encounter, note: str) -> None:
    if note not in entry.common_notes:
        entry.common_notes.append(note)


def set_land_common(entry: Encounter, species: str, level: int | None = None, note: str | None = None, slots: tuple[int, ...] = ()) -> None:
    if not has_real_land(entry):
        return
    if species_in_common_land_slot(entry, species):
        existing_slots = [
            slot
            for slot in range(8)
            if entry.morning[slot] == species or entry.day[slot] == species or entry.night[slot] == species
        ]
        rate = sum(LAND_RATES[slot] for slot in existing_slots)
        level_text = f"lv{round(sum(entry.levels[slot] for slot in existing_slots) / len(existing_slots))}" if existing_slots else "lv?"
        append_common_note(entry, f"land common {species} {rate}% {level_text}" + (f" - {note}" if note else ""))
        return
    if level is None:
        level = average_land_level(entry)
    target_slots = slots or (choose_common_land_slot(entry),)
    for slot in target_slots:
        if slot >= 8:
            slot = choose_common_land_slot(entry)
        entry.levels[slot] = level
        entry.morning[slot] = species
        entry.day[slot] = species
        entry.night[slot] = species
    rate = sum(LAND_RATES[slot] for slot in target_slots if slot < len(LAND_RATES))
    append_common_note(entry, f"land common {species} {rate}% lv{level}" + (f" - {note}" if note else ""))


def species_in_common_slots(slots: list[Slot], species: str, common_limit: int) -> bool:
    return any(slot.species == species for slot in slots[:common_limit])


def choose_common_slot(slots: list[Slot], preferred_slots: tuple[int, ...]) -> int | None:
    real_slots = [slot for slot, value in enumerate(slots) if value.species != "SPECIES_NONE"]
    if not real_slots:
        return None
    counts = Counter(
        slots[slot].species
        for slot in preferred_slots
        if slot < len(slots) and slots[slot].species != "SPECIES_NONE"
    )
    for slot in preferred_slots:
        if slot < len(slots) and slots[slot].species == "SPECIES_NONE":
            return slot
    candidates = [
        slot
        for slot in preferred_slots
        if slot < len(slots) and slots[slot].species != "SPECIES_NONE" and counts[slots[slot].species] > 1
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda slot: (counts[slots[slot].species], -slot))


def set_slot_common(
    slots: list[Slot],
    species: str,
    level: int | None,
    preferred_slots: tuple[int, ...],
    rates: list[int],
    note: str | None,
) -> str | None:
    if not slots or all(slot.species == "SPECIES_NONE" for slot in slots):
        return None
    common_limit = max(preferred_slots) + 1 if preferred_slots else len(slots)
    if species_in_common_slots(slots, species, common_limit):
        existing_slots = [idx for idx, slot in enumerate(slots[:common_limit]) if slot.species == species]
        rate = sum(rates[idx] for idx in existing_slots if idx < len(rates))
        min_level = min(slots[idx].min_level for idx in existing_slots)
        max_level = max(slots[idx].max_level for idx in existing_slots)
        return f"{species} {rate}% lv{min_level}-{max_level}" + (f" - {note}" if note else "")
    target = choose_common_slot(slots, preferred_slots)
    if target is None:
        return None
    if level is None:
        real = [slot for slot in slots if slot.species != "SPECIES_NONE"]
        level = round(sum((slot.min_level + slot.max_level) / 2 for slot in real) / len(real))
    slots[target] = Slot(max(1, level - 1), level + 1, species)
    rate = rates[target] if target < len(rates) else 0
    return f"{species} {rate}% lv{max(1, level - 1)}-{level + 1}" + (f" - {note}" if note else "")


def set_surf_common(entry: Encounter, species: str, level: int | None = None, note: str | None = None) -> None:
    placed = set_slot_common(entry.surf, species, level, (1, 2, 0), SURF_RATES, note)
    if placed:
        append_common_note(entry, "surf common " + placed)


def set_fish_common(entry: Encounter, species: str, level: int | None = None, rod: str = "super", note: str | None = None) -> None:
    slots = {"old": entry.old_rod, "good": entry.good_rod, "super": entry.super_rod}[rod]
    placed = set_slot_common(slots, species, level, (1, 2, 3, 0), FISH_RATES_PHASE6, note)
    if placed:
        append_common_note(entry, f"{rod} rod common " + placed)


def set_any_fish_common(entry: Encounter, species: str, level: int | None = None, note: str | None = None) -> None:
    for rod in ("super", "good", "old"):
        before = water_pool_species(entry)
        set_fish_common(entry, species, level, rod, note)
        if len(water_pool_species(entry)) > len(before):
            return


def set_special_common(entry: Encounter, species: str, note: str | None = None) -> bool:
    if species in encounter_species(entry):
        return False
    if has_real_surf(entry) and entry.surf_swarm == "SPECIES_NONE":
        entry.surf_swarm = species
        append_common_note(entry, "surf swarm variety " + species + (f" - {note}" if note else ""))
        return True
    if has_real_fish(entry):
        if entry.fish_swarm == "SPECIES_NONE":
            entry.fish_swarm = species
            append_common_note(entry, "fish swarm variety " + species + (f" - {note}" if note else ""))
            return True
        if entry.night_fish == "SPECIES_NONE":
            entry.night_fish = species
            append_common_note(entry, "night fish variety " + species + (f" - {note}" if note else ""))
            return True
    for label, values in [("Hoenn sound", entry.hoenn_sound), ("Sinnoh sound", entry.sinnoh_sound)]:
        for idx, current in enumerate(values):
            if current == "SPECIES_NONE":
                values[idx] = species
                append_common_note(entry, f"{label} variety {species}" + (f" - {note}" if note else ""))
                return True
    if has_real_land(entry) and entry.land_swarm == "SPECIES_NONE":
        entry.land_swarm = species
        append_common_note(entry, "land swarm variety " + species + (f" - {note}" if note else ""))
        return True
    return False


def commonized_note(note: str | None, fallback: str) -> str:
    if not note:
        return fallback
    return re.sub(r"\brare\b", "common", note)


def set_land_rare(entry: Encounter, species: str, level: int | None = None, slots=(8,), note: str | None = None) -> None:
    if not has_real_land(entry):
        return
    if not is_rare_species(species):
        set_land_common(entry, species, level, commonized_note(note, "featured common placement"))
        return
    if level is None:
        level = average_land_level(entry)
    slots = normalized_land_rare_slots(slots)
    preserve_land_common_slots(entry, slots, level, species, species, species)
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
    slots=(8,),
    note: str | None = None,
) -> None:
    if not has_real_land(entry):
        return
    if level is None:
        level = average_land_level(entry)
    slots = normalized_land_rare_slots(slots)
    split = [morning, day, night]
    rare_split = [species for species in split if is_rare_species(species)]
    for species in split:
        if not is_rare_species(species):
            set_land_common(entry, species, level, commonized_note(note, "featured common timed placement"))
    if not rare_split:
        return
    fallback = rare_split[0]
    morning = morning if is_rare_species(morning) else fallback
    day = day if is_rare_species(day) else fallback
    night = night if is_rare_species(night) else fallback
    if not land_slots_match(entry, slots, level, morning, day, night) and not merged_daytime_slots_match(entry, slots, level, morning, day, night):
        copy_land_slot(entry, 8, 10)
        copy_land_slot(entry, 9, 11)
    for slot in slots:
        entry.levels[slot] = level
        entry.morning[slot] = morning
        entry.day[slot] = day
        entry.night[slot] = night
    rate = sum(LAND_RATES[slot] for slot in slots)
    species_split = f"{morning}/{day}/{night}"
    entry.rare_notes.append(f"land timed rare {species_split} {rate}% lv{level}" + (f" - {note}" if note else ""))


def set_surf_rare(entry: Encounter, species: str, level: int | None = None, note: str | None = None) -> None:
    if not has_real_surf(entry):
        return
    if not is_rare_species(species):
        set_surf_common(entry, species, level, commonized_note(note, "featured common surf placement"))
        return
    if level is None:
        real = [s for s in entry.surf if s.species != "SPECIES_NONE"]
        level = round(sum((s.min_level + s.max_level) / 2 for s in real) / len(real))
    rare_slot = Slot(max(1, level - 1), level + 1, species)
    if entry.surf[3].species == species:
        pass
    elif entry.surf[4].species == species:
        entry.surf[4] = entry.surf[3]
    else:
        entry.surf[4] = entry.surf[3]
    entry.surf[3] = rare_slot
    entry.rare_notes.append(f"surf {species} 4% lv{max(1, level - 1)}-{level + 1}" + (f" - {note}" if note else ""))


def set_fish_rare(entry: Encounter, species: str, level: int | None = None, rod: str = "super", note: str | None = None) -> None:
    slots = {"old": entry.old_rod, "good": entry.good_rod, "super": entry.super_rod}[rod]
    if not slots or all(slot.species == "SPECIES_NONE" for slot in slots):
        return
    if not is_rare_species(species):
        set_fish_common(entry, species, level, rod, commonized_note(note, "featured common fishing placement"))
        return
    if level is None:
        real = [s for s in slots if s.species != "SPECIES_NONE"]
        level = round(sum((s.min_level + s.max_level) / 2 for s in real) / len(real))
    slots[4] = Slot(max(1, level - 1), level + 1, species)
    entry.rare_notes.append(f"{rod} rod {species} 4% lv{max(1, level - 1)}-{level + 1}" + (f" - {note}" if note else ""))


def scale_land(entry: Encounter, levels: list[int]) -> None:
    if has_real_land(entry):
        entry.levels = levels[:12]


def land_level_band(target_min: int, target_max: int) -> list[int]:
    if target_max < target_min:
        raise ValueError("target_max must be at least target_min")
    anchors = (0.0, 0.0, 0.15, 0.15, 0.30, 0.30, 0.50, 0.50, 0.75, 0.75, 0.90, 1.0)
    levels: list[int] = []
    last = target_min
    for anchor in anchors:
        level = int(target_min + (target_max - target_min) * anchor + 0.5)
        level = max(target_min, min(target_max, level))
        level = max(last, level)
        levels.append(level)
        last = level
    return levels


def scale_land_band(entry: Encounter, target_min: int, target_max: int) -> None:
    scale_land(entry, land_level_band(target_min, target_max))


def scale_slots(slots: list[Slot], target_min: int, target_max: int, *, only_raise: bool = False) -> None:
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
            min_level = max(1, lo)
            max_level = max(min_level, hi)
            if only_raise:
                min_level = max(slot.min_level, min_level)
                max_level = max(slot.max_level, max_level, min_level)
            slot.min_level = min_level
            slot.max_level = max_level


def scale_water_band(entry: Encounter, target_min: int, target_max: int) -> None:
    for slots in [entry.surf, entry.good_rod, entry.super_rod]:
        scale_slots(slots, target_min, target_max, only_raise=True)


def scale_progression_levels(entries: list[Encounter]) -> None:
    kanto_standard_route = re.compile(r"ENCDATA_(R0[1-9]|R1[0-8]|R22|R24|R25|R02R0101|D46R0101)")
    pre_league_keys = {
        "ENCDATA_R26_ROUTE_26",
        "ENCDATA_R27_ROUTE_27",
        "ENCDATA_D43R0101_VICTORY_ROAD_1F",
        "ENCDATA_D43R0102_VICTORY_ROAD_2F",
        "ENCDATA_D43R0103_VICTORY_ROAD_3F",
        "ENCDATA_D45R0101_TOHJO_FALLS",
    }
    west_johto_land = {"ENCDATA_R38_ROUTE_38", "ENCDATA_R39_ROUTE_39"}
    west_johto_water = {"ENCDATA_W40_ROUTE_40", "ENCDATA_W41_ROUTE_41", "ENCDATA_T24_CIANWOOD_CITY"}
    lake_johto = {"ENCDATA_R43_ROUTE_43", "ENCDATA_T29_LAKE_OF_RAGE"}
    late_johto_land = {
        "ENCDATA_R45_ROUTE_45",
        "ENCDATA_D42R0101_DARK_CAVE_ROUTE_45_ENTRANCE",
    }
    frontier_johto_land = {"ENCDATA_R47_ROUTE_47", "ENCDATA_D50R0101_CLIFF_CAVE", "ENCDATA_R48_ROUTE_48"}
    kanto_city_water = {
        "ENCDATA_T01_PALLET_TOWN",
        "ENCDATA_T02_VIRIDIAN_CITY",
        "ENCDATA_T04_CERULEAN_CITY",
        "ENCDATA_T06_VERMILION_CITY",
        "ENCDATA_T07_CELADON_CITY",
        "ENCDATA_T08_FUCHSIA_CITY",
        "ENCDATA_R12_ROUTE_12",
    }
    kanto_sea_water = {
        "ENCDATA_T09_CINNABAR_ISLAND",
        "ENCDATA_W19_ROUTE_19",
        "ENCDATA_W20_ROUTE_20",
        "ENCDATA_W21_ROUTE_21",
    }
    for entry in entries:
        key = entry.key
        if key in pre_league_keys:
            scale_land_band(entry, 42, 50)
        elif key in west_johto_land:
            scale_land_band(entry, 24, 30)
        elif "WHIRL_ISLANDS" in key:
            scale_land_band(entry, 24, 32)
        elif key == "ENCDATA_R42_ROUTE_42":
            scale_land_band(entry, 24, 30)
        elif "MT_MORTAR" in key:
            scale_land_band(entry, 28, 36)
        elif key in lake_johto:
            scale_land_band(entry, 28, 34)
        elif key == "ENCDATA_R44_ROUTE_44":
            scale_land_band(entry, 30, 36)
        elif "ICE_PATH" in key:
            scale_land_band(entry, 32, 38)
        elif key in late_johto_land:
            scale_land_band(entry, 34, 40)
        elif key in frontier_johto_land:
            scale_land_band(entry, 36, 42)
        elif any(tag in key for tag in ["CERULEAN_CAVE"]):
            scale_land_band(entry, 60, 68)
        elif any(tag in key for tag in ["MT_SILVER", "R28_ROUTE_28"]):
            scale_land_band(entry, 58, 66)
        elif any(tag in key for tag in ["SEAFOAM"]):
            scale_land_band(entry, 52, 60)
        elif any(tag in key for tag in ["ROCK_TUNNEL", "MT_MOON"]):
            scale_land_band(entry, 50, 58)
        elif any(tag in key for tag in ["DIGLETTS_CAVE"]):
            scale_land_band(entry, 48, 56)
        elif kanto_standard_route.search(key):
            scale_land_band(entry, 46, 54)

        if any(tag in key for tag in ["CERULEAN_CAVE", "MT_SILVER"]):
            scale_water_band(entry, 56, 66)
        elif key == "ENCDATA_R28_ROUTE_28":
            scale_water_band(entry, 54, 64)
        elif "SEAFOAM" in key:
            scale_water_band(entry, 52, 62)
        elif any(tag in key for tag in ["MT_MOON", "ROCK_TUNNEL", "DIGLETTS_CAVE"]):
            scale_water_band(entry, 50, 58)
        elif kanto_standard_route.search(key) or key in kanto_city_water:
            scale_water_band(entry, 46, 56)
        elif key in kanto_sea_water:
            scale_water_band(entry, 50, 60)
        elif key in pre_league_keys:
            scale_water_band(entry, 40, 48)
        elif key in west_johto_water or "WHIRL_ISLANDS" in key:
            scale_water_band(entry, 24, 32)
        elif key == "ENCDATA_R42_ROUTE_42":
            scale_water_band(entry, 26, 34)
        elif "MT_MORTAR" in key or key in lake_johto:
            scale_water_band(entry, 28, 36)
        elif key == "ENCDATA_R44_ROUTE_44":
            scale_water_band(entry, 30, 38)
        elif key in {"ENCDATA_T30_BLACKTHORN_CITY", "ENCDATA_D44R0102_DRAGONS_DEN"}:
            scale_water_band(entry, 38, 46)
        elif key in late_johto_land:
            scale_water_band(entry, 34, 42)
        elif key in {"ENCDATA_R47_ROUTE_47", "ENCDATA_D48R0101_CLIFF_EDGE_GATE"}:
            scale_water_band(entry, 36, 44)


def entry_by_key(entries: list[Encounter]) -> dict[str, Encounter]:
    return {entry.key: entry for entry in entries}


def add_explicit_placements(entries: list[Encounter]) -> None:
    e = entry_by_key(entries)
    if "ENCDATA_T07_CELADON_CITY" in e:
        celadon = e["ENCDATA_T07_CELADON_CITY"]
        celadon.rate_old_rod = 25
        celadon.rate_good_rod = 50
        celadon.rate_super_rod = 75
        celadon.old_rod = [
            Slot(10, 10, "SPECIES_MAGIKARP"),
            Slot(10, 10, "SPECIES_MAGIKARP"),
            Slot(10, 10, "SPECIES_MAGIKARP"),
            Slot(10, 10, "SPECIES_POLIWAG"),
            Slot(10, 10, "SPECIES_POLIWAG"),
        ]
        celadon.good_rod = [
            Slot(46, 48, "SPECIES_MAGIKARP"),
            Slot(46, 49, "SPECIES_POLIWAG"),
            Slot(48, 54, "SPECIES_POLIWAG"),
            Slot(49, 55, "SPECIES_GRIMER"),
            Slot(54, 56, "SPECIES_POLIWAG"),
        ]
        celadon.super_rod = [
            Slot(46, 48, "SPECIES_POLIWAG"),
            Slot(46, 49, "SPECIES_GRIMER"),
            Slot(48, 54, "SPECIES_MAGIKARP"),
            Slot(49, 55, "SPECIES_MUK"),
            Slot(54, 56, "SPECIES_MAGIKARP"),
        ]
        append_common_note(celadon, "Celadon pond fishing enabled for six-species surf/fishing variety")

    land = [
        ("ENCDATA_R29_ROUTE_29", "SPECIES_SHINX", 4, (8,), "early electric variety without starter clutter"),
        ("ENCDATA_R30_ROUTE_30", "SPECIES_RALTS", 4, (8,), "quiet wooded-route empath line"),
        ("ENCDATA_R31_ROUTE_31", "SPECIES_TREECKO", 5, (8,), "forest-edge Hoenn starter rare"),
        ("ENCDATA_D15R0102_SPROUT_TOWER_2F", "SPECIES_SHUPPET", 6, (8,), "restless ghost in the quiet tower"),
        ("ENCDATA_D15R0103_SPROUT_TOWER_3F", "SPECIES_DUSKULL", 7, (8,), "watchful tower ghost rare"),
        ("ENCDATA_R32_ROUTE_32", "SPECIES_ELECTRIKE", 8, (8,), "Mareep-route electric Hoenn rare"),
        ("ENCDATA_R32_ROUTE_32", "SPECIES_WOOPER_PALDEAN", 8, (8,), "muddy route-bank regional Wooper rare"),
        ("ENCDATA_D24R0101_RUINS_OF_ALPH_OUTSIDE", "SPECIES_BALTOY", 12, (8,), "ancient clay guardian rare"),
        ("ENCDATA_D24R0205_RUINS_OF_ALPH_INSIDE_MAIN_ROOM", "SPECIES_SPIRITOMB", 16, (8,), "ancient sealed-spirit rare"),
        ("ENCDATA_D24R0217_RUINS_OF_ALPH_INSIDE_LADDER_ROOM", "SPECIES_MAWILE", 5, (8,), "sealed ladder-room steel-line rare"),
        ("ENCDATA_D25R0101_UNION_CAVE_1F", "SPECIES_ARON", 9, (8,), "mineral cave line"),
        ("ENCDATA_D25R0102_UNION_CAVE_B1F", "SPECIES_GIBLE", 10, (8,), "early rocky cave pseudo rare"),
        ("ENCDATA_R33_ROUTE_33", "SPECIES_CROAGUNK", 11, (8,), "rainy lowland poison/fighting rare"),
        ("ENCDATA_R33_ROUTE_33", "SPECIES_ZIGZAGOON_GALARIAN", 11, (8,), "rainy lowland regional dark-line rare"),
        ("ENCDATA_D26R0102_SLOWPOKE_WELL_1F", "SPECIES_SLOWPOKE_GALARIAN", 12, (8,), "approved Slowpoke-family regional form"),
        ("ENCDATA_D26R0103_SLOWPOKE_WELL_B2F", "SPECIES_MUDKIP", 15, (8,), "wet cave Hoenn starter rare"),
        ("ENCDATA_D22R0101_NATIONAL_PARK", "SPECIES_SCYTHER", 16, (8,), "classic park rare"),
        ("ENCDATA_D22R0102_NATIONAL_PARK_BUG_CATCHING_CONTEST", "SPECIES_PINSIR", 16, (8,), "contest counterpart rare"),
        ("ENCDATA_D18R0102_BURNED_TOWER_B1F", "SPECIES_TORCHIC", 19, (8,), "haunted burned-basement fire starter access"),
        ("ENCDATA_D17R0102_BELL_TOWER_2F", "SPECIES_TOGEPI", 22, (8,), "sacred tower line"),
        ("ENCDATA_D17R0103_BELL_TOWER_3F", "SPECIES_CHIMECHO", 23, (8,), "bell-themed rare"),
        ("ENCDATA_D17R0104_BELL_TOWER_4F", "SPECIES_DRIFLOON", 24, (8,), "windborne tower rare"),
        ("ENCDATA_D17R0105_BELL_TOWER_5F", "SPECIES_ABSOL", 25, (8,), "omens near a sacred tower"),
        ("ENCDATA_D17R0106_BELL_TOWER_6F", "SPECIES_PONYTA_GALARIAN", 26, (8,), "approved mystical regional form"),
        ("ENCDATA_D17R0107_BELL_TOWER_7F", "SPECIES_SWABLU", 27, (8,), "sky-tower cloud dragon line"),
        ("ENCDATA_D17R0108_BELL_TOWER_8F", "SPECIES_RALTS", 28, (8,), "sacred tower psychic-line rare"),
        ("ENCDATA_D17R0109_BELL_TOWER_9F", "SPECIES_RIOLU", 29, (8,), "aura-sensitive tower rare"),
        ("ENCDATA_R35_ROUTE_35", "SPECIES_KANGASKHAN", 18, (9,), "early family-route guardian rare outside Safari"),
        ("ENCDATA_R38_ROUTE_38", "SPECIES_SNEASEL", 24, (9,), "early west-Johto nocturnal dark/ice rare"),
        ("ENCDATA_R39_ROUTE_39", "SPECIES_TAUROS", 25, (9,), "farm-route herd bull rare before Kanto"),
        ("ENCDATA_D40R0101_WHIRL_ISLANDS_1F", "SPECIES_BAGON", 28, (8,), "rugged sea-cave dragon rare"),
        ("ENCDATA_D40R0102_WHIRL_ISLANDS_B1F", "SPECIES_QWILFISH_HISUIAN", 30, (8,), "approved Qwilfish regional form"),
        ("ENCDATA_D40R0104_WHIRL_ISLANDS_B2F", "SPECIES_CORSOLA_GALARIAN", 31, (8,), "deep ghostly coral form"),
        ("ENCDATA_D40R0106_WHIRL_ISLANDS_B3F_LEDGE_OVERLOOKING_LUGIA_ROOM", "SPECIES_DRATINI", 32, (8,), "dragon-water pilgrimage rare"),
        ("ENCDATA_D38R0101_MT_MORTAR_WATERFALL_ROOM", "SPECIES_TYROGUE", 30, (8,), "Mt. Mortar fighting-line access"),
        ("ENCDATA_D38R0102_MT_MORTAR_CENTRAL_ROOM", "SPECIES_BELDUM", 32, (8,), "mineral/steel pseudo rare"),
        ("ENCDATA_D38R0103_MT_MORTAR_ROOM_ABOVE_WATERFALL", "SPECIES_CRANIDOS", 34, (8,), "rugged fossil-line rare"),
        ("ENCDATA_D38R0104_MT_MORTAR_B1F", "SPECIES_SHIELDON", 34, (8,), "deep fossil-line counterpart"),
        ("ENCDATA_R43_ROUTE_43", "SPECIES_CASTFORM", 30, (8,), "Lake of Rage weather-route rare"),
        ("ENCDATA_R44_ROUTE_44", "SPECIES_KECLEON", 34, (8,), "concealed roadside rare"),
        ("ENCDATA_D39R0102_ICE_PATH_B1F", "SPECIES_SANDSHREW_ALOLAN", 35, (8,), "approved cold regional form"),
        ("ENCDATA_D39R0103_ICE_PATH_B2F", "SPECIES_VULPIX_ALOLAN", 36, (8,), "stronger cold regional rare"),
        ("ENCDATA_D39R0101_ICE_PATH_1F", "SPECIES_SNEASEL", 35, (8,), "early Ice Path dark/ice rare while keeping late Sneasel locations"),
        ("ENCDATA_D39R0104_ICE_PATH_B3F", "SPECIES_SNOVER", 37, (8,), "deep ice forest line"),
        ("ENCDATA_D44R0102_DRAGONS_DEN", "SPECIES_DRATINI", 40, (8,), "Johto dragon identity"),
        ("ENCDATA_R45_ROUTE_45", "SPECIES_SKARMORY", 38, (8,), "cliffside steel bird"),
        ("ENCDATA_R46_ROUTE_46", "SPECIES_TRAPINCH", 10, (8,), "dry cliff rare without early power spike"),
        ("ENCDATA_D42R0102_DARK_CAVE_ROUTE_31_ENTRANCE", "SPECIES_LARVITAR", 7, (8,), "Sacred Gold-style early pseudo surprise"),
        ("ENCDATA_D42R0101_DARK_CAVE_ROUTE_45_ENTRANCE", "SPECIES_GIBLE", 38, (8,), "deep rocky tunnel pseudo rare"),
        ("ENCDATA_R47_ROUTE_47", "SPECIES_TURTWIG", 40, (8,), "late Johto starter access"),
        ("ENCDATA_R48_ROUTE_48", "SPECIES_TREECKO", 40, (8,), "Safari-frontier Hoenn starter access"),
        ("ENCDATA_D50R0101_CLIFF_CAVE", "SPECIES_ANORITH", 40, (8,), "cliff fossil-line rare"),
        ("ENCDATA_D02R0103_MT_MOON_OUTSIDE_AREA", "SPECIES_CLEFFA", 52, (8,), "Mt. Moon moonlight rare"),
        ("ENCDATA_D02R0104_MT_MOON_OUTSIDE_CLEFAIRY_ACTIVE", "SPECIES_CLEFAIRY", 54, (8,), "active moonlight table"),
        ("ENCDATA_D02R0102_MT_MOON_2F", "SPECIES_AERODACTYL", 56, (8,), "ancient mountain fossil rare"),
        ("ENCDATA_D11R0101_SEAFOAM_ISLANDS_1F", "SPECIES_PIPLUP", 53, (8,), "postgame cold-water starter access"),
        ("ENCDATA_D11R0102_SEAFOAM_ISLANDS_B1F", "SPECIES_MR_MIME_GALARIAN", 55, (8,), "approved cold regional form"),
        ("ENCDATA_D11R0103_SEAFOAM_ISLANDS_B2F", "SPECIES_SPHEAL", 56, (8,), "deep cold Hoenn ice/water line"),
        ("ENCDATA_D11R0104_SEAFOAM_ISLANDS_B3F", "SPECIES_SNORUNT", 57, (8,), "deep ice family reinforcement"),
        ("ENCDATA_D11R0105_SEAFOAM_ISLANDS_B4F", "SPECIES_VULPIX_ALOLAN", 58, (8,), "deep cold regional rare"),
        ("ENCDATA_D41R0105_MT_SILVER_MOLTRES_ROOM", "SPECIES_CHIMCHAR", 62, (8,), "postgame fire starter access"),
        ("ENCDATA_D41R0106_MT_SILVER_3F", "SPECIES_BAGON", 64, (8,), "high mountain dragon rare"),
        ("ENCDATA_D41R0107_MT_SILVER_4F", "SPECIES_SNEASEL_HISUIAN", 65, (8,), "approved high-cliff regional form"),
        ("ENCDATA_D41R0101_MT_SILVER_1F", "SPECIES_TORCHIC", 62, (8,), "postgame fire starter access"),
        ("ENCDATA_D41R0103_MT_SILVER_MOUNTAINSIDE", "SPECIES_GROWLITHE_HISUIAN", 64, (8,), "approved volcanic mountain regional form"),
        ("ENCDATA_D41R0104_MT_SILVER_EXPERT_BELT_ROOM", "SPECIES_RIOLU", 64, (8,), "expert training chamber rare"),
        ("ENCDATA_D41R0102_MT_SILVER_TOP_SNOWY_AREA", "SPECIES_SNEASEL_HISUIAN", 66, (8,), "snowy summit form"),
        ("ENCDATA_R26_ROUTE_26", "SPECIES_MUDKIP", 43, (8,), "late pre-League starter access"),
        ("ENCDATA_R27_ROUTE_27", "SPECIES_PORYGON", 43, (8,), "Tohjo technical rare"),
        ("ENCDATA_R28_ROUTE_28", "SPECIES_SNORLAX", 62, (8,), "postgame mountain-gate rare"),
        ("ENCDATA_D05R0101_ROCK_TUNNEL_1F", "SPECIES_OMANYTE", 52, (8,), "ancient damp cave fossil"),
        ("ENCDATA_D05R0102_ROCK_TUNNEL_B1F", "SPECIES_KABUTO", 54, (8,), "ancient damp cave counterpart"),
        ("ENCDATA_D05R0102_ROCK_TUNNEL_B1F", "SPECIES_GEODUDE_ALOLAN", 54, (8,), "magnetized Rock Tunnel regional Geodude rare"),
        ("ENCDATA_D43R0101_VICTORY_ROAD_1F", "SPECIES_BAGON", 45, (8,), "late rugged dragon rare"),
        ("ENCDATA_D43R0102_VICTORY_ROAD_2F", "SPECIES_GIBLE", 46, (8,), "late tunnel pseudo rare"),
        ("ENCDATA_D43R0103_VICTORY_ROAD_3F", "SPECIES_BELDUM", 47, (8,), "late mineral pseudo rare"),
        ("ENCDATA_R01_ROUTE_1", "SPECIES_BULBASAUR", 49, (8,), "postgame Kanto starter access"),
        ("ENCDATA_R02_ROUTE_2_SOUTH_BELOW_VIRIDIAN_FOREST", "SPECIES_COMBEE", 49, (8,), "Viridian forest-edge honey-tree rare"),
        ("ENCDATA_R02R0101_ROUTE_2_NORTH_ABOVE_VIRIDIAN_FOREST", "SPECIES_BULBASAUR", 50, (8,), "postgame forest starter access"),
        ("ENCDATA_D46R0101_VIRIDIAN_FOREST", "SPECIES_CHIKORITA", 50, (8,), "postgame forest starter access"),
        ("ENCDATA_R03_ROUTE_3", "SPECIES_CHARMANDER", 50, (8,), "postgame rocky Kanto starter access"),
        ("ENCDATA_R04_ROUTE_4", "SPECIES_EEVEE", 50, (8,), "Cerulean-edge rare"),
        ("ENCDATA_R05_ROUTE_5", "SPECIES_MEOWTH_ALOLAN", 49, (8,), "urban regional dark-cat rare"),
        ("ENCDATA_R06_ROUTE_6", "SPECIES_GLAMEOW", 49, (8,), "urban Sinnoh cat counterpart"),
        ("ENCDATA_R07_ROUTE_7", "SPECIES_PORYGON", 51, (8,), "Celadon technical rare"),
        ("ENCDATA_R09_ROUTE_9", "SPECIES_VOLTORB_HISUIAN", 51, (8,), "Power Plant-adjacent regional form"),
        ("ENCDATA_R10_ROUTE_10", "SPECIES_ROTOM", 51, (8,), "Power Plant-adjacent ghost/electric rare"),
        ("ENCDATA_R11_ROUTE_11", "SPECIES_MUNCHLAX", 51, (8,), "Snorlax-route family access"),
        ("ENCDATA_R12_ROUTE_12", "SPECIES_TOTODILE", 50, (8,), "postgame water starter access"),
        ("ENCDATA_R13_ROUTE_13", "SPECIES_CARNIVINE", 50, (8,), "marsh-edge Sinnoh rare"),
        ("ENCDATA_R13_ROUTE_13", "SPECIES_KANGASKHAN", 50, (8,), "southern Kanto guardian rare outside Safari"),
        ("ENCDATA_R14_ROUTE_14", "SPECIES_TROPIUS", 51, (8,), "warm southern Kanto rare"),
        ("ENCDATA_R14_ROUTE_14", "SPECIES_TAUROS", 50, (8,), "southern Kanto herd bull rare outside Safari"),
        ("ENCDATA_R15_ROUTE_15", "SPECIES_BURMY", 50, (8,), "tree-lined route Sinnoh line"),
        ("ENCDATA_R17_ROUTE_17", "SPECIES_HIPPOPOTAS", 51, (8,), "dusty Cycling Road ground rare"),
        ("ENCDATA_R18_ROUTE_18", "SPECIES_PONYTA_GALARIAN", 51, (8,), "quiet western-route regional form"),
        ("ENCDATA_R22_ROUTE_22", "SPECIES_TREECKO", 50, (8,), "postgame starter echo near Victory Road"),
        ("ENCDATA_R24_ROUTE_24", "SPECIES_SQUIRTLE", 50, (8,), "postgame water starter access"),
        ("ENCDATA_R25_ROUTE_25", "SPECIES_SHELLOS", 51, (8,), "coastal Sinnoh water line"),
        ("ENCDATA_D45R0101_TOHJO_FALLS", "SPECIES_FEEBAS", 42, (8,), "waterfall beauty line rare"),
        ("ENCDATA_D01R0101_DIGLETTS_CAVE", "SPECIES_DIGLETT_ALOLAN", 52, (8,), "approved Diglett regional form"),
        ("ENCDATA_D03R0101_CERULEAN_CAVE_1F", "SPECIES_DITTO", 64, (8,), "identity-shifting cave rare"),
        ("ENCDATA_D03R0102_CERULEAN_CAVE_B1F", "SPECIES_BELDUM", 66, (8,), "deep artificial/mineral pseudo"),
        ("ENCDATA_D03R0103_CERULEAN_CAVE_B2F", "SPECIES_ROTOM", 68, (8,), "deep strange-energy rare"),
    ]
    for key, species, level, slots, note in land:
        if key in e:
            set_land_rare(e[key], species, level, slots, note)

    timed = [
        ("ENCDATA_D25R0103_UNION_CAVE_B2F", "SPECIES_BAGON", "SPECIES_LILEEP", "SPECIES_BAGON", 22, "deeper cave Bagon with fossil-line daytime echo"),
        ("ENCDATA_D36R0101_ILEX_FOREST", "SPECIES_BULBASAUR", "SPECIES_NINCADA", "SPECIES_TREECKO", 14, "forest starter and hidden molt-line split"),
        ("ENCDATA_R34_ROUTE_34", "SPECIES_RIOLU", "SPECIES_IGGLYBUFF", "SPECIES_WYNAUT", 15, "Day-Care route friendship and baby-form surprises"),
        ("ENCDATA_R35_ROUTE_35", "SPECIES_PICHU", "SPECIES_EEVEE", "SPECIES_HAPPINY", 16, "city-edge happiness-line rare split"),
        ("ENCDATA_R36_ROUTE_36", "SPECIES_BONSLY", "SPECIES_MEDITITE", "SPECIES_BONSLY", 17, "Sudowoodo-route baby form and meditation rare"),
        ("ENCDATA_R37_ROUTE_37", "SPECIES_VULPIX", "SPECIES_VULPIX", "SPECIES_CHARMANDER", 18, "daytime fox-fire and night Kanto fire-starter split"),
        ("ENCDATA_R38_ROUTE_38", "SPECIES_MEOWTH_GALARIAN", "SPECIES_MEOWTH_GALARIAN", "SPECIES_MEOWTH_ALOLAN", 26, "Meowth-family regional split by time"),
        ("ENCDATA_D18R0101_BURNED_TOWER_1F", "SPECIES_HOUNDOUR", "SPECIES_HOUNDOUR", "SPECIES_MAGBY", 18, "burned ruins dark/fire line and night Magby split"),
        ("ENCDATA_D17R0112_BELL_TOWER_10F", "SPECIES_CYNDAQUIL", "SPECIES_CYNDAQUIL", "SPECIES_CHIMCHAR", 32, "sacred tower Johto/Sinnoh fire-starter split"),
        ("ENCDATA_R39_ROUTE_39", "SPECIES_FARFETCHD_GALARIAN", "SPECIES_FARFETCHD_GALARIAN", "SPECIES_ELEKID", 27, "farm-route regional bird and night electric baby split"),
        ("ENCDATA_R42_ROUTE_42", "SPECIES_TURTWIG", "SPECIES_TEDDIURSA", "SPECIES_TEDDIURSA", 28, "mountain-edge Sinnoh starter and bear-line split"),
        ("ENCDATA_D39R0101_ICE_PATH_1F", "SPECIES_SNORUNT", "SPECIES_SMOOCHUM", "SPECIES_SNORUNT", 34, "cold-cave Hoenn ice and baby ice split"),
        ("ENCDATA_D02R0101_MT_MOON_1F", "SPECIES_CHARMANDER", "SPECIES_CHARMANDER", "SPECIES_CLEFFA", 53, "Kanto fire starter by day, moon baby at night"),
        ("ENCDATA_R08_ROUTE_8", "SPECIES_STUNKY", "SPECIES_MIME_JR", "SPECIES_STUNKY", 51, "urban poison/dark and performer baby split"),
        ("ENCDATA_R16R0301_ROUTE_16", "SPECIES_RATTATA_ALOLAN", "SPECIES_RATTATA_ALOLAN", "SPECIES_GRIMER_ALOLAN", 51, "urban regional dark/poison forms"),
    ]
    for key, morning, day, night, level, note in timed:
        if key in e:
            set_time_land_rare(e[key], morning, day, night, level, (8,), note)

    if "ENCDATA_R34_ROUTE_34" in e:
        set_land_common(e["ENCDATA_R34_ROUTE_34"], "SPECIES_IGGLYBUFF", 15, "Day-Care route baby-form common", (3,))
    if "ENCDATA_R39_ROUTE_39" in e:
        set_land_common(e["ENCDATA_R39_ROUTE_39"], "SPECIES_MILTANK", 27, "farm-route signature dairy cow common", (5,))

    surf = [
        ("ENCDATA_T20_NEW_BARK_TOWN", "SPECIES_CLAMPERL", 18, "coastal pearl-line rare"),
        ("ENCDATA_T21_CHERRYGROVE_CITY", "SPECIES_SQUIRTLE", 18, "early coastal Kanto water starter rare"),
        ("ENCDATA_R30_ROUTE_30", "SPECIES_SURSKIT", 16, "pond bug/water rare"),
        ("ENCDATA_R31_ROUTE_31", "SPECIES_SURSKIT", 16, "pond bug/water rare"),
        ("ENCDATA_T22_VIOLET_CITY", "SPECIES_PIPLUP", 18, "quiet city-pond Sinnoh water starter rare"),
        ("ENCDATA_R32_ROUTE_32", "SPECIES_FEEBAS", 12, "very early but weak beauty-line rare"),
        ("ENCDATA_R34_ROUTE_34", "SPECIES_CLAMPERL", 22, "coastal pearl rare"),
        ("ENCDATA_D25R0103_UNION_CAVE_B2F", "SPECIES_LAPRAS", 22, "deep Union Cave water rare outside Safari"),
        ("ENCDATA_T27_ECRUTEAK_CITY", "SPECIES_SURSKIT", 19, "old-city pond bug/water rare"),
        ("ENCDATA_T26_OLIVINE_CITY", "SPECIES_WAILMER", 30, "port-city whale line"),
        ("ENCDATA_W40_ROUTE_40", "SPECIES_MANTYKE", 28, "open-sea Sinnoh ray"),
        ("ENCDATA_W41_ROUTE_41", "SPECIES_CARVANHA", 32, "rough ocean predator"),
        ("ENCDATA_T24_CIANWOOD_CITY", "SPECIES_CLAMPERL", 32, "island pearl rare"),
        ("ENCDATA_T29_LAKE_OF_RAGE", "SPECIES_FEEBAS", 32, "lake beauty-line rare"),
        ("ENCDATA_T30_BLACKTHORN_CITY", "SPECIES_DRATINI", 40, "dragon-city water rare"),
        ("ENCDATA_R47_ROUTE_47", "SPECIES_SHELLOS", 40, "cliffside coastal Sinnoh line"),
        ("ENCDATA_D02R0103_MT_MOON_OUTSIDE_AREA", "SPECIES_CLAMPERL", 54, "moonlit pond pearl-line rare"),
        ("ENCDATA_D02R0104_MT_MOON_OUTSIDE_CLEFAIRY_ACTIVE", "SPECIES_FEEBAS", 54, "moonlit pond beauty-line rare"),
        ("ENCDATA_D48R0101_CLIFF_EDGE_GATE", "SPECIES_BUIZEL", 40, "cliffside water-route Sinnoh line"),
        ("ENCDATA_T31_MT_SILVER_OUTSIDE_POKEMON_CENTER", "SPECIES_DRATINI", 62, "remote mountain water rare"),
        ("ENCDATA_R12_ROUTE_12", "SPECIES_TOTODILE", 50, "postgame water starter access"),
        ("ENCDATA_T01_PALLET_TOWN", "SPECIES_SQUIRTLE", 48, "postgame starter coastal access"),
        ("ENCDATA_T02_VIRIDIAN_CITY", "SPECIES_LOTAD", 49, "city pond Hoenn water/grass rare"),
        ("ENCDATA_T04_CERULEAN_CITY", "SPECIES_SQUIRTLE", 50, "postgame water-starter city access"),
        ("ENCDATA_T06_VERMILION_CITY", "SPECIES_WAILMER", 50, "major-port whale line"),
        ("ENCDATA_T07_CELADON_CITY", "SPECIES_LOTAD", 49, "garden-city pond Hoenn water/grass rare"),
        ("ENCDATA_T08_FUCHSIA_CITY", "SPECIES_FINNEON", 50, "southern water-route fish"),
        ("ENCDATA_T09_CINNABAR_ISLAND", "SPECIES_CLAMPERL", 54, "island shellfish rare"),
        ("ENCDATA_W19_ROUTE_19", "SPECIES_PIPLUP", 52, "cold sea starter access"),
        ("ENCDATA_W20_ROUTE_20", "SPECIES_CARVANHA", 53, "rough current predator"),
        ("ENCDATA_W21_ROUTE_21", "SPECIES_WAILMER", 52, "deep ocean-route whale line"),
        ("ENCDATA_R24_ROUTE_24", "SPECIES_SQUIRTLE", 50, "Cerulean cape water starter"),
        ("ENCDATA_R25_ROUTE_25", "SPECIES_SHELLOS", 51, "coastal Sinnoh water line"),
        ("ENCDATA_D45R0101_TOHJO_FALLS", "SPECIES_FEEBAS", 43, "waterfall beauty-line rare"),
    ]
    for key, species, level, note in surf:
        if key in e:
            set_surf_rare(e[key], species, level, note)

    fish = [
        ("ENCDATA_W40_ROUTE_40", "SPECIES_MANTYKE", 32, "warm open-sea Sinnoh ray"),
        ("ENCDATA_W41_ROUTE_41", "SPECIES_RELICANTH", 42, "ancient deep-sea rare"),
        ("ENCDATA_T29_LAKE_OF_RAGE", "SPECIES_FEEBAS", 32, "lake beauty-line rare"),
        ("ENCDATA_D44R0102_DRAGONS_DEN", "SPECIES_DRATINI", 40, "dragon shrine fishing rare"),
        ("ENCDATA_T09_CINNABAR_ISLAND", "SPECIES_CLAMPERL", 54, "island shellfish rare"),
        ("ENCDATA_W19_ROUTE_19", "SPECIES_FINNEON", 52, "southern sea Sinnoh fish"),
        ("ENCDATA_W20_ROUTE_20", "SPECIES_CARVANHA", 53, "rough current predator"),
        ("ENCDATA_W21_ROUTE_21", "SPECIES_WAILMER", 52, "open sea whale line"),
        ("ENCDATA_D03R0101_CERULEAN_CAVE_1F", "SPECIES_FEEBAS", 64, "deep cave water rare"),
        ("ENCDATA_D03R0102_CERULEAN_CAVE_B1F", "SPECIES_RELICANTH", 66, "ancient cave-pool rare"),
        ("ENCDATA_D03R0103_CERULEAN_CAVE_B2F", "SPECIES_DRATINI", 66, "deep cave dragon-water rare"),
    ]
    for key, species, level, note in fish:
        if key in e:
            set_fish_rare(e[key], species, level, "super", note)


def encounter_species(entry: Encounter) -> set[str]:
    species = set(entry.morning + entry.day + entry.night)
    species.update(entry.hoenn_sound + entry.sinnoh_sound)
    for slots in [entry.surf, entry.rock_smash, entry.old_rod, entry.good_rod, entry.super_rod]:
        species.update(slot.species for slot in slots)
    species.update([entry.land_swarm, entry.surf_swarm, entry.night_fish, entry.fish_swarm])
    species.discard("SPECIES_NONE")
    return species


def land_pool_species(entry: Encounter) -> set[str]:
    species = set(entry.morning + entry.day + entry.night)
    species.discard("SPECIES_NONE")
    return species


def water_pool_species(entry: Encounter) -> set[str]:
    species = {
        slot.species
        for slots in [entry.surf, entry.old_rod, entry.good_rod, entry.super_rod]
        for slot in slots
    }
    species.discard("SPECIES_NONE")
    return species


def encounter_rare_species(entry: Encounter) -> list[str]:
    species: list[str] = []
    for note in entry.rare_notes:
        for value in re.findall(r"SPECIES_[A-Z0-9_]+", note):
            if value not in species:
                species.append(value)
    return species


def default_rares(entries: list[Encounter]) -> None:
    route_cycle = [
        "SPECIES_RALTS",
        "SPECIES_RIOLU",
        "SPECIES_EEVEE",
        "SPECIES_MUNCHLAX",
        "SPECIES_ABSOL",
        "SPECIES_HERACROSS",
        "SPECIES_SCYTHER",
        "SPECIES_PINSIR",
    ]
    cave_cycle = [
        "SPECIES_ARON",
        "SPECIES_LARVITAR",
        "SPECIES_BAGON",
        "SPECIES_GIBLE",
        "SPECIES_BELDUM",
        "SPECIES_BRONZOR",
        "SPECIES_SPIRITOMB",
        "SPECIES_AERODACTYL",
    ]
    forest_cycle = ["SPECIES_RALTS", "SPECIES_EEVEE", "SPECIES_MUNCHLAX", "SPECIES_BULBASAUR", "SPECIES_TREECKO"]
    water_cycle = ["SPECIES_FEEBAS", "SPECIES_DRATINI", "SPECIES_LAPRAS", "SPECIES_TOTODILE", "SPECIES_PIPLUP", "SPECIES_RELICANTH"]

    for idx, entry in enumerate(entries):
        if not is_meaningful(entry) or encounter_rare_species(entry):
            continue
        key = entry.key
        if has_real_land(entry):
            if any(tag in key for tag in ["FOREST", "PARK"]):
                set_land_rare(entry, forest_cycle[idx % len(forest_cycle)], None, (8,), "default forest rare layer")
            elif any(tag in key for tag in ["CAVE", "TUNNEL", "MORTAR", "ROAD", "MOON", "RUINS", "TOWER", "DEN", "PATH"]):
                set_land_rare(entry, cave_cycle[idx % len(cave_cycle)], None, (8,), "default cave/dungeon rare layer")
            else:
                set_land_rare(entry, route_cycle[idx % len(route_cycle)], None, (8,), "default route rare layer")
        if not entry.rare_notes and has_real_surf(entry):
            set_surf_rare(entry, water_cycle[idx % len(water_cycle)], None, "default surf rare layer")
        if not entry.rare_notes and has_real_fish(entry):
            set_fish_rare(entry, water_cycle[idx % len(water_cycle)], None, "super", "default fishing rare layer")


def apply_post_rare_common_pins(entries: list[Encounter]) -> None:
    e = entry_by_key(entries)
    if "ENCDATA_W40_ROUTE_40" in e and has_real_surf(e["ENCDATA_W40_ROUTE_40"]):
        entry = e["ENCDATA_W40_ROUTE_40"]
        entry.surf[2] = Slot(27, 29, "SPECIES_MANTYKE")
        append_common_note(entry, "surf common SPECIES_MANTYKE 5% lv27-29 - open-sea Sinnoh ray common")


def apply_featured_common_placements(entries: list[Encounter]) -> None:
    e = entry_by_key(entries)
    for key, species_list in FEATURED_COMMON_LAND_PLACEMENTS.items():
        if key not in e:
            continue
        for species in species_list:
            set_land_common(e[key], species, None, "featured Gen 3-4 common Johto variety")
    if "ENCDATA_R48_ROUTE_48" in e:
        set_land_common(e["ENCDATA_R48_ROUTE_48"], "SPECIES_TROPIUS", None, "featured warm-route Gen 3 common variety", (5,))
    for key, species_list in FEATURED_COMMON_SURF_PLACEMENTS.items():
        if key not in e:
            continue
        for species in species_list:
            set_surf_common(e[key], species, None, "featured Gen 3-4 common Johto water variety")
            set_fish_common(e[key], species, None, "super", "featured Gen 3-4 common Johto water variety")


def filler_pool_for_entry(entry: Encounter) -> list[str]:
    key = entry.key
    if not has_real_land(entry):
        return MIN_VARIETY_FILLERS["water"]
    if any(tag in key for tag in ["ICE_PATH", "SEAFOAM"]):
        return MIN_VARIETY_FILLERS["cold"]
    if "TOWER" in key:
        return MIN_VARIETY_FILLERS["tower"]
    if any(tag in key for tag in ["FOREST", "PARK"]):
        return MIN_VARIETY_FILLERS["forest"]
    if any(tag in key for tag in ["CAVE", "MORTAR", "UNION", "RUINS", "ROAD", "DEN"]):
        return MIN_VARIETY_FILLERS["cave"]
    return MIN_VARIETY_FILLERS["route"]


def ensure_minimum_species_variety(entries: list[Encounter]) -> None:
    for entry in entries:
        if not is_meaningful(entry):
            continue
        if has_real_land(entry):
            pools = [filler_pool_for_entry(entry), MIN_VARIETY_FILLERS["route"], MIN_VARIETY_FILLERS["cave"]]
            for pool in pools:
                for species in pool:
                    if len(land_pool_species(entry)) >= 6:
                        break
                    if species in land_pool_species(entry):
                        continue
                    set_land_common(entry, species, None, "minimum six-species land/cave variety")
                if len(land_pool_species(entry)) >= 6:
                    break
        if has_real_surf(entry) or has_real_fish(entry):
            pools = [MIN_VARIETY_FILLERS["water"], MIN_VARIETY_FILLERS["route"]]
            for pool in pools:
                for species in pool:
                    if len(water_pool_species(entry)) >= 6:
                        break
                    if species in water_pool_species(entry):
                        continue
                    before = len(water_pool_species(entry))
                    if has_real_surf(entry):
                        set_surf_common(entry, species, None, "minimum six-species surf/fishing variety")
                    if len(water_pool_species(entry)) <= before and has_real_fish(entry):
                        set_any_fish_common(entry, species, None, "minimum six-species surf/fishing variety")
                if len(water_pool_species(entry)) >= 6:
                    break


def first_real_land_slot(entry: Encounter, preferred: tuple[int, ...]) -> int | None:
    for slot in preferred:
        if slot < len(entry.day) and entry.day[slot] != "SPECIES_NONE":
            return slot
    for slot, species in enumerate(entry.day[:8]):
        if species != "SPECIES_NONE":
            return slot
    return None


def duplicate_land_low_rate_fillers(entry: Encounter) -> None:
    if not has_real_land(entry):
        return
    for target, preferred in [(9, (0, 1, 2, 3)), (10, (0, 2, 4, 6)), (11, (1, 3, 5, 7))]:
        if target == 9 and land_slot_has_explicit_rare(entry, target):
            continue
        source = first_real_land_slot(entry, preferred)
        if source is not None:
            copy_land_slot(entry, source, target)


def first_real_slot(slots: list[Slot], preferred: tuple[int, ...]) -> Slot | None:
    for slot in preferred:
        if slot < len(slots) and slots[slot].species != "SPECIES_NONE":
            return slots[slot]
    for slot in slots:
        if slot.species != "SPECIES_NONE":
            return slot
    return None


def has_surf_rare(entry: Encounter) -> bool:
    return any("surf " in note for note in entry.rare_notes)


def duplicate_surf_low_rate_filler(entry: Encounter) -> None:
    if not has_real_surf(entry):
        return
    source = first_real_slot(entry.surf, (0, 1, 2))
    if source is not None and len(entry.surf) > 3 and not has_surf_rare(entry):
        entry.surf[3] = source
    if source is not None:
        entry.surf[4] = source


def has_super_rod_rare(entry: Encounter) -> bool:
    return any("super rod " in note for note in entry.rare_notes)


def duplicate_rod_low_rate_filler(slots: list[Slot]) -> None:
    if len(slots) <= 4:
        return
    source = first_real_slot(slots, (0, 1, 2, 3))
    if source is not None:
        slots[4] = source


def duplicate_fish_low_rate_fillers(entry: Encounter) -> None:
    if not has_real_fish(entry):
        return
    duplicate_rod_low_rate_filler(entry.old_rod)
    duplicate_rod_low_rate_filler(entry.good_rod)
    if not has_super_rod_rare(entry):
        duplicate_rod_low_rate_filler(entry.super_rod)


def normalize_low_rate_fillers(entries: list[Encounter]) -> None:
    for entry in entries:
        duplicate_land_low_rate_fillers(entry)
        duplicate_surf_low_rate_filler(entry)
        duplicate_fish_low_rate_fillers(entry)


def validate_low_rate_fillers(entry: Encounter) -> list[str]:
    errors: list[str] = []
    if has_real_land(entry):
        common = set(entry.morning[:8] + entry.day[:8] + entry.night[:8])
        common.discard("SPECIES_NONE")
        for slot in (9, 10, 11):
            low = {entry.morning[slot], entry.day[slot], entry.night[slot]} - {"SPECIES_NONE"}
            if slot == 9:
                low -= explicit_land_rare_species(entry, slot)
            if not low <= common:
                errors.append(f"{entry.key}: land low-rate slot {slot} has unique species {', '.join(sorted(low - common))}")
    if has_real_surf(entry):
        common = {slot.species for slot in entry.surf[:3] if slot.species != "SPECIES_NONE"}
        if len(entry.surf) > 3 and not has_surf_rare(entry) and entry.surf[3].species != "SPECIES_NONE" and entry.surf[3].species not in common:
            errors.append(f"{entry.key}: non-rare surf 4% slot has unique species {entry.surf[3].species}")
        if len(entry.surf) > 4 and entry.surf[4].species != "SPECIES_NONE" and entry.surf[4].species not in common:
            errors.append(f"{entry.key}: surf 1% slot has unique species {entry.surf[4].species}")
    for rod_name, slots, preserve_rare in [
        ("old rod", entry.old_rod, False),
        ("good rod", entry.good_rod, False),
        ("super rod", entry.super_rod, has_super_rod_rare(entry)),
    ]:
        if len(slots) <= 4 or preserve_rare:
            continue
        common = {slot.species for slot in slots[:4] if slot.species != "SPECIES_NONE"}
        if slots[4].species != "SPECIES_NONE" and slots[4].species not in common:
            errors.append(f"{entry.key}: {rod_name} 4% filler slot has unique species {slots[4].species}")
    return errors


def explicit_land_rare_species(entry: Encounter, slot: int) -> set[str]:
    rare = set(encounter_rare_species(entry))
    return {
        species
        for species in {entry.morning[slot], entry.day[slot], entry.night[slot]} - {"SPECIES_NONE"}
        if species in rare and is_rare_species(species)
    }


def land_slot_has_explicit_rare(entry: Encounter, slot: int) -> bool:
    return bool(explicit_land_rare_species(entry, slot))


def ordered_unique_species(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for species in values:
        if species == "SPECIES_NONE" or species in seen:
            continue
        seen.add(species)
        unique.append(species)
    return unique


def choose_daytime_merge_slot(combined: list[str], preferred_slots: list[int]) -> int | None:
    counts = Counter(combined)

    candidates = [
        slot
        for slot in preferred_slots
        if combined[slot] == "SPECIES_NONE" or counts[combined[slot]] > 1
    ]
    if not candidates:
        candidates = [
            slot
            for slot, species in enumerate(combined)
            if species != "SPECIES_NONE" and counts[species] > 1
        ]
    if not candidates:
        candidates = [slot for slot, species in enumerate(combined) if species == "SPECIES_NONE"]
    if not candidates:
        candidates = preferred_slots
    if not candidates:
        return None
    return max(candidates, key=lambda slot: (LAND_RATES[slot], -slot))


def merge_daytime_land_slots(entry: Encounter) -> None:
    if not has_real_land(entry):
        return

    combined = entry.day[:]
    desired = set(ordered_unique_species(entry.morning + entry.day))
    pending = [
        species
        for species in ordered_unique_species(entry.morning + entry.day)
        if species not in combined
    ]

    while pending:
        species = pending.pop(0)
        if species in combined:
            continue
        preferred_slots = [
            slot
            for slot, slot_species in enumerate(entry.morning)
            if slot_species == species
        ] + [
            slot
            for slot, slot_species in enumerate(entry.day)
            if slot_species == species
        ]
        slot = choose_daytime_merge_slot(combined, preferred_slots)
        if slot is None:
            continue
        displaced = combined[slot]
        combined[slot] = species
        if displaced in desired and displaced not in combined and displaced not in pending:
            pending.append(displaced)

    entry.morning = combined[:]
    entry.day = combined[:]


def merge_daytime_encounters(entries: list[Encounter]) -> None:
    for entry in entries:
        merge_daytime_land_slots(entry)


def apply_phase6(entries: list[Encounter]) -> None:
    scale_progression_levels(entries)
    apply_featured_common_placements(entries)
    add_explicit_placements(entries)
    ensure_minimum_species_variety(entries)
    default_rares(entries)
    apply_post_rare_common_pins(entries)
    merge_daytime_encounters(entries)
    normalize_low_rate_fillers(entries)
    ensure_minimum_species_variety(entries)
    merge_daytime_encounters(entries)
    normalize_low_rate_fillers(entries)


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


@lru_cache(maxsize=1)
def species_base_stat_totals() -> dict[str, int]:
    text = (ENGINE / "data" / "Species.c").read_text(encoding="utf-8", errors="ignore")
    totals: dict[str, int] = {}
    for match in re.finditer(r"\[(SPECIES_[A-Z0-9_]+)\]\s*=\s*\{", text):
        species = match.group(1)
        block, _ = extract_braced(text, match.end() - 1)
        try:
            stats = find_field_block(block, "baseStats")
        except ValueError:
            continue
        values = [
            int(value)
            for value in re.findall(r"\.(?:hp|attack|defense|spAttack|spDefense|speed)\s*=\s*(\d+)", stats)
        ]
        if len(values) == 6:
            totals[species] = sum(values)
    return totals


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


@lru_cache(maxsize=1)
def rare_family_species() -> set[str]:
    name_to_num, _ = species_constants()
    totals = species_base_stat_totals()
    rare: set[str] = set()
    for comp in evolution_components(name_to_num):
        if comp & LEGENDARY_OR_MYTHICAL:
            continue
        if max((totals.get(species, 0) for species in comp), default=0) >= 500:
            rare.update(comp)
    return rare


def is_rare_species(species: str) -> bool:
    if species == "SPECIES_NONE" or species in FORCED_COMMON_SPECIES:
        return False
    if species in APPROVED_LATER_PLACEMENTS or species in STRONG_CURRENT_RARES:
        return True
    if species_base_stat_totals().get(species, 0) >= 500:
        return True
    return species in rare_family_species()


def directed_evolution_edges(name_to_num: dict[str, int]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    text = (ENGINE / "data" / "Evolutions.c").read_text(encoding="utf-8", errors="ignore")
    outgoing: dict[str, set[str]] = defaultdict(set)
    incoming: dict[str, set[str]] = defaultdict(set)
    parent: str | None = None
    for line in text.splitlines():
        m = re.match(r"\s*\[(SPECIES_[A-Z0-9_]+)\]\s*=\s*\{", line)
        if m:
            parent = m.group(1)
            continue
        if not parent or not 1 <= name_to_num.get(parent, 99999) <= 493:
            continue
        for target in re.findall(r"(?:MON_WITH_FORM\()?\s*(SPECIES_[A-Z0-9_]+)", line):
            if target != "SPECIES_NONE" and target != parent and 1 <= name_to_num.get(target, 99999) <= 493:
                outgoing[parent].add(target)
                incoming[target].add(parent)
    return outgoing, incoming


def evolution_base_forms(name_to_num: dict[str, int]) -> list[str]:
    outgoing, incoming = directed_evolution_edges(name_to_num)
    graph: dict[str, set[str]] = defaultdict(set)
    for species, targets in outgoing.items():
        for target in targets:
            graph[species].add(target)
            graph[target].add(species)

    species_order = lambda species: name_to_num.get(species, 99999)
    nodes = [species for species, num in name_to_num.items() if 1 <= num <= 493 and species != "SPECIES_NONE"]
    seen: set[str] = set()
    bases: list[str] = []
    for species in sorted(nodes, key=species_order):
        if species in seen:
            continue
        queue = deque([species])
        seen.add(species)
        comp: set[str] = set()
        while queue:
            cur = queue.popleft()
            comp.add(cur)
            for nxt in graph[cur]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        if comp & LEGENDARY_OR_MYTHICAL:
            continue
        comp_bases = [member for member in comp if not (incoming[member] & comp)]
        if not comp_bases:
            comp_bases = [min(comp, key=species_order)]
        bases.extend(sorted(comp_bases, key=species_order))
    return bases


def missing_base_forms(name_to_num: dict[str, int], placed: set[str]) -> list[str]:
    return [species for species in evolution_base_forms(name_to_num) if species not in placed]


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


def is_johto_main_entry(entry: Encounter) -> bool:
    key = entry.key
    if not is_meaningful(entry):
        return False
    if re.search(r"ENCDATA_R(0[1-9]|1[0-8]|22|24|25|28)_", key):
        return False
    if any(
        tag in key
        for tag in [
            "PALLET",
            "VIRIDIAN",
            "PEWTER",
            "CERULEAN_CITY",
            "VERMILION",
            "CELADON",
            "FUCHSIA",
            "CINNABAR",
            "SEAFOAM",
            "ROCK_TUNNEL",
            "DIGLETTS_CAVE",
            "MT_MOON",
            "MT_SILVER",
            "CERULEAN_CAVE",
        ]
    ):
        return False
    return True


def johto_main_species(entries: list[Encounter]) -> set[str]:
    placed: set[str] = set()
    for entry in entries:
        if is_johto_main_entry(entry):
            placed.update(encounter_species(entry))
    placed.discard("SPECIES_NONE")
    return placed


def gen3_4_base_forms(name_to_num: dict[str, int]) -> list[str]:
    return [species for species in evolution_base_forms(name_to_num) if 252 <= name_to_num.get(species, 0) <= 493]


def validate(entries: list[Encounter]) -> list[str]:
    errors: list[str] = []
    for entry in entries:
        if len(entry.levels) != 12 or len(entry.morning) != 12 or len(entry.day) != 12 or len(entry.night) != 12:
            errors.append(f"{entry.key}: land slot length mismatch")
        if has_real_land(entry) and entry.morning != entry.day:
            errors.append(f"{entry.key}: morning/day land tables are not merged")
        for field_name in ["surf", "old_rod", "good_rod", "super_rod"]:
            if len(getattr(entry, field_name)) != 5:
                errors.append(f"{entry.key}: {field_name} slot length mismatch")
        if len(entry.rock_smash) != 2:
            errors.append(f"{entry.key}: rock smash slot length mismatch")
        if is_meaningful(entry) and not entry.rare_notes:
            errors.append(f"{entry.key}: no rare layer placement")
        if is_meaningful(entry) and len(encounter_species(entry)) < 6:
            errors.append(f"{entry.key}: fewer than 6 encounter species")
        if is_meaningful(entry) and has_real_land(entry) and len(land_pool_species(entry)) < 6:
            errors.append(f"{entry.key}: fewer than 6 land/cave encounter species")
        if is_meaningful(entry) and (has_real_surf(entry) or has_real_fish(entry)) and len(water_pool_species(entry)) < 6:
            errors.append(f"{entry.key}: fewer than 6 surf/fishing encounter species")
        errors.extend(validate_low_rate_fillers(entry))
        rare_species = encounter_rare_species(entry)
        if is_meaningful(entry) and not 1 <= len(rare_species) <= 3:
            errors.append(f"{entry.key}: rare species count {len(rare_species)} is outside 1-3")
        for species in rare_species:
            if not is_rare_species(species):
                errors.append(f"{entry.key}: rare species does not satisfy rare rule: {species}")

    name_to_num, _ = species_constants()
    placed = placed_species_all_sources(entries)
    forbidden = encounter_species_forbidden(placed, name_to_num)
    if forbidden:
        errors.append("forbidden later-generation encounter species: " + ", ".join(forbidden))

    missing_bases = missing_base_forms(name_to_num, placed)
    if missing_bases:
        errors.append("missing wild base/pre-evolution encounter species: " + ", ".join(missing_bases))

    johto_placed = johto_main_species(entries)
    missing_johto_gen3_4 = [species for species in gen3_4_base_forms(name_to_num) if species not in johto_placed]
    if missing_johto_gen3_4:
        errors.append("Gen 3-4 base forms missing from Johto main encounters: " + ", ".join(missing_johto_gen3_4))

    for entry in entries:
        for note in entry.rare_notes:
            m = re.search(r" (\d+)% ", note)
            if m and not 3 <= int(m.group(1)) <= 5:
                errors.append(f"{entry.key}: rare placement is outside the 3-5% target: {note}")
    return errors


def make_report(entries: list[Encounter]) -> str:
    name_to_num, _ = species_constants()
    comps = evolution_components(name_to_num)
    placed = placed_species_all_sources(entries)
    missing_bases = missing_base_forms(name_to_num, placed)
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
    with_six_species = [entry for entry in meaningful if len(encounter_species(entry)) >= 6]
    land_meaningful = [entry for entry in meaningful if has_real_land(entry)]
    water_meaningful = [entry for entry in meaningful if has_real_surf(entry) or has_real_fish(entry)]
    with_six_land_species = [entry for entry in land_meaningful if len(land_pool_species(entry)) >= 6]
    with_six_water_species = [entry for entry in water_meaningful if len(water_pool_species(entry)) >= 6]
    rare_count_ok = [entry for entry in meaningful if 1 <= len(encounter_rare_species(entry)) <= 3]
    johto_gen3_4_bases = gen3_4_base_forms(name_to_num)
    johto_gen3_4_covered = [species for species in johto_gen3_4_bases if species in johto_main_species(entries)]
    rare_lines = []
    for entry in meaningful:
        notes = "; ".join(entry.rare_notes)
        rare_lines.append(f"- `{entry.key}`: {notes}")
    common_lines = []
    for entry in meaningful:
        if entry.common_notes:
            notes = "; ".join(entry.common_notes)
            common_lines.append(f"- `{entry.key}`: {notes}")

    notable = [
        "- Routes 29-31 now carry early common-route variety across generations, including Zigzagoon, Starly, Bidoof, Taillow, Wurmple, Poochyena, Lotad, and Seedot.",
        "- Johto routes and dungeons use Gen 3-4 Pokemon as ordinary ecological encounters at common rates where slot space allows, not only as rare prizes.",
        "- Every non-legendary Gen 3-4 base/pre-evolution form is represented in the main Johto encounter set.",
        "- Rare encounter slots are reserved for strong current forms, lines whose final form reaches 500+ BST, or approved regional forms.",
        "- Rare Finds now explicitly include Alolan Geodude, Galarian Zigzagoon, Paldean Wooper, Lapras, Kangaskhan, Tauros, and an earlier Ice Path Sneasel placement.",
        "- Land/cave and surf/fishing pools are now each filled to at least six species when that encounter mode exists.",
        "- Route 31, Ilex Forest, Route 37, Slowpoke Well, Route 42, Cherrygrove, and Violet: earlier Johto access to Gen 1/3/4 starter lines.",
        "- Dark Cave Route 31 entrance: Larvitar at 4%, level 7.",
        "- Union Cave B1F/B2F: Gible and Bagon become early cave pseudo-legendary surprises.",
        "- Route 34/35/36/39, Ice Path, Burned Tower, Mt. Moon, and Route 8: missing baby/base forms are placed semantically, with common forms demoted out of rare slots.",
        "- Dragon's Den and Whirl Islands: Dratini/Bagon access in dragon- and water-themed spaces.",
        "- Mt. Mortar, Victory Road, Cerulean Cave, and Mt. Silver: Beldum, Gible, Bagon, and Riolu as late cave/mountain rares.",
        "- Ice Path and Seafoam Islands: Snorunt, Snover, Spheal, Alolan Sandshrew, Alolan Vulpix, and Galarian Mr. Mime.",
        "- Sprout Tower and Burned Tower: Shuppet, Duskull, Houndour, and other ghost/dark-flavored surprises.",
        "- Ruins of Alph: Baltoy, Mawile, and Spiritomb as ancient/mystic rares.",
        "- Late Johto, Kanto routes, and Kanto caves: common levels track the smoother boss curve, with post-League Kanto no longer stuck in the 30s.",
        "- Power Plant-adjacent Route 9/10 and Burned Tower: Hisuian Voltorb and Rotom are available without treating Rotom as a strong rare.",
    ]

    missing_text = "None." if not wild_missing else ", ".join(
        sorted(
            min(comp, key=lambda s: name_to_num.get(s, 99999)).replace("SPECIES_", "")
            for comp in wild_missing
        )
    )
    forbidden_text = "None." if not forbidden else ", ".join(forbidden)
    missing_bases_text = "None." if not missing_bases else ", ".join(species.replace("SPECIES_", "") for species in missing_bases)

    return "\n".join(
        [
            "# Phase 6 Obtainability and Rare Encounter Report",
            "",
            "Generated by `tools/perfect_johto/phase6_encounter_tools.py`.",
            "",
            "## Coverage Summary",
            "",
            f"- Meaningful non-Safari encounter areas with rare layer placements: {len(with_rares)} / {len(meaningful)}.",
            f"- Meaningful non-Safari encounter areas with at least six encounter species: {len(with_six_species)} / {len(meaningful)}.",
            f"- Meaningful land/cave encounter pools with at least six species: {len(with_six_land_species)} / {len(land_meaningful)}.",
            f"- Meaningful surf/fishing encounter pools with at least six species: {len(with_six_water_species)} / {len(water_meaningful)}.",
            f"- Meaningful non-Safari encounter areas with 1-3 rare species: {len(rare_count_ok)} / {len(meaningful)}.",
            f"- Non-legendary Gen 1-4 evolution-family components with wild encounter coverage: {len(wild_covered)} / {len(wild_covered) + len(wild_missing)}.",
            f"- Non-legendary Gen 1-4 family components still missing from wild tables: {missing_text}",
            f"- Non-legendary Gen 1-4 base/pre-evolution species still missing from wild tables: {missing_bases_text}",
            f"- Non-legendary Gen 3-4 base/pre-evolution species covered in Johto main encounters: {len(johto_gen3_4_covered)} / {len(johto_gen3_4_bases)}.",
            f"- Unrelated later-generation species found in encounter tables: {forbidden_text}",
            "- Gen 1-4 non-mythical legendaries are covered by low-rate random surprise overlays: weaker-tier legends at 1/500 beginning at 4 badges and true/cover-story legends at 1/1000 once unlocked.",
            "- Gen 1-4 mythicals are included only in the 16-badge surprise pool, following the personalized tweak file's permissive direction while preserving proper events as future official encounters.",
            "",
            "## Featured Common Variety",
            "",
            *common_lines,
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
            "- Primary land rare slots use HGSS slot 8, a 4% slot; curated secondary land rares may use slot 9 at 4%, while non-rare land low-rate filler still duplicates common species.",
            "- Main land encounter tables merge morning and day into one daytime table; night remains separate.",
            "- Surf rare slots use slot 3, a 4% slot; non-rare surf 4% slots and old 1% surf slots duplicate common surf species.",
            "- Fishing rare slots use slot 4, which Phase 6 changes from 5% to 4%; non-rare old/good/super rod 4% filler slots duplicate common rod species.",
            "- Rare species validation allows only strong current forms, lines whose final form reaches 500+ BST, or approved regional forms.",
            "- Common Gen 3-4 ecology placements use normal land, surf, and fishing slots; land/cave and surf/fishing minimums are validated separately.",
            "- Rock Smash has only 80%/20% slots and is not used for 3-5% rare placement.",
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
