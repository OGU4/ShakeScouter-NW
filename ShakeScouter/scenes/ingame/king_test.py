# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from os import chdir
from parameterized import parameterized
from pathlib import Path
from unittest import IsolatedAsyncioTestCase

from constants import env
from scenes import SceneEvent, SceneStatus
from scenes.ingame import KingScene
from scenes.contexttest import TestSceneContext
from utils.images import Frame

class TestKingScene(IsolatedAsyncioTestCase):
	@classmethod
	def setUpClass(cls):
		currentDir = Path(__file__)
		sourceDir  = next(p for p in currentDir.parents if p.name == 'ShakeScouter')
		chdir(sourceDir)

		cls.__ctx   = TestSceneContext()
		cls.__scene = KingScene()

	@parameterized.expand([
		('cohozuna00', 'cohozuna'),
		('cohozuna01', 'cohozuna'),
		('cohozuna02', 'cohozuna'),
		('cohozuna03', 'cohozuna'),

		('horrorboros00', 'horrorboros'),
		('horrorboros01', 'horrorboros'),
		('horrorboros02', 'horrorboros'),

		('megalodontia00', 'megalodontia'),
		('megalodontia01', 'megalodontia'),
		('megalodontia02', 'megalodontia'),
		('megalodontia03', 'megalodontia'),

		('triumvirate00', 'triumvirate'),
		('triumvirate01', 'triumvirate'),
		('triumvirate02', 'triumvirate'),
		('triumvirate03', 'triumvirate'),
		('triumvirate04', 'triumvirate'),
		('triumvirate05', 'triumvirate'),
		('triumvirate06', 'triumvirate'),
		('triumvirate07', 'triumvirate'),
		('triumvirate08', 'triumvirate'),
		('triumvirate09', 'triumvirate'),
	])
	async def test_analysisKing(self, filename: str, kingKey: str):
		filepath = env.DEV_ASSET_PATH.format(f'kings/{filename}')
		frame = Frame(filepath=filepath)

		data = self.__scene.setup()

		ret = await self.__scene.analysis(self.__ctx, data, frame)
		self.assertEqual(ret, SceneStatus.DONE)
		self.assertEqual(self.__ctx.message['event'], SceneEvent.GAME_KING.value)
		self.assertEqual(self.__ctx.message['king'], kingKey)
