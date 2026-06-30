#include "../../include/bag.h"
#include "../../include/battle.h"
#include "../../include/config.h"
#include "../../include/constants/ability.h"
#include "../../include/constants/file.h"
#include "../../include/constants/game.h"
#include "../../include/constants/hold_item_effects.h"
#include "../../include/constants/item.h"
#include "../../include/constants/moves.h"
#include "../../include/constants/species.h"
#include "../../include/constants/weather_numbers.h"
#include "../../include/debug.h"
#include "../../include/perfect_johto_game_modes.h"
#include "../../include/pokemon.h"
#include "../../include/rtc.h"
#include "../../include/save.h"
#include "../../include/script.h"
#include "../../include/trainer_data.h"
#include "../../include/types.h"

#ifdef DEBUG_BATTLE_SCENARIOS
#include "../../include/test_battle.h"
#endif // DEBUG_BATTLE_SCENARIOS

struct BattleSetup LONG_CALL *BattleSetup_New_Tutorial(u32 heapID, FieldSystem *fieldSystem);
int LONG_CALL BattleSetup_GetWildTransitionEffect(struct BattleSetup *setup);
int LONG_CALL BattleSetup_GetWildBattleMusic(struct BattleSetup *setup);
void LONG_CALL *Encounter_New(struct BattleSetup *setup, s32 effect, s32 bgm, u32 *winFlag);

/**
 *  @brief swap two integer values with each other given pointers
 *
 *  @param a first to swap
 *  @param b second to swap
 */
void swap(int *a, int *b)
{
    int temp = *a;
    *a = *b;
    *b = temp;
}

/**
 *  @brief randomize the order of an array size n
 *
 *  @param arr array to randomize
 *  @param n size of array
 */
void randomize(int arr[], int n)
{
    int i;
    for (i = n - 1; i > 0; i--) {
        int j = gf_rand() % (i + 1);
        swap(&arr[i], &arr[j]);
    }
}

extern u32 gLastPokemonLevelForMoneyCalc;

/**
 *  @brief create the trainer Party from the trainer data file and trainer party file
 *
 *  @param bp battle param
 *  @param num trainer index to read from both ARC_TRAINER_DATA and ARC_TRAINER_PARTY_DATA
 *  @param heapID heap to use for memory usage
 */
