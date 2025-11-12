# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import numpy as np
import torch

from torch.utils.data import Dataset
from typing import Optional

from constants import env, screen
from recognizers.digit.model import DatasetAsset, DatasetRoot
from recognizers.digit.normalize import normalizeDigitImage

from utils import calcDigits, getDigit
from utils.images import detectBbox, Frame

class DigitDataset(Dataset):
	def __init__(self, inputs: torch.Tensor, labels: torch.Tensor):
		if len(inputs) != len(labels):
			raise ValueError('The lengths of "inputs" and "labels" must match')
		self.__inputs = inputs
		self.__labels = labels

	def __len__(self):
		return len(self.__inputs)

	def __getitem__(self, index):
		input = self.__inputs[index]
		label = self.__labels[index]
		return input, label

def addData(
	dataset: list[list[torch.Tensor]],
	subimage: np.ndarray,
	value: int,
	message: str,
):
	# Get digits
	digits = calcDigits(value)

	# Detect bbox
	bboxes = detectBbox(subimage)

	# Fail if bbox count != digits
	if len(bboxes) != digits:
		print(message)
		return

	# Add data
	for k in range(digits):
		number = getDigit(value, k)
		x, y, width, height = bboxes[digits - k - 1]
		eachDigitImage = subimage[y:y + height, x:x + width]
		normDigitImage = normalizeDigitImage(eachDigitImage)
		dataset[number].append(normDigitImage)

def aggregateAsset(config: DatasetAsset, filepath: str, dataset: list[list[torch.Tensor]], index: int):
	frame = Frame(filepath=filepath)

	if config.timer is not None:
		timerImage = frame.apply(screen.TIMER_PART)
		i = index if config.timer == 'range' else config.timer
		addData(dataset, timerImage, i, message=f'Cannot split timer image (filepath: {filepath})')

	if config.amount is not None:
		amountImage = frame.apply(screen.AMOUNT_PART)
		i = index if config.amount == 'range' else config.amount
		addData(dataset, amountImage, i, message=f'Cannot split amount image (filepath: {filepath})')

	if config.quota is not None:
		quotaImage = frame.apply(screen.QUOTA_PART)
		i = index if config.quota == 'range' else config.quota
		addData(dataset, quotaImage, i, message=f'Cannot split quota image (filepath: {filepath})')

def aggregateAssets(config: DatasetRoot) -> list[list[torch.Tensor]]:
	dataset: list[list[torch.Tensor]] = [[] for _ in range(10)]

	for asset in config.items:
		if asset.range is None:
			filepath = f'{config.root_dir}{asset.filename}'
			aggregateAsset(asset, filepath, dataset, 0)
		else:
			start = asset.range.start or 0
			stop  = asset.range.stop
			step  = asset.range.step  or 1

			for i in range(start, stop, step):
				filepath = f'{config.root_dir}{asset.filename}'.format(i)
				aggregateAsset(asset, filepath, dataset, i)

	return dataset

def buildDataset(config: DatasetRoot) -> tuple[DigitDataset, DigitDataset]:
	dataset = aggregateAssets(config)
	c = 4

	trainInputs: torch.Tensor = torch.zeros(10 * c, env.DIGIT_HEIGHT, env.DIGIT_WIDTH, dtype=torch.float32)
	trainLabels: torch.Tensor = torch.zeros(10 * c, dtype=torch.int64)

	testInputs: list[torch.Tensor] = []
	testLabels: list[int] = []

	for i, d in enumerate(dataset):
		for j, v in enumerate(d):
			if j < c:
				trainInputs[c * i + j] = v
				trainLabels[c * i + j] = i
			else:
				testInputs.append(v)
				testLabels.append(i)

	trainDataset = DigitDataset(trainInputs, trainLabels)
	testDataset  = DigitDataset(torch.stack(testInputs), torch.tensor(testLabels, dtype=torch.int64))

	return trainDataset, testDataset
