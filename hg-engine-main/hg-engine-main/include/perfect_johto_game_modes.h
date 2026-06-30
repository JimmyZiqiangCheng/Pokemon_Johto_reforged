#ifndef PERFECT_JOHTO_GAME_MODES_H
#define PERFECT_JOHTO_GAME_MODES_H

#include "types.h"

#define VAR_PERFECT_JOHTO_NUZLOCKE_LEGAL_AREA 0x416D
#define VAR_PERFECT_JOHTO_GAME_MODE           0x416E
#define VAR_PERFECT_JOHTO_LEVEL_CAP           0x416F

#define PERFECT_JOHTO_NUZLOCKE_NO_AREA       0xFFFF
#define PERFECT_JOHTO_NUZLOCKE_MAPSEC_COUNT  235
#define PERFECT_JOHTO_NUZLOCKE_AREA_BYTES    ((PERFECT_JOHTO_NUZLOCKE_MAPSEC_COUNT + 7) / 8)

typedef enum PerfectJohtoGameMode {
    PERFECT_JOHTO_MODE_NORMAL = 0,
    PERFECT_JOHTO_MODE_CHALLENGE = 1,
    PERFECT_JOHTO_MODE_HARDCORE = 2,
    PERFECT_JOHTO_MODE_NUZLOCKE = 3,
} PerfectJohtoGameMode;

struct BattleSystem;
struct BATTLE_PARAM;
struct FieldSystem;
struct SAVE_MISC_DATA;

u16 LONG_CALL PerfectJohto_GetGameMode(void *saveData);
void LONG_CALL PerfectJohto_SetGameMode(void *saveData, u16 mode);
void LONG_CALL PerfectJohto_ResetModeStateForNewGame(void *saveData);
void LONG_CALL PerfectJohto_OakModeMenuShowInitialPage(void *oakSpeechData);
BOOL LONG_CALL PerfectJohto_OakModeMenuApplySelection(void *oakSpeechData);

BOOL LONG_CALL PerfectJohto_ModeHasChallengeRules(void *saveData);
BOOL LONG_CALL PerfectJohto_ModeHasHardcoreDeaths(void *saveData);
BOOL LONG_CALL PerfectJohto_ModeIsNuzlocke(void *saveData);

u32 LONG_CALL PerfectJohto_GetLevelCap(void *saveData);
u32 LONG_CALL PerfectJohto_BattleSystem_GetBattleStyle(struct BattleSystem *battleSystem);
BOOL LONG_CALL PerfectJohto_ModeDisablesBattleItems(void);

void LONG_CALL PerfectJohto_ClearNuzlockeAreas(struct SAVE_MISC_DATA *saveMiscData);
void LONG_CALL PerfectJohto_NuzlockePrepareBattleArea(void *saveData, u16 mapsec);
BOOL LONG_CALL PerfectJohto_NuzlockeCanCatchCurrentBattle(void *saveData, u16 mapsec);
BOOL LONG_CALL PerfectJohto_NuzlockeTryClaimGift(struct FieldSystem *fieldSystem);
BOOL LONG_CALL PerfectJohto_NuzlockeTryClaimGiftForSave(void *saveData);

void LONG_CALL PerfectJohto_ReleaseFaintedBattleParty(struct BattleSystem *battleSystem);

#endif
