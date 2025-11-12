# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from os import chdir
from parameterized import parameterized
from pathlib import Path
from unittest import IsolatedAsyncioTestCase

from ShakeScouter.constants import assets, env
from ShakeScouter.scenes import SceneEvent, SceneStatus
from ShakeScouter.scenes.ingame import StageScene
from ShakeScouter.scenes.contexttest import TestSceneContext
from ShakeScouter.utils.images import Frame

class TestStageScene(IsolatedAsyncioTestCase):
	@classmethod
	def setUpClass(cls):
		currentDir = Path(__file__)
		sourceDir  = next(p for p in currentDir.parents if p.name == 'ShakeScouter')
		chdir(sourceDir)

		cls.__ctx   = TestSceneContext()
		cls.__scene = StageScene()

	@parameterized.expand([[key] for key in assets.stageKeys])
	async def test_analysis(self, stageKey):
		filepath = env.DEV_ASSET_PATH.format(f'stages/{stageKey}')
		frame = Frame(filepath=filepath)

		data = self.__scene.setup()

		ret = await self.__scene.analysis(self.__ctx, data, frame)
		self.assertEqual(ret, SceneStatus.DONE)
		self.assertEqual(self.__ctx.message['event'], SceneEvent.GAME_STAGE.value)
		self.assertEqual(self.__ctx.message['stage'], stageKey[4:])
