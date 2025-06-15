# ../gungame/plugins/custom/gg_capture_the_flag/rules.py

"""Creates the gg_capture_the_flag rules."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# GunGame
from gungame.core.rules.instance import GunGameRules

# Plugin
from .info import info

# =============================================================================
# >> RULES
# =============================================================================
capture_the_flag_rules = GunGameRules(info.name)
capture_the_flag_rules.register_all_rules()
