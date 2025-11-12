# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from typing import Any

from ShakeScouter.scenes import Scene, SceneContext, SceneStatus
from ShakeScouter.utils.images import Frame

class TestScene(Scene):
	def __init__(self, result: SceneStatus) -> None:
		self.__result = result

	async def analysis(self, context: SceneContext, data: Any, frame: Frame) -> SceneStatus:
		return self.__result

class CountDownTestScene(Scene):
	def __init__(self, count: int) -> None:
		self.__count = count

	def setup(self) -> Any:
		data = {
			'count': self.__count,
		}
		return data

	async def analysis(self, context: SceneContext, data: Any, frame: Frame) -> SceneStatus:
		if data['count'] > 0:
			data['count'] = data['count'] - 1
			return SceneStatus.FALSE

		return SceneStatus.DONE
