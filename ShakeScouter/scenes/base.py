# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import cv2 as cv
import numpy as np

from abc import abstractmethod
from enum import Enum
from numpy.typing import NDArray
from typing import Any, Optional

from constants import env
from utils.images import Frame

class SceneEvent(Enum):
	DEV_COMMENT = 'dev_comment'
	DEV_WARN    = 'dev_warn'
	MATCHMAKING = 'matchmaking'
	GAME_STAGE  = 'game_stage'
	GAME_KING   = 'game_king'
	GAME_UPDATE = 'game_update'
	GAME_RESULT = 'game_result'
	GAME_ERROR  = 'game_error'

class SceneStatus(Enum):
	FALSE = 0
	DONE = 1
	CONTINUE = 2

class SceneContext:
	@property
	def session(self) -> str:
		raise NotImplementedError()

	@property
	def timestamp(self) -> float:
		raise NotImplementedError()

	def updateTimestamp(self) -> float:
		raise NotImplementedError()

	@abstractmethod
	async def sendImmediately(self, event: SceneEvent, message: Optional[dict[str, Any]] = None) -> None:
		raise NotImplementedError()

	@abstractmethod
	async def send(self, event: SceneEvent, message: dict[str, Any]) -> None:
		raise NotImplementedError()

class Scene:
	def setup(self) -> Any:
		return None

	def reset(self, data: Any) -> None:
		pass

	@abstractmethod
	async def analysis(self, context: SceneContext, data: Any, frame: Frame) -> SceneStatus:
		raise NotImplementedError()

	@staticmethod
	def loadTemplate(templateName: str) -> NDArray[np.uint8]:
		filepath = env.template_path(templateName)
		image = cv.imread(str(filepath), cv.IMREAD_GRAYSCALE)
		if image is None:
			raise TypeError(f'Image is not found: {filepath}')
		if image.dtype != np.uint8:
			raise TypeError(f'Image type is not np.uint8')
		return image.astype(np.uint8)
