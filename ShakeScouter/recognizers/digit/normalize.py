# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import cv2 as cv
import numpy as np
import torch

from ShakeScouter.constants import env

DIGIT_SIZE = (env.DIGIT_WIDTH, env.DIGIT_HEIGHT)

def normalizeDigitImage(image: np.ndarray) -> torch.Tensor:
	# Resize char image
	resize = cv.resize(image, DIGIT_SIZE, interpolation=cv.INTER_LANCZOS4)

	# Binalyze
	_, binary = cv.threshold(resize, 127, 255, cv.THRESH_BINARY)

	# Convert ndarray to torch.Tensor
	tensor = torch.from_numpy(binary.astype(np.float32))

	return tensor
