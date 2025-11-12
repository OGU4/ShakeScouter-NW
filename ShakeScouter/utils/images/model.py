# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from typing import TypedDict

from utils.images.filters.filter import Filter

class RectF(TypedDict):
	left: float
	top: float
	right: float
	bottom: float

class PartInfo(TypedDict):
	area: RectF
	filters: list[Filter]
