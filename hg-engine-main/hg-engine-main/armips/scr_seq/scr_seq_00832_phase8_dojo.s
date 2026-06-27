.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
.include "asm/include/species.inc"

.macro get_static_encounter_outcome,arg0
.halfword 683
.halfword arg0
.endmacro

.create "build/a012/2_832", 0

scrdef scr_seq_T11R0101_000
scrdef scr_seq_T11R0101_001
scrdef scr_seq_T11R0101_002
scrdef scr_seq_T11R0101_003
scrdef scr_seq_T11R0101_004
scrdef scr_seq_T11R0101_005
scrdef scr_seq_T11R0101_006
scrdef scr_seq_T11R0101_007
scrdef scr_seq_T11R0101_008
scrdef scr_seq_T11R0101_009
scrdef scr_seq_T11R0101_010
scrdef scr_seq_T11R0101_011
scrdef scr_seq_T11R0101_012
scrdef scr_seq_T11R0101_013
scrdef scr_seq_T11R0101_014
scrdef scr_seq_T11R0101_015
scrdef scr_seq_T11R0101_016
scrdef scr_seq_T11R0101_017
scrdef scr_seq_T11R0101_018
scrdef scr_seq_T11R0101_019
scrdef_end

scr_seq_T11R0101_003:
	get_phone_book_rematch PHONE_CONTACT_WHITNEY, VAR_TEMP_x4000
	get_phone_book_rematch PHONE_CONTACT_JANINE, VAR_TEMP_x4001
	get_phone_book_rematch PHONE_CONTACT_CLAIR, VAR_TEMP_x4002
	get_phone_book_rematch PHONE_CONTACT_ERIKA, VAR_TEMP_x4003
	get_phone_book_rematch PHONE_CONTACT_MISTY, VAR_TEMP_x4004
	get_phone_book_rematch PHONE_CONTACT_BLAINE, VAR_TEMP_x4005
	get_phone_book_rematch PHONE_CONTACT_BLUE, VAR_TEMP_x4006
	get_phone_book_rematch PHONE_CONTACT_CHUCK, VAR_TEMP_x4007
	get_phone_book_rematch PHONE_CONTACT_BROCK, VAR_TEMP_x4008
	get_phone_book_rematch PHONE_CONTACT_BUGSY, VAR_TEMP_x4009
	get_phone_book_rematch PHONE_CONTACT_SABRINA, VAR_TEMP_x400A
	get_phone_book_rematch PHONE_CONTACT_FALKNER, VAR_TEMP_x400B
	get_phone_book_rematch PHONE_CONTACT_LT__SURGE, VAR_TEMP_x400C
	get_phone_book_rematch PHONE_CONTACT_MORTY, VAR_TEMP_x400D
	get_phone_book_rematch PHONE_CONTACT_JASMINE, VAR_TEMP_x400E
	get_phone_book_rematch PHONE_CONTACT_PRYCE, VAR_TEMP_x400F
	compare VAR_TEMP_x4003, 0
	goto_if_ne _00C9
	setflag FLAG_UNK_2B8
	goto _00CD

_00C9:
	clearflag FLAG_UNK_2B8
_00CD:
	compare VAR_TEMP_x4000, 0
	goto_if_ne _00E4
	setflag FLAG_UNK_2B5
	goto _00E8

_00E4:
	clearflag FLAG_UNK_2B5
_00E8:
	compare VAR_TEMP_x4001, 0
	goto_if_ne _00FF
	setflag FLAG_UNK_2B6
	goto _0103

_00FF:
	clearflag FLAG_UNK_2B6
_0103:
	compare VAR_TEMP_x4002, 0
	goto_if_ne _011A
	setflag FLAG_UNK_2B7
	goto _011E

_011A:
	clearflag FLAG_UNK_2B7
_011E:
	compare VAR_TEMP_x4004, 0
	goto_if_ne _0135
	setflag FLAG_UNK_2B9
	goto _0139

_0135:
	clearflag FLAG_UNK_2B9
_0139:
	compare VAR_TEMP_x4005, 0
	goto_if_ne _0150
	setflag FLAG_UNK_2BA
	goto _0154

_0150:
	clearflag FLAG_UNK_2BA
_0154:
	compare VAR_TEMP_x4006, 0
	goto_if_ne _016B
	setflag FLAG_UNK_2BB
	goto _016F

_016B:
	clearflag FLAG_UNK_2BB
_016F:
	compare VAR_TEMP_x4007, 0
	goto_if_ne _0186
	setflag FLAG_UNK_2BC
	goto _018A

_0186:
	clearflag FLAG_UNK_2BC
_018A:
	compare VAR_TEMP_x4008, 0
	goto_if_ne _01A1
	setflag FLAG_UNK_2BD
	goto _01A5

_01A1:
	clearflag FLAG_UNK_2BD
_01A5:
	compare VAR_TEMP_x4009, 0
	goto_if_ne _01BC
	setflag FLAG_UNK_2BE
	goto _01C0

