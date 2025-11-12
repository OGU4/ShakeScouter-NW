# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from typing import Any

from ShakeScouter.constants import screen
from ShakeScouter.scenes.base import *
from ShakeScouter.utils.images import errorMAE, Frame

class MatchmakingScene(Scene):
	MIN_ERROR = 0.1

	def __init__(self) -> None:
		self.__startTemplate = Scene.loadTemplate('start')

	async def analysis(self, context: SceneContext, data: Any, frame: Frame) -> SceneStatus:
		# Detect "Start"
		startImage = frame.apply(screen.MESSAGE_PART)
		startError = errorMAE(startImage, self.__startTemplate)

		if startError > MatchmakingScene.MIN_ERROR:
			return SceneStatus.FALSE

		# Send message
		await context.sendImmediately(SceneEvent.MATCHMAKING)

		return SceneStatus.DONE
