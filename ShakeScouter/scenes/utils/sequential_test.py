# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from unittest import IsolatedAsyncioTestCase

from ShakeScouter.scenes import SceneStatus
from ShakeScouter.scenes.contexttest import TestSceneContext
from ShakeScouter.scenes.utils import Sequential
from ShakeScouter.scenes.utils.test import *

class TestSequentialScene(IsolatedAsyncioTestCase):
	@classmethod
	def setUpClass(cls):
		cls.__ctx = TestSceneContext()

	async def test_analysisFastDone(self):
		scene = Sequential([
			TestScene(SceneStatus.DONE),
			TestScene(SceneStatus.DONE),
		])

		data = scene.setup()

		# index = 0
		ret = await scene.analysis(self.__ctx, data, None)
		self.assertEqual(ret, SceneStatus.CONTINUE)
		self.assertEqual(data['index'], 1)

		# index = 1
		ret = await scene.analysis(self.__ctx, data, None)
		self.assertEqual(ret, SceneStatus.DONE)
		self.assertEqual(data['index'], 2)

	async def test_analysisDone(self):
		scene = Sequential([
			TestScene(SceneStatus.DONE),
			CountDownTestScene(1),
		])

		data = scene.setup()

		# index = 0, count = 1
		ret = await scene.analysis(self.__ctx, data, None)
		self.assertEqual(ret, SceneStatus.CONTINUE)
		self.assertEqual(data['index'], 1)
		self.assertEqual(data['children'][1]['count'], 1)

		# index = 1, count = 0
		ret = await scene.analysis(self.__ctx, data, None)
		self.assertEqual(ret, SceneStatus.CONTINUE)
		self.assertEqual(data['index'], 1)
		self.assertEqual(data['children'][1]['count'], 0)

		# index = 1, count = 0
		ret = await scene.analysis(self.__ctx, data, None)
		self.assertEqual(ret, SceneStatus.DONE)
		self.assertEqual(data['index'], 2)
		self.assertEqual(data['children'][1]['count'], 0)
