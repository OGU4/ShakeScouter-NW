# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from importlib import import_module

class PluginLoader:
	def __init__(self, moduleName: str) -> None:
		self.__module = import_module(moduleName)

	def load(self, className: str):
		if not hasattr(self.__module, className):
			raise ValueError(f'"className" is not found: {className}')

		klass = getattr(self.__module, className)
		return klass
