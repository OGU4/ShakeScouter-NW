# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import numpy as np

from dataclasses import dataclass
from enum import Enum

@dataclass
class ColorData:
	name: str
	colorA: np.ndarray
	colorB: np.ndarray
	hueA: float

class Color(Enum):
	# Use training mode only
	# DEFAULT = ColorData(
	# 	'default',
	# 	np.array([ 49,  84, 201]),
	# 	np.array([ 75, 100,   3]),
	# 	6.91,
	# )
	BLUE = ColorData(
		'blue',
		np.array([243,  91,  67]),
		np.array([ 99, 126,   6]),
		115.91,
	)
	ORANGE = ColorData(
		'orange',
		np.array([ 33,  75, 196]),
		np.array([100, 130,   9]),
		7.73,
	)
	PINK = ColorData(
		'pink',
		np.array([132,  65, 198]),
		np.array([116, 110,  13]),
		164.885,
	)
	PURPLE = ColorData(
		'purple',
		np.array([234,  97, 147]),
		np.array([ 94, 122,  10]),
		130.95,
	)
	SUNYELLOW = ColorData(
		'sunyellow',
		np.array([ 36, 160, 221]),
		np.array([100, 130,   9]),
		20.11,
	)
	YELLOW = ColorData(
		'yellow',
		np.array([ 51, 217, 180]),
		np.array([113, 138,   9]),
		36.685,
	)
	SUPPORT_YELLOW = ColorData(
		'support_yellow',
		np.array([ 18, 209, 221]),
		np.array([139, 123,   4]),
		28.225,
	)

	@property
	def colorA(self) -> np.ndarray:
		return self.value.colorA

	@property
	def colorB(self) -> np.ndarray:
		return self.value.colorB

	@property
	def hueA(self) -> float:
		return self.value.hueA

	@classmethod
	def all(cls):
		return [c for c in cls]

	@classmethod
	def keys(cls) -> list[str]:
		return cls._member_names_

	@classmethod
	def values(cls) -> list[ColorData]:
		return [c.value for c in cls]

	@classmethod
	def hues(cls) -> np.ndarray:
		return np.array([c.hueA for c in cls])
