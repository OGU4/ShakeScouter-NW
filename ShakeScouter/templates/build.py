#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import cv2 as cv
import numpy as np

from dataclasses import dataclass
from os import chdir
from os.path import dirname, join, realpath
from sys import path
from typing import Callable, Optional

# Set current working directory.
chdir(realpath(join(dirname(__file__), '../ShakeScouter/')))
path.append('.')

from ShakeScouter.constants import assets, env, screen
from ShakeScouter.utils.images import Frame
from ShakeScouter.utils.images.model import PartInfo

@dataclass
class AssetData:
	name: str
	input: str
	output: str
	part: PartInfo
	fn: Optional[Callable[[np.ndarray], np.ndarray]] = None

	def buildTemplate(self):
		outputPath = env.template_path(self.output)
		if outputPath.exists():
			print(f'[{self.name}] Mask file exists (path: {outputPath})')
		else:
			inputPath = env.DEV_ASSET_PATH.format(self.input)
			image = Frame(filepath=inputPath).apply(self.part)
			if self.fn is not None:
				image = self.fn(image)
			cv.imwrite(str(outputPath), image, [cv.IMWRITE_PNG_COMPRESSION, 0])


ASSET_INFO: list[AssetData] = [
	# Dialog Mask
	AssetData('Matchmaking', 'other/start',                  'start',              screen.MESSAGE_PART),

	# Intro Logo Mask
	AssetData('Intro Logo',  'stages/104_barnacle_and_dime', 'logo',               screen.LOGO_PART),

	# Wave Masks
	AssetData('Wave "n"',    'counts/count100',              'wave',               screen.WAVE_PART, lambda i: i[:, :-72]),
	AssetData('Extra Wave',  'other/wave-extra00',           'wave_ex',            screen.WAVE_PART),

	# Signal Mask
	#AssetData('Signal',      'other/gegg_all',               'signal',             screen.SIGNAL_PART),

	# Kings Masks
	AssetData('Cohozuna',    'kings/cohozuna00',             'kings/cohozuna',     screen.KING_NAME_PART),
	AssetData('Cohozuna',    'kings/horrorboros01',          'kings/horrorboros',  screen.KING_NAME_PART),
	AssetData('Cohozuna',    'kings/megalodontia01',         'kings/megalodontia', screen.KING_NAME_PART),
	AssetData('Cohozuna',    'kings/triumvirate04',          'kings/triumvirate',  screen.KING_NAME_PART),

	# Result Masks
	AssetData('Mr. Grizz',   'other/result02',               'mrgrizz',            screen.GRIZZ_PART),

	# Unstable and Error Masks
	AssetData('Unstable',    'other/unstable',               'unstable',           screen.UNSTABLE_PART),
	AssetData('Error',       'other/error',                  'error',              screen.ERROR_PART),
]

def buildStageTemplate():
	stageTemplateDirPath = env.TEMPLATE_DIR / 'stages'
	stageTemplateDirPath.mkdir(parents=True, exist_ok=True)

	for stageKey in assets.stageKeys:
		outputPath = env.template_path(f'stages/{stageKey}')
		if outputPath.exists():
			print(f'Stage mask file exists (path: {outputPath})')
		else:
			inputPath = env.DEV_ASSET_PATH.format(f'stages/{stageKey}')
			image = Frame(filepath=inputPath).apply(screen.STAGE_NAME_PART)
			cv.imwrite(str(outputPath), image, [cv.IMWRITE_PNG_COMPRESSION, 0])

def main():
	for asset in ASSET_INFO:
		asset.buildTemplate()
	buildStageTemplate()

if __name__ == "__main__":
	main()
