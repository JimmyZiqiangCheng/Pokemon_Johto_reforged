#include "../include/perfect_johto_game_modes.h"

#include "../include/battle.h"
#include "../include/npc_trade.h"
#include "../include/pokemon.h"
#include "../include/save.h"
#include "../include/script.h"

enum PerfectJohtoBadge {
    PERFECT_JOHTO_BADGE_ZEPHYR = 0,
    PERFECT_JOHTO_BADGE_HIVE,
    PERFECT_JOHTO_BADGE_PLAIN,
    PERFECT_JOHTO_BADGE_FOG,
    PERFECT_JOHTO_BADGE_STORM,
    PERFECT_JOHTO_BADGE_MINERAL,
    PERFECT_JOHTO_BADGE_GLACIER,
    PERFECT_JOHTO_BADGE_RISING,
    PERFECT_JOHTO_BADGE_BOULDER,
    PERFECT_JOHTO_BADGE_CASCADE,
    PERFECT_JOHTO_BADGE_THUNDER,
    PERFECT_JOHTO_BADGE_RAINBOW,
    PERFECT_JOHTO_BADGE_SOUL,
    PERFECT_JOHTO_BADGE_MARSH,
    PERFECT_JOHTO_BADGE_VOLCANO,
    PERFECT_JOHTO_BADGE_EARTH,
};

#define OAK_SPEECH_SAVE_DATA_OFFSET                0x04
#define OAK_SPEECH_MENU_DATA_OFFSET                0x160
#define OAK_SPEECH_MENU_NUM_OPTIONS_OFFSET         (OAK_SPEECH_MENU_DATA_OFFSET + 1)
#define OAK_SPEECH_MENU_IN_PAD_MODE_OFFSET         (OAK_SPEECH_MENU_DATA_OFFSET + 2)
#define OAK_SPEECH_MENU_CURSOR_POS_OFFSET          (OAK_SPEECH_MENU_DATA_OFFSET + 3)
#define OAK_SPEECH_MENU_FLASH_DELAY_OFFSET         (OAK_SPEECH_MENU_DATA_OFFSET + 4)
#define OAK_SPEECH_MENU_FLASH_FRAMES_PER_OFFSET    (OAK_SPEECH_MENU_DATA_OFFSET + 5)
#define OAK_SPEECH_MENU_PRESS_DELAY_OFFSET         (OAK_SPEECH_MENU_DATA_OFFSET + 6)
#define OAK_SPEECH_MENU_FLASH_STATE_OFFSET         (OAK_SPEECH_MENU_DATA_OFFSET + 7)

#define OAK_SPEECH_MSG_NORMAL      44
#define OAK_SPEECH_MSG_CHALLENGE   45
#define OAK_SPEECH_MSG_MORE        46
#define OAK_SPEECH_MSG_HARDCORE    49
#define OAK_SPEECH_MSG_NUZLOCKE    50
#define OAK_SPEECH_MSG_BACK        51

#define OAK_SPEECH_BG_SUB_1        5
#define OAK_SPEECH_TOGGLE_OFF      0

typedef void (*OakSpeechPrintMultichoiceMenu)(void *oakSpeechData, int msg1, int msg2, int msg3, int numChoices);
typedef void (*OakSpeechFreeWindows)(void *oakSpeechData);
typedef void (*OakSpeechToggleBgLayer)(int bgLayer, int toggle);

static u8 sPerfectJohtoOakModeMenuPage;

static u16 PerfectJohto_SanitizeMode(u16 mode)
{
    if (mode > PERFECT_JOHTO_MODE_NUZLOCKE) {
        return PERFECT_JOHTO_MODE_NORMAL;
    }
    return mode;
}

static u16 PerfectJohto_GetVar(void *saveData, u16 varId)
{
    if (saveData == NULL) {
        return 0;
    }
    return GetScriptVarPassSave(SavArray_Flags_get(saveData), varId);
}

static void PerfectJohto_SetVar(void *saveData, u16 varId, u16 value)
{
    if (saveData == NULL) {
        return;
    }
    SetScriptVarPassSave(SavArray_Flags_get(saveData), varId, value);
}