void MakeTrainerPokemonParty(struct BATTLE_PARAM *bp, int num, int heapID)
{
    u8 *buf;
    int i, j;
    u32 rnd_tmp, rnd, seed_tmp;
    u8 pow;

    seed_tmp = gf_get_seed();

    PokeParty_Init(bp->poke_party[num], 6);

    buf = (u8 *)sys_AllocMemory(heapID, sizeof(struct FULL_TRAINER_MON_DATA_STRUCTURE) * 6);

    TT_TrainerPokeDataGet(bp->trainer_id[num], buf);

    if (TT_TrainerTypeSexGet(bp->trainer_data[num].tr_type) == 1) // if trainer is female
    {
        rnd_tmp = 120;
    } else {
        rnd_tmp = 136;
    }

    u8 pokecount = bp->trainer_data[num].poke_count;
    u8 randomorder_flag = pokecount & TRAINER_DATA_RANDOM_PARTY_ORDER;
    pokecount &= 0x7f;

    // goal:  get rid of massive switch statement with each individual byte.  make the trainer type a bitfield
    u32 id;
    u16 species = 0, adjustedSpecies = 0, item = 0, ability = 0, level = 0, ball = 0, hp = 0, atk = 0, def = 0, speed = 0, spatk = 0, spdef = 0, ab1 = 0, ab2 = 0;
    u16 offset = 0;
    u16 moves[4];
    u8 ivnums[6];
    u8 evnums[6];
    u8 ppcounts[4];
    u16 *nickname = sys_AllocMemory(heapID, 11 * sizeof(u16));
    u8 form_no = 0, abilityslot = 0, nature = 0, ballseal = 0, shinylock = 0, status = 0;
    u32 additionalflags = 0;

    int partyOrder[pokecount];
    if (randomorder_flag) {
        if (gf_rand() % 2 == 0) {
            for (i = 0; i < pokecount; i++) {
                partyOrder[i] = pokecount - 1 - i;
            }
        } else {
            for (i = 0; i < pokecount; i++) {
                partyOrder[i] = i;
            }
        }
    } else {
        for (i = 0; i < pokecount; i++) {
            partyOrder[i] = i;
        }
    }

    if (randomorder_flag && pokecount > 1) {
        int numtimes = gf_rand() % 6 + 1;
        for (i = 0; i < numtimes; i++) {
            randomize(partyOrder, pokecount);
        }
    }

    struct PartyPokemon *mons[pokecount];

    for (i = 0; i < pokecount; i++) {
        mons[i] = AllocMonZeroed(heapID);
        // ivs field
        pow = buf[offset];
        offset++;

        // abilityslot field
        abilityslot = buf[offset];
        offset++;

        // level field
        level = buf[offset] | (buf[offset + 1] << 8);
        gLastPokemonLevelForMoneyCalc = level; // ends up being the last level at the end of the loop that we use for the money calc loop default case
        offset += 2;

        // species field
        species = buf[offset] | (buf[offset + 1] << 8);
        offset += 2;
        form_no = (species & 0xF800) >> 11;
        species &= 0x07FF;

        // item field - conditional
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_ITEMS) {
            item = buf[offset] | (buf[offset + 1] << 8);
            offset += 2;
        }

        // moves field - conditional
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_MOVES) {
            for (j = 0; j < 4; j++) {
                moves[j] = buf[offset] | (buf[offset + 1] << 8);
                offset += 2;
            }
        }

        // ability field
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_ABILITY) {
            ability = buf[offset] | (buf[offset + 1] << 8);
            offset += 2;
        }

        // custom ball field
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_BALL) {
            ball = buf[offset] | (buf[offset + 1] << 8);
            offset += 2;
        }

        // ivs and evs fields
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_IV_EV_SET) {
            for (j = 0; j < 6; j++) {
                ivnums[j] = buf[offset];
                if (ivnums[j] > 31) {
                    ivnums[j] = 31;
                }
                offset++;
            }

            for (j = 0; j < 6; j++) {
                evnums[j] = buf[offset];
                offset++;
            }
        }

        // nature field
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_NATURE_SET) {
            nature = buf[offset];
            offset++;
        }

        // shiny lock field
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_SHINY_LOCK) {
            shinylock = buf[offset];
            offset++;
        }

        // reads extra flags from the trainer pokemon file
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_ADDITIONAL_FLAGS) {
            additionalflags = buf[offset] | (buf[offset + 1] << 8) | (buf[offset + 2] << 16) | (buf[offset + 3] << 24);
            offset += 4;

            // status pre-set field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_STATUS) {
                status = buf[offset] | (buf[offset + 1] << 8) | (buf[offset + 2] << 16) | (buf[offset + 3] << 24);
                offset += 4;
            }

            // custom hp stat field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_HP) {
                hp = buf[offset] | (buf[offset + 1] << 8);
                offset += 2;
            }

            // custom atk stat field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_ATK) {
                atk = buf[offset] | (buf[offset + 1] << 8);
                offset += 2;
            }

            // custom def stat field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_DEF) {
                def = buf[offset] | (buf[offset + 1] << 8);
                offset += 2;
            }

            // custom speed stat field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_SPEED) {
                speed = buf[offset] | (buf[offset + 1] << 8);
                offset += 2;
            }

            // custom spatk stat field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_SP_ATK) {
                spatk = buf[offset] | (buf[offset + 1] << 8);
                offset += 2;
            }

            // custom spdef stat field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_SP_DEF) {
                spdef = buf[offset] | (buf[offset + 1] << 8);
                offset += 2;
            }

            // move PP counts field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_PP_COUNTS) {
                for (j = 0; j < 4; j++) {
                    ppcounts[j] = buf[offset];
                    offset++;
                }
            }

            // nickname field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_NICKNAME) {
                for (j = 0; j < 11; j++) {
                    nickname[j] = buf[offset] | (buf[offset + 1] << 8);
                    offset += 2;
                }
            }
        }

        // ball seal field
        ballseal = buf[offset] | (buf[offset + 1] << 8);
        offset += 2;

        // now set mon data
        try_force_gender_maybe(species, form_no, abilityslot, &rnd_tmp);
        rnd = pow + level + species + bp->trainer_id[num];
        gf_srand(rnd);
        for (j = 0; j < bp->trainer_data[num].tr_type; j++) {
            rnd = gf_rand();
        }
        rnd = (rnd << 8) + rnd_tmp;
        pow = pow * 31 / 255;
        PokeParaSet(mons[i], species, level, pow, 1, rnd, 2, 0);
        SetMonData(mons[i], MON_DATA_FORM, &form_no);

        // set default abilities
        adjustedSpecies = PokeOtherFormMonsNoGet(species, form_no);
        ab1 = PokePersonalParaGet(adjustedSpecies, PERSONAL_ABILITY_1);
        ab2 = PokePersonalParaGet(adjustedSpecies, PERSONAL_ABILITY_2);
        if (ab2 != 0) {
            if (abilityslot & 1 || abilityslot == TRAINER_POKEMON_ABILITY_2) {
                SetMonData(mons[i], MON_DATA_ABILITY, (u16 *)&ab2);
            } else {
                SetMonData(mons[i], MON_DATA_ABILITY, (u16 *)&ab1);
            }
        } else {
            SetMonData(mons[i], MON_DATA_ABILITY, (u16 *)&ab1);
        }

        // if abilityslot is 2 force hidden ability with the bit set.  this specifically to cover darmanitan with zen mode switching between forms and such.
        if (abilityslot == TRAINER_POKEMON_ABILITY_HIDDEN) {
            u16 hiddenability = GetMonHiddenAbility(species, form_no);
            SET_MON_HIDDEN_ABILITY_BIT(mons[i]);
            SetMonData(mons[i], MON_DATA_ABILITY, (u16 *)&hiddenability);
        }

        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_ITEMS) {
            SetMonData(mons[i], MON_DATA_HELD_ITEM, &item);
        }
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_MOVES) {
            for (j = 0; j < 4; j++) {
#ifdef BLOCK_LEARNING_UNIMPLEMENTED_MOVES
                if (IsMoveUnimplemented(moves[j])) {
                    moves[j] = MOVE_NONE;
                }
#endif
                SetPartyPokemonMoveAtPos(mons[i], moves[j], j);
            }
        }
        TrainerCBSet(ballseal, mons[i], heapID);
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_ABILITY) {
            SetMonData(mons[i], MON_DATA_ABILITY, &ability);
        }
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_BALL) {
            SetMonData(mons[i], MON_DATA_POKEBALL, &ball);
        }
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_IV_EV_SET) {
            for (j = 0; j < 6; j++) {
                SetMonData(mons[i], MON_DATA_HP_IV + j, &ivnums[j]);
            }

            for (j = 0; j < 6; j++) {
                SetMonData(mons[i], MON_DATA_HP_EV + j, &evnums[j]);
            }
        }
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_NATURE_SET) {
            u32 pid = GetMonData(mons[i], MON_DATA_PERSONALITY, NULL);
            u8 currentNature = pid % 25;
            pid = pid + nature - currentNature;
            SetMonData(mons[i], MON_DATA_PERSONALITY, &pid);
        }
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_SHINY_LOCK) {
            u32 pid = GetMonData(mons[i], MON_DATA_PERSONALITY, NULL);
            if (shinylock != 0) {
                do {
                    id = (gf_rand() | (gf_rand() << 16));
                } while (!SHINY_CHECK(id, pid));
                SetMonData(mons[i], MON_DATA_OTID, &id);
            }
        }

        ChangeToBattleForm(mons[i]);

        RecalcPartyPokemonStats(mons[i]); // recalculate stats here

        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_ADDITIONAL_FLAGS) {
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_STATUS) {
                SetMonData(mons[i], MON_DATA_STATUS, &status);
            }
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_HP) {
                SetMonData(mons[i], MON_DATA_MAXHP, &hp);
                SetMonData(mons[i], MON_DATA_HP, &hp);
            }
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_ATK) {
                SetMonData(mons[i], MON_DATA_ATTACK, &atk);
            }
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_DEF) {
                SetMonData(mons[i], MON_DATA_DEFENSE, &def);
            }
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_SPEED) {
                SetMonData(mons[i], MON_DATA_SPEED, &speed);
            }
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_SP_ATK) {
                SetMonData(mons[i], MON_DATA_SPECIAL_ATTACK, &spatk);
            }
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_SP_DEF) {
                SetMonData(mons[i], MON_DATA_SPECIAL_DEFENSE, &spdef);
            }
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_PP_COUNTS) {
                for (j = 0; j < 4; j++) {
                    SetMonData(mons[i], MON_DATA_MOVE1PP + j, &ppcounts[j]);
                }
            }
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_NICKNAME) {
                u32 one = 1;

                SetMonData(mons[i], MON_DATA_HAS_NICKNAME, &one);
                SetMonData(mons[i], MON_DATA_NICKNAME, nickname);
            }
        }
        TrainerMonHandleFrustration(mons[i]);
    }

    for (i = 0; i < pokecount; i++) {
        PokeParty_Add(bp->poke_party[num], mons[partyOrder[i]]);
        sys_FreeMemoryEz(mons[i]);
    }

    sys_FreeMemoryEz(buf);
    sys_FreeMemoryEz(nickname);

    gf_srand(seed_tmp);

