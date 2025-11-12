# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import cv2 as cv
import numpy as np

from utils.images.filters.filter import Filter

class Threshold(Filter):
	__threshold: float
	__maxValue: float
	__type: int

	def __init__(
		self,
		threshold: float,
		maxValue: float,
		type: int = cv.THRESH_BINARY,
	) -> None:
		self.__threshold = threshold
		self.__maxValue  = maxValue
		self.__type      = type

	def apply(self, image: np.ndarray) -> np.ndarray:
		_, binary = cv.threshold(
			image,
			self.__threshold,
			self.__maxValue,
			self.__type
		)

		return binary
