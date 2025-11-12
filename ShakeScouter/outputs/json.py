# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from datetime import datetime
from json import dump
from typing import Any

from constants import env
from outputs.base import Output
from scenes.base import SceneEvent

class JsonOutput(Output):
	TIMESTAMP_FILENAME = 'match_%Y%m%d-%H%M'

	def __init__(self, args: Any) -> None:
		self.__curPath = None
		self.__useTimestampFilename = args.timestamp

	async def setup(self, _):
		pass

	def __writeFile(self, message: Output.Message) -> None:
		if self.__curPath is None or message['event'] == SceneEvent.MATCHMAKING.value:
			self.__curPath = self.__getNewFilepath(message)

		with open(self.__curPath, 'a', encoding='utf8') as fh:
			dump(message, fh, separators=(',', ':'))
			fh.write('\n')

	def onMessage(self, message: Output.Message):
		self.__writeFile(message)

	def __getNewFilepath(self, message: Output.Message) -> str:
		filename: str
		if self.__useTimestampFilename:
			date = datetime.now()
			filename = date.strftime(JsonOutput.TIMESTAMP_FILENAME)
		else:
			filename = message['session']
		filepath = env.TELEMETRY_PATH.format(filename)
		return filepath