#ifdef DEBUG_BATTLE_SCENARIOS
    // Override parties with test scenario if enabled
    TestBattle_OverrideParties(bp);
#endif

    // Change battle forms for player party
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 6; j++) {
            struct PartyPokemon *mon = Party_GetMonByIndex(bp->poke_party[i], j);
            if (mon != NULL) {
                ChangeToBattleForm(mon);
                RecalcPartyPokemonStats(mon);
            }
        }
    }
}

extern u32 space_for_setmondata;

typedef struct PerfectJohtoRandomLegendary {
    u16 species;
    u8 minBadges;
    u8 tier;
} PerfectJohtoRandomLegendary;

enum {
    PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_NONE,
    PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER,
    PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_TRUE,
};

#define PERFECT_JOHTO_RANDOM_LEGENDARY_ROLL_DENOMINATOR 1000
#define PERFECT_JOHTO_RANDOM_LEGENDARY_WEAKER_HITS 2
#define PERFECT_JOHTO_RANDOM_LEGENDARY_TRUE_HITS 1

static const PerfectJohtoRandomLegendary sPerfectJohtoRandomLegendaryPool[] = {
    { SPECIES_ARTICUNO, 4, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_ZAPDOS, 4, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_MOLTRES, 4, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_RAIKOU, 4, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_ENTEI, 4, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_SUICUNE, 4, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_REGIROCK, 5, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_REGICE, 5, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_REGISTEEL, 5, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_LATIAS, 5, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_LATIOS, 5, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_UXIE, 5, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_MESPRIT, 5, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_AZELF, 5, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_HEATRAN, 5, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_CRESSELIA, 5, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_MEWTWO, 6, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_TRUE },
    { SPECIES_LUGIA, 6, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_TRUE },
    { SPECIES_HO_OH, 6, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_TRUE },
    { SPECIES_KYOGRE, 6, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_TRUE },
    { SPECIES_GROUDON, 6, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_TRUE },
    { SPECIES_RAYQUAZA, 6, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_TRUE },
    { SPECIES_DIALGA, 6, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_TRUE },
    { SPECIES_PALKIA, 6, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_TRUE },
    { SPECIES_GIRATINA, 6, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_TRUE },
    { SPECIES_REGIGIGAS, 6, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_TRUE },
    { SPECIES_MEW, 16, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_CELEBI, 16, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_JIRACHI, 16, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_DEOXYS, 16, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_PHIONE, 16, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_MANAPHY, 16, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_DARKRAI, 16, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_SHAYMIN, 16, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER },
    { SPECIES_ARCEUS, 16, PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_TRUE },
};

