"""Temp file used for testing new logic system."""
import json
import os
import random
import unittest

from parameterized import parameterized_class

# from randomizer.Enums.Items import Items
from randomizer.Enums.HintType import HintType
import randomizer.Lists.Exceptions as Ex
from randomizer.Enums.Settings import (ActivateAllBananaports, BananaportRando,
                                       CrownEnemyRando, DamageAmount,
                                       ExtraCutsceneSkips, FillAlgorithm,
                                       FreeTradeSetting, HelmDoorItem,
                                       HelmSetting, KasplatRandoSetting,
                                       KrushaUi, LevelRandomization, LogicType,
                                       MicrohintsEnabled, MoveRando,
                                       RandomPrices, SettingsMap,
                                       ShockwaveStatus, SpoilerHints,
                                       TrainingBarrels, WinCondition,
                                       WrinklyHints)
from randomizer.Fill import Generate_Spoiler
from randomizer.Settings import Settings
from randomizer.SettingStrings import decrypt_settings_string_enum
from randomizer.Spoiler import Spoiler

# Get the preset_files.json file from static/presets
with open("static/presets/preset_files.json", "r") as file:
    preset_files = json.load(file)
    # For each preset in the list if settings_string is not None, add the preset to the list
    valid_presets = [(preset.get("name"), preset.get("settings_string")) for preset in preset_files if preset.get("settings_string")]

# Add a custom preset for testing
# If we're not running on github actions, add the custom preset
if not os.environ.get("GITHUB_ACTIONS"):
    valid_presets.append(("Custom", "bKEFCSKzzecrKEDRAejpFjAIbiDLWIQXr5/ANnj4YTRzu6leyszOKbOrYvhTgfVA8IhkQlS2Nc+EZU8Ro9dpcviFOWJtOCFAB2j0gOitNXwFILdT1+BJAMmihlEjILrJZYKAugBBgJ1AQOBuwDCAR3AgSCvAFCgZ5AwWDvQHDAhQhpk9shSPUTzORKRcklWi3gZwdHqLcFP0VEWARMRQBXrXHI3ar/fZFA5ixFASazZvPYkiwAJjAAJjQAHjgAHjwAFkAAFkQADkgADkwADlAADU5coclwqdMISQRfQJyQYYSofMxtMZaFpXLArQ5bDQnFgqMBMGBGJCmOKKTIjUoAqgEuAhk4AA"))


