# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from unittest import IsolatedAsyncioTestCase

from ShakeScouter.scenes import SceneStatus
from ShakeScouter.scenes.contexttest import TestSceneContext
from ShakeScouter.scenes.utils import PriorityParallel
from ShakeScouter.scenes.utils.test import *

class TestPriorityParallelScene(IsolatedAsyncioTestCase):
	@classmethod
	def setUpClass(cls):
		cls.__ctx = TestSceneContext()

	async def test_analysis(self):
		scene = PriorityParallel([
			(0, TestScene(SceneStatus.CONTINUE)),
			(1, CountDownTestScene(1)),
		])

		data = scene.setup()
		self.assertEqual(data['priority'], -1)
		self.assertEqual(data['children'][1]['count'], 1)

		ret = await scene.analysis(self.__ctx, data, None)
		self.assertEqual(ret, SceneStatus.CONTINUE)
		self.assertEqual(data['priority'], -1)
		self.assertEqual(data['children'][1]['count'], 0)

		ret = await scene.analysis(self.__ctx, data, None)
		self.assertEqual(ret, SceneStatus.DONE)
		self.assertEqual(data['priority'], 2)
		self.assertEqual(data['children'][1]['count'], 0)