static u8 PerfectJohto_CountBadges(void *saveData)
{
    u8 badgeCount = 0;
    struct PlayerProfile *profile;

    if (saveData == NULL) {
        saveData = SaveBlock2_get();
    }
    if (saveData == NULL) {
        return 0;
    }

    profile = Sav2_PlayerData_GetProfileAddr(saveData);
    for (u8 i = 0; i < 16; i++) {
        if (PlayerProfile_TestBadgeFlag(profile, i) == TRUE) {
            badgeCount++;
        }
    }
    return badgeCount;
}

static u8 PerfectJohto_RandomLegendaryRollTier(u8 badgeCount)
{
    u16 roll;

    if (badgeCount < 4) {
        return PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_NONE;
    }

    roll = gf_rand() % PERFECT_JOHTO_RANDOM_LEGENDARY_ROLL_DENOMINATOR;
    if (roll < PERFECT_JOHTO_RANDOM_LEGENDARY_TRUE_HITS) {
        return PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_TRUE;
    }
    if (roll < PERFECT_JOHTO_RANDOM_LEGENDARY_TRUE_HITS + PERFECT_JOHTO_RANDOM_LEGENDARY_WEAKER_HITS) {
        return PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_WEAKER;
    }
    return PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_NONE;
}

static u8 PerfectJohto_RandomLegendaryLevel(u8 badgeCount, u8 mapLevel)
{
    u8 minLevel;
    u8 maxLevel;
    u8 level = mapLevel + 2 + badgeCount / 4;

    if (badgeCount < 5) {
        minLevel = 25;
        maxLevel = 32;
    } else if (badgeCount < 6) {
        minLevel = 32;
        maxLevel = 38;
    } else if (badgeCount < 8) {
        minLevel = 38;
        maxLevel = 45;
    } else if (badgeCount < 12) {
        minLevel = 45;
        maxLevel = 55;
    } else if (badgeCount < 16) {
        minLevel = 50;
        maxLevel = 60;
    } else {
        minLevel = 55;
        maxLevel = 70;
    }

    if (level < minLevel) {
        return minLevel;
    }
    if (level > maxLevel) {
        return maxLevel;
    }
    return level;
}