_01BC:
	clearflag FLAG_UNK_2BE
_01C0:
	compare VAR_TEMP_x400A, 0
	goto_if_ne _01D7
	setflag FLAG_UNK_2BF
	goto _01DB

_01D7:
	clearflag FLAG_UNK_2BF
_01DB:
	compare VAR_TEMP_x400B, 0
	goto_if_ne _01F2
	setflag FLAG_UNK_2C0
	goto _01F6

_01F2:
	clearflag FLAG_UNK_2C0
_01F6:
	compare VAR_TEMP_x400C, 0
	goto_if_ne _020D
	setflag FLAG_UNK_2C1
	goto _0211

_020D:
	clearflag FLAG_UNK_2C1
_0211:
	compare VAR_TEMP_x400D, 0
	goto_if_ne _0228
	setflag FLAG_UNK_2C2
	goto _022C

_0228:
	clearflag FLAG_UNK_2C2
_022C:
	compare VAR_TEMP_x400E, 0
	goto_if_ne _0243
	setflag FLAG_UNK_2C3
	goto _0247

_0243:
	clearflag FLAG_UNK_2C3
_0247:
	compare VAR_TEMP_x400F, 0
	goto_if_ne _025E
	setflag FLAG_UNK_2C4
	goto _0262

_025E:
	clearflag FLAG_UNK_2C4
_0262:
	end

scr_seq_T11R0101_004:
	play_se SEQ_SE_DP_SELECT
	lockall
	faceplayer
	npc_msg 8
	closemsg
	trainer_battle 714, 0, 0, 0
	check_battle_won VAR_SPECIAL_RESULT
	compare VAR_SPECIAL_RESULT, 0
	goto_if_eq _02C1
	npc_msg 9
	wait_button
	closemsg
	fade_screen 6, 1, 0, RGB_BLACK
	wait_fade
	scrcmd_462 17
	setflag FLAG_UNK_2B5
	hide_person 1
	play_se SEQ_SE_DP_KAIDAN2
	wait_se SEQ_SE_DP_KAIDAN2
	fade_screen 6, 1, 1, RGB_BLACK
	wait_fade
	releaseall
	end

_02C1:
	white_out
	releaseall
	end

scr_seq_T11R0101_005:
	play_se SEQ_SE_DP_SELECT
	lockall
	faceplayer
	npc_msg 30
	closemsg
	trainer_battle 724, 0, 0, 0
	check_battle_won VAR_SPECIAL_RESULT
	compare VAR_SPECIAL_RESULT, 0
	goto_if_eq _0324
	npc_msg 31
	wait_button
	closemsg
	fade_screen 6, 1, 0, RGB_BLACK
	wait_fade
	scrcmd_462 26
	setflag FLAG_UNK_2B6
	hide_person 2
	play_se SEQ_SE_DP_KAIDAN2
	wait_se SEQ_SE_DP_KAIDAN2
	fade_screen 6, 1, 1, RGB_BLACK
	wait_fade
	releaseall
	end

_0324:
	white_out
	releaseall
	end

scr_seq_T11R0101_006:
	play_se SEQ_SE_DP_SELECT
	lockall
	faceplayer
	npc_msg 18
	closemsg
	trainer_battle 719, 0, 0, 0
	check_battle_won VAR_SPECIAL_RESULT
	compare VAR_SPECIAL_RESULT, 0
	goto_if_eq _0387
	npc_msg 19
	wait_button
	closemsg
	fade_screen 6, 1, 0, RGB_BLACK
	wait_fade
	scrcmd_462 27
	setflag FLAG_UNK_2B7
	hide_person 3
	play_se SEQ_SE_DP_KAIDAN2
	wait_se SEQ_SE_DP_KAIDAN2
	fade_screen 6, 1, 1, RGB_BLACK
	wait_fade
	releaseall
	end

_0387:
	white_out
	releaseall
	end

scr_seq_T11R0101_007:
	play_se SEQ_SE_DP_SELECT
	lockall
	faceplayer
	npc_msg 24
	closemsg
	trainer_battle 723, 0, 0, 0
	check_battle_won VAR_SPECIAL_RESULT
	compare VAR_SPECIAL_RESULT, 0
	goto_if_eq _03EA
	npc_msg 25
	wait_button
	closemsg
	fade_screen 6, 1, 0, RGB_BLACK
	wait_fade
	scrcmd_462 28
	setflag FLAG_UNK_2B8
	hide_person 4
	play_se SEQ_SE_DP_KAIDAN2
	wait_se SEQ_SE_DP_KAIDAN2
	fade_screen 6, 1, 1, RGB_BLACK
	wait_fade
	releaseall
	end

_03EA:
	white_out
	releaseall
	end

