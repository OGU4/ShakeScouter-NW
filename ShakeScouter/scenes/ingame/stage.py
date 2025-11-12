# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from typing import Any

from ShakeScouter.constants import assets, screen
from ShakeScouter.scenes.base import *
from ShakeScouter.utils.images import errorMAE, Frame, getMinErrorKey

class StageScene(Scene):
	MIN_ERROR = 0.1

	def __init__(self) -> None:
		self.__logoTemplate = Scene.loadTemplate('logo')
		self.__stageTemplates = {
			key: Scene.loadTemplate(f'stages/{key}')
			for key in assets.stageKeys
		}

	async def analysis(self, context: SceneContext, data: Any, frame: Frame) -> SceneStatus:
		logoImage = frame.apply(screen.LOGO_PART)
		logoError = errorMAE(logoImage, self.__logoTemplate)

		if logoError > StageScene.MIN_ERROR:
			return SceneStatus.FALSE

		stageImage = frame.apply(screen.STAGE_NAME_PART)
		stageKey = getMinErrorKey(
			stageImage,
			self.__stageTemplates,
			minError=StageScene.MIN_ERROR,
		)

		if stageKey is None:
			return SceneStatus.FALSE

		# Send message
		message = {
			'stage': stageKey[4:],
		}
		await context.sendImmediately(SceneEvent.GAME_STAGE, message)

		return SceneStatus.DONE
