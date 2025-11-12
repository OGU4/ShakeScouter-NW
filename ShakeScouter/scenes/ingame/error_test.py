# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from os import chdir
from parameterized import parameterized
from pathlib import Path
from unittest import IsolatedAsyncioTestCase

from constants import env
from scenes import SceneEvent, SceneStatus
from scenes.ingame import ErrorScene
from scenes.contexttest import TestSceneContext
from utils.images import Frame

class TestErrorScene(IsolatedAsyncioTestCase):
	@classmethod
	def setUpClass(cls):
		currentDir = Path(__file__)
		sourceDir  = next(p for p in currentDir.parents if p.name == 'ShakeScouter')
		chdir(sourceDir)

		cls.__ctx   = TestSceneContext()
		cls.__scene = ErrorScene()

	@parameterized.expand([
		('error'),
	])
	async def test_analysis(self, filename: str):
		filepath = env.DEV_ASSET_PATH.format(f'other/{filename}')
		frame = Frame(filepath=filepath)

		data = self.__scene.setup()

		ret = await self.__scene.analysis(self.__ctx, data, frame)
		self.assertEqual(ret, SceneStatus.DONE)
		self.assertEqual(self.__ctx.message['event'], SceneEvent.GAME_ERROR.value)
