# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import cv2 as cv
import numpy as np

from utils.images.filters.filter import Filter

class Grayscale(Filter):
	def apply(self, image: np.ndarray) -> np.ndarray:
		match len(image.shape):
			case 2:
				return image
			case 3:
				if image.shape[2] == 3:
					return cv.cvtColor(image, cv.COLOR_BGR2GRAY)

		raise TypeError('"image" must be in one of the following formats: BGR or Grayscale')

class HSV(Filter):
	def apply(self, image: np.ndarray) -> np.ndarray:
		if len(image.shape) == 3 and image.shape[2] == 3:
			return cv.cvtColor(image, cv.COLOR_BGR2HSV)
		else:
			raise TypeError('"image" must be in one of the following formats: BGR')

class BGR(Filter):
	def apply(self, image: np.ndarray) -> np.ndarray:
		if len(image.shape) == 3 and image.shape[2] == 3:
			return cv.cvtColor(image, cv.COLOR_BGR2HSV)
		else:
			raise TypeError('"image" must be in one of the following formats: BGR')
