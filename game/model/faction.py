from enum import StrEnum

import discord

from discord_helpers.emoji import get_emoji


class Faction(StrEnum):
    REBEL_ALLIANCE = 'rebelalliance'
    GALACTIC_EMPIRE = 'galacticempire'
    SCUM_AND_VILLAINY = 'scumandvillainy'
    RESISTANCE = 'resistance'
    FIRST_ORDER = 'firstorder'
    GALACTIC_REPUBLIC = 'galacticrepublic'
    SEPARATIST_ALLIANCE = 'separatistalliance'

    @property
    def emoji(self) -> str:
        match self:
            case Faction.REBEL_ALLIANCE:
                return get_emoji('rebel')
            case Faction.GALACTIC_EMPIRE:
                return get_emoji('empire')
            case Faction.SCUM_AND_VILLAINY:
                return get_emoji('scum')
            case Faction.FIRST_ORDER:
                return get_emoji('first_order')
            case Faction.RESISTANCE:
                return get_emoji('resistance')
            case Faction.GALACTIC_REPUBLIC:
                return get_emoji('republic')
            case Faction.SEPARATIST_ALLIANCE:
                return get_emoji('separatist')

    @property
    def upgrade_str(self) -> str:
        match self:
            case Faction.REBEL_ALLIANCE:
                return 'Rebel'
            case Faction.GALACTIC_EMPIRE:
                return 'Empire'
            case Faction.SCUM_AND_VILLAINY:
                return 'Scum'
            case Faction.FIRST_ORDER:
                return 'First Order'
            case Faction.RESISTANCE:
                return 'Resistance'
            case Faction.GALACTIC_REPUBLIC:
                return 'Republic'
            case Faction.SEPARATIST_ALLIANCE:
                return 'Separatist'

    @property
    def color(self) -> discord.Color:
        match self:
            case Faction.REBEL_ALLIANCE:
                return discord.Color.brand_red()
            case Faction.GALACTIC_EMPIRE:
                return discord.Color.darker_grey()
            case Faction.SCUM_AND_VILLAINY:
                return discord.Color.dark_green()
            case Faction.FIRST_ORDER:
                return discord.Color.dark_red()
            case Faction.RESISTANCE:
                return discord.Color.dark_orange()
            case Faction.GALACTIC_REPUBLIC:
                return discord.Color.gold()
            case Faction.SEPARATIST_ALLIANCE:
                return discord.Color.dark_blue()