scr_seq_T11R0101_008:
	play_se SEQ_SE_DP_SELECT
	lockall
	faceplayer
	npc_msg 26
	closemsg
	trainer_battle 721, 0, 0, 0
	check_battle_won VAR_SPECIAL_RESULT
	compare VAR_SPECIAL_RESULT, 0
	goto_if_eq _044D
	npc_msg 27
	wait_button
	closemsg
	fade_screen 6, 1, 0, RGB_BLACK
	wait_fade
	scrcmd_462 29
	setflag FLAG_UNK_2B9
	hide_person 5
	play_se SEQ_SE_DP_KAIDAN2
	wait_se SEQ_SE_DP_KAIDAN2
	fade_screen 6, 1, 1, RGB_BLACK
	wait_fade
	releaseall
	end

_044D:
	white_out
	releaseall
	end

scr_seq_T11R0101_009:
	play_se SEQ_SE_DP_SELECT
	lockall
	faceplayer
	npc_msg 32
	closemsg
	trainer_battle 726, 0, 0, 0
	check_battle_won VAR_SPECIAL_RESULT
	compare VAR_SPECIAL_RESULT, 0
	goto_if_eq _04B0
	npc_msg 33
	wait_button
	closemsg
	fade_screen 6, 1, 0, RGB_BLACK
	wait_fade
	scrcmd_462 30
	setflag FLAG_UNK_2BA
	hide_person 115
	play_se SEQ_SE_DP_KAIDAN2
	wait_se SEQ_SE_DP_KAIDAN2
	fade_screen 6, 1, 1, RGB_BLACK
	wait_fade
	releaseall
	end

_04B0:
	white_out
	releaseall
	end

scr_seq_T11R0101_010:
	play_se SEQ_SE_DP_SELECT
	lockall
	faceplayer
	npc_msg 34
	closemsg
	trainer_battle 727, 0, 0, 0
	check_battle_won VAR_SPECIAL_RESULT
	compare VAR_SPECIAL_RESULT, 0
	goto_if_eq _0513
	npc_msg 35
	wait_button
	closemsg
	fade_screen 6, 1, 0, RGB_BLACK
	wait_fade
	scrcmd_462 31
	setflag FLAG_UNK_2BB
	hide_person 6
	play_se SEQ_SE_DP_KAIDAN2
	wait_se SEQ_SE_DP_KAIDAN2
	fade_screen 6, 1, 1, RGB_BLACK
	wait_fade
	releaseall
	end

_0513:
	white_out
	releaseall
	end

scr_seq_T11R0101_011:
	play_se SEQ_SE_DP_SELECT
	lockall
	faceplayer
	npc_msg 10
	closemsg
	trainer_battle 718, 0, 0, 0
	check_battle_won VAR_SPECIAL_RESULT
	compare VAR_SPECIAL_RESULT, 0
	goto_if_eq _0576
	npc_msg 11
	wait_button
	closemsg
	fade_screen 6, 1, 0, RGB_BLACK
	wait_fade
	scrcmd_462 32
	setflag FLAG_UNK_2BC
	hide_person 7
	play_se SEQ_SE_DP_KAIDAN2
	wait_se SEQ_SE_DP_KAIDAN2
	fade_screen 6, 1, 1, RGB_BLACK
	wait_fade
	releaseall
	end

_0576:
	white_out
	releaseall
	end

scr_seq_T11R0101_012:
	play_se SEQ_SE_DP_SELECT
	lockall
	faceplayer
	npc_msg 28
	closemsg
	trainer_battle 720, 0, 0, 0
	check_battle_won VAR_SPECIAL_RESULT
	compare VAR_SPECIAL_RESULT, 0
	goto_if_eq _05D9
	npc_msg 29
	wait_button
	closemsg
	fade_screen 6, 1, 0, RGB_BLACK
	wait_fade
	scrcmd_462 33
	setflag FLAG_UNK_2BD
	hide_person 8
	play_se SEQ_SE_DP_KAIDAN2
	wait_se SEQ_SE_DP_KAIDAN2
	fade_screen 6, 1, 1, RGB_BLACK
	wait_fade
	releaseall
	end

_05D9:
	white_out
	releaseall
	end

scr_seq_T11R0101_013:
	play_se SEQ_SE_DP_SELECT
	lockall
	faceplayer
	npc_msg 6
	closemsg
	trainer_battle 713, 0, 0, 0
	check_battle_won VAR_SPECIAL_RESULT
	compare VAR_SPECIAL_RESULT, 0
	goto_if_eq _063C
	npc_msg 7
	wait_button
	closemsg
	fade_screen 6, 1, 0, RGB_BLACK
	wait_fade
	scrcmd_462 34
	setflag FLAG_UNK_2BE
	hide_person 9
	play_se SEQ_SE_DP_KAIDAN2
	wait_se SEQ_SE_DP_KAIDAN2
	fade_screen 6, 1, 1, RGB_BLACK
	wait_fade
	releaseall
	end

_063C:
	white_out
	releaseall
	end