static BOOL PerfectJohto_HasBadge(struct PlayerProfile *profile, enum PerfectJohtoBadge badge)
{
    return PlayerProfile_TestBadgeFlag(profile, badge) == TRUE;
}

static u16 PerfectJohto_GetCurrentMapSection(struct FieldSystem *fieldSystem)
{
    if (fieldSystem == NULL || fieldSystem->location == NULL) {
        return PERFECT_JOHTO_NUZLOCKE_NO_AREA;
    }
    return MapHeader_GetMapSec(fieldSystem->location->mapId);
}

static BOOL PerfectJohto_NuzlockeAreaClaimed(void *saveData, u16 mapsec)
{
    struct SAVE_MISC_DATA *saveMiscData;

    if (saveData == NULL || mapsec >= PERFECT_JOHTO_NUZLOCKE_MAPSEC_COUNT) {
        return TRUE;
    }

    saveMiscData = Sav2_Misc_get(saveData);
    return (saveMiscData->perfectJohtoNuzlockeAreas[mapsec / 8] & (1 << (mapsec & 7))) != 0;
}

static void PerfectJohto_NuzlockeClaimArea(void *saveData, u16 mapsec)
{
    struct SAVE_MISC_DATA *saveMiscData;

    if (saveData == NULL || mapsec >= PERFECT_JOHTO_NUZLOCKE_MAPSEC_COUNT) {
        return;
    }

    saveMiscData = Sav2_Misc_get(saveData);
    saveMiscData->perfectJohtoNuzlockeAreas[mapsec / 8] |= (1 << (mapsec & 7));
}

static u32 PerfectJohto_CountPartyNonEggMons(struct Party *party)
{
    u32 count = 0;

    if (party == NULL) {
        return 0;
    }

    for (s32 i = 0; i < party->count; i++) {
        struct PartyPokemon *mon = Party_GetMonByIndex(party, i);
        if (GetMonData(mon, MON_DATA_SPECIES_EXISTS, NULL) && !GetMonData(mon, MON_DATA_IS_EGG, NULL)) {
            count++;
        }
    }

    return count;
}

static void *PerfectJohto_OakModeMenuGetSaveData(void *oakSpeechData)
{
    if (oakSpeechData == NULL) {
        return NULL;
    }
    return *(void **)((u8 *)oakSpeechData + OAK_SPEECH_SAVE_DATA_OFFSET);
}

static void PerfectJohto_OakModeMenuResetInput(void *oakSpeechData)
{
    u8 *data = oakSpeechData;

    data[OAK_SPEECH_MENU_NUM_OPTIONS_OFFSET] = 3;
    data[OAK_SPEECH_MENU_IN_PAD_MODE_OFFSET] = 0;
    data[OAK_SPEECH_MENU_CURSOR_POS_OFFSET] = 0;
    data[OAK_SPEECH_MENU_FLASH_DELAY_OFFSET] = 0;
    data[OAK_SPEECH_MENU_FLASH_FRAMES_PER_OFFSET] = 16;
    data[OAK_SPEECH_MENU_PRESS_DELAY_OFFSET] = 0;
    data[OAK_SPEECH_MENU_FLASH_STATE_OFFSET] = 0;
}

static void PerfectJohto_OakModeMenuShowPageInternal(void *oakSpeechData, u8 page, BOOL freeExistingWindows)
{
    OakSpeechFreeWindows freeWindows = (OakSpeechFreeWindows)(0x021E65B4 | 1);
    OakSpeechPrintMultichoiceMenu printMenu = (OakSpeechPrintMultichoiceMenu)(0x021E64C4 | 1);
    OakSpeechToggleBgLayer toggleBgLayer = (OakSpeechToggleBgLayer)(0x0201BC28 | 1);

    if (oakSpeechData == NULL) {
        return;
    }

    sPerfectJohtoOakModeMenuPage = page;
    if (freeExistingWindows) {
        freeWindows(oakSpeechData);
    }

    if (page == 0) {
        printMenu(oakSpeechData, OAK_SPEECH_MSG_NORMAL, OAK_SPEECH_MSG_CHALLENGE, OAK_SPEECH_MSG_MORE, 3);
    } else {
        printMenu(oakSpeechData, OAK_SPEECH_MSG_HARDCORE, OAK_SPEECH_MSG_NUZLOCKE, OAK_SPEECH_MSG_BACK, 3);
    }

    toggleBgLayer(OAK_SPEECH_BG_SUB_1, OAK_SPEECH_TOGGLE_OFF);
    PerfectJohto_OakModeMenuResetInput(oakSpeechData);
}

