#!/usr/bin/env python3
"""Phase 8 postgame, legendary, and champion-circuit tooling."""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import re
from typing import Iterable


ROOT = pathlib.Path(__file__).resolve().parents[2]
ENGINE = ROOT / "hg-engine-main" / "hg-engine-main"
TRAINERS = ENGINE / "data" / "Trainers.c"
FLAGS = ENGINE / "armips" / "include" / "flags.s"
DOJO_SCRIPT = ENGINE / "armips" / "scr_seq" / "scr_seq_00832_phase8_dojo.s"
DOJO_TEXT = ENGINE / "data" / "text" / "533.txt"
BASE_DOJO_SCRIPT = ROOT / "pokeheartgold-master" / "files" / "fielddata" / "script" / "scr_seq" / "scr_seq_0832_T11R0101.s"
REPORT = ROOT / "docs" / "phase8_postgame_report.md"

TRAINER_TYPE_BOSS = "TRAINER_DATA_TYPE_MOVES | TRAINER_DATA_TYPE_ITEMS"
AI_CHAMPION = "F_PRIORITIZE_SUPER_EFFECTIVE | F_EVALUATE_ATTACKS | F_EXPERT_ATTACKS | F_PRIORITIZE_DAMAGE"

PHASE8_TEXT_ORDER = (738, 739, 740)

PHASE8_FLAGS = {
    "FLAG_PHASE8_CAUGHT_MEW": 2865,
    "FLAG_PHASE8_CAUGHT_CELEBI": 2866,
    "FLAG_PHASE8_CAUGHT_REGIROCK": 2867,
    "FLAG_PHASE8_CAUGHT_REGICE": 2868,
    "FLAG_PHASE8_CAUGHT_REGISTEEL": 2869,
    "FLAG_PHASE8_CAUGHT_REGIGIGAS": 2870,
    "FLAG_PHASE8_CAUGHT_LATIAS": 2871,
    "FLAG_PHASE8_CAUGHT_LATIOS": 2872,
    "FLAG_PHASE8_CAUGHT_JIRACHI": 2873,
    "FLAG_PHASE8_CAUGHT_DEOXYS": 2874,
    "FLAG_PHASE8_CAUGHT_UXIE": 2875,
    "FLAG_PHASE8_CAUGHT_MESPRIT": 2876,
    "FLAG_PHASE8_CAUGHT_AZELF": 2877,
    "FLAG_PHASE8_CAUGHT_DIALGA": 2878,
    "FLAG_PHASE8_CAUGHT_PALKIA": 2879,
    "FLAG_PHASE8_CAUGHT_GIRATINA": 2880,
    "FLAG_PHASE8_CAUGHT_HEATRAN": 2881,
    "FLAG_PHASE8_CAUGHT_CRESSELIA": 2882,
    "FLAG_PHASE8_CAUGHT_DARKRAI": 2883,
    "FLAG_PHASE8_CAUGHT_SHAYMIN": 2884,
    "FLAG_PHASE8_CAUGHT_MANAPHY": 2885,
    "FLAG_PHASE8_CAUGHT_PHIONE": 2886,
    "FLAG_PHASE8_CAUGHT_ARCEUS": 2887,
}

TEXT = {
    "NEED_BADGES": 36,
    "HUB_PROMPT": 37,
    "ARTICUNO": 38,
    "ZAPDOS": 39,
    "MOLTRES": 40,
    "MEWTWO": 41,
    "LUGIA": 42,
    "HO_OH": 43,
    "SUICUNE": 44,
    "LATIAS": 45,
    "LATIOS": 46,
    "BACK": 47,
    "REGIROCK": 48,
    "REGICE": 49,
    "REGISTEEL": 50,
    "REGIGIGAS": 51,
    "KYOGRE": 52,
    "GROUDON": 53,
    "RAYQUAZA": 54,
    "MEW": 55,
    "CELEBI": 56,
    "JIRACHI": 57,
    "DEOXYS": 58,
    "HEATRAN": 59,
    "CRESSELIA": 60,
    "DARKRAI": 61,
    "SHAYMIN": 62,
    "MANAPHY": 63,
    "PHIONE": 64,
    "UXIE": 65,
    "MESPRIT": 66,
    "AZELF": 67,
    "DIALGA": 68,
    "PALKIA": 69,
    "GIRATINA": 70,
    "ARCEUS": 71,
    "LANCE": 72,
    "BLUE": 73,
    "RED": 74,
    "STEVEN": 75,
    "WALLACE": 76,
    "CYNTHIA": 77,
    "CHAMPIONS": 78,
    "KANTO_LEGENDS": 79,
    "ANCIENT_SEALS": 80,
    "MYTHIC_DOSSIERS": 81,
    "CREATION_ECHOES": 82,
    "CHAMPION_PROMPT": 83,
    "KANTO_PROMPT": 84,
    "ANCIENT_PROMPT": 85,
    "MYTHIC_PROMPT": 86,
    "CREATION_PROMPT": 87,
    "NEED_RED": 88,
    "NEED_REGIS": 89,
    "NEED_WEATHER": 90,
    "NEED_CRESSELIA": 91,
    "NEED_MANAPHY": 92,
    "NEED_CREATION": 93,
    "ALREADY_CAUGHT": 94,
    "ENCOUNTER_STIRS": 95,
    "NOT_CAUGHT": 96,
    "CHAMPION_WIN": 97,
    "SEALED": 98,
}


@dataclasses.dataclass(frozen=True)
class Mon:
    species: str
    level: int
    moves: tuple[str, str, str, str]
    item: str = "ITEM_NONE"
    ivs: int = 250
    ability_slot: str = "TRAINER_POKEMON_ABILITY_1"


@dataclasses.dataclass(frozen=True)
class Trainer:
    trainer_id: int
    name: str
    trainer_class: str
    mons: tuple[Mon, ...]
    lose_text: str


@dataclasses.dataclass(frozen=True)
class LegendaryEvent:
    name: str
    species: str
    level: int
    flag: str
    menu_text: int
    category: str
    location: str
    prerequisites: str
    encounter_type: str = "stationary scripted Dojo dossier"
    hide_flags: tuple[str, ...] = ()
    prelude: tuple[str, ...] = ()


