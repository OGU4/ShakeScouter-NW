# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from typing import Any

from ShakeScouter.scenes import Scene, SceneContext, SceneStatus
from ShakeScouter.utils.images import Frame

class Parallel(Scene):
	def __init__(self, children: list[Scene], anyDone: bool = False) -> None:
		self.__children = children
		self.__check    = any if anyDone else all

	def setup(self) -> Any:
		data = [
			{
				'stop': False,
				'data': c.setup(),
			}
			for c in self.__children
		]
		return data

	def reset(self, data: Any) -> None:
		for i, c in enumerate(self.__children):
			data[i]['stop'] = False
			c.reset(data[i]['data'])

	async def analysis(self, context: SceneContext, data: Any, frame: Frame) -> SceneStatus:
		for i, scene in enumerate(self.__children):
			d = data[i]

			if d['stop']:
				continue

			# Analysis frame
			result = await scene.analysis(context, d['data'], frame)

			# Handle result
			if result == SceneStatus.DONE:
				d['stop'] = True

		if self.__check(d['stop'] for d in data):
			return SceneStatus.DONE
		else:
			return SceneStatus.CONTINUE
