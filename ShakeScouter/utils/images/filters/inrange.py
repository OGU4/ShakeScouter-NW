# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import cv2 as cv
import numpy as np

from pathlib import Path
from time import strftime

from ShakeScouter.utils import debug_flags
from ShakeScouter.utils.debug_io import debug_log, debug_save
from ShakeScouter.utils.images.filters.filter import Filter

TELEMETRY_DIR = Path(__file__).resolve().parents[3] / '.telemetry'

class InRange(Filter):
	__lower: np.ndarray
	__upper: np.ndarray

	def __init__(
		self,
		lower: np.ndarray,
		upper: np.ndarray,
	) -> None:
		self.__lower = lower
		self.__upper = upper

	def apply(self, image: np.ndarray) -> np.ndarray:
		if debug_flags.WAVE_DEBUG:
			debug_log(f'[DEBUG] InRange: dtype={image.dtype}, shape={image.shape}, lower={self.__lower.tolist()}, upper={self.__upper.tolist()}')
		mask = cv.inRange(image, self.__lower, self.__upper)
		if debug_flags.WAVE_DEBUG:
			if mask.size:
				valueMin = int(mask.min())
				valueMax = int(mask.max())
				valueMean = float(mask.mean())
				nonzero = int(cv.countNonZero(mask))
			else:
				valueMin = valueMax = nonzero = 0
				valueMean = 0.0
			debug_log(f'[DEBUG] InRange result: min={valueMin}, max={valueMax}, mean={valueMean}, nonzero={nonzero}')
			if mask.shape[:2] in {(45, 200), (45, 128)}:
				timestamp = strftime('%Y%m%d-%H%M%S')
				filename = TELEMETRY_DIR / f'inrange_mask_{timestamp}.png'
				debug_save(filename, mask)
		return mask
