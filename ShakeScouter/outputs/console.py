# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from outputs.base import Output

class ConsoleOutput(Output):
	def __init__(self, _) -> None:
		pass

	async def setup(self, _):
		pass

	def onMessage(self, message: Output.Message):
		print(message)
