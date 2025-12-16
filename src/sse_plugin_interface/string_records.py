"""
Copyright (c) Cutleast
"""

STRING_RECORDS: dict[str, list[str]] = {
    "ACTI": ["FULL", "RNAM"],
    "ALCH": ["FULL"],
    "AMMO": ["FULL", "DESC"],
    "APPA": ["FULL", "DESC"],
    "ARMO": ["FULL", "DESC"],
    "AVIF": ["FULL", "DESC"],
    "BOOK": ["FULL", "DESC", "CNAM"],
    "CLAS": ["FULL"],
    "CELL": ["FULL"],
    "CONT": ["FULL"],
    "DIAL": ["FULL"],
    "DOOR": ["FULL"],
    "ENCH": ["FULL"],
    "EXPL": ["FULL"],
    "FLOR": ["FULL", "RNAM"],
    "FURN": ["FULL"],
    "HAZD": ["FULL"],
    "INFO": ["NAM1", "RNAM"],
    "INGR": ["FULL"],
    "KEYM": ["FULL"],
    "LCTN": ["FULL"],
    "LIGH": ["FULL"],
    "LSCR": ["DESC"],
    "MESG": ["DESC", "FULL", "ITXT"],
    "MGEF": ["FULL", "DNAM"],
    "MISC": ["FULL"],
    "NPC_": ["FULL", "SHRT"],
    "NOTE": ["FULL", "TNAM"],
    "PERK": ["FULL", "DESC", "EPF2", "EPFD"],
    "PROJ": ["FULL"],
    "QUST": ["FULL", "CNAM", "NNAM"],
    "RACE": ["FULL", "DESC"],
    "REFR": ["FULL"],
    "REGN": ["RDMP"],
    "SCRL": ["FULL", "DESC"],
    "SHOU": ["FULL", "DESC"],
    "SLGM": ["FULL"],
    "SPEL": ["FULL", "DESC"],
    "TACT": ["FULL"],
    "TREE": ["FULL"],
    "WEAP": ["DESC", "FULL"],
    "WOOP": ["FULL", "TNAM"],
    "WRLD": ["FULL"],
}
"""
A dictionary mapping record types to a list of subrecord types that are known to contain
strings that are visible in-game.
"""
