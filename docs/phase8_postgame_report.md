# Phase 8 Postgame Report

## Kanto Postgame Hub

- Saffron Fighting Dojo karate master is repurposed after 8 badges as a postgame hub for early legendary dossiers.
- Existing 16 Gym Leader phone-rematch scripts remain intact and still use the visible leader NPCs.
- Blue remains the late Kanto boss through the level 92-96 six-Pokemon Champion Circuit rematch.
- Champion Circuit, Ancient Seals, Mythic Dossiers, Creation Echoes, and deeper Kanto/Johto legends remain gated at 16 badges.
- Lance and Blue are repeatable from the Champion Circuit after 16 badges; Red rematch and visiting champions unlock after Red is defeated.

## Legendary And Mythical Availability

| Pokemon | Location | Level | Prerequisites | Encounter type | Flag |
| --- | --- | ---: | --- | --- | --- |
| Raikou | Burned Tower release | 40 | Burned Tower event releases the Johto roamer | roaming | native roamer |
| Entei | Burned Tower release | 40 | Burned Tower event releases the Johto roamer | roaming | native roamer |
| Articuno | Seafoam dossier, Saffron Fighting Dojo | 60 | 8 badges | stationary scripted Dojo dossier | `FLAG_CAUGHT_ARTICUNO` |
| Zapdos | Power Plant dossier, Saffron Fighting Dojo | 60 | 8 badges | stationary scripted Dojo dossier | `FLAG_CAUGHT_ZAPDOS` |
| Moltres | Mt. Silver dossier, Saffron Fighting Dojo | 72 | 16 badges | stationary scripted Dojo dossier | `FLAG_CAUGHT_MOLTRES` |
| Mewtwo | Cerulean Cave dossier, Saffron Fighting Dojo | 80 | 16 badges | stationary scripted Dojo dossier | `FLAG_CAUGHT_MEWTWO` |
| Lugia | Whirl Islands dossier, Saffron Fighting Dojo | 75 | 16 badges | stationary scripted Dojo dossier | `FLAG_CAUGHT_LUGIA` |
| Ho-Oh | Bell Tower dossier, Saffron Fighting Dojo | 75 | 16 badges | stationary scripted Dojo dossier | `FLAG_CAUGHT_HO_OH` |
| Suicune | Eusine dossier, Saffron Fighting Dojo | 55 | 8 badges | stationary scripted Dojo dossier | `FLAG_CAUGHT_SUICUNE` |
| Latias | Kanto roaming dossier, Saffron Fighting Dojo | 68 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_LATIAS` |
| Latios | Kanto roaming dossier, Saffron Fighting Dojo | 68 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_LATIOS` |
| Regirock | Ruins of Alph seal dossier, Saffron Fighting Dojo | 70 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_REGIROCK` |
| Regice | Ruins of Alph seal dossier, Saffron Fighting Dojo | 70 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_REGICE` |
| Registeel | Ruins of Alph seal dossier, Saffron Fighting Dojo | 70 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_REGISTEEL` |
| Regigigas | Ruins of Alph seal dossier, Saffron Fighting Dojo | 80 | 16 badges plus Regirock, Regice, and Registeel caught | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_REGIGIGAS` |
| Kyogre | Embedded Tower weather dossier, Saffron Fighting Dojo | 75 | 16 badges | stationary scripted Dojo dossier | `FLAG_CAUGHT_KYOGRE` |
| Groudon | Embedded Tower weather dossier, Saffron Fighting Dojo | 75 | 16 badges | stationary scripted Dojo dossier | `FLAG_CAUGHT_GROUDON` |
| Rayquaza | Embedded Tower sky dossier, Saffron Fighting Dojo | 80 | 16 badges plus Kyogre and Groudon caught | stationary scripted Dojo dossier | `FLAG_CAUGHT_RAYQUAZA` |
| Mew | Faraway dossier, Saffron Fighting Dojo | 70 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_MEW` |
| Celebi | Ilex Shrine dossier, Saffron Fighting Dojo | 70 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_CELEBI` |
| Jirachi | Mt. Moon stargazing dossier, Saffron Fighting Dojo | 75 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_JIRACHI` |
| Deoxys | Pewter meteorite dossier, Saffron Fighting Dojo | 80 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_DEOXYS` |
| Heatran | Volcanic dossier, Saffron Fighting Dojo | 78 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_HEATRAN` |
| Cresselia | Dream dossier, Saffron Fighting Dojo | 78 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_CRESSELIA` |
| Darkrai | Nightmare dossier, Saffron Fighting Dojo | 82 | 16 badges plus Cresselia caught | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_DARKRAI` |
| Shaymin | Flower restoration dossier, Saffron Fighting Dojo | 75 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_SHAYMIN` |
| Manaphy | Ocean egg dossier, Saffron Fighting Dojo | 75 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_MANAPHY` |
| Phione | Ocean egg dossier, Saffron Fighting Dojo | 65 | 16 badges plus Manaphy caught | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_PHIONE` |
| Uxie | Lake insight dossier, Saffron Fighting Dojo | 72 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_UXIE` |
| Mesprit | Lake emotion dossier, Saffron Fighting Dojo | 72 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_MESPRIT` |
| Azelf | Lake willpower dossier, Saffron Fighting Dojo | 72 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_AZELF` |
| Dialga | Sinjoh time dossier, Saffron Fighting Dojo | 82 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_DIALGA` |
| Palkia | Sinjoh space dossier, Saffron Fighting Dojo | 82 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_PALKIA` |
| Giratina | Sinjoh distortion dossier, Saffron Fighting Dojo | 82 | 16 badges | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_GIRATINA` |
| Arceus | Ultimate Sinjoh dossier, Saffron Fighting Dojo | 100 | 16 badges, Red defeated, lake trio caught, and creation trio caught | stationary scripted Dojo dossier | `FLAG_PHASE8_CAUGHT_ARCEUS` |

Failed or fled static dossier battles remain retryable because caught flags are set only when static encounter outcome `4` is returned.

## Rematches

- All 16 Gym Leader rematches remain available through the existing Dojo phone-rematch flow, using the Phase 7 six-Pokemon rematch teams.
- Elite Four rematches and Lance rematch remain available through existing League trainer data; Lance is also exposed in the Champion Circuit.
- Champion Circuit repeatable battles: Lance, Blue, Red, Steven, Wallace, Cynthia.

## Champion Trainers Added

| Trainer ID | Trainer | Levels | Notes |
| ---: | --- | --- | --- |
| 738 | Steven | 92-96 | Six-Pokemon Champion Circuit team |
| 739 | Wallace | 92-96 | Six-Pokemon Champion Circuit team |
| 740 | Cynthia | 92-96 | Six-Pokemon Champion Circuit team |

## Scope Validation

- Phase 8 battle and event species are Gen 1-4 only.
- No unrelated Gen 5+ Pokemon are introduced.
- No later-generation legendary forms, regional forms, Megas, Primals, Z-Moves, Dynamax, or Terastal mechanics are used.

## Files

- `hg-engine-main/hg-engine-main/armips/scr_seq/scr_seq_00832_phase8_dojo.s`
- `hg-engine-main/hg-engine-main/armips/include/flags.s`
- `hg-engine-main/hg-engine-main/data/Trainers.c`
- `hg-engine-main/hg-engine-main/data/text/533.txt`
- `tools/perfect_johto/phase8_postgame_tools.py`
