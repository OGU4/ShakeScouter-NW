# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from os import chdir
from parameterized import parameterized
from pathlib import Path
from unittest import IsolatedAsyncioTestCase

from constants import env
from recognizers import selectDevice
from recognizers.digit import DigitReader
from scenes import SceneEvent, SceneStatus
from scenes.ingame import ResultScene
from scenes.contexttest import TestSceneContext
from utils.images import Frame

class TestWaveScene(IsolatedAsyncioTestCase):
	@classmethod
	def setUpClass(cls):
		currentDir = Path(__file__)
		sourceDir  = next(p for p in currentDir.parents if p.name == 'src')
		chdir(sourceDir)

		device = selectDevice('cpu')
		reader = DigitReader(device)
		cls.__ctx   = TestSceneContext()
		cls.__scene = ResultScene(reader)

	@parameterized.expand([
		('result02',  59, 2651),
		('result03', 104, 4917),
		('result04', 113, 3682),
	])
	async def test_analysisResult(self, filename: str, golden: int, power: int):
		filepath = env.DEV_ASSET_PATH.format(f'other/{filename}')
		frame = Frame(filepath=filepath)

		data = self.__scene.setup()

		ret = await self.__scene.analysis(self.__ctx, data, frame)
		self.assertEqual(ret, SceneStatus.DONE)
		self.assertEqual(self.__ctx.message['event'], SceneEvent.GAME_RESULT.value)
		self.assertEqual(self.__ctx.message['golden'], golden)
		self.assertEqual(self.__ctx.message['power'], power)
