"""
Copyright (c) Cutleast
"""

import logging
from pathlib import Path
from typing import Optional, Self

from sse_plugin_interface.datatypes import RawString

from .flags import RecordFlags
from .group import Group
from .plugin_string import PluginString
from .record import Record
from .subrecord import EDID, MAST, StringSubrecord
from .utilities import Stream, peek


class SSEPlugin:
    """
    Represents a Skyrim Special Edition Plugin file (.esp, .esm, .esl).
    """

    __plugin_name: str
    """The name of the plugin (e.g. "Skyrim.esm")."""

    __header: Record
    """The plugin's header record containing metadata and other information."""

    __masters: list[RawString]
    """A list of all master plugins from the plugin header."""

    __groups: list[Group]
    """A list of all groups in the plugin."""

    __string_subrecords: Optional[dict[PluginString, StringSubrecord]] = None
    """Dictionary mapping extracted strings to their subrecords."""

    log: logging.Logger = logging.getLogger("PluginInterface")

    def __init__(self, name: str) -> None:
        """
        Args:
            name (str): The name of the plugin.
        """

        self.__plugin_name = name

    # Read/Write methods

    @classmethod
    def from_file(cls, path: Path) -> Self:
        """
        Reads and parses a plugin from a real file path.

        Args:
            path (Path): The path to the plugin file.

        Returns:
            Self: The parsed plugin.
        """

        with path.open("rb") as stream:
            return cls.from_stream(stream, path.name)

    @classmethod
    def from_stream(cls, stream: Stream, name: str) -> Self:
        """
        Reads and parses a plugin from a stream of bytes.

        Args:
            stream (Stream): The stream of bytes.
            name (str): The name of the plugin.

        Returns:
            Self: The parsed plugin.
        """

        plugin = cls(name)
        plugin.__parse_stream(stream)

        return plugin

    def __parse_stream(self, stream: Stream) -> None:
        """
        Parses the data from a stream of bytes.

        Args:
            stream (Stream): The stream of bytes.
        """

        self.__groups = []

        self.__header = Record()
        self.__header.parse(stream, RecordFlags(0))

        self.__masters = [
            subrecord.file
            for subrecord in self.__header.subrecords
            if isinstance(subrecord, MAST)
        ]

        while peek(stream, 1):
            group = Group()
            group.parse(stream, self.__header.flags)
            self.__groups.append(group)

    def dump(self) -> bytes:
        """
        Dumps the plugin data back to bytes.

        Returns:
            bytes: The plugin data.
        """

        data: bytes = b""
        data += self.__header.dump()

        for group in self.__groups:
            data += group.dump()

        return data

    def save(self, output_file: Path) -> None:
        """
        Writes the plugin's data to an output file.

        Args:
            output_file (Path): The path to the output file.
        """

        output_file.write_bytes(self.dump())

    # Extraction methods

    def extract_group_strings(
        self, group: Group, extract_localized: bool = False
    ) -> dict[PluginString, StringSubrecord]:
        """
        Extracts all strings from a group of records.

        Args:
            group (Group): The group to extract strings from.
            extract_localized (bool, optional):
                Whether to extract localized strings. Defaults to False.

        Returns:
            dict[PluginString, StringSubrecord]:
                A dictionary mapping extracted strings to their subrecords.
        """

        strings: dict[PluginString, StringSubrecord] = {}

        record: Record
        for record in SSEPlugin.extract_group_records(group):
            edid: Optional[RawString] = self.get_record_edid(record)
            master_index = int(record.formid[:2], base=16)

            # Get plugin that first defines this record from masters
            master: str
            try:
                master = str(self.__masters[master_index])
            # If index is not in masters, then the record is first defined in this plugin
            except IndexError:
                master = self.__plugin_name

            formid: str = f"{record.formid}|{master}"

            for subrecord in record.subrecords:
                if isinstance(subrecord, StringSubrecord):
                    string: RawString | int = subrecord.string

                    if isinstance(string, RawString) or extract_localized:
                        string_data = PluginString(
                            editor_id=edid,
                            form_id=formid,
                            index=subrecord.index,
                            type=f"{record.type} {subrecord.type}",
                            string=str(string),
                        )

                        strings[string_data] = subrecord

        return strings

    def extract_strings(self, extract_localized: bool = False) -> list[PluginString]:
        """
        Extracts all strings from the plugin.

        Args:
            extract_localized (bool, optional):
                Whether to extract localized strings. Defaults to False.

        Returns:
            list[PluginString]: A list of extracted strings.
        """

        strings: list[PluginString] = []
        for group in self.__groups:
            current_group: list[PluginString] = list(
                self.extract_group_strings(group, extract_localized).keys()
            )
            strings.extend(current_group)

        return strings

    def find_string_subrecord(
        self, form_id: str, type: str, string: str, index: Optional[int]
    ) -> Optional[StringSubrecord]:
        """
        Finds a subrecord that matches the given parameters.

        Args:
            form_id (str): Form ID of the subrecord.
            type (str): Type of the subrecord.
            string (str): String of the subrecord.
            index (Optional[int]): Index of the subrecord.

        Returns:
            Optional[StringSubrecord]: The found subrecord, or None if not found.
        """

        string_subrecord: Optional[StringSubrecord] = None

        if self.__string_subrecords is None:
            string_subrecords: dict[PluginString, StringSubrecord] = {}

            for group in self.__groups:
                current_group = self.extract_group_strings(group)
                string_subrecords |= current_group

            self.__string_subrecords = string_subrecords

        for plugin_string, subrecord in self.__string_subrecords.items():
            if (
                plugin_string.form_id[2:]
                == form_id[2:]  # Ignore master index and FE prefix
                and plugin_string.type == type
                and plugin_string.string == string
                and plugin_string.index == index
            ):
                string_subrecord = subrecord
                break

        return string_subrecord

    # Modification methods

    def replace_strings(self, strings: list[PluginString]) -> None:
        """
        Replaces the strings in the plugin.

        Args:
            strings (list[PluginString]): The strings to replace.
        """

        for string in strings:
            subrecord: Optional[StringSubrecord] = self.find_string_subrecord(
                string.form_id, string.type, string.string, string.index
            )

            if subrecord is not None:
                subrecord.set_string(string.string)
            else:
                self.log.error(
                    f"Failed to replace string {string}: Subrecord not found!"
                )

    def eslify_formids(self) -> None:
        """
        Recounts FormIDs beginning with `0x800`.
        """

        records: list[Record] = [
            record
            for group in self.__groups
            for record in SSEPlugin.extract_group_records(group)
        ]

        cur_formid: int = 0x800
        for record in records:
            # Recount only records that were first-defined in this plugin
            if int(record.formid[:2], base=16) >= len(self.__masters):
                new_formid: str = record.formid[:-3] + hex(cur_formid)[-3:]
                record.formid = new_formid

                cur_formid += 1

    def eslify_plugin(self) -> None:
        """
        Recounts FormIDs and sets Light Flag in Header.
        """

        if RecordFlags.LightMaster in self.__header.flags:
            return

        self.eslify_formids()
        self.__header.flags |= RecordFlags.LightMaster

    # Utilities

    @staticmethod
    def get_record_edid(record: Record) -> Optional[RawString]:
        """
        Determines the Editor ID of a record by looking for its EDID subrecord (if any).

        Args:
            record (Record): The record to get the Editor ID from.

        Returns:
            Optional[RawString]: The Editor ID of the record, or None if not found.
        """

        editor_id: Optional[RawString] = None
        try:
            for subrecord in record.subrecords:
                if isinstance(subrecord, EDID):
                    editor_id = subrecord.editor_id
                    break
        except AttributeError:
            pass

        return editor_id

    @staticmethod
    def extract_group_records(group: Group, recursive: bool = True) -> list[Record]:
        """
        Extracts all records from a group and its children (if recursive is True).

        Args:
            group (Group): The group to extract records from.
            recursive (bool, optional):
                Whether to extract records from child groups. Defaults to True.

        Returns:
            list[Record]: A list of extracted records.
        """

        records: list[Record] = []
        for child in group.children:
            if isinstance(child, Record):
                records.append(child)
            elif recursive:
                records.extend(SSEPlugin.extract_group_records(child, recursive))

        return records

    @staticmethod
    def is_light(plugin_path: Path) -> bool:
        """
        Checks if a plugin file is a light-flagged plugin. This is indicated either by
        the file extension (.esl) or the light flag in the header.

        Args:
            plugin_path (Path): The path to the plugin file.

        Returns:
            bool: True if the plugin is light-flagged, False otherwise.
        """

        if plugin_path.suffix.lower() == ".esl":
            return True

        with plugin_path.open("rb") as stream:
            header = Record()
            header.parse(stream, RecordFlags(0))

        return RecordFlags.LightMaster in header.flags
