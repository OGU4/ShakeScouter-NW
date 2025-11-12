# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from unittest import IsolatedAsyncioTestCase

from scenes import SceneStatus
from scenes.contexttest import TestSceneContext
from scenes.utils import Root
from scenes.utils.test import *

class TestRootScene(IsolatedAsyncioTestCase):
	@classmethod
	def setUpClass(cls):
		cls.__ctx = TestSceneContext()

	async def test_analysisProd(self):
		scene = Root(
			TestScene(SceneStatus.DONE),
			devMode=False
		)

		data = scene.setup()
		ret = await scene.analysis(self.__ctx, data, None)
		self.assertEqual(ret, SceneStatus.CONTINUE)

	async def test_analysisDev(self):
		scene = Root(
			TestScene(SceneStatus.DONE),
			devMode=True
		)

		data = scene.setup()
		ret = await scene.analysis(self.__ctx, data, None)
		self.assertEqual(ret, SceneStatus.DONE)
