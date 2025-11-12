# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import cv2 as cv
import numpy as np

from ShakeScouter.utils.images.filters.filter import Filter

class Blur(Filter):
	__ksize: cv.typing.Size

	def __init__(
		self,
		ksize: cv.typing.Size,
	) -> None:
		self.__ksize = ksize

	def apply(self, image: np.ndarray) -> np.ndarray:
		blur = cv.blur(image, self.__ksize)

		return blur
