# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from unittest import IsolatedAsyncioTestCase

from scenes import SceneStatus
from scenes.contexttest import TestSceneContext
from scenes.utils import Parallel
from scenes.utils.test import *

class TestParallelScene(IsolatedAsyncioTestCase):
	@classmethod
	def setUpClass(cls):
		cls.__ctx = TestSceneContext()

	async def test_analysisFastDone(self):
		scene = Parallel([
			TestScene(SceneStatus.DONE),
			TestScene(SceneStatus.DONE),
		])

		data = scene.setup()
		ret = await scene.analysis(self.__ctx, data, None)
		self.assertEqual(ret, SceneStatus.DONE)
		self.assertEqual(data[0]['stop'], True)
		self.assertEqual(data[1]['stop'], True)

	async def test_analysisDone(self):
		scene = Parallel([
			TestScene(SceneStatus.DONE),
			CountDownTestScene(1),
		])

		data = scene.setup()

		# count = 1
		ret = await scene.analysis(self.__ctx, data, None)
		self.assertEqual(ret, SceneStatus.CONTINUE)
		self.assertEqual(data[0]['stop'], True)
		self.assertEqual(data[1]['stop'], False)
		self.assertEqual(data[1]['data']['count'], 0)

		# count = 0
		ret = await scene.analysis(self.__ctx, data, None)
		self.assertEqual(ret, SceneStatus.DONE)
		self.assertEqual(data[0]['stop'], True)
		self.assertEqual(data[1]['stop'], True)
		self.assertEqual(data[1]['data']['count'], 0)