static void PerfectJohto_OakModeMenuShowPage(void *oakSpeechData, u8 page)
{
    PerfectJohto_OakModeMenuShowPageInternal(oakSpeechData, page, TRUE);
}

u16 LONG_CALL PerfectJohto_GetGameMode(void *saveData)
{
    return PerfectJohto_SanitizeMode(PerfectJohto_GetVar(saveData, VAR_PERFECT_JOHTO_GAME_MODE));
}

void LONG_CALL PerfectJohto_SetGameMode(void *saveData, u16 mode)
{
    PerfectJohto_SetVar(saveData, VAR_PERFECT_JOHTO_GAME_MODE, PerfectJohto_SanitizeMode(mode));
    PerfectJohto_SetVar(saveData, VAR_PERFECT_JOHTO_NUZLOCKE_LEGAL_AREA, PERFECT_JOHTO_NUZLOCKE_NO_AREA);
    PerfectJohto_SetVar(saveData, VAR_PERFECT_JOHTO_LEVEL_CAP, PerfectJohto_GetLevelCap(saveData));
}

void LONG_CALL PerfectJohto_ResetModeStateForNewGame(void *saveData)
{
    PerfectJohto_SetVar(saveData, VAR_PERFECT_JOHTO_GAME_MODE, PERFECT_JOHTO_MODE_NORMAL);
    PerfectJohto_SetVar(saveData, VAR_PERFECT_JOHTO_NUZLOCKE_LEGAL_AREA, PERFECT_JOHTO_NUZLOCKE_NO_AREA);
    PerfectJohto_SetVar(saveData, VAR_PERFECT_JOHTO_LEVEL_CAP, 100);

    if (saveData != NULL) {
        PerfectJohto_ClearNuzlockeAreas(Sav2_Misc_get(saveData));
    }
}

void LONG_CALL PerfectJohto_OakModeMenuShowInitialPage(void *oakSpeechData)
{
    PerfectJohto_OakModeMenuShowPageInternal(oakSpeechData, 0, FALSE);
}

BOOL LONG_CALL PerfectJohto_OakModeMenuApplySelection(void *oakSpeechData)
{
    u8 selected;
    u16 mode;
    void *saveData;

    if (oakSpeechData == NULL) {
        return FALSE;
    }

    selected = *((u8 *)oakSpeechData + OAK_SPEECH_MENU_CURSOR_POS_OFFSET);

    if (sPerfectJohtoOakModeMenuPage == 0) {
        if (selected == 2) {
            PerfectJohto_OakModeMenuShowPage(oakSpeechData, 1);
            return FALSE;
        }
        mode = selected == 1 ? PERFECT_JOHTO_MODE_CHALLENGE : PERFECT_JOHTO_MODE_NORMAL;
    } else {
        if (selected == 2) {
            PerfectJohto_OakModeMenuShowPage(oakSpeechData, 0);
            return FALSE;
        }
        mode = selected == 1 ? PERFECT_JOHTO_MODE_NUZLOCKE : PERFECT_JOHTO_MODE_HARDCORE;
    }

    saveData = PerfectJohto_OakModeMenuGetSaveData(oakSpeechData);
    PerfectJohto_ResetModeStateForNewGame(saveData);
    PerfectJohto_SetGameMode(saveData, mode);
    sPerfectJohtoOakModeMenuPage = 0;

    *((u8 *)oakSpeechData + OAK_SPEECH_MENU_CURSOR_POS_OFFSET) = 2;
    return TRUE;
}

BOOL LONG_CALL PerfectJohto_ModeHasChallengeRules(void *saveData)
{
    return PerfectJohto_GetGameMode(saveData) >= PERFECT_JOHTO_MODE_CHALLENGE;
}

