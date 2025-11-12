# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from typing import Any

from scenes import Scene, SceneContext, SceneStatus
from utils.images import Frame

class Root(Scene):
	def __init__(self, child: Scene, devMode: bool = False) -> None:
		self.__child = child
		self.__dev   = devMode

	def setup(self) -> Any:
		data = self.__child.setup()
		return data

	def reset(self, data: Any) -> None:
		self.__child.reset(data)

	async def analysis(self, context: SceneContext, data: Any, frame: Frame) -> SceneStatus:
		# Update timestamp
		context.updateTimestamp()

		# Analysis frame
		result = await self.__child.analysis(context, data, frame)

		# Handle result
		if result != SceneStatus.DONE:
			return SceneStatus.CONTINUE

		# Avoid infinite loop in dev mode as it can hinder debugging
		if self.__dev:
			return SceneStatus.DONE

		# Reset all data
		self.reset(data)

		return SceneStatus.CONTINUE