static void PerfectJohto_SetRandomLegendaryFleeMove(struct PartyPokemon *mon)
{
    u16 move = MOVE_TELEPORT;
    u8 pp = 20;

    if (mon == NULL) {
        return;
    }

    SetMonData(mon, MON_DATA_MOVE4, &move);
    SetMonData(mon, MON_DATA_MOVE4PP, &pp);
}

enum {
    PERFECT_JOHTO_ABILITY_SLOT_1,
    PERFECT_JOHTO_ABILITY_SLOT_2,
    PERFECT_JOHTO_ABILITY_SLOT_HIDDEN,
};

static void PerfectJohto_SetMonHiddenAbilityBit(struct PartyPokemon *mon, BOOL enabled)
{
    u8 flags = GetMonData(mon, MON_DATA_RESERVED_113, NULL);

    if (enabled == TRUE) {
        flags |= DUMMY_P2_1_HIDDEN_ABILITY_MASK;
    } else {
        flags &= ~DUMMY_P2_1_HIDDEN_ABILITY_MASK;
    }
    SetMonData(mon, MON_DATA_RESERVED_113, &flags);
}

static void PerfectJohto_SetMonSwapAbilitySlotBit(struct PartyPokemon *mon, BOOL enabled)
{
    u16 flags = GetMonData(mon, MON_DATA_RESERVED_114, NULL);

    if (enabled == TRUE) {
        flags |= DUMMY_P2_2_CHANGE_ABILITY_SLOT;
    } else {
        flags &= ~DUMMY_P2_2_CHANGE_ABILITY_SLOT;
    }
    SetMonData(mon, MON_DATA_RESERVED_114, &flags);
}