BOOL LONG_CALL PerfectJohto_ModeHasHardcoreDeaths(void *saveData)
{
    return PerfectJohto_GetGameMode(saveData) >= PERFECT_JOHTO_MODE_HARDCORE;
}

BOOL LONG_CALL PerfectJohto_ModeIsNuzlocke(void *saveData)
{
    return PerfectJohto_GetGameMode(saveData) == PERFECT_JOHTO_MODE_NUZLOCKE;
}

u32 LONG_CALL PerfectJohto_GetLevelCap(void *saveData)
{
    struct PlayerProfile *profile;

    if (!PerfectJohto_ModeHasChallengeRules(saveData)) {
        return 100;
    }

    profile = Sav2_PlayerData_GetProfileAddr(saveData);

    if (!PerfectJohto_HasBadge(profile, PERFECT_JOHTO_BADGE_ZEPHYR)) {
        return 16;
    }
    if (!PerfectJohto_HasBadge(profile, PERFECT_JOHTO_BADGE_HIVE)) {
        return 22;
    }
    if (!PerfectJohto_HasBadge(profile, PERFECT_JOHTO_BADGE_PLAIN)) {
        return 27;
    }
    if (!PerfectJohto_HasBadge(profile, PERFECT_JOHTO_BADGE_FOG)) {
        return 33;
    }
    if (!PerfectJohto_HasBadge(profile, PERFECT_JOHTO_BADGE_STORM)
     || !PerfectJohto_HasBadge(profile, PERFECT_JOHTO_BADGE_MINERAL)
     || !PerfectJohto_HasBadge(profile, PERFECT_JOHTO_BADGE_GLACIER)) {
        return 45;
    }
    if (!PerfectJohto_HasBadge(profile, PERFECT_JOHTO_BADGE_RISING)) {
        return 52;
    }

    if (!profile->gameClear) {
        return 62;
    }

    if (!PerfectJohto_HasBadge(profile, PERFECT_JOHTO_BADGE_THUNDER)) {
        return 65;
    }
    if (!PerfectJohto_HasBadge(profile, PERFECT_JOHTO_BADGE_BOULDER)) {
        return 66;
    }
    if (!PerfectJohto_HasBadge(profile, PERFECT_JOHTO_BADGE_SOUL)) {
        return 66;
    }
    if (!PerfectJohto_HasBadge(profile, PERFECT_JOHTO_BADGE_CASCADE)) {
        return 68;
    }
    if (!PerfectJohto_HasBadge(profile, PERFECT_JOHTO_BADGE_RAINBOW)) {
        return 70;
    }
    if (!PerfectJohto_HasBadge(profile, PERFECT_JOHTO_BADGE_MARSH)) {
        return 74;
    }
    if (!PerfectJohto_HasBadge(profile, PERFECT_JOHTO_BADGE_VOLCANO)) {
        return 78;
    }
    if (!PerfectJohto_HasBadge(profile, PERFECT_JOHTO_BADGE_EARTH)) {
        return 84;
    }

    return 98;
}

u32 LONG_CALL PerfectJohto_BattleSystem_GetBattleStyle(struct BattleSystem *battleSystem)
{
    if (PerfectJohto_ModeHasChallengeRules(SaveBlock2_get())) {
        return 1;
    }
    if (battleSystem != NULL && battleSystem->options != NULL) {
        return battleSystem->options->battleStyle;
    }
    return 0;
}

BOOL LONG_CALL PerfectJohto_ModeDisablesBattleItems(void)
{
    return PerfectJohto_ModeHasChallengeRules(SaveBlock2_get());
}

void LONG_CALL PerfectJohto_ClearNuzlockeAreas(struct SAVE_MISC_DATA *saveMiscData)
{
    if (saveMiscData == NULL) {
        return;
    }
    memset(saveMiscData->perfectJohtoNuzlockeAreas, 0, PERFECT_JOHTO_NUZLOCKE_AREA_BYTES);
}

