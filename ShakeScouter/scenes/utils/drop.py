# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from typing import Any

from scenes import Scene, SceneContext, SceneStatus
from utils.images import Frame

class Drop(Scene):
	def __init__(self, child: Scene, rate: float = 1) -> None:
		self.__child = child
		self.__diff  = 1 / rate

	def setup(self) -> Any:
		data = {
			'cache': SceneStatus.FALSE,
			'next':  0,

			'child': self.__child.setup(),
		}
		return data

	def reset(self, data: Any) -> None:
		data['cache'] = SceneStatus.FALSE
		data['next']  = 0
		self.__child.reset(data['child'])

	async def analysis(self, context: SceneContext, data: Any, frame: Frame) -> SceneStatus:
		next = data['next']

		if context.timestamp >= next:
			data['cache'] = await self.__child.analysis(context, data['child'], frame)
			data['next']  = context.timestamp + self.__diff

		return data['cache']
