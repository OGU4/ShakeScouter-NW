# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from typing import Any

from constants import assets, screen
from scenes.base import *
from utils.images import Frame, getMinErrorKey

class KingScene(Scene):
	MIN_ERROR = 0.1

	def __init__(self) -> None:
		self.__kingTemplates = {
			key: Scene.loadTemplate(f'kings/{key}')
			for key in assets.kingKeys
		}

	async def analysis(self, context: SceneContext, data: Any, frame: Frame) -> SceneStatus:
		kingImage = frame.apply(screen.KING_NAME_PART)
		kingKey = getMinErrorKey(
			kingImage,
			self.__kingTemplates,
			minError=KingScene.MIN_ERROR,
		)

		if kingKey is None:
			return SceneStatus.FALSE

		# Send message
		message = {
			'king': kingKey,
		}
		await context.sendImmediately(SceneEvent.GAME_KING, message)

		return SceneStatus.DONE