void LONG_CALL PerfectJohto_NuzlockePrepareBattleArea(void *saveData, u16 mapsec)
{
    u16 currentLegalArea;

    if (!PerfectJohto_ModeIsNuzlocke(saveData)) {
        return;
    }

    currentLegalArea = PerfectJohto_GetVar(saveData, VAR_PERFECT_JOHTO_NUZLOCKE_LEGAL_AREA);
    if (currentLegalArea == mapsec) {
        return;
    }

    if (mapsec >= PERFECT_JOHTO_NUZLOCKE_MAPSEC_COUNT || PerfectJohto_NuzlockeAreaClaimed(saveData, mapsec)) {
        PerfectJohto_SetVar(saveData, VAR_PERFECT_JOHTO_NUZLOCKE_LEGAL_AREA, PERFECT_JOHTO_NUZLOCKE_NO_AREA);
        return;
    }

    PerfectJohto_NuzlockeClaimArea(saveData, mapsec);
    PerfectJohto_SetVar(saveData, VAR_PERFECT_JOHTO_NUZLOCKE_LEGAL_AREA, mapsec);
}

BOOL LONG_CALL PerfectJohto_NuzlockeCanCatchCurrentBattle(void *saveData, u16 mapsec)
{
    if (!PerfectJohto_ModeIsNuzlocke(saveData)) {
        return TRUE;
    }
    return PerfectJohto_GetVar(saveData, VAR_PERFECT_JOHTO_NUZLOCKE_LEGAL_AREA) == mapsec;
}

BOOL LONG_CALL PerfectJohto_NuzlockeTryClaimGift(struct FieldSystem *fieldSystem)
{
    void *saveData;
    u16 mapsec;

    if (fieldSystem == NULL) {
        return TRUE;
    }

    saveData = fieldSystem->savedata;
    if (!PerfectJohto_ModeIsNuzlocke(saveData)) {
        return TRUE;
    }

    mapsec = PerfectJohto_GetCurrentMapSection(fieldSystem);
    if (mapsec >= PERFECT_JOHTO_NUZLOCKE_MAPSEC_COUNT || PerfectJohto_NuzlockeAreaClaimed(saveData, mapsec)) {
        return FALSE;
    }

    PerfectJohto_NuzlockeClaimArea(saveData, mapsec);
    return TRUE;
}

BOOL LONG_CALL PerfectJohto_NuzlockeTryClaimGiftForSave(void *saveData)
{
    if (gFieldSysPtr != NULL && gFieldSysPtr->savedata == saveData) {
        return PerfectJohto_NuzlockeTryClaimGift(gFieldSysPtr);
    }
    return TRUE;
}

void LONG_CALL PerfectJohto_ReleaseFaintedBattleParty(struct BattleSystem *battleSystem)
{
    struct Party *party;
    u32 nonEggCount;
    void *saveData = SaveBlock2_get();

    if (PerfectJohto_ModeIsNuzlocke(saveData)) {
        PerfectJohto_SetVar(saveData, VAR_PERFECT_JOHTO_NUZLOCKE_LEGAL_AREA, PERFECT_JOHTO_NUZLOCKE_NO_AREA);
    }

    if (battleSystem == NULL || !PerfectJohto_ModeHasHardcoreDeaths(saveData)) {
        return;
    }
    if (BattleTypeGet(battleSystem) & (BATTLE_TYPE_WIRELESS | BATTLE_TYPE_BATTLE_TOWER | BATTLE_TYPE_PAL_PARK | BATTLE_TYPE_CATCHING_DEMO)) {
        return;
    }

    party = battleSystem->trainerParty[0];
    if (party == NULL) {
        return;
    }

    nonEggCount = PerfectJohto_CountPartyNonEggMons(party);
    if (nonEggCount <= 1) {
        return;
    }

    for (s32 i = party->count - 1; i >= 0 && nonEggCount > 1; i--) {
        struct PartyPokemon *mon = Party_GetMonByIndex(party, i);
        if (!GetMonData(mon, MON_DATA_SPECIES_EXISTS, NULL) || GetMonData(mon, MON_DATA_IS_EGG, NULL)) {
            continue;
        }
        if (GetMonData(mon, MON_DATA_HP, NULL) == 0) {
            PokeParty_Delete(party, i);
            nonEggCount--;
        }
    }
}
