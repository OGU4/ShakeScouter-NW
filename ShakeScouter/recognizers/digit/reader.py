# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import cv2 as cv
import numpy as np
import torch

from functools import reduce
from typing import Optional

from ShakeScouter.constants import env
from ShakeScouter.recognizers.digit.cnn import DigitCNN
from ShakeScouter.recognizers.digit.normalize import normalizeDigitImage
from ShakeScouter.utils.images import detectBbox

class DigitReader:
	def __init__(self, device: torch.device) -> None:
		model = DigitCNN()
		model.load_state_dict(torch.load(env.DIGIT_MODEL_PATH, map_location=device))
		self.__model = model

	def read(self, image: np.ndarray) -> Optional[int]:
		def convertItem(image: np.ndarray, bbox: cv.typing.Rect) -> torch.Tensor:
			x, y, width, height = bbox

			# Get each image
			eachImage = image[y:y + height, x:x + width]

			# Normalize digit image
			normImage = normalizeDigitImage(eachImage)

			# Add dims: (16, 20) to (1, 16, 20)
			input = normImage.unsqueeze(0)

			return input

		def recognize(pyInputs: list[torch.Tensor]) -> int:
			# Get inputs as Tensor
			inputs = torch.stack(pyInputs)

			# Get predicted data
			outputs = self.__model(inputs)
			_, predicted = torch.max(outputs.data, 1)

			# Get predicted integer
			predictedInt = reduce(lambda n, i: 10 * n + predicted[i].item(), range(len(pyInputs)), 0)

			return predictedInt

		# Calc min height
		minHeight = round(0.6 * image.shape[0])

		# Get inputs
		inputs = [
			convertItem(image, bbox)
			for bbox in detectBbox(image, minHeight)
		]

		# Check empty
		if len(inputs) == 0:
			return None

		# Get integer
		integer = recognize(inputs)

		return integer
