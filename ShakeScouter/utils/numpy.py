# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import numpy as np

def mode(arr: np.ndarray) -> np.intc:
	# Get unique values and counts
	uniqueValues, counts = np.unique(arr, return_counts=True)

	# Find index for mode
	modeIndex = np.argmax(counts)

	# Get mode value
	modeValue = uniqueValues[modeIndex]

	return modeValue

def packBits(arr: np.ndarray, reverse=False) -> np.int64:
	p = np.power(2, np.arange(arr.shape[-1]), dtype=np.int64)
	if not reverse:
		p = p[::-1]
	return np.dot(arr, p)

def unpackBits(bits: int) -> np.ndarray:
	boolArray = np.array([
		bool(bits & (1 << i))
		for i in range(63, -1, -1)
	])
	return boolArray

def hammingDistance(hash1: np.ndarray, hash2: np.ndarray) -> np.int32:
	distance = np.sum(hash1 != hash2)
	return distance
