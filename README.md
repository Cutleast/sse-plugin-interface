# SSE Plugin Interface

A pure Python library for reading and writing Skyrim Special Edition Plugin files (.esp, .esm, .esl).

See here for more information about the Plugin file format: https://en.uesp.net/wiki/Skyrim_Mod:Mod_File_Format

**Please note** that this library was originally intended for extraction of strings that are visible in-game.
Other features may not be fully implemented or tested and are used at your own risk!

## Installation

Run `pip install sse-plugin-interface` to install the library in the current active environment.

## Usage

### Load a plugin

**From file:**

```python
>>> plugin = SSEPlugin.from_file(Path("my_plugin.esp"))
```

**Directly from a stream of bytes:**

```python
>>> plugin = SSEPlugin.from_file(open("my_plugin.esp"), "my_plugin.esp")
```

### Extract strings from the plugin

```python
>>> strings: list[PluginString] = SSEPlugin.from_file(Path("my_plugin.esp")).extract_strings()
```

See here for information about the PluginString type: [plugin_string.py](./src/sse_plugin_interface/plugin_string.py)

### Replace strings in a plugin

```python
>>> plugin = SSEPlugin.from_file(Path("my_plugin.esp"))
>>> plugin.replace_strings([PluginString(...), ...])
```

### Dump or save the plugin to a file

**Dump the plugin data to a byte array:**

```python
>>> plugin.dump()
b"This is the dumped content of the plugin"
```

**Save the plugin data to a file:**

```python
>>> plugin.save(Path("output.esp"))
```
