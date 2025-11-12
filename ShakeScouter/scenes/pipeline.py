# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import scenes.utils as su

from recognizers import selectDevice
from recognizers.digit import DigitReader
from scenes import Scene
from scenes.matchmaking import MatchmakingScene
from scenes.ingame import *

def getCorePipeline(dev: str) -> Scene:
	device = selectDevice(dev)
	reader = DigitReader(device)
	pipeline = \
		su.PriorityParallel([
			(0, su.Drop(
				StageScene(),
				rate=2,
			)),
			(1, su.Parallel([
				su.Drop(
					WaveScene(reader),
					rate=2,
				),
				su.Drop(
					KingScene(),
					rate=0.5,
				),
			])),
			(2, su.Drop(
				su.Parallel(
					[
						ResultScene(reader),
						ErrorScene(),
					],
					anyDone=True,
				),
				rate=1,
			)),
		])
	return pipeline

def getDefaultPipeline(device: str, devMode: bool) -> Scene:
	pipeline = \
		su.Root(
			su.Sequential([
				su.Drop(
					MatchmakingScene(),
					rate=2,
				),
				getCorePipeline(device),
			]),
			devMode,
		)
	return pipeline
