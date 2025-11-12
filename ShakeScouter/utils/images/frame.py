# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import cv2 as cv
import numpy as np

from math import ceil, floor
from numpy.typing import NDArray
from pathlib import Path
from time import strftime
from typing import Optional

from ShakeScouter.constants import screen
from ShakeScouter.utils import debug_flags
from ShakeScouter.utils.debug_io import debug_log, debug_save
from ShakeScouter.utils.images.model import PartInfo, RectF
from ShakeScouter.utils.images.filters.filter import Filter

TELEMETRY_DIR = Path(__file__).resolve().parents[3] / '.telemetry'

class Frame:
	__image: NDArray[np.uint8]

	def __init__(self, **kwargs) -> None:
		if 'raw' in kwargs:
			self.__image = kwargs['raw']
		elif 'filepath' in kwargs:
			image = cv.imread(kwargs['filepath'], cv.IMREAD_ANYCOLOR)
			if image is None:
				raise TypeError(f'Image is not found: {kwargs['filepath']}')
			if image.dtype != np.uint8:
				raise TypeError(f'Image type is not np.uint8')
			self.__image = image.astype(np.uint8)
		else:
			raise TypeError('At least the "raw" or "filepath" is required')

	@property
	def native(self) -> NDArray[np.uint8]:
		return self.__image

	def apply(self, partInfo: PartInfo) -> NDArray[np.uint8]:
		isWavePart = partInfo is screen.WAVE_PART
		timestamp = strftime('%Y%m%d-%H%M%S') if isWavePart else None
		subimage = self.__subimage(partInfo['area'])
		if isWavePart:
			Frame.__logWaveDebug('apply_in', subimage, timestamp)
		filtered = Frame.__filter(subimage, partInfo['filters'])
		if isWavePart:
			Frame.__logWaveDebug('apply_out', filtered, timestamp)
		return filtered

	def filter(self, filters: list[Filter]) -> NDArray[np.uint8]:
		image = Frame.__filter(self.__image, filters)
		return image

	def subimage(self, rect: RectF) -> 'Frame':
		subimage = self.__subimage(rect)
		newFrame = Frame(raw=subimage)
		return newFrame

	def __subimage(self, rect: RectF) -> NDArray[np.uint8]:
		if rect['left'] < 0 or rect['left'] > 1:
			raise ValueError('"rect[\'left\']" must be between 0 and 1')
		if rect['top'] < 0 or rect['top'] > 1:
			raise ValueError('"rect[\'top\']" must be between 0 and 1')
		if rect['right'] < 0 or rect['right'] > 1:
			raise ValueError('"rect[\'right\']" must be between 0 and 1')
		if rect['bottom'] < 0 or rect['bottom'] > 1:
			raise ValueError('"rect[\'bottom\']" must be between 0 and 1')

		image = self.__image
		height, width = image.shape[:2]
		top = floor(rect['top'] * height)
		bottom = ceil(rect['bottom'] * height)
		left = floor(rect['left'] * width)
		right = ceil(rect['right'] * width)

		subimage = image[top:bottom, left:right]
		return subimage

	def update(self, raw: NDArray[np.uint8]):
		self.__image = raw

	@staticmethod
	def __filter(src: NDArray[np.uint8], filters: list[Filter]) -> NDArray[np.uint8]:
		image = src
		for idx, filterInstance in enumerate(filters):
			image = filterInstance.apply(image)
			if debug_flags.WAVE_DEBUG:
				valueMin = int(image.min()) if image.size else 0
				valueMax = int(image.max()) if image.size else 0
				valueMean = float(image.mean()) if image.size else 0.0
				if image.size:
					if image.ndim == 2:
						nonzero = int(cv.countNonZero(image))
					else:
						gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
						nonzero = int(cv.countNonZero(gray))
				else:
					nonzero = 0
				className = filterInstance.__class__.__name__
				debug_log(f'[DEBUG] filter#{idx} {className}: dtype={image.dtype}, shape={image.shape}, min={valueMin}, max={valueMax}, mean={valueMean}, nonzero={nonzero}')
				if image.shape[:2] in {(45, 200), (45, 128)}:
					timestamp = strftime('%Y%m%d-%H%M%S')
					filename = TELEMETRY_DIR / f'wave_step_{idx:02d}_{className}_{timestamp}.png'
					debug_save(filename, image)
		return image

	@staticmethod
	def __logWaveDebug(label: str, image: NDArray[np.uint8], timestamp: Optional[str]) -> None:
		if not debug_flags.WAVE_DEBUG:
			return
		if timestamp is None:
			timestamp = strftime('%Y%m%d-%H%M%S')
		valueMin = int(image.min()) if image.size else 0
		valueMax = int(image.max()) if image.size else 0
		valueMean = float(image.mean()) if image.size else 0.0
		if image.size:
			if image.ndim == 2:
				nonzero = int(cv.countNonZero(image))
			else:
				gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
				nonzero = int(cv.countNonZero(gray))
		else:
			nonzero = 0
		debug_log(f'[DEBUG] {label} stats: dtype={image.dtype}, shape={image.shape}, min={valueMin}, max={valueMax}, mean={valueMean}, nonzero={nonzero}')
		filename = TELEMETRY_DIR / f'wave_{label}_{timestamp}.png'
		debug_save(filename, image)