def mon(species: str, level: int, moves: tuple[str, str, str, str], item: str = "ITEM_NONE", ivs: int = 250) -> Mon:
    return Mon(f"SPECIES_{species}", level, tuple(f"MOVE_{move}" for move in moves), item, ivs)


CHAMPIONS = (
    Trainer(
        738,
        "Steven",
        "TRAINERCLASS_CHAMPION",
        (
            mon("SKARMORY", 90, ("STEEL_WING", "AIR_SLASH", "NIGHT_SLASH", "SPIKES")),
            mon("CLAYDOL", 90, ("EARTH_POWER", "PSYCHIC", "ANCIENT_POWER", "LIGHT_SCREEN")),
            mon("CRADILY", 91, ("ENERGY_BALL", "STONE_EDGE", "CONFUSE_RAY", "RECOVER")),
            mon("ARMALDO", 91, ("X_SCISSOR", "ROCK_SLIDE", "AQUA_TAIL", "CRUSH_CLAW")),
            mon("AGGRON", 93, ("IRON_HEAD", "STONE_EDGE", "EARTHQUAKE", "DRAGON_CLAW")),
            mon("METAGROSS", 96, ("METEOR_MASH", "ZEN_HEADBUTT", "EARTHQUAKE", "BULLET_PUNCH"), "ITEM_SITRUS_BERRY", 255),
        ),
        "Your bond with your Pokemon is stronger than any stone.\\n",
    ),
    Trainer(
        739,
        "Wallace",
        "TRAINERCLASS_CHAMPION",
        (
            mon("WAILORD", 90, ("WATER_SPOUT", "ICE_BEAM", "AMNESIA", "REST")),
            mon("TENTACRUEL", 90, ("SURF", "SLUDGE_BOMB", "ICE_BEAM", "TOXIC_SPIKES")),
            mon("GYARADOS", 91, ("WATERFALL", "ICE_FANG", "DRAGON_DANCE", "CRUNCH")),
            mon("LUDICOLO", 92, ("SURF", "ENERGY_BALL", "ICE_BEAM", "RAIN_DANCE")),
            mon("WHISCASH", 92, ("EARTHQUAKE", "AQUA_TAIL", "ZEN_HEADBUTT", "REST")),
            mon("MILOTIC", 96, ("SURF", "ICE_BEAM", "AQUA_RING", "RECOVER"), "ITEM_SITRUS_BERRY", 255),
        ),
        "A splendid battle. Beauty and strength in full measure.\\n",
    ),
    Trainer(
        740,
        "Cynthia",
        "TRAINERCLASS_CHAMPION",
        (
            mon("SPIRITOMB", 92, ("DARK_PULSE", "SHADOW_BALL", "WILL_O_WISP", "SILVER_WIND")),
            mon("ROSERADE", 92, ("ENERGY_BALL", "SLUDGE_BOMB", "SHADOW_BALL", "STUN_SPORE")),
            mon("TOGEKISS", 93, ("AIR_SLASH", "AURA_SPHERE", "EXTREME_SPEED", "ROOST")),
            mon("LUCARIO", 94, ("AURA_SPHERE", "DRAGON_PULSE", "EXTREME_SPEED", "DARK_PULSE")),
            mon("MILOTIC", 94, ("SURF", "ICE_BEAM", "MIRROR_COAT", "RECOVER")),
            mon("GARCHOMP", 98, ("DRAGON_RUSH", "EARTHQUAKE", "STONE_EDGE", "SWORDS_DANCE"), "ITEM_SITRUS_BERRY", 255),
        ),
        "There are still more myths for us to investigate.\\n",
    ),
)


