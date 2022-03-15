from typing import Callable, Dict, List
import pathlib
import json
import importlib
import visitor
import pkg_resources


class ModuleInterface:
    """Represents a plugin interface. A plugin has a single register function."""

    @staticmethod
    def register(PluginManager) -> None:
        """Register the necessary items in the game character factory."""


def import_module(name: str) -> ModuleInterface:
    """Imports a module given a name."""
    return importlib.import_module(name)  # type: ignore


class PluginManager():
    def __init__(self):
        self.plugins: Dict[str, "visitor.NodeVisitor"] = {}

    def register(self, plugin_name: str, plugin_init_fun: Callable[[], "NodeVisitor"]) -> None:
        try:
            plugin: "visitor.NodeVisitor" = plugin_init_fun()
            self.plugins[plugin_name] = plugin
        except Exception:
            print(f"error loading Plugin {plugin_name}")

    def getPluginList(self) -> List["visitor.NodeVisitor"]:
        retList: List[visitor.NodeVisitor] = []
        for key, val in self.plugins.items():
            retList.append(val)
        return retList

    def loadPlugins(self):
        plugin_file = open(f"{pathlib.Path(__file__).resolve().parent.parent}/plugins.json")
        plugin_data = json.load(plugin_file)["plugins"]

        for plugin_file in plugin_data:
            # print(f"plugin {plugin_file} loading")
            plugin = import_module(plugin_file)
            plugin.register(self)
        for entry_point in pkg_resources.iter_entry_points('excal_plugins'):
            # print(f"plugin {entry_point.name} loading")
            entry_point.load()(self)
