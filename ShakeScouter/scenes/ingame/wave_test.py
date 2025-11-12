# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from os import chdir
from parameterized import parameterized
from pathlib import Path
from unittest import IsolatedAsyncioTestCase

from constants import Color, env
from recognizers import selectDevice
from recognizers.digit import DigitReader
from scenes import SceneEvent, SceneStatus
from scenes.ingame import WaveScene
from scenes.contexttest import TestSceneContext
from utils.images import Frame

COLORS = [
	Color.ORANGE,
	Color.BLUE,
	Color.PINK,
	Color.PURPLE,
	Color.SUNYELLOW,
	Color.YELLOW,
]

class TestWaveScene(IsolatedAsyncioTestCase):
	@classmethod
	def setUpClass(cls):
		currentDir = Path(__file__)
		sourceDir  = next(p for p in currentDir.parents if p.name == 'src')
		chdir(sourceDir)

		device = selectDevice('cpu')
		reader = DigitReader(device)
		cls.__ctx   = TestSceneContext()
		cls.__scene = WaveScene(reader)

	@parameterized.expand([[color] for color in COLORS])
	async def test_analysisColor(self, color: Color):
		filepath = env.DEV_ASSET_PATH.format(f'other/color_{color.name}')

		data = self.__scene.setup()
		frame = Frame(filepath=filepath)

		ret = await self.__scene.analysis(self.__ctx, data, frame)
		self.assertEqual(ret, SceneStatus.CONTINUE)
		self.assertEqual(self.__ctx.message['event'], SceneEvent.GAME_UPDATE.value)
		self.assertEqual(self.__ctx.message['color'], color.value.name, color.value)

	@parameterized.expand([
		('color_orange01', Color.ORANGE, True,  True, False, True),
		('test_dead00',    Color.YELLOW, False, True, True,  True),
		('color_blue',     Color.BLUE,   False, True, True,  True),
		('bad03',          Color.BLUE,   True,  True, True,  True),
		('color_pink',     Color.PINK,   True,  True, True,  True),
	])
	async def test_analysisAlive(self, filename: str, color: Color, a0: bool, a1: bool, a2: bool, a3: bool):
		filepath = env.DEV_ASSET_PATH.format(f'other/{filename}')
		frame = Frame(filepath=filepath)

		data = self.__scene.setup()
		data['color'] = color

		ret = await self.__scene.analysis(self.__ctx, data, frame)
		self.assertEqual(ret, SceneStatus.CONTINUE)
		self.assertEqual(self.__ctx.message['event'], SceneEvent.GAME_UPDATE.value)
		self.assertEqual(self.__ctx.message['players'][0]['alive'], a0)
		self.assertEqual(self.__ctx.message['players'][1]['alive'], a1)
		self.assertEqual(self.__ctx.message['players'][2]['alive'], a2)
		self.assertEqual(self.__ctx.message['players'][3]['alive'], a3)

	@parameterized.expand([
		('gegg_all',       True,  True,  True,  True),
		('gegg_center',    False, True,  True,  False),
		('gegg_left',      True,  True,  False, False),
		('gegg_right',     False, False, True,  True),
		('gegg_single1',   True,  False, False, False),
		('gegg_single3',   False, False, True,  False),
		('gegg_single4',   False, False, False, True),
		('gegg_skipright', True,  False, True,  False),
	])
	async def test_analysisGegg(self, filename: str, a0: bool, a1: bool, a2: bool, a3: bool):
		filepath = env.DEV_ASSET_PATH.format(f'other/{filename}')
		frame = Frame(filepath=filepath)

		data = self.__scene.setup()

		ret = await self.__scene.analysis(self.__ctx, data, frame)
		self.assertEqual(ret, SceneStatus.CONTINUE)
		self.assertEqual(self.__ctx.message['event'], SceneEvent.GAME_UPDATE.value)
		self.assertEqual(self.__ctx.message['players'][0]['gegg'], a0)
		self.assertEqual(self.__ctx.message['players'][1]['gegg'], a1)
		self.assertEqual(self.__ctx.message['players'][2]['gegg'], a2)
		self.assertEqual(self.__ctx.message['players'][3]['gegg'], a3)
