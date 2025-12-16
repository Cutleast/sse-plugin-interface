"""
Copyright (c) Cutleast
"""

from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from sse_plugin_interface.plugin import SSEPlugin
from sse_plugin_interface.plugin_string import PluginString


class TestSSEPlugin:
    """
    Tests `SSEPlugin`.
    """

    EXTRACT_STRINGS_DATA: list[tuple[Path, int]] = [
        (Path("tests") / "test_data" / "Obsidian Weathers.esp", 31),
        (Path("tests") / "test_data" / "Ordinator - Perks of Skyrim.esp", 7107),
        (Path("tests") / "test_data" / "RSChildren Patch - BS Bruma.esp", 13),
        (Path("tests") / "test_data" / "RSChildren.esp", 69),
        (Path("tests") / "test_data" / "RSkyrimChildren.esm", 78),
    ]

    @pytest.mark.parametrize("plugin_path, expected_string_count", EXTRACT_STRINGS_DATA)
    def test_extract_strings(
        self, plugin_path: Path, expected_string_count: int
    ) -> None:
        """
        Tests the extraction of strings.

        Args:
            plugin_path (Path): Path to the test plugin file.
            expected_string_count (int): Expected number of strings.
        """

        # given
        plugin = SSEPlugin.from_file(plugin_path)

        # when
        strings: list[PluginString] = plugin.extract_strings()

        # then
        assert len(strings) == expected_string_count

    def test_dump(self, fs: FakeFilesystem) -> None:
        """
        Tests dumping and reloading a plugin file.

        Args:
            fs (FakeFilesystem): The fake filesystem.
        """

        # given
        plugin_path = Path("tests") / "test_data" / "Obsidian Weathers.esp"
        fs.add_real_directory(plugin_path.parent)
        plugin = SSEPlugin.from_file(plugin_path)
        output_file = Path("output") / "Obsidian Weathers.esp"
        output_file.parent.mkdir(parents=True)

        # when
        plugin.save(output_file)
        reloaded_plugin = SSEPlugin.from_file(output_file)

        # then
        assert reloaded_plugin.extract_strings() == plugin.extract_strings()
