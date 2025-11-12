# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import cv2 as cv
import numpy as np

from math import ceil, floor

def calcBbox(bbox: cv.typing.Rect, top: int, height: int) -> cv.typing.Rect:
	x, _, width, _ = bbox
	cx = x + 0.5 * width
	realWidth = round(0.333333 * height)

	left = max(0, floor(cx - realWidth))
	right = ceil(cx + realWidth)
	return left, top, right - left, height

def detectBbox(image: np.ndarray, minHeight: int = 8) -> list[cv.typing.Rect]:
	# Find contours
	contours, _ = cv.findContours(image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

	# Calc bounding boxes
	bboxes = [cv.boundingRect(c) for c in contours]

	# Check empty
	if len(bboxes) == 0:
		return bboxes

	# Normalize top and bottom
	top = min(map(lambda t: t[1], bboxes))
	bottom = max(map(lambda t: t[1] + t[3], bboxes))
	height = bottom - top

	# Sort and apply normalized data to bounding boxes
	patchedBboxes: list[cv.typing.Rect] = [
		calcBbox(bbox, top, height)
		for bbox in sorted(bboxes, key=lambda r: r[0])
		if bbox[3] >= minHeight
	]
	return patchedBboxes