@parameterized_class(('name', 'settings_string'), valid_presets)
class TestSpoiler(unittest.TestCase):
    def setUp(self):
        """Base Setup."""
        # PLEASE NOTE: THIS LIST OF SETTINGS IS NOT COMPREHENSIVE - use the comments as quick references, not the entire story
        # You may have to add new options as you add them or as they get added

        data = {}
        data["seed"] = random.randint(0, 100000000)  # Can be fixed if you want to test a specific seed repeatedly
        data["settings_string"] = self.settings_string
        # Randomizers
        # Major Items
        data["shuffle_items"] = False  # Must be true to trigger the list selector below
        # data["item_rando_list_selected"] = ["shop", "banana", "toughbanana", "crown", "blueprint", "key", "medal", "coin", "kong", "fairy", "rainbowcoin", "beanpearl", "fakeitem", "junkitem"]  # all options
        data["move_rando"] = MoveRando.on  # usually "on" but i like "cross_purchase", rarely need to test with "start_with"
        # if start_with, training barrels and "camera and shockwave" are FORCED to be normal and vanilla respectively
        data["training_barrels"] = TrainingBarrels.normal  # usually "normal", could be "shuffled"
        data["starting_moves_count"] = 4  # 0-40

        # Shuffled Locations
        data["random_patches"] = True  # usually False
        data["cb_rando"] = False  # likely to be False?
        data["coin_rando"] = False
        data["random_fairies"] = False  # likely to be False
        data["wrinkly_location_rando"] = False  # likely to be False
        data["tns_location_rando"] = False  # likely to be False
        data["vanilla_door_rando"] = False  # unclear, likely prefer True? easier to debug when False
        data["crown_placement_rando"] = False  # usually false
        data["kasplat_rando_setting"] = KasplatRandoSetting.vanilla_locations  # usually vanilla_locations but i like location_shuffle, RARELY set to off

        # Global
        data["enemy_rando"] = True
        data["bonus_barrel_rando"] = True
        data["enemy_speed_rando"] = True
        data["boss_location_rando"] = True  # usually True
        data["kong_rando"] = True  # usually True - FORCED True if level_order shuffle
        data["puzzle_rando"] = True
        data["krool_phase_order_rando"] = True  # usually True
        data["helm_phase_order_rando"] = True
        data["boss_kong_rando"] = True  # usually True
        data["randomize_pickups"] = False
        data["shuffle_shops"] = True  # usually False
        data["random_starting_region"] = False  # likely to be False

        data["level_randomization"] = LevelRandomization.vanilla  # usually "level_order" may need to test with "loadingzone" or "loadingzonesdecoupled"
        data["random_prices"] = RandomPrices.low  # usually "medium, might need free, rarely vanilla"
        # If shuffle_items is true, shockwave_status is always shuffled_decoupled, vanilla, or start_with
        data["shockwave_status"] = ShockwaveStatus.vanilla  # usually "vanilla", could be "shuffled" or "shuffled_decoupled" or "start_with"
        data["bananaport_rando"] = BananaportRando.in_level  # usually "off", could be "in_level" "crossmap_coupled" "crossmap_decoupled"

        # Overworld
        # Global Settings
        data["bonus_barrel_auto_complete"] = False  # usually False
        data["open_lobbies"] = False
        data["open_levels"] = False  # usually False
        data["alter_switch_allocation"] = False  # likely to be True, easier to test things when false
        data["high_req"] = True  # usually True
        data["fast_gbs"] = True  # usually True
        data["helm_hurry"] = False
        data["smaller_shops"] = False  # likely to be True in item rando, many settings force it to be false

        data["logic_type"] = LogicType.glitchless  # "glitchless", "glitch", "nologic"
        data["glitches_selected"] = []
        # glitch options:
        # "advanced_platforming", "b_locker_skips", "general_clips", "ledge_clips", "moonkicks", "phase_swimming", "phase_walking", "skew", "spawn_snags", "swim_through_shores", "tag_barrel_storage", "troff_n_scoff_skips"
        data["win_condition"] = WinCondition.beat_krool  # lots of options: all_keys | get_key8 | beat_krool | all_medals | all_fairies | all_blueprints | poke_snap
        data["free_trade_setting"] = FreeTradeSetting.none  # none | not_blueprints | major_collectibles
        data["activate_all_bananaports"] = ActivateAllBananaports.isles  # usually isles, could be all or off
        data["krusha_ui"] = KrushaUi.dk

        # Difficulty
        data["no_healing"] = False
        data["no_melons"] = False
        data["hard_shooting"] = False
        data["perma_death"] = False
        data["disable_tag_barrels"] = False
        data["hard_blockers"] = False  # likely to be False
        data["hard_troff_n_scoff"] = False  # likely to be False
        data["hard_level_progression"] = False  # likely to be False
        data["hard_mode"] = False

        data["damage_amount"] = DamageAmount.default
        data["crown_enemy_rando"] = CrownEnemyRando.easy

        # Progression
        # Level Requirements
        data["randomize_blocker_required_amounts"] = True  # usually True, if false set values below
        data["blocker_0"] = 1
        data["blocker_1"] = 2
        data["blocker_2"] = 3
        data["blocker_3"] = 4
        data["blocker_4"] = 5
        data["blocker_5"] = 6
        data["blocker_6"] = 7
        data["blocker_7"] = 8
        data["blocker_text"] = 40  # usually 69
        data["maximize_helm_blocker"] = True  # usually True

        data["randomize_cb_required_amounts"] = True  # usually True, if false set values below
        data["troff_0"] = 1
        data["troff_1"] = 2
        data["troff_2"] = 3
        data["troff_3"] = 4
        data["troff_4"] = 5
        data["troff_5"] = 6
        data["troff_6"] = 7
        data["troff_text"] = 300  # usually 400?

        # Banana Medal/Fairy Requirements
        data["medal_requirement"] = 15  # vanilla is 15
        data["medal_cb_req"] = 75  # vanilla is 75
        data["rareware_gb_fairies"] = 20

        data["fast_start_beginning_of_game"] = True
        data["random_medal_requirement"] = False

        # Game Length Settings
        data["krool_random"] = False  # "phase count is random" setting
        data["krool_phase_count"] = 3  # usually 3
        data["helm_random"] = False  # "room count is random" setting
        data["helm_phase_count"] = 3  # usually 3
        data["keys_random"] = False  # "key count is random" setting
        data["select_keys"] = False  # usually False, if True use below
        # data["starting_keys_list_selected"] = [Items.JungleJapesKey]  # JungleJapesKey, AngryAztecKey, etc.
        data["key_8_helm"] = False  # likely to be True in most settings
        data["krool_access"] = True  # usually True - this is the weirdly named key 8 required setting
        data["krool_key_count"] = 8  # usually 5
        data["starting_random"] = False  # "starting kong count is random" setting
        data["starting_kongs_count"] = 3  # usually 2

        data["crown_door_item"] = HelmDoorItem.opened  # opened | random | specify the item: req_xxx
        data["crown_door_item_count"] = 1  # no need to specify when random
        data["coin_door_item"] = HelmDoorItem.opened  # opened | random | specify the item: req_xxx
        data["coin_door_item_count"] = 1  # no need to specify when random

        # QoL
        # Gameplay
        data["quality_of_life"] = True
        data["misc_changes_selected"] = []  # a whole suite of things it includes
        data["shorten_boss"] = True
        data["enable_tag_anywhere"] = True
        data["enable_shop_hints"] = True
        data["shop_indicator"] = True
        data["wrinkly_available"] = False
        data["warp_to_isles"] = True
        data["fast_warps"] = True
        data["auto_keys"] = True

        data["wrinkly_hints"] = WrinklyHints.standard
        data["helm_setting"] = HelmSetting.skip_start
        data["microhints_enabled"] = MicrohintsEnabled.base  # off/base/all
        data["more_cutscene_skips"] = ExtraCutsceneSkips.auto

        # Other
        data["fps_display"] = False
        data["portal_numbers"] = True
        data["item_reward_previews"] = True

        return data

    def test_settings_string(self):
        """Confirm that settings strings decryption is working and generate a spoiler log with it."""
        # The settings string is defined from the preset_files.json file
        # self.settings_string = "bKEGiRqzxNXnerKEDRAejpFjAIbiDLWIQXr5/ANnj4YTRzu6leyszOKbOrYvhTgfVA8IhkMhKlsa58Ij8Ro9dpcviFOWJtOCFA0ekCRNGeKvgKQW6nr8CSAZNFDKKGQXWSywUBdACDATqAgcDdgGEAjuBAkFeAKFAzyBgsHegOGBChDTx7ZCkQoqGciUy5JLNFvAjg6RaRcFP0VEWARMRQBXrXHI3ar/fZFA5ixFAGazZlUYkiwAJjAAJjQAHjgAHjwAFkAAFkQADkgADkwADlAADU5coclwqdMISQRfQJyQYYSqnMxtMYOLQtK5YFaHLYaE4sFRgJgwIymOKeRSZEalAFUAlwEMnCEICQoLDaUiKw8QESMsExQVJC0XGBklLhscHSYvHyAhJyg"
        settings_dict = decrypt_settings_string_enum(self.settings_string)
        settings_dict["seed"] = random.randint(0, 100000000)  # Can be fixed if you want to test a specific seed repeatedly

        # Plando testing - fill the data with a json string
        # settings_dict["enable_plandomizer"] = True
        # settings_dict["plandomizer_data"] = '{"plando_starting_kongs_selected": [0], "plando_kong_rescue_diddy": -1, "plando_kong_rescue_lanky": -1, "plando_kong_rescue_tiny": -1, "plando_kong_rescue_chunky": -1, "plando_level_order_0": 4, "plando_level_order_1": 2, "plando_level_order_2": 5, "plando_level_order_3": 3, "plando_level_order_4": 6, "plando_level_order_5": 1, "plando_level_order_6": 0, "plando_krool_order_0": -1, "plando_krool_order_1": -1, "plando_krool_order_2": -1, "plando_krool_order_3": -1, "plando_krool_order_4": -1, "plando_helm_order_0": -1, "plando_helm_order_1": -1, "plando_helm_order_2": -1, "plando_helm_order_3": -1, "plando_helm_order_4": -1, "locations": {"42": 26, "537": 50, "594": 47, "72": 25, "67": 49, "83": 16, "88": 23, "125": 30, "164": 29, "159": 21, "166": 9, "194": 24, "210": 39, "211": 28, "212": 32, "213": 8, "214": 39, "245": 4, "224": 19, "243": 12, "244": 45, "222": 35, "231": 18, "255": 31, "251": 27, "261": 6, "252": 48, "312": 3, "296": 5, "299": 22, "286": 17, "310": 10, "287": 7, "539": 34, "331": 10, "332": 39, "326": 38, "327": 37, "328": 36, "329": 14, "330": 11, "369": 15, "443": 2, "447": 20}, "prices": {}, "plando_bonus_barrels": {"231": 13, "296": 59, "299": 70, "310": 39}, "hints": {}}'

        settings = Settings(settings_dict)
        # settings.extreme_debugging = True  # Greatly slows seed gen, use with caution
        spoiler = Spoiler(settings)
        Generate_Spoiler(spoiler)
        print(spoiler)
        print(spoiler.json)
        # self.printHintDistribution(spoiler)
        # self.printDesiredOutput(spoiler)
        with open(f"test-result-{self.name}.json", "w") as outfile:
            outfile.write(spoiler.json)
        print(f"test {self.name} done")

    def printHintDistribution(self, spoiler: Spoiler):
        """Print the hint distribution for the given spoiler log."""
        types = ""
        values = ""
        for key, value in spoiler.hint_distribution.items():
            types += (key.name + ", ")
            values += (str(value) + ", ")
        print(types)
        print(values)

    def printDesiredOutput(self, spoiler: Spoiler):
        """Print any desired output from the spoiler. Customize to your heart's desire."""
        print("# of path hints: " + str(spoiler.hint_distribution[HintType.Multipath]) + " | woth length: " + str(len(spoiler.woth_locations) - 2))
        print()