static void PerfectJohto_SetWildNaturalAbility(struct PartyPokemon *mon)
{
    u8 slots[3];
    u8 slotCount = 0;
    u8 selectedSlot;
    u16 ability;
    u16 species;
    u32 form;
    u32 pid;
    u16 ability1;
    u16 ability2;
    u16 hiddenAbility;

    if (mon == NULL) {
        return;
    }

    species = GetMonData(mon, MON_DATA_SPECIES, NULL);
    if (species == SPECIES_NONE || species == SPECIES_EGG || species == SPECIES_BAD_EGG) {
        return;
    }

    form = GetMonData(mon, MON_DATA_FORM, NULL);
    pid = GetMonData(mon, MON_DATA_PERSONALITY, NULL);
    ability1 = PokeFormNoPersonalParaGet(species, form, PERSONAL_ABILITY_1);
    ability2 = PokeFormNoPersonalParaGet(species, form, PERSONAL_ABILITY_2);
    hiddenAbility = GetMonHiddenAbility(species, form);

    if (ability1 != ABILITY_NONE) {
        slots[slotCount++] = PERFECT_JOHTO_ABILITY_SLOT_1;
    }
    if (ability2 != ABILITY_NONE) {
        slots[slotCount++] = PERFECT_JOHTO_ABILITY_SLOT_2;
    }
    if (hiddenAbility != ABILITY_NONE) {
        slots[slotCount++] = PERFECT_JOHTO_ABILITY_SLOT_HIDDEN;
    }
    if (slotCount == 0) {
        return;
    }

    selectedSlot = slots[gf_rand() % slotCount];
    PerfectJohto_SetMonHiddenAbilityBit(mon, FALSE);

    if (selectedSlot == PERFECT_JOHTO_ABILITY_SLOT_HIDDEN) {
        ability = hiddenAbility;
        PerfectJohto_SetMonSwapAbilitySlotBit(mon, FALSE);
        PerfectJohto_SetMonHiddenAbilityBit(mon, TRUE);
    } else if (selectedSlot == PERFECT_JOHTO_ABILITY_SLOT_2) {
        ability = ability2;
        PerfectJohto_SetMonSwapAbilitySlotBit(mon, (pid & 1) == 0);
    } else {
        ability = ability1;
        PerfectJohto_SetMonSwapAbilitySlotBit(mon, (pid & 1) != 0);
    }

    SetMonData(mon, MON_DATA_ABILITY, &ability);
}

static BOOL PerfectJohto_TryRandomLegendary(
    EncounterInfo *encounterInfo,
    struct PartyPokemon *encounterPartyPokemon,
    struct BATTLE_PARAM *encounterBattleParam)
{
    u8 badgeCount;
    u8 tier;
    u16 candidates[NELEMS(sPerfectJohtoRandomLegendaryPool)];
    u8 candidateCount = 0;
    u16 species;
    u8 level;
    u32 blockedBattleTypes = BATTLE_TYPE_TRAINER
                           | BATTLE_TYPE_SAFARI
                           | BATTLE_TYPE_ROAMER
                           | BATTLE_TYPE_PAL_PARK
                           | BATTLE_TYPE_CATCHING_DEMO
                           | BATTLE_TYPE_BUG_CONTEST;

    if (encounterInfo == NULL || encounterPartyPokemon == NULL || encounterBattleParam == NULL) {
        return FALSE;
    }
    if (encounterInfo->isEgg != 0 || (encounterBattleParam->fight_type & blockedBattleTypes) != 0) {
        return FALSE;
    }

    badgeCount = PerfectJohto_CountBadges(encounterBattleParam->savedata);
    tier = PerfectJohto_RandomLegendaryRollTier(badgeCount);
    if (tier == PERFECT_JOHTO_RANDOM_LEGENDARY_TIER_NONE) {
        return FALSE;
    }

    for (u8 i = 0; i < NELEMS(sPerfectJohtoRandomLegendaryPool); i++) {
        if (
            badgeCount >= sPerfectJohtoRandomLegendaryPool[i].minBadges
            && tier == sPerfectJohtoRandomLegendaryPool[i].tier
        ) {
            candidates[candidateCount++] = sPerfectJohtoRandomLegendaryPool[i].species;
        }
    }
    if (candidateCount == 0) {
        return FALSE;
    }

    species = candidates[gf_rand() % candidateCount];
    level = PerfectJohto_RandomLegendaryLevel(badgeCount, GetMonData(encounterPartyPokemon, MON_DATA_LEVEL, NULL));
    PokeParaSet(encounterPartyPokemon, species, level, 32, FALSE, 0, 0, 0);
    PerfectJohto_SetRandomLegendaryFleeMove(encounterPartyPokemon);
    encounterInfo->level = level;
    space_for_setmondata = 0;
    return TRUE;
}

/**
 *  @brief add a PartyPokemon to the "wild battler"'s party
 *
 *  @param inTarget battler whose party to add to
 *  @param encounterInfo various encounter information structure
 *  @param encounterPartyPokemon PartyPokemon to modify and add
 *  @param encounterBattleParam battle param
 *  @return TRUE if PokeParty_Add was successful
 */
