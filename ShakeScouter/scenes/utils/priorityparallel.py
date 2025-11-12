# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from copy import copy
from heapq import heapify, heappop
from typing import Any

from scenes import Scene, SceneContext, SceneStatus
from utils.images import Frame

class PriorityParallel(Scene):
	def __init__(self, children: list[tuple[int, Scene]]) -> None:
		self.__children = children
		self.__maxPrio  = max(p[0] for p in children)

	def setup(self) -> Any:
		data = {
			'priority': -1,
			'children': [c.setup() for _, c in self.__children],
		}
		return data

	def reset(self, data: Any) -> None:
		data['priority'] = -1

		for i, c in enumerate(self.__children):
			c[1].reset(data['children'][i])

	async def analysis(self, context: SceneContext, data: Any, frame: Frame) -> SceneStatus:
		# Init priority queue
		prio = copy(self.__children)
		heapify(prio)

		for _ in range(len(prio)):
			# Get current scene
			p, scene = heappop(prio)

			# Return if priority is exceeded
			if p < data['priority']:
				continue

			# Get data index
			dataIndex = self.__children.index((p, scene))

			# Analysis frame
			result = await scene.analysis(context, data['children'][dataIndex], frame)

			# Handle result
			if result == SceneStatus.DONE:
				data['priority'] = p + 1

		if data['priority'] >= self.__maxPrio:
			return SceneStatus.DONE
		else:
			return SceneStatus.CONTINUE