scr_seq_T11R0101_014:
	play_se SEQ_SE_DP_SELECT
	lockall
	faceplayer
	npc_msg 22
	closemsg
	trainer_battle 725, 0, 0, 0
	check_battle_won VAR_SPECIAL_RESULT
	compare VAR_SPECIAL_RESULT, 0
	goto_if_eq _069F
	npc_msg 23
	wait_button
	closemsg
	fade_screen 6, 1, 0, RGB_BLACK
	wait_fade
	scrcmd_462 35
	setflag FLAG_UNK_2BF
	hide_person 10
	play_se SEQ_SE_DP_KAIDAN2
	wait_se SEQ_SE_DP_KAIDAN2
	fade_screen 6, 1, 1, RGB_BLACK
	wait_fade
	releaseall
	end

_069F:
	white_out
	releaseall
	end

scr_seq_T11R0101_015:
	play_se SEQ_SE_DP_SELECT
	lockall
	faceplayer
	npc_msg 4
	closemsg
	trainer_battle 712, 0, 0, 0
	check_battle_won VAR_SPECIAL_RESULT
	compare VAR_SPECIAL_RESULT, 0
	goto_if_eq _0702
	npc_msg 5
	wait_button
	closemsg
	fade_screen 6, 1, 0, RGB_BLACK
	wait_fade
	scrcmd_462 18
	setflag FLAG_UNK_2C0
	hide_person 11
	play_se SEQ_SE_DP_KAIDAN2
	wait_se SEQ_SE_DP_KAIDAN2
	fade_screen 6, 1, 1, RGB_BLACK
	wait_fade
	releaseall
	end

_0702:
	white_out
	releaseall
	end

scr_seq_T11R0101_016:
	play_se SEQ_SE_DP_SELECT
	lockall
	faceplayer
	npc_msg 20
	closemsg
	trainer_battle 722, 0, 0, 0
	check_battle_won VAR_SPECIAL_RESULT
	compare VAR_SPECIAL_RESULT, 0
	goto_if_eq _0765
	npc_msg 21
	wait_button
	closemsg
	fade_screen 6, 1, 0, RGB_BLACK
	wait_fade
	scrcmd_462 36
	setflag FLAG_UNK_2C1
	hide_person 12
	play_se SEQ_SE_DP_KAIDAN2
	wait_se SEQ_SE_DP_KAIDAN2
	fade_screen 6, 1, 1, RGB_BLACK
	wait_fade
	releaseall
	end

_0765:
	white_out
	releaseall
	end

scr_seq_T11R0101_017:
	play_se SEQ_SE_DP_SELECT
	lockall
	faceplayer
	npc_msg 14
	closemsg
	trainer_battle 715, 0, 0, 0
	check_battle_won VAR_SPECIAL_RESULT
	compare VAR_SPECIAL_RESULT, 0
	goto_if_eq _07C8
	npc_msg 15
	wait_button
	closemsg
	fade_screen 6, 1, 0, RGB_BLACK
	wait_fade
	scrcmd_462 37
	setflag FLAG_UNK_2C2
	hide_person 13
	play_se SEQ_SE_DP_KAIDAN2
	wait_se SEQ_SE_DP_KAIDAN2
	fade_screen 6, 1, 1, RGB_BLACK
	wait_fade
	releaseall
	end

_07C8:
	white_out
	releaseall
	end

scr_seq_T11R0101_018:
	play_se SEQ_SE_DP_SELECT
	lockall
	faceplayer
	npc_msg 12
	closemsg
	trainer_battle 717, 0, 0, 0
	check_battle_won VAR_SPECIAL_RESULT
	compare VAR_SPECIAL_RESULT, 0
	goto_if_eq _082B
	npc_msg 13
	wait_button
	closemsg
	fade_screen 6, 1, 0, RGB_BLACK
	wait_fade
	scrcmd_462 38
	setflag FLAG_UNK_2C3
	hide_person 14
	play_se SEQ_SE_DP_KAIDAN2
	wait_se SEQ_SE_DP_KAIDAN2
	fade_screen 6, 1, 1, RGB_BLACK
	wait_fade
	releaseall
	end

_082B:
	white_out
	releaseall
	end

scr_seq_T11R0101_019:
	play_se SEQ_SE_DP_SELECT
	lockall
	faceplayer
	npc_msg 16
	closemsg
	trainer_battle 716, 0, 0, 0
	check_battle_won VAR_SPECIAL_RESULT
	compare VAR_SPECIAL_RESULT, 0
	goto_if_eq _088E
	npc_msg 17
	wait_button
	closemsg
	fade_screen 6, 1, 0, RGB_BLACK
	wait_fade
	scrcmd_462 39
	setflag FLAG_UNK_2C4
	hide_person 15
	play_se SEQ_SE_DP_KAIDAN2
	wait_se SEQ_SE_DP_KAIDAN2
	fade_screen 6, 1, 1, RGB_BLACK
	wait_fade
	releaseall
	end

_088E:
	white_out
	releaseall
	end

scr_seq_T11R0101_000:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    count_badges VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 16
    goto_if_lt _p8_need_badges
