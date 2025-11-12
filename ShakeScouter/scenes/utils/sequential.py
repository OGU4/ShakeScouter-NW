# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from typing import Any

from ShakeScouter.scenes import Scene, SceneContext, SceneStatus
from ShakeScouter.utils.images import Frame

class Sequential(Scene):
	def __init__(self, children: list[Scene]) -> None:
		self.__children = children

	def setup(self) -> Any:
		data = {
			'index': 0,
			'children': [c.setup() for c in self.__children],
		}
		return data

	def reset(self, data: Any) -> None:
		data['index'] = 0

		for i, c in enumerate(self.__children):
			c.reset(data['children'][i])

	async def analysis(self, context: SceneContext, data: Any, frame: Frame) -> SceneStatus:
		# Get index
		i = data['index']

		# Get current scene
		scene = self.__children[i]

		# Analysis frame
		result = await scene.analysis(context, data['children'][i], frame)

		# Handle result
		# - FALSE, CONTINUE ->            CONTINUE
		# - DONE -> if not LAST:          CONTINUE
		#           else:                 DONE
		match result:
			case SceneStatus.FALSE | SceneStatus.CONTINUE:
				return SceneStatus.CONTINUE
			case SceneStatus.DONE:
				data['index'] = i + 1
				if data['index'] < len(self.__children):
					return SceneStatus.CONTINUE
				else:
					return SceneStatus.DONE
