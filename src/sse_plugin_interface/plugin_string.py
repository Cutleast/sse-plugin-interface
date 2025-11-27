"""
Copyright (c) Cutleast
"""

from dataclasses import dataclass
from typing import Optional, override


@dataclass
class PluginString:
    """
    Dataclass for all strings that are extracted from a plugin.
    """

    form_id: str
    """The form id of the record housing the string (e.g. "FE012345")."""

    type: str
    """The types of the record and subrecord (e.g. "WEAP FULL")."""

    string: str
    """The string itself."""

    editor_id: Optional[str] = None
    """The editor id of the record (if any)."""

    index: Optional[int] = None
    """The internal index of the string within the record."""

    @override
    def __hash__(self) -> int:
        return hash((self.form_id, self.type, self.editor_id, self.index))