_p8_main_menu:
    npc_msg 37
    touchscreen_menu_hide
    menu_init 1, 1, 0, 1, VAR_SPECIAL_RESULT
    menu_item_add 78, 255, 0
    menu_item_add 79, 255, 1
    menu_item_add 80, 255, 2
    menu_item_add 81, 255, 3
    menu_item_add 82, 255, 4
    menu_item_add 47, 255, 5
    menu_exec
    touchscreen_menu_show
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_champions
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _p8_kanto_legends
    compare VAR_SPECIAL_RESULT, 2
    goto_if_eq _p8_ancient_seals
    compare VAR_SPECIAL_RESULT, 3
    goto_if_eq _p8_mythic_dossiers
    compare VAR_SPECIAL_RESULT, 4
    goto_if_eq _p8_creation_echoes
    compare VAR_SPECIAL_RESULT, 5
    goto_if_eq _p8_close
    goto _p8_close

_p8_champions:
    npc_msg 83
    touchscreen_menu_hide
    menu_init 1, 1, 0, 1, VAR_SPECIAL_RESULT
    menu_item_add 72, 255, 0
    menu_item_add 73, 255, 1
    menu_item_add 74, 255, 2
    menu_item_add 75, 255, 3
    menu_item_add 76, 255, 4
    menu_item_add 77, 255, 5
    menu_item_add 47, 255, 6
    menu_exec
    touchscreen_menu_show
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_champion_lance
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _p8_champion_blue
    compare VAR_SPECIAL_RESULT, 2
    goto_if_eq _p8_champion_red
    compare VAR_SPECIAL_RESULT, 3
    goto_if_eq _p8_champion_steven
    compare VAR_SPECIAL_RESULT, 4
    goto_if_eq _p8_champion_wallace
    compare VAR_SPECIAL_RESULT, 5
    goto_if_eq _p8_champion_cynthia
    compare VAR_SPECIAL_RESULT, 6
    goto_if_eq _p8_main_menu
    goto _p8_main_menu

_p8_kanto_legends:
    npc_msg 84
    touchscreen_menu_hide
    menu_init 1, 1, 0, 1, VAR_SPECIAL_RESULT
    menu_item_add 38, 255, 0
    menu_item_add 39, 255, 1
    menu_item_add 40, 255, 2
    menu_item_add 41, 255, 3
    menu_item_add 42, 255, 4
    menu_item_add 43, 255, 5
    menu_item_add 44, 255, 6
    menu_item_add 45, 255, 7
    menu_item_add 46, 255, 8
    menu_item_add 47, 255, 9
    menu_exec
    touchscreen_menu_show
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_articuno
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _p8_zapdos
    compare VAR_SPECIAL_RESULT, 2
    goto_if_eq _p8_moltres
    compare VAR_SPECIAL_RESULT, 3
    goto_if_eq _p8_mewtwo
    compare VAR_SPECIAL_RESULT, 4
    goto_if_eq _p8_lugia
    compare VAR_SPECIAL_RESULT, 5
    goto_if_eq _p8_ho_oh
    compare VAR_SPECIAL_RESULT, 6
    goto_if_eq _p8_suicune
    compare VAR_SPECIAL_RESULT, 7
    goto_if_eq _p8_latias
    compare VAR_SPECIAL_RESULT, 8
    goto_if_eq _p8_latios
    compare VAR_SPECIAL_RESULT, 9
    goto_if_eq _p8_main_menu
    goto _p8_main_menu

_p8_ancient_seals:
    npc_msg 85
    touchscreen_menu_hide
    menu_init 1, 1, 0, 1, VAR_SPECIAL_RESULT
    menu_item_add 48, 255, 0
    menu_item_add 49, 255, 1
    menu_item_add 50, 255, 2
    menu_item_add 51, 255, 3
    menu_item_add 52, 255, 4
    menu_item_add 53, 255, 5
    menu_item_add 54, 255, 6
    menu_item_add 47, 255, 7
    menu_exec
    touchscreen_menu_show
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_regirock
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _p8_regice
    compare VAR_SPECIAL_RESULT, 2
    goto_if_eq _p8_registeel
    compare VAR_SPECIAL_RESULT, 3
    goto_if_eq _p8_regigigas
    compare VAR_SPECIAL_RESULT, 4
    goto_if_eq _p8_kyogre
    compare VAR_SPECIAL_RESULT, 5
    goto_if_eq _p8_groudon
    compare VAR_SPECIAL_RESULT, 6
    goto_if_eq _p8_rayquaza
    compare VAR_SPECIAL_RESULT, 7
    goto_if_eq _p8_main_menu
    goto _p8_main_menu

