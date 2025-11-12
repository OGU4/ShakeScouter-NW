# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from anyio.streams.memory import MemoryObjectSendStream
from copy import deepcopy
from nanoid import generate
from time import time
from typing import Any, Optional

from scenes.base import SceneContext, SceneEvent

class SceneContextImpl(SceneContext):
	EXCLUDE_KEYS = set(['session', 'event', 'timestamp'])

	def __init__(self, streams: list[MemoryObjectSendStream[Any]] = []) -> None:
		self.__cache: dict[SceneEvent, dict[str, Any]] = {}
		self.__streams = streams
		self.__timestamp = time()

	def __del__(self) -> None:
		for stream in self.__streams:
			stream.close()

	def __newSession(self) -> str:
		self.__session = generate()
		return self.__session

	@property
	def session(self) -> str:
		return self.__session

	@property
	def timestamp(self) -> float:
		return self.__timestamp

	def updateTimestamp(self) -> float:
		self.__timestamp = time()
		return self.__timestamp

	async def __send(self, message: dict[str, Any]) -> None:
		for stream in self.__streams:
			await stream.send(message)

	async def sendImmediately(self, event: SceneEvent, message: Optional[dict[str, Any]] = None) -> None:
		eventMessage = {
			'session': self.__newSession() if event == SceneEvent.MATCHMAKING else self.session,
			'event': event.value,
			'timestamp': self.__timestamp,
		}

		if message is not None:
			# Set additional field
			for key, val in message.items():
				if val is not None:
					eventMessage[key] = val

		# Send
		await self.__send(eventMessage)

	async def send(self, event: SceneEvent, message: dict[str, Any]) -> None:
		def compare(dict1: dict, dict2: dict, exclude: set[str]):
			keys1 = set(dict1.keys()) - exclude
			keys2 = set(dict2.keys()) - exclude
			match = all(dict1[key] == dict2[key] for key in keys1 & keys2)
			return match

		# Compare cache
		if event in self.__cache:
			if compare(self.__cache[event], message, SceneContextImpl.EXCLUDE_KEYS):
				return

		eventMessage = {
			'session': self.__newSession() if event == SceneEvent.MATCHMAKING else self.session,
			'event': event.value,
			'timestamp': self.__timestamp,
		}

		# Set additional field
		for key, val in message.items():
			if val is not None:
				eventMessage[key] = deepcopy(val)

		# Add clone message to cache
		self.__cache[event] = eventMessage

		# Send
		await self.__send(eventMessage)