BOOL LONG_CALL AddWildPartyPokemon(int inTarget, EncounterInfo *encounterInfo, struct PartyPokemon *encounterPartyPokemon, struct BATTLE_PARAM *encounterBattleParam)
{
    struct BattleSetup *battleSetup = (struct BattleSetup *)encounterBattleParam;
    int range = 0;
    u8 change_form = 0;
    u8 form_no;
    u16 species;
    BOOL forcedHiddenAbility = FALSE;

    if (encounterInfo->isEgg == 0 && encounterInfo->ability == ABILITY_COMPOUND_EYES) {
        range = 1;
    }

    if (encounterInfo->isEgg == 0 && encounterBattleParam != NULL) {
        PerfectJohto_NuzlockePrepareBattleArea(encounterBattleParam->savedata, battleSetup->mapSection);
    }

    PerfectJohto_TryRandomLegendary(encounterInfo, encounterPartyPokemon, encounterBattleParam);

    species = GetMonData(encounterPartyPokemon, MON_DATA_SPECIES, NULL);

    if (space_for_setmondata != 0) {
        change_form = 1;
        form_no = space_for_setmondata; //(species & 0xF800) >> 11;
        space_for_setmondata = 0;
    }

    WildMonSetRandomHeldItem(encounterPartyPokemon, encounterBattleParam->fight_type, range);

    if (species == SPECIES_UNOWN) {
        change_form = 1;
        form_no = GrabAndRegisterUnownForm(encounterInfo);
    } else if (species == SPECIES_DEERLING || species == SPECIES_SAWSBUCK) {
        UpdatePassiveForms(encounterPartyPokemon);
    }

    if (CheckScriptFlag(HIDDEN_ABILITIES_FLAG) == 1) {
        SET_MON_HIDDEN_ABILITY_BIT(encounterPartyPokemon)
        ClearScriptFlag(HIDDEN_ABILITIES_FLAG);
        ResetPartyPokemonAbility(encounterPartyPokemon);
        forcedHiddenAbility = TRUE;
    }

    if (change_form) {
        SetMonData(encounterPartyPokemon, MON_DATA_FORM, (u8 *)&form_no);
        RecalcPartyPokemonStats(encounterPartyPokemon);
        ResetPartyPokemonAbility(encounterPartyPokemon);
        InitBoxMonMoveset(&encounterPartyPokemon->box);
    }

    if (forcedHiddenAbility == FALSE) {
        PerfectJohto_SetWildNaturalAbility(encounterPartyPokemon);
    }

    ChangeToBattleForm(encounterPartyPokemon);

    return PokeParty_Add(encounterBattleParam->poke_party[inTarget], encounterPartyPokemon);
}

void LONG_CALL SetupAndStartTutorialBattle(TaskManager *taskManager)
{
    struct BattleSetup *setup = BattleSetup_New_Tutorial(11, taskManager->fieldSystem);

    struct PartyPokemon *marill = Party_GetMonByIndex(setup->party[BATTLER_PLAYER], 0);

    // move slot 1 is tackle
    u16 data = MOVE_TACKLE;
    SetMonData(marill, MON_DATA_MOVE1, &data);
    data = GetMoveMaxPP(data, 0);
    SetMonData(marill, MON_DATA_MOVE1PP, &data);
    data = 0;
    SetMonData(marill, MON_DATA_MOVE1PPUP, &data);

    // move slot 2 is tail whip
    data = MOVE_TAIL_WHIP;
    SetMonData(marill, MON_DATA_MOVE2, &data);
    data = GetMoveMaxPP(data, 0);
    SetMonData(marill, MON_DATA_MOVE2PP, &data);
    data = 0;
    SetMonData(marill, MON_DATA_MOVE2PPUP, &data);

    // move slot 3 and 4 none
    data = MOVE_NONE;
    SetMonData(marill, MON_DATA_MOVE3, &data);
    SetMonData(marill, MON_DATA_MOVE4, &data);

    void *encounter = Encounter_New(setup, BattleSetup_GetWildTransitionEffect(setup), BattleSetup_GetWildBattleMusic(setup), NULL);

    TaskManager_Call(taskManager, Task_TutorialBattle, encounter);
}