_p8_mythic_dossiers:
    npc_msg 86
    touchscreen_menu_hide
    menu_init 1, 1, 0, 1, VAR_SPECIAL_RESULT
    menu_item_add 55, 255, 0
    menu_item_add 56, 255, 1
    menu_item_add 57, 255, 2
    menu_item_add 58, 255, 3
    menu_item_add 59, 255, 4
    menu_item_add 60, 255, 5
    menu_item_add 61, 255, 6
    menu_item_add 62, 255, 7
    menu_item_add 63, 255, 8
    menu_item_add 64, 255, 9
    menu_item_add 47, 255, 10
    menu_exec
    touchscreen_menu_show
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_mew
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _p8_celebi
    compare VAR_SPECIAL_RESULT, 2
    goto_if_eq _p8_jirachi
    compare VAR_SPECIAL_RESULT, 3
    goto_if_eq _p8_deoxys
    compare VAR_SPECIAL_RESULT, 4
    goto_if_eq _p8_heatran
    compare VAR_SPECIAL_RESULT, 5
    goto_if_eq _p8_cresselia
    compare VAR_SPECIAL_RESULT, 6
    goto_if_eq _p8_darkrai
    compare VAR_SPECIAL_RESULT, 7
    goto_if_eq _p8_shaymin
    compare VAR_SPECIAL_RESULT, 8
    goto_if_eq _p8_manaphy
    compare VAR_SPECIAL_RESULT, 9
    goto_if_eq _p8_phione
    compare VAR_SPECIAL_RESULT, 10
    goto_if_eq _p8_main_menu
    goto _p8_main_menu

_p8_creation_echoes:
    npc_msg 87
    touchscreen_menu_hide
    menu_init 1, 1, 0, 1, VAR_SPECIAL_RESULT
    menu_item_add 65, 255, 0
    menu_item_add 66, 255, 1
    menu_item_add 67, 255, 2
    menu_item_add 68, 255, 3
    menu_item_add 69, 255, 4
    menu_item_add 70, 255, 5
    menu_item_add 71, 255, 6
    menu_item_add 47, 255, 7
    menu_exec
    touchscreen_menu_show
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_uxie
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _p8_mesprit
    compare VAR_SPECIAL_RESULT, 2
    goto_if_eq _p8_azelf
    compare VAR_SPECIAL_RESULT, 3
    goto_if_eq _p8_dialga
    compare VAR_SPECIAL_RESULT, 4
    goto_if_eq _p8_palkia
    compare VAR_SPECIAL_RESULT, 5
    goto_if_eq _p8_giratina
    compare VAR_SPECIAL_RESULT, 6
    goto_if_eq _p8_arceus
    compare VAR_SPECIAL_RESULT, 7
    goto_if_eq _p8_main_menu
    goto _p8_main_menu

_p8_champion_lance:
    closemsg
    trainer_battle 733, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    npc_msg 97
    wait_button
    closemsg
    releaseall
    end

_p8_champion_blue:
    closemsg
    trainer_battle 727, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    npc_msg 97
    wait_button
    closemsg
    releaseall
    end

_p8_champion_red:
    goto_if_not_defeated 260, _p8_need_red
    closemsg
    trainer_battle 260, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    npc_msg 97
    wait_button
    closemsg
    releaseall
    end

_p8_champion_steven:
    goto_if_not_defeated 260, _p8_need_red
    closemsg
    trainer_battle 738, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    npc_msg 97
    wait_button
    closemsg
    releaseall
    end

_p8_champion_wallace:
    goto_if_not_defeated 260, _p8_need_red
    closemsg
    trainer_battle 739, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    npc_msg 97
    wait_button
    closemsg
    releaseall
    end

_p8_champion_cynthia:
    goto_if_not_defeated 260, _p8_need_red
    closemsg
    trainer_battle 740, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    npc_msg 97
    wait_button
    closemsg
    releaseall
    end

_p8_articuno:
    goto_if_set FLAG_CAUGHT_ARTICUNO, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_ARTICUNO, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_ARTICUNO, 70, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_CAUGHT_ARTICUNO
    setflag FLAG_HIDE_SEAFOAM_ISLAND_ARTICUNO
    releaseall
    end

_p8_zapdos:
    goto_if_set FLAG_CAUGHT_ZAPDOS, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_ZAPDOS, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_ZAPDOS, 70, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_CAUGHT_ZAPDOS
    setflag FLAG_HIDE_ROUTE_10_ZAPDOS
    releaseall
    end

_p8_moltres:
    goto_if_set FLAG_CAUGHT_MOLTRES, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_MOLTRES, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_MOLTRES, 72, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_CAUGHT_MOLTRES
    setflag FLAG_HIDE_MT_SILVER_CAVE_MOLTRES
    releaseall
    end

_p8_mewtwo:
    goto_if_set FLAG_CAUGHT_MEWTWO, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_MEWTWO, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_MEWTWO, 80, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_CAUGHT_MEWTWO
    setflag FLAG_HIDE_CERULEAN_CAVE_MEWTWO
    releaseall
    end

_p8_lugia:
    goto_if_set FLAG_CAUGHT_LUGIA, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_LUGIA, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_LUGIA, 75, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_CAUGHT_LUGIA
    setflag FLAG_HIDE_WHIRL_ISLAND_LUGIA
    releaseall
    end

