# ../gungame/plugins/custom/gg_capture_the_flag/gg_capture_the_flag.py

"""."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
from operator import attrgetter

# Source.Python
from cvars import ConVar
from events import Event
from events.hooks import EventAction, PreEvent
from filters.players import PlayerIter
from listeners import OnLevelEnd
from plugins.manager import plugin_manager
from players.teams import teams_by_number

# GunGame
from gungame.core.events.included.teams import GG_Team_Level_Up, GG_Team_Win
from gungame.core.messages.hooks import MessagePrefixHook
from gungame.core.players.attributes import AttributePreHook
from gungame.core.players.dictionary import player_dictionary
from gungame.core.sounds.hooks import SoundHook
from gungame.core.teams import team_levels
from gungame.core.weapons.manager import weapon_order_manager

if "capture_the_flag" not in map(
    attrgetter("name"),
    plugin_manager.loaded_plugins,
):
    msg = "Capture the flag is not loaded."
    raise ValueError(msg)


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
win_count = ConVar("ctf_win_count")
DEFAULT_WIN_COUNT = win_count.get_int()


# =============================================================================
# >> LOAD & UNLOAD
# =============================================================================
def load():
    win_count.set_int(weapon_order_manager.max_levels)
    team_levels.clear(value=1)


def unload():
    win_count.set_int(DEFAULT_WIN_COUNT)
    team_levels.clear()


# =============================================================================
# >> GAME EVENTS
# =============================================================================
@Event("flag_captured")
def _increase_team_score(game_event):
    team = int(game_event["team"])
    current = team_levels[team]
    team_levels[team] += 1
    for player in PlayerIter(teams_by_number[team]):
        player_dictionary[player.userid].increase_level(1, "ctf")
    if team_levels[team] > weapon_order_manager.max_levels:
        with GG_Team_Win() as event:
            event.winner = team
            event.loser = 5 - team
            event.style = "ctf"
        return

    with GG_Team_Level_Up() as event:
        event.team = team
        event.old_level = current
        event.new_level = team_levels[team]
        event.style = "ctf"


@Event("gg_start")
def _set_win_count(game_event):
    win_count.set_int(weapon_order_manager.max_levels)


# =============================================================================
# >> HOOKS
# =============================================================================
@AttributePreHook("level")
def _level_hook(player, attribute, new_value):
    level = team_levels.get(player.team_index)
    if level is not None and level != new_value:
        return False

    return None


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnLevelEnd
def _reset_team_level():
    team_levels.clear(value=1)


# =============================================================================
# >> EVENT HOOKS
# =============================================================================
@PreEvent("gg_level_up", "gg_win")
def _block_level_up(game_event):
    return EventAction.BLOCK


# =============================================================================
# >> MESSAGE HOOKS
# =============================================================================
@MessagePrefixHook("LevelInfo:")
def _level_info_hook(message_name, message_prefix):
    """Hooks the LevelInfo messages so that the team messages can be sent."""
    return False


# =============================================================================
# >> SOUND HOOKS
# =============================================================================
@SoundHook("multi_kill")
def _suppress_multi_kill_sound(sound_name):
    """Stop the multi-kill sound from spamming."""
    return False