LEGENDARIES = (
    LegendaryEvent("Articuno", "SPECIES_ARTICUNO", 70, "FLAG_CAUGHT_ARTICUNO", TEXT["ARTICUNO"], "kanto", "Seafoam dossier, Saffron Fighting Dojo", "16 badges", hide_flags=("FLAG_HIDE_SEAFOAM_ISLAND_ARTICUNO",)),
    LegendaryEvent("Zapdos", "SPECIES_ZAPDOS", 70, "FLAG_CAUGHT_ZAPDOS", TEXT["ZAPDOS"], "kanto", "Power Plant dossier, Saffron Fighting Dojo", "16 badges", hide_flags=("FLAG_HIDE_ROUTE_10_ZAPDOS",)),
    LegendaryEvent("Moltres", "SPECIES_MOLTRES", 72, "FLAG_CAUGHT_MOLTRES", TEXT["MOLTRES"], "kanto", "Mt. Silver dossier, Saffron Fighting Dojo", "16 badges", hide_flags=("FLAG_HIDE_MT_SILVER_CAVE_MOLTRES",)),
    LegendaryEvent("Mewtwo", "SPECIES_MEWTWO", 80, "FLAG_CAUGHT_MEWTWO", TEXT["MEWTWO"], "kanto", "Cerulean Cave dossier, Saffron Fighting Dojo", "16 badges", hide_flags=("FLAG_HIDE_CERULEAN_CAVE_MEWTWO",)),
    LegendaryEvent("Lugia", "SPECIES_LUGIA", 75, "FLAG_CAUGHT_LUGIA", TEXT["LUGIA"], "kanto", "Whirl Islands dossier, Saffron Fighting Dojo", "16 badges", hide_flags=("FLAG_HIDE_WHIRL_ISLAND_LUGIA",)),
    LegendaryEvent("Ho-Oh", "SPECIES_HO_OH", 75, "FLAG_CAUGHT_HO_OH", TEXT["HO_OH"], "kanto", "Bell Tower dossier, Saffron Fighting Dojo", "16 badges", hide_flags=("FLAG_HIDE_BELL_TOWER_HO_OH",)),
    LegendaryEvent(
        "Suicune",
        "SPECIES_SUICUNE",
        65,
        "FLAG_CAUGHT_SUICUNE",
        TEXT["SUICUNE"],
        "kanto",
        "Eusine dossier, Saffron Fighting Dojo",
        "16 badges",
        hide_flags=(
            "FLAG_HIDE_BURNED_TOWER_B1F_SUICUNE",
            "FLAG_HIDE_BURNED_TOWER_1F_SUICUNE",
            "FLAG_HIDE_CIANWOOD_SUICUNE",
            "FLAG_HIDE_ROUTE_42_SUICUNE",
            "FLAG_HIDE_VERMILION_SUICUNE",
            "FLAG_HIDE_ROUTE_14_SUICUNE",
            "FLAG_HIDE_ROUTE_25_SUICUNE",
            "FLAG_HIDE_BURNED_TOWER_STATIC_SUICUNE",
        ),
    ),
    LegendaryEvent("Latias", "SPECIES_LATIAS", 68, "FLAG_PHASE8_CAUGHT_LATIAS", TEXT["LATIAS"], "kanto", "Kanto roaming dossier, Saffron Fighting Dojo", "16 badges", hide_flags=("FLAG_HIDE_PEWTER_CITY_LATIAS",)),
    LegendaryEvent("Latios", "SPECIES_LATIOS", 68, "FLAG_PHASE8_CAUGHT_LATIOS", TEXT["LATIOS"], "kanto", "Kanto roaming dossier, Saffron Fighting Dojo", "16 badges", hide_flags=("FLAG_HIDE_PEWTER_CITY_LATIOS",)),
    LegendaryEvent("Regirock", "SPECIES_REGIROCK", 70, "FLAG_PHASE8_CAUGHT_REGIROCK", TEXT["REGIROCK"], "ancient", "Ruins of Alph seal dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent("Regice", "SPECIES_REGICE", 70, "FLAG_PHASE8_CAUGHT_REGICE", TEXT["REGICE"], "ancient", "Ruins of Alph seal dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent("Registeel", "SPECIES_REGISTEEL", 70, "FLAG_PHASE8_CAUGHT_REGISTEEL", TEXT["REGISTEEL"], "ancient", "Ruins of Alph seal dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent(
        "Regigigas",
        "SPECIES_REGIGIGAS",
        80,
        "FLAG_PHASE8_CAUGHT_REGIGIGAS",
        TEXT["REGIGIGAS"],
        "ancient",
        "Ruins of Alph seal dossier, Saffron Fighting Dojo",
        "16 badges plus Regirock, Regice, and Registeel caught",
        prelude=(
            "goto_if_unset FLAG_PHASE8_CAUGHT_REGIROCK, _p8_need_regis",
            "goto_if_unset FLAG_PHASE8_CAUGHT_REGICE, _p8_need_regis",
            "goto_if_unset FLAG_PHASE8_CAUGHT_REGISTEEL, _p8_need_regis",
        ),
    ),
    LegendaryEvent("Kyogre", "SPECIES_KYOGRE", 75, "FLAG_CAUGHT_KYOGRE", TEXT["KYOGRE"], "ancient", "Embedded Tower weather dossier, Saffron Fighting Dojo", "16 badges", hide_flags=("FLAG_HIDE_EMBEDDED_TOWER_KYOGRE", "FLAG_HIDE_EMBEDDED_TOWER_KYOGRE_HIKER")),
    LegendaryEvent("Groudon", "SPECIES_GROUDON", 75, "FLAG_CAUGHT_GROUDON", TEXT["GROUDON"], "ancient", "Embedded Tower weather dossier, Saffron Fighting Dojo", "16 badges", hide_flags=("FLAG_HIDE_EMBEDDED_TOWER_GROUDON", "FLAG_HIDE_EMBEDDED_TOWER_GROUDON_HIKER")),
    LegendaryEvent(
        "Rayquaza",
        "SPECIES_RAYQUAZA",
        80,
        "FLAG_CAUGHT_RAYQUAZA",
        TEXT["RAYQUAZA"],
        "ancient",
        "Embedded Tower sky dossier, Saffron Fighting Dojo",
        "16 badges plus Kyogre and Groudon caught",
        hide_flags=("FLAG_HIDE_EMBEDDED_TOWER_RAYQUAZA",),
        prelude=("goto_if_unset FLAG_CAUGHT_KYOGRE, _p8_need_weather", "goto_if_unset FLAG_CAUGHT_GROUDON, _p8_need_weather"),
    ),
    LegendaryEvent("Mew", "SPECIES_MEW", 70, "FLAG_PHASE8_CAUGHT_MEW", TEXT["MEW"], "mythic", "Faraway dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent("Celebi", "SPECIES_CELEBI", 70, "FLAG_PHASE8_CAUGHT_CELEBI", TEXT["CELEBI"], "mythic", "Ilex Shrine dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent("Jirachi", "SPECIES_JIRACHI", 75, "FLAG_PHASE8_CAUGHT_JIRACHI", TEXT["JIRACHI"], "mythic", "Mt. Moon stargazing dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent("Deoxys", "SPECIES_DEOXYS", 80, "FLAG_PHASE8_CAUGHT_DEOXYS", TEXT["DEOXYS"], "mythic", "Pewter meteorite dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent("Heatran", "SPECIES_HEATRAN", 78, "FLAG_PHASE8_CAUGHT_HEATRAN", TEXT["HEATRAN"], "mythic", "Volcanic dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent("Cresselia", "SPECIES_CRESSELIA", 78, "FLAG_PHASE8_CAUGHT_CRESSELIA", TEXT["CRESSELIA"], "mythic", "Dream dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent(
        "Darkrai",
        "SPECIES_DARKRAI",
        82,
        "FLAG_PHASE8_CAUGHT_DARKRAI",
        TEXT["DARKRAI"],
        "mythic",
        "Nightmare dossier, Saffron Fighting Dojo",
        "16 badges plus Cresselia caught",
        prelude=("goto_if_unset FLAG_PHASE8_CAUGHT_CRESSELIA, _p8_need_cresselia",),
    ),
    LegendaryEvent("Shaymin", "SPECIES_SHAYMIN", 75, "FLAG_PHASE8_CAUGHT_SHAYMIN", TEXT["SHAYMIN"], "mythic", "Flower restoration dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent("Manaphy", "SPECIES_MANAPHY", 75, "FLAG_PHASE8_CAUGHT_MANAPHY", TEXT["MANAPHY"], "mythic", "Ocean egg dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent(
        "Phione",
        "SPECIES_PHIONE",
        65,
        "FLAG_PHASE8_CAUGHT_PHIONE",
        TEXT["PHIONE"],
        "mythic",
        "Ocean egg dossier, Saffron Fighting Dojo",
        "16 badges plus Manaphy caught",
        prelude=("goto_if_unset FLAG_PHASE8_CAUGHT_MANAPHY, _p8_need_manaphy",),
    ),
    LegendaryEvent("Uxie", "SPECIES_UXIE", 72, "FLAG_PHASE8_CAUGHT_UXIE", TEXT["UXIE"], "creation", "Lake insight dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent("Mesprit", "SPECIES_MESPRIT", 72, "FLAG_PHASE8_CAUGHT_MESPRIT", TEXT["MESPRIT"], "creation", "Lake emotion dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent("Azelf", "SPECIES_AZELF", 72, "FLAG_PHASE8_CAUGHT_AZELF", TEXT["AZELF"], "creation", "Lake willpower dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent("Dialga", "SPECIES_DIALGA", 82, "FLAG_PHASE8_CAUGHT_DIALGA", TEXT["DIALGA"], "creation", "Sinjoh time dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent("Palkia", "SPECIES_PALKIA", 82, "FLAG_PHASE8_CAUGHT_PALKIA", TEXT["PALKIA"], "creation", "Sinjoh space dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent("Giratina", "SPECIES_GIRATINA", 82, "FLAG_PHASE8_CAUGHT_GIRATINA", TEXT["GIRATINA"], "creation", "Sinjoh distortion dossier, Saffron Fighting Dojo", "16 badges"),
    LegendaryEvent(
        "Arceus",
        "SPECIES_ARCEUS",
        100,
        "FLAG_PHASE8_CAUGHT_ARCEUS",
        TEXT["ARCEUS"],
        "creation",
        "Ultimate Sinjoh dossier, Saffron Fighting Dojo",
        "16 badges, Red defeated, lake trio caught, and creation trio caught",
        prelude=(
            "goto_if_not_defeated 260, _p8_need_red",
            "goto_if_unset FLAG_PHASE8_CAUGHT_UXIE, _p8_need_creation",
            "goto_if_unset FLAG_PHASE8_CAUGHT_MESPRIT, _p8_need_creation",
            "goto_if_unset FLAG_PHASE8_CAUGHT_AZELF, _p8_need_creation",
            "goto_if_unset FLAG_PHASE8_CAUGHT_DIALGA, _p8_need_creation",
            "goto_if_unset FLAG_PHASE8_CAUGHT_PALKIA, _p8_need_creation",
            "goto_if_unset FLAG_PHASE8_CAUGHT_GIRATINA, _p8_need_creation",
        ),
    ),
)

NATIVE_EVENTS = (
    ("Raikou", "roaming", 40, "Burned Tower release", "Burned Tower event releases the Johto roamer"),
    ("Entei", "roaming", 40, "Burned Tower release", "Burned Tower event releases the Johto roamer"),
)

DOJO_TEXT_LINES = [
    "The master is making a pilgrimage with his Pokemon.\\n",
    "This is the Fighting Dojo. Trainers who have earned Gym Leader rematches gather here.\\n",
    "Struggle for vengeance!\\nFighting Dojo\\n",
    "A complicated fracture.\\nThe Karate King, the Fighting Master, is in a cave in Johto for training.\\n",
    "Falkner: You have never felt the rush of soaring through the sky!\\n",
    "Falkner: Someday, I will be able to fly in the sky with them...\\n",
    "Bugsy: Study shall reveal the great secrets of Bug-type Pokemon!\\n",
    "Bugsy: Tough Pokemon like yours are another great subject for research.\\n",
    "Whitney: You came all the way to see me? Then let us battle!\\n",
    "Whitney: No fair! You are still too strong!\\n",
    "Chuck: Let your fists do the talking!\\n",
    "Chuck: Wahaha! You landed a clean one!\\n",
    "Jasmine: I will battle with steel-hard resolve.\\n",
    "Jasmine: Your strength is gentle, but it does not bend.\\n",
    "Morty: I have trained to see even further into the future.\\n",
    "Morty: I saw this result...but it still stings.\\n",
    "Pryce: The winter of training never ends.\\n",
    "Pryce: Hm. I still have much to learn.\\n",
    "Clair: I will show you the pride of the Dragon Den.\\n",
    "Clair: I accept it. You are strong.\\n",
    "Lt. Surge: Hey, kid! My Electric Pokemon are ready to shock you!\\n",
    "Lt. Surge: You shorted out my strategy!\\n",
    "Sabrina: I foresaw your arrival. Let us battle.\\n",
    "Sabrina: The vision was correct. You are exceptional.\\n",
    "Erika: Let us have a graceful battle.\\n",
    "Erika: Oh my. Your skill blooms beautifully.\\n",
    "Misty: Are you ready for my Water Pokemon?\\n",
    "Misty: You splashed right through me!\\n",
    "Brock: Rock-hard defense, full power!\\n",
    "Brock: Your tactics cracked my wall.\\n",
    "Janine: I will battle in my father name!\\n",
    "Janine: I still need more training.\\n",
    "Blaine: My fiery spirit has not cooled one bit!\\n",
    "Blaine: Burned out again! Hah!\\n",
    "Blue: A real challenger? Fine. Show me what you have got.\\n",
    "Blue: Not bad. I can see why the League keeps talking about you.\\n",
    "Earn all sixteen badges first. Kanto has deeper challenges for a proven Champion.\\n",
    "The Dojo now keeps postgame battle records and legendary dossiers. Choose a challenge.\\n",
    "Articuno\\n",
    "Zapdos\\n",
    "Moltres\\n",
    "Mewtwo\\n",
    "Lugia\\n",
    "Ho-Oh\\n",
    "Suicune\\n",
    "Latias\\n",
    "Latios\\n",
    "Back\\n",
    "Regirock\\n",
    "Regice\\n",
    "Registeel\\n",
    "Regigigas\\n",
    "Kyogre\\n",
    "Groudon\\n",
    "Rayquaza\\n",
    "Mew\\n",
    "Celebi\\n",
    "Jirachi\\n",
    "Deoxys\\n",
    "Heatran\\n",
    "Cresselia\\n",
    "Darkrai\\n",
    "Shaymin\\n",
    "Manaphy\\n",
    "Phione\\n",
    "Uxie\\n",
    "Mesprit\\n",
    "Azelf\\n",
    "Dialga\\n",
    "Palkia\\n",
    "Giratina\\n",
    "Arceus\\n",
    "Lance\\n",
    "Blue\\n",
    "Red\\n",
    "Steven\\n",
    "Wallace\\n",
    "Cynthia\\n",
    "Champion Circuit\\n",
    "Kanto Legends\\n",
    "Ancient Seals\\n",
    "Mythic Dossiers\\n",
    "Creation Echoes\\n",
    "Choose a Champion Circuit battle.\\n",
    "Choose a Kanto or Johto legendary dossier.\\n",
    "Choose an ancient seal or weather dossier.\\n",
    "Choose a mythical or dream dossier.\\n",
    "Choose a lake or creation dossier.\\n",
    "Defeat Red on Mt. Silver before advanced circuit challenges open.\\n",
    "The three ancient seals must be claimed before Regigigas awakens.\\n",
    "Rayquaza will not descend until Kyogre and Groudon have both been claimed.\\n",
    "The nightmare dossier will not open until Cresselia has been claimed.\\n",
    "The Phione dossier will not open until Manaphy has been claimed.\\n",
    "Arceus requires Red defeated plus the lake trio and creation trio.\\n",
    "That dossier has already gone quiet.\\n",
    "The dossier seal opens. A presence answers the challenge!\\n",
    "The presence withdraws. The dossier remains active for another attempt.\\n",
    "The Champion Circuit records your victory.\\n",
    "The seal is not ready to open.\\n",
]


def trainer_block(trainer: Trainer) -> str:
    lines = [
        f"    [{trainer.trainer_id}] = {{",
        f'        .name = "{trainer.name}",',
        "        .data = {",
        f"            .trainerType = {TRAINER_TYPE_BOSS},",
        f"            .trainerClass = {trainer.trainer_class},",
        "            .items = { ITEM_FULL_RESTORE, ITEM_FULL_RESTORE, ITEM_FULL_RESTORE, ITEM_FULL_RESTORE },",
        f"            .aiFlags = {AI_CHAMPION},",
        "            .battleType = SINGLE_BATTLE,",
        "        },",
        "        .party = {",
    ]
    for entry in trainer.mons:
        lines.extend(
            [
                "            {",
                f"                .ivs = {entry.ivs},",
                f"                .abilitySlot = {entry.ability_slot},",
                f"                .level = {entry.level},",
                f"                .species = {entry.species},",
                f"                .item = {entry.item},",
                "                .moves = { " + ", ".join(entry.moves) + " },",
                "                .ballSeal = 0,",
                "            },",
            ]
        )
    lines.extend(
        [
            "        },",
            "        .text = {",
            "            {",
            "                .type = TRMSG_LOSE,",
            f'                .text = "{trainer.lose_text}",',
            "            },",
            "        },",
            "    },",
        ]
    )
    return "\n".join(lines)


def remove_marked_block(text: str, start_marker: str, end_marker: str) -> str:
    pattern = re.compile(rf"\n?{re.escape(start_marker)}.*?{re.escape(end_marker)}\n?", re.S)
    return pattern.sub("", text)


def write_trainers() -> None:
    text = TRAINERS.read_text(encoding="utf-8")
    start_marker = "    // Phase 8 Champion Circuit start"
    end_marker = "    // Phase 8 Champion Circuit end"
    text = remove_marked_block(text, start_marker, end_marker)
    for trainer_id in PHASE8_TEXT_ORDER:
        text = re.sub(rf"(?m)^    {trainer_id},\n", "", text)
    block = "\n".join([start_marker, *(trainer_block(trainer) for trainer in CHAMPIONS), end_marker])
    insert_at = text.index("\n};\n\nconst u16 sTrainerTextOrder[]")
    text = text[:insert_at] + "\n\n" + block + text[insert_at:]

    order_marker = "    // Phase 8 Champion Circuit text"
    text = re.sub(rf"\n*{re.escape(order_marker)}\n*", "\n", text)
    order_insert = "\n\n\n" + order_marker + "\n" + "".join(f"    {trainer_id},\n" for trainer_id in PHASE8_TEXT_ORDER)
    order_at = text.index("\n};\n\nconst u32 sTrainerDataCount")
    text = text[:order_at].rstrip() + order_insert + text[order_at:]
    TRAINERS.write_text(text, encoding="utf-8", newline="\n")


def write_flags() -> None:
    text = FLAGS.read_text(encoding="utf-8")
    start_marker = "// Phase 8 legendary caught flags start"
    end_marker = "// Phase 8 legendary caught flags end"
    text = remove_marked_block(text, start_marker, end_marker)
    lines = [start_marker]
    for flag, value in PHASE8_FLAGS.items():
        lines.append(f"{flag:<58} equ {value}")
    lines.append(end_marker)
    insert = "\n".join(lines) + "\n\n"
    text = text.replace("\nNUM_FLAGS", "\n" + insert + "NUM_FLAGS", 1)
    FLAGS.write_text(text, encoding="utf-8", newline="\n")


def transform_base_dojo_rematches() -> str:
    base = BASE_DOJO_SCRIPT.read_text(encoding="utf-8")
    start = base.index("scr_seq_T11R0101_003:")
    end = base.index("scr_seq_T11R0101_000:")
    body = base[start:end]
    trainer_ids = {
        "TRAINER_LEADER_WHITNEY_2": "714",
        "TRAINER_LEADER_JANINE_JANINE_2": "724",
        "TRAINER_LEADER_CLAIR_CLAIR_2": "719",
        "TRAINER_LEADER_ERIKA_ERIKA_2": "723",
        "TRAINER_LEADER_MISTY_MISTY_2": "721",
        "TRAINER_LEADER_BLAINE_BLAINE_2": "726",
        "TRAINER_LEADER_BLUE_BLUE_2": "727",
        "TRAINER_LEADER_CHUCK_CHUCK_2": "718",
        "TRAINER_LEADER_BROCK_BROCK_2": "720",
        "TRAINER_LEADER_BUGSY_BUGSY_2": "713",
        "TRAINER_LEADER_SABRINA_SABRINA_2": "725",
        "TRAINER_LEADER_FALKNER_FALKNER_2": "712",
        "TRAINER_LEADER_LT_SURGE_LT__SURGE_2": "722",
        "TRAINER_LEADER_MORTY_MORTY_2": "715",
        "TRAINER_LEADER_JASMINE_JASMINE_2": "717",
        "TRAINER_LEADER_PRYCE_PRYCE_2": "716",
    }
    object_ids = {
        "obj_T11R0101_gsleader3": "1",
        "obj_T11R0101_gsleader13": "2",
        "obj_T11R0101_gsleader8": "3",
        "obj_T11R0101_gsleader12": "4",
        "obj_T11R0101_gsleader11": "5",
        "obj_T11R0101_gsleader16": "6",
        "obj_T11R0101_gsleader5": "7",
        "obj_T11R0101_gsleader14": "8",
        "obj_T11R0101_gsleader2": "9",
        "obj_T11R0101_gsleader10": "10",
        "obj_T11R0101_gsleader1": "11",
        "obj_T11R0101_gsleader9": "12",
        "obj_T11R0101_gsleader4": "13",
        "obj_T11R0101_gsleader6": "14",
        "obj_T11R0101_gsleader7": "15",
        "obj_T11R0101_gsleader15": "16",
    }
    macros = {
        "GetPhoneBookRematch": "get_phone_book_rematch",
        "Compare": "compare",
        "GoToIfNe": "goto_if_ne",
        "GoToIfEq": "goto_if_eq",
        "GoTo": "goto",
        "SetFlag": "setflag",
        "ClearFlag": "clearflag",
        "End": "end",
        "PlaySE": "play_se",
        "LockAll": "lockall",
        "FacePlayer": "faceplayer",
        "NPCMsg": "npc_msg",
        "CloseMsg": "closemsg",
        "TrainerBattle": "trainer_battle",
        "CheckBattleWon": "check_battle_won",
        "WaitButton": "wait_button",
        "FadeScreen": "fade_screen",
        "WaitFade": "wait_fade",
        "ScrCmd_462": "scrcmd_462",
        "HidePerson": "hide_person",
        "WaitSE": "wait_se",
        "ReleaseAll": "releaseall",
        "WhiteOut": "white_out",
    }
    for old, new in {**trainer_ids, **object_ids}.items():
        body = body.replace(old, new)
    body = re.sub(r"msg_0533_T11R0101_0*(\d+)", lambda m: str(int(m.group(1))), body)
    for old, new in macros.items():
        body = re.sub(rf"\b{re.escape(old)}\b", new, body)
    return body.strip() + "\n"


def menu(label: str, prompt: int, items: list[tuple[int, str]], fallback: str) -> str:
    lines = [
        f"{label}:",
        f"    npc_msg {prompt}",
        "    touchscreen_menu_hide",
        "    menu_init 1, 1, 0, 1, VAR_SPECIAL_RESULT",
    ]
    for value, (msg_id, _target) in enumerate(items):
        lines.append(f"    menu_item_add {msg_id}, 255, {value}")
    lines.extend(["    menu_exec", "    touchscreen_menu_show"])
    for value, (_msg_id, target) in enumerate(items):
        lines.extend([f"    compare VAR_SPECIAL_RESULT, {value}", f"    goto_if_eq {target}"])
    lines.append(f"    goto {fallback}")
    return "\n".join(lines) + "\n"


def champion_battle(label: str, trainer_id: int, require_red: bool = False) -> str:
    lines = [f"{label}:"]
    if require_red:
        lines.append("    goto_if_not_defeated 260, _p8_need_red")
    lines.extend(
        [
            "    closemsg",
            f"    trainer_battle {trainer_id}, 0, 0, 0",
            "    check_battle_won VAR_SPECIAL_RESULT",
            "    compare VAR_SPECIAL_RESULT, 0",
            "    goto_if_eq _p8_whiteout",
            f"    npc_msg {TEXT['CHAMPION_WIN']}",
            "    wait_button",
            "    closemsg",
            "    releaseall",
            "    end",
        ]
    )
    return "\n".join(lines) + "\n"


def encounter_label(event: LegendaryEvent) -> str:
    label = "_p8_" + event.name.lower().replace("-", "_")
    lines = [f"{label}:"]
    lines.extend(f"    {line}" for line in event.prelude)
    lines.extend(
        [
            f"    goto_if_set {event.flag}, _p8_already_caught",
            f"    npc_msg {TEXT['ENCOUNTER_STIRS']}",
            "    wait_button",
            "    closemsg",
            f"    play_cry {event.species}, 0",
            "    wait_cry",
            "    setflag FLAG_ENGAGING_STATIC_POKEMON",
            f"    wild_battle {event.species}, {event.level}, 0",
            "    clearflag FLAG_ENGAGING_STATIC_POKEMON",
            "    check_battle_won VAR_SPECIAL_RESULT",
            "    compare VAR_SPECIAL_RESULT, 0",
            "    goto_if_eq _p8_whiteout",
            "    get_static_encounter_outcome VAR_TEMP_x4002",
            "    compare VAR_TEMP_x4002, 4",
            "    goto_if_ne _p8_not_caught",
            f"    setflag {event.flag}",
        ]
    )
    lines.extend(f"    setflag {flag}" for flag in event.hide_flags)
    lines.extend(["    releaseall", "    end"])
    return "\n".join(lines) + "\n"


def category_items(category: str) -> list[tuple[int, str]]:
    return [(event.menu_text, "_p8_" + event.name.lower().replace("-", "_")) for event in LEGENDARIES if event.category == category]


def generate_dojo_script() -> str:
    header = [
        ".nds",
        ".thumb",
        "",
        '.include "armips/include/scriptmacros.s"',
        '.include "armips/include/flags.s"',
        '.include "armips/include/soundeffects.s"',
        '.include "armips/include/vars.s"',
        '.include "asm/include/species.inc"',
        "",
        ".macro get_static_encounter_outcome,arg0",
        ".halfword 683",
        ".halfword arg0",
        ".endmacro",
        "",
        '.create "build/a012/2_832", 0',
        "",
    ]
    header.extend(f"scrdef scr_seq_T11R0101_{index:03d}" for index in range(20))
    header.extend(["scrdef_end", ""])
    script0 = [
        "scr_seq_T11R0101_000:",
        "    play_se SEQ_SE_DP_SELECT",
        "    lockall",
        "    faceplayer",
        "    count_badges VAR_SPECIAL_RESULT",
        "    compare VAR_SPECIAL_RESULT, 16",
        "    goto_if_lt _p8_need_badges",
    ]
    script0.append(
        menu(
            "_p8_main_menu",
            TEXT["HUB_PROMPT"],
            [
                (TEXT["CHAMPIONS"], "_p8_champions"),
                (TEXT["KANTO_LEGENDS"], "_p8_kanto_legends"),
                (TEXT["ANCIENT_SEALS"], "_p8_ancient_seals"),
                (TEXT["MYTHIC_DOSSIERS"], "_p8_mythic_dossiers"),
                (TEXT["CREATION_ECHOES"], "_p8_creation_echoes"),
                (TEXT["BACK"], "_p8_close"),
            ],
            "_p8_close",
        ).strip()
    )
    menus = [
        menu(
            "_p8_champions",
            TEXT["CHAMPION_PROMPT"],
            [
                (TEXT["LANCE"], "_p8_champion_lance"),
                (TEXT["BLUE"], "_p8_champion_blue"),
                (TEXT["RED"], "_p8_champion_red"),
                (TEXT["STEVEN"], "_p8_champion_steven"),
                (TEXT["WALLACE"], "_p8_champion_wallace"),
                (TEXT["CYNTHIA"], "_p8_champion_cynthia"),
                (TEXT["BACK"], "_p8_main_menu"),
            ],
            "_p8_main_menu",
        ),
        menu("_p8_kanto_legends", TEXT["KANTO_PROMPT"], category_items("kanto") + [(TEXT["BACK"], "_p8_main_menu")], "_p8_main_menu"),
        menu("_p8_ancient_seals", TEXT["ANCIENT_PROMPT"], category_items("ancient") + [(TEXT["BACK"], "_p8_main_menu")], "_p8_main_menu"),
        menu("_p8_mythic_dossiers", TEXT["MYTHIC_PROMPT"], category_items("mythic") + [(TEXT["BACK"], "_p8_main_menu")], "_p8_main_menu"),
        menu("_p8_creation_echoes", TEXT["CREATION_PROMPT"], category_items("creation") + [(TEXT["BACK"], "_p8_main_menu")], "_p8_main_menu"),
    ]
    champions = [
        champion_battle("_p8_champion_lance", 733),
        champion_battle("_p8_champion_blue", 727),
        champion_battle("_p8_champion_red", 260, True),
        champion_battle("_p8_champion_steven", 738, True),
        champion_battle("_p8_champion_wallace", 739, True),
        champion_battle("_p8_champion_cynthia", 740, True),
    ]
    common = [
        "_p8_need_badges:",
        f"    npc_msg {TEXT['NEED_BADGES']}",
        "    wait_button",
        "    closemsg",
        "    releaseall",
        "    end",
        "_p8_need_red:",
        f"    npc_msg {TEXT['NEED_RED']}",
        "    wait_button",
        "    closemsg",
        "    releaseall",
        "    end",
        "_p8_need_regis:",
        f"    npc_msg {TEXT['NEED_REGIS']}",
        "    wait_button",
        "    closemsg",
        "    releaseall",
        "    end",
        "_p8_need_weather:",
        f"    npc_msg {TEXT['NEED_WEATHER']}",
        "    wait_button",
        "    closemsg",
        "    releaseall",
        "    end",
        "_p8_need_cresselia:",
        f"    npc_msg {TEXT['NEED_CRESSELIA']}",
        "    wait_button",
        "    closemsg",
        "    releaseall",
        "    end",
        "_p8_need_manaphy:",
        f"    npc_msg {TEXT['NEED_MANAPHY']}",
        "    wait_button",
        "    closemsg",
        "    releaseall",
        "    end",
        "_p8_need_creation:",
        f"    npc_msg {TEXT['NEED_CREATION']}",
        "    wait_button",
        "    closemsg",
        "    releaseall",
        "    end",
        "_p8_already_caught:",
        f"    npc_msg {TEXT['ALREADY_CAUGHT']}",
        "    wait_button",
        "    closemsg",
        "    releaseall",
        "    end",
        "_p8_not_caught:",
        f"    npc_msg {TEXT['NOT_CAUGHT']}",
        "    wait_button",
        "    closemsg",
        "    releaseall",
        "    end",
        "_p8_close:",
        "    closemsg",
        "    releaseall",
        "    end",
        "_p8_whiteout:",
        "    white_out",
        "    releaseall",
        "    end",
    ]
    signs = [
        "scr_seq_T11R0101_001:",
        "    simple_npc_msg 2",
        "    end",
        "",
        "scr_seq_T11R0101_002:",
        "    simple_npc_msg 3",
        "    end",
    ]
    parts = [
        "\n".join(header),
        transform_base_dojo_rematches(),
        "\n".join(script0),
        *menus,
        *champions,
        *(encounter_label(event) for event in LEGENDARIES),
        "\n".join(common),
        "\n".join(signs),
        "    .align 4\n.close\n",
    ]
    return "\n\n".join(part.strip("\n") for part in parts) + "\n"


def write_dojo_script() -> None:
    DOJO_SCRIPT.write_text(generate_dojo_script(), encoding="utf-8", newline="\n")


def write_dojo_text() -> None:
    DOJO_TEXT.write_text("\n".join(DOJO_TEXT_LINES) + "\n", encoding="utf-8", newline="\n")


def generate_report() -> str:
    lines = [
        "# Phase 8 Postgame Report",
        "",
        "## Kanto Postgame Hub",
        "",
        "- Saffron Fighting Dojo karate master is repurposed after all 16 badges as a postgame hub.",
        "- Existing 16 Gym Leader phone-rematch scripts remain intact and still use the visible leader NPCs.",
        "- Blue remains the late Kanto boss through the existing level 84-90 six-Pokemon rematch and is repeatable from the Champion Circuit.",
        "- Lance and Blue are repeatable from the Champion Circuit after 16 badges; Red rematch and visiting champions unlock after Red is defeated.",
        "",
        "## Legendary And Mythical Availability",
        "",
        "| Pokemon | Location | Level | Prerequisites | Encounter type | Flag |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for native in NATIVE_EVENTS:
        name, kind, level, location, prereq = native
        lines.append(f"| {name} | {location} | {level} | {prereq} | {kind} | native roamer |")
    for event in LEGENDARIES:
        lines.append(
            f"| {event.name} | {event.location} | {event.level} | {event.prerequisites} | {event.encounter_type} | `{event.flag}` |"
        )
    lines.extend(
        [
            "",
            "Failed or fled static dossier battles remain retryable because caught flags are set only when static encounter outcome `4` is returned.",
            "",
            "## Rematches",
            "",
            "- All 16 Gym Leader rematches remain available through the existing Dojo phone-rematch flow, using the Phase 7 six-Pokemon rematch teams.",
            "- Elite Four rematches and Lance rematch remain available through existing League trainer data; Lance is also exposed in the Champion Circuit.",
            "- Champion Circuit repeatable battles: Lance, Blue, Red, Steven, Wallace, Cynthia.",
            "",
            "## Champion Trainers Added",
            "",
            "| Trainer ID | Trainer | Levels | Notes |",
            "| ---: | --- | --- | --- |",
        ]
    )
    for trainer in CHAMPIONS:
        levels = f"{min(mon.level for mon in trainer.mons)}-{max(mon.level for mon in trainer.mons)}"
        lines.append(f"| {trainer.trainer_id} | {trainer.name} | {levels} | Six-Pokemon Champion Circuit team |")
    lines.extend(
        [
            "",
            "## Scope Validation",
            "",
            "- Phase 8 battle and event species are Gen 1-4 only.",
            "- No unrelated Gen 5+ Pokemon are introduced.",
            "- No later-generation legendary forms, regional forms, Megas, Primals, Z-Moves, Dynamax, or Terastal mechanics are used.",
            "",
            "## Files",
            "",
            "- `hg-engine-main/hg-engine-main/armips/scr_seq/scr_seq_00832_phase8_dojo.s`",
            "- `hg-engine-main/hg-engine-main/armips/include/flags.s`",
            "- `hg-engine-main/hg-engine-main/data/Trainers.c`",
            "- `hg-engine-main/hg-engine-main/data/text/533.txt`",
            "- `tools/perfect_johto/phase8_postgame_tools.py`",
            "",
        ]
    )
    return "\n".join(lines)


def write_report() -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(generate_report(), encoding="utf-8", newline="\n")


def constants(path: pathlib.Path, prefix: str) -> set[str]:
    return set(re.findall(rf"\b({prefix}_[A-Z0-9_]+)\b", path.read_text(encoding="utf-8")))


def validate_constants() -> list[str]:
    errors: list[str] = []
    species_constants = constants(ENGINE / "asm" / "include" / "species.inc", "SPECIES")
    move_constants = constants(ENGINE / "asm" / "include" / "moves.inc", "MOVE")
    item_constants = constants(ENGINE / "asm" / "include" / "items.inc", "ITEM")
    flag_text = FLAGS.read_text(encoding="utf-8")
    flag_constants = set(re.findall(r"\b(FLAG_[A-Z0-9_]+)\b", flag_text))
    for trainer in CHAMPIONS:
        for entry in trainer.mons:
            if entry.species not in species_constants:
                errors.append(f"missing species constant {entry.species}")
            if entry.item not in item_constants:
                errors.append(f"missing item constant {entry.item}")
            for move in entry.moves:
                if move not in move_constants:
                    errors.append(f"missing move constant {move}")
    for event in LEGENDARIES:
        if event.species not in species_constants:
            errors.append(f"missing legendary species constant {event.species}")
        if event.flag not in flag_constants and event.flag not in PHASE8_FLAGS:
            errors.append(f"missing caught flag {event.flag}")
        for flag in event.hide_flags:
            if flag not in flag_constants:
                errors.append(f"missing hide flag {flag}")
    return errors


def validate_scope() -> list[str]:
    errors: list[str] = []
    species_values: dict[str, int] = {}
    for match in re.finditer(r"\.equ\s+(SPECIES_[A-Z0-9_]+),\s+([0-9]+)", (ENGINE / "asm" / "include" / "species.inc").read_text(encoding="utf-8")):
        species_values[match.group(1)] = int(match.group(2))
    used = {event.species for event in LEGENDARIES}
    used.update(mon.species for trainer in CHAMPIONS for mon in trainer.mons)
    for species in sorted(used):
        value = species_values.get(species)
        if value is None:
            continue
        if value > 493:
            errors.append(f"Phase 8 uses post-Gen4 species {species} ({value})")
    return errors


def validate_text_indices() -> list[str]:
    errors: list[str] = []
    max_index = max(TEXT.values())
    if len(DOJO_TEXT_LINES) <= max_index:
        errors.append(f"dojo text has {len(DOJO_TEXT_LINES)} lines but needs index {max_index}")
    for index, line in enumerate(DOJO_TEXT_LINES):
        if not line.endswith("\\n"):
            errors.append(f"dojo text line {index} is missing explicit newline escape")
    return errors


def validate_outputs() -> list[str]:
    errors = validate_constants() + validate_scope() + validate_text_indices()
    script = generate_dojo_script()
    for event in LEGENDARIES:
        label = "_p8_" + event.name.lower().replace("-", "_")
        if label not in script:
            errors.append(f"missing script label {label}")
    if len({event.flag for event in LEGENDARIES}) != len([event.flag for event in LEGENDARIES]):
        errors.append("duplicate legendary caught flags in Phase 8 event list")
    return errors


def write_all() -> None:
    write_flags()
    write_trainers()
    write_dojo_script()
    write_dojo_text()
    write_report()


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write Phase 8 generated files")
    args = parser.parse_args(argv)
    if args.write:
        write_all()
    errors = validate_outputs()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Phase 8 postgame data validated.")
    print(f"Legendary/mythical coverage: {len(LEGENDARIES) + len(NATIVE_EVENTS)}")
    print(f"Champion trainers added: {', '.join(str(trainer.trainer_id) for trainer in CHAMPIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