_p8_ho_oh:
    goto_if_set FLAG_CAUGHT_HO_OH, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_HO_OH, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_HO_OH, 75, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_CAUGHT_HO_OH
    setflag FLAG_HIDE_BELL_TOWER_HO_OH
    releaseall
    end

_p8_suicune:
    goto_if_set FLAG_CAUGHT_SUICUNE, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_SUICUNE, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_SUICUNE, 65, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_CAUGHT_SUICUNE
    setflag FLAG_HIDE_BURNED_TOWER_B1F_SUICUNE
    setflag FLAG_HIDE_BURNED_TOWER_1F_SUICUNE
    setflag FLAG_HIDE_CIANWOOD_SUICUNE
    setflag FLAG_HIDE_ROUTE_42_SUICUNE
    setflag FLAG_HIDE_VERMILION_SUICUNE
    setflag FLAG_HIDE_ROUTE_14_SUICUNE
    setflag FLAG_HIDE_ROUTE_25_SUICUNE
    setflag FLAG_HIDE_BURNED_TOWER_STATIC_SUICUNE
    releaseall
    end

_p8_latias:
    goto_if_set FLAG_PHASE8_CAUGHT_LATIAS, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_LATIAS, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_LATIAS, 68, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_LATIAS
    setflag FLAG_HIDE_PEWTER_CITY_LATIAS
    releaseall
    end

_p8_latios:
    goto_if_set FLAG_PHASE8_CAUGHT_LATIOS, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_LATIOS, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_LATIOS, 68, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_LATIOS
    setflag FLAG_HIDE_PEWTER_CITY_LATIOS
    releaseall
    end

_p8_regirock:
    goto_if_set FLAG_PHASE8_CAUGHT_REGIROCK, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_REGIROCK, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_REGIROCK, 70, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_REGIROCK
    releaseall
    end

_p8_regice:
    goto_if_set FLAG_PHASE8_CAUGHT_REGICE, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_REGICE, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_REGICE, 70, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_REGICE
    releaseall
    end

_p8_registeel:
    goto_if_set FLAG_PHASE8_CAUGHT_REGISTEEL, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_REGISTEEL, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_REGISTEEL, 70, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_REGISTEEL
    releaseall
    end

_p8_regigigas:
    goto_if_unset FLAG_PHASE8_CAUGHT_REGIROCK, _p8_need_regis
    goto_if_unset FLAG_PHASE8_CAUGHT_REGICE, _p8_need_regis
    goto_if_unset FLAG_PHASE8_CAUGHT_REGISTEEL, _p8_need_regis
    goto_if_set FLAG_PHASE8_CAUGHT_REGIGIGAS, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_REGIGIGAS, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_REGIGIGAS, 80, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_REGIGIGAS
    releaseall
    end

_p8_kyogre:
    goto_if_set FLAG_CAUGHT_KYOGRE, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_KYOGRE, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_KYOGRE, 75, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_CAUGHT_KYOGRE
    setflag FLAG_HIDE_EMBEDDED_TOWER_KYOGRE
    setflag FLAG_HIDE_EMBEDDED_TOWER_KYOGRE_HIKER
    releaseall
    end

_p8_groudon:
    goto_if_set FLAG_CAUGHT_GROUDON, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_GROUDON, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_GROUDON, 75, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_CAUGHT_GROUDON
    setflag FLAG_HIDE_EMBEDDED_TOWER_GROUDON
    setflag FLAG_HIDE_EMBEDDED_TOWER_GROUDON_HIKER
    releaseall
    end

_p8_rayquaza:
    goto_if_unset FLAG_CAUGHT_KYOGRE, _p8_need_weather
    goto_if_unset FLAG_CAUGHT_GROUDON, _p8_need_weather
    goto_if_set FLAG_CAUGHT_RAYQUAZA, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_RAYQUAZA, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_RAYQUAZA, 80, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_CAUGHT_RAYQUAZA
    setflag FLAG_HIDE_EMBEDDED_TOWER_RAYQUAZA
    releaseall
    end

_p8_mew:
    goto_if_set FLAG_PHASE8_CAUGHT_MEW, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_MEW, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_MEW, 70, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_MEW
    releaseall
    end

_p8_celebi:
    goto_if_set FLAG_PHASE8_CAUGHT_CELEBI, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_CELEBI, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_CELEBI, 70, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_CELEBI
    releaseall
    end

_p8_jirachi:
    goto_if_set FLAG_PHASE8_CAUGHT_JIRACHI, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_JIRACHI, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_JIRACHI, 75, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_JIRACHI
    releaseall
    end

_p8_deoxys:
    goto_if_set FLAG_PHASE8_CAUGHT_DEOXYS, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_DEOXYS, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_DEOXYS, 80, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_DEOXYS
    releaseall
    end

_p8_heatran:
    goto_if_set FLAG_PHASE8_CAUGHT_HEATRAN, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_HEATRAN, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_HEATRAN, 78, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_HEATRAN
    releaseall
    end

