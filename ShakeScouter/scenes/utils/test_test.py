# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from unittest import IsolatedAsyncioTestCase

from scenes import SceneStatus
from scenes.contexttest import TestSceneContext
from scenes.utils.test import *

class TestTestScene(IsolatedAsyncioTestCase):
	@classmethod
	def setUpClass(cls):
		cls.__ctx = TestSceneContext()

	async def test_analysisTest(self):
		scene = TestScene(SceneStatus.DONE)

		data = scene.setup()
		ret = await scene.analysis(self.__ctx, data, None)
		self.assertEqual(ret, SceneStatus.DONE)

	async def test_analysisDone(self):
		scene = CountDownTestScene(1)

		data = scene.setup()
		self.assertEqual(data['count'], 1)

		# count = 1
		ret = await scene.analysis(self.__ctx, data, None)
		self.assertEqual(ret, SceneStatus.FALSE)
		self.assertEqual(data['count'], 0)

		# count = 0
		ret = await scene.analysis(self.__ctx, data, None)
		self.assertEqual(ret, SceneStatus.DONE)
		self.assertEqual(data['count'], 0)
