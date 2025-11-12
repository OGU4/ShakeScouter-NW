# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from typing import Any

from ShakeScouter.constants import screen
from ShakeScouter.scenes.base import *
from ShakeScouter.utils.images import errorMAE, Frame

class ErrorScene(Scene):
	MIN_ERROR = 0.05

	def __init__(self) -> None:
		self.__errorTemplate = Scene.loadTemplate('error')

	async def analysis(self, context: SceneContext, data: Any, frame: Frame) -> SceneStatus:
		# Detect error message
		errorImage = frame.apply(screen.ERROR_PART)
		errorError = errorMAE(errorImage, self.__errorTemplate)

		if errorError > ErrorScene.MIN_ERROR:
			return SceneStatus.FALSE

		# Send message
		await context.sendImmediately(SceneEvent.GAME_ERROR)

		return SceneStatus.DONE