_p8_cresselia:
    goto_if_set FLAG_PHASE8_CAUGHT_CRESSELIA, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_CRESSELIA, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_CRESSELIA, 78, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_CRESSELIA
    releaseall
    end

_p8_darkrai:
    goto_if_unset FLAG_PHASE8_CAUGHT_CRESSELIA, _p8_need_cresselia
    goto_if_set FLAG_PHASE8_CAUGHT_DARKRAI, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_DARKRAI, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_DARKRAI, 82, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_DARKRAI
    releaseall
    end

_p8_shaymin:
    goto_if_set FLAG_PHASE8_CAUGHT_SHAYMIN, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_SHAYMIN, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_SHAYMIN, 75, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_SHAYMIN
    releaseall
    end

_p8_manaphy:
    goto_if_set FLAG_PHASE8_CAUGHT_MANAPHY, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_MANAPHY, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_MANAPHY, 75, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_MANAPHY
    releaseall
    end

_p8_phione:
    goto_if_unset FLAG_PHASE8_CAUGHT_MANAPHY, _p8_need_manaphy
    goto_if_set FLAG_PHASE8_CAUGHT_PHIONE, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_PHIONE, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_PHIONE, 65, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_PHIONE
    releaseall
    end

_p8_uxie:
    goto_if_set FLAG_PHASE8_CAUGHT_UXIE, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_UXIE, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_UXIE, 72, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_UXIE
    releaseall
    end

_p8_mesprit:
    goto_if_set FLAG_PHASE8_CAUGHT_MESPRIT, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_MESPRIT, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_MESPRIT, 72, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_MESPRIT
    releaseall
    end

_p8_azelf:
    goto_if_set FLAG_PHASE8_CAUGHT_AZELF, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_AZELF, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_AZELF, 72, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_AZELF
    releaseall
    end

_p8_dialga:
    goto_if_set FLAG_PHASE8_CAUGHT_DIALGA, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_DIALGA, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_DIALGA, 82, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_DIALGA
    releaseall
    end

_p8_palkia:
    goto_if_set FLAG_PHASE8_CAUGHT_PALKIA, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_PALKIA, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_PALKIA, 82, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_PALKIA
    releaseall
    end

_p8_giratina:
    goto_if_set FLAG_PHASE8_CAUGHT_GIRATINA, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_GIRATINA, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_GIRATINA, 82, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_GIRATINA
    releaseall
    end

_p8_arceus:
    goto_if_not_defeated 260, _p8_need_red
    goto_if_unset FLAG_PHASE8_CAUGHT_UXIE, _p8_need_creation
    goto_if_unset FLAG_PHASE8_CAUGHT_MESPRIT, _p8_need_creation
    goto_if_unset FLAG_PHASE8_CAUGHT_AZELF, _p8_need_creation
    goto_if_unset FLAG_PHASE8_CAUGHT_DIALGA, _p8_need_creation
    goto_if_unset FLAG_PHASE8_CAUGHT_PALKIA, _p8_need_creation
    goto_if_unset FLAG_PHASE8_CAUGHT_GIRATINA, _p8_need_creation
    goto_if_set FLAG_PHASE8_CAUGHT_ARCEUS, _p8_already_caught
    npc_msg 95
    wait_button
    closemsg
    play_cry SPECIES_ARCEUS, 0
    wait_cry
    setflag FLAG_ENGAGING_STATIC_POKEMON
    wild_battle SPECIES_ARCEUS, 100, 0
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _p8_whiteout
    get_static_encounter_outcome VAR_TEMP_x4002
    compare VAR_TEMP_x4002, 4
    goto_if_ne _p8_not_caught
    setflag FLAG_PHASE8_CAUGHT_ARCEUS
    releaseall
    end

_p8_need_badges:
    npc_msg 36
    wait_button
    closemsg
    releaseall
    end
_p8_need_red:
    npc_msg 88
    wait_button
    closemsg
    releaseall
    end
_p8_need_regis:
    npc_msg 89
    wait_button
    closemsg
    releaseall
    end
_p8_need_weather:
    npc_msg 90
    wait_button
    closemsg
    releaseall
    end
_p8_need_cresselia:
    npc_msg 91
    wait_button
    closemsg
    releaseall
    end
_p8_need_manaphy:
    npc_msg 92
    wait_button
    closemsg
    releaseall
    end
_p8_need_creation:
    npc_msg 93
    wait_button
    closemsg
    releaseall
    end
_p8_already_caught:
    npc_msg 94
    wait_button
    closemsg
    releaseall
    end
_p8_not_caught:
    npc_msg 96
    wait_button
    closemsg
    releaseall
    end
_p8_close:
    closemsg
    releaseall
    end
_p8_whiteout:
    white_out
    releaseall
    end

scr_seq_T11R0101_001:
    simple_npc_msg 2
    end

scr_seq_T11R0101_002:
    simple_npc_msg 3
    end

    .balign 4, 0
.close
