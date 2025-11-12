# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from abc import abstractmethod
from anyio.abc import TaskGroup
from anyio.streams.memory import MemoryObjectReceiveStream
from typing import Any, TypeAlias

class Output:
	Message: TypeAlias = dict[str, Any]

	@abstractmethod
	async def setup(self, tg: TaskGroup):
		raise NotImplementedError()

	@abstractmethod
	def onMessage(self, message: Message):
		raise NotImplementedError()

	async def onReceive(self, stream: MemoryObjectReceiveStream[Any]) -> None:
		async with stream:
			async for message in stream:
				self.onMessage(message)
