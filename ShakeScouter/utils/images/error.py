# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import cv2 as cv
import numpy as np

from enum import Enum
from numpy.typing import NDArray
from typing import Callable, Optional

class ErrorType(Enum):
	BITWISE       = 'bitwise'
	MEAN_ABSOLUTE = 'mean_absolute'
	MEAN_SQUARE   = 'mean_square'

def errorBWE(image: NDArray[np.uint8], template: NDArray[np.uint8]) -> float:
	mask  = cv.bitwise_and(image, template)
	count = cv.countNonZero(mask)
	error = count / image.size
	return error

def errorMAE(image: NDArray[np.uint8], template: NDArray[np.uint8]) -> float:
	diff  = cv.absdiff(image, template)
	error = cv.mean(diff)[0] / 255.0
	return error

def errorMSE(image: NDArray[np.uint8], template: NDArray[np.uint8]) -> float:
	diff  = cv.absdiff(image, template)
	power = cv.pow(diff, 2)
	error = cv.mean(power)[0] / (255.0 ** 2)
	return error

def errors(
	image: NDArray[np.uint8],
	templates: dict[str, NDArray[np.uint8]],
	type: ErrorType = ErrorType.MEAN_ABSOLUTE,
) -> dict[str, float]:
	errorFn: Callable[[NDArray[np.uint8], NDArray[np.uint8]], float]
	match type:
		case ErrorType.BITWISE:
			errorFn = errorBWE
		case ErrorType.MEAN_ABSOLUTE:
			errorFn = errorMAE
		case ErrorType.MEAN_SQUARE:
			errorFn = errorMSE
		case _:
			raise ValueError('"type" is unknown value')

	errors = {
		key: errorFn(image, template)
		for key, template in templates.items()
	}
	return errors

def getMinErrorKey(
	image: NDArray[np.uint8],
	templates: dict[str, NDArray[np.uint8]],
	minError: float = 0.9,
	type: ErrorType = ErrorType.MEAN_ABSOLUTE,
) -> Optional[str]:
	errorValues = {
		key: error
		for key, error in errors(image, templates, type).items()
		if error <= minError
	}

	if len(errorValues) == 0:
		return None

	key = min(errorValues, key=lambda key: errorValues[key])
	return key
