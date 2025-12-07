# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import numpy as np

from numpy.typing import NDArray

from ShakeScouter.utils.images.filters import *
from ShakeScouter.utils.images.model import PartInfo, RectF

# Message in Lobby
MESSAGE_PART = PartInfo(
	area = RectF(
		left   =  750 / 1920,
		top    =  545 / 1080,
		right  = 1170 / 1920,
		bottom =  600 / 1080,
	),
	filters = [
		HSV(),
		InRange(
			lower=np.array([  0,   0, 179]),  # V=70%
			upper=np.array([180,  38, 255]),
		),
	],
)

# Logo in Introduction
LOGO_PART = PartInfo(
	area = RectF(
		left   =   48 / 1920,
		top    =  860 / 1080,
		right  =  340 / 1920,
		bottom =  988 / 1080,
	),
	filters = [
		# Grayscale(),
		# ScaleAbs(1.6, 32),
		# Laplacian(5),
		# Threshold(250, 255),

		Blur((5, 5)),
		HSV(),
		InRange(
			lower=np.array([  0,   0, 179]),  # V=70%
			upper=np.array([ 40, 255, 255]),
		),
	],
)

# Stage Name in Introduction
STAGE_NAME_PART = PartInfo(
	area = RectF(
		left   =   78 / 1920,  # 4%
		top    =  986 / 1080,
		right  =  500 / 1920,
		bottom = 1039 / 1080,
	),
	filters = [
		HSV(),
		InRange(
			lower=np.array([  0,   0, 230]),  # V=90%
			upper=np.array([180,  38, 255]),
		),
	],
)

# King Name in Xtrawave
KING_NAME_PART = PartInfo(
	area = RectF(
		left   =   40 / 1920,
		top    =  790 / 1080,
		right  =  810 / 1920,
		bottom = 1040 / 1080,
	),
	filters = [
		InRange(
			lower=np.array([235, 235, 235]),
			upper=np.array([255, 255, 255]),
		),
	],
)

# Wave in Game
WAVE_PART = PartInfo(
	area = RectF(
		left   =  38 / 1920,
		top    =  35 / 1080,
		right  = 238 / 1920,
		bottom =  80 / 1080,
	),
	filters = [
		HSV(),
		InRange(
			lower=np.array([  0,   0, 200]),
			upper=np.array([180,  80, 255]),
		),
	],
)

def removeNumberAreaFromWaveImage(waveImage: NDArray[np.uint8]) -> NDArray[np.uint8]:
	return waveImage[:, :-72]

# Timer Counter in Game
TIMER_PART = PartInfo(
	area = RectF(
		left   =  70 / 1920,
		top    =  93 / 1080,
		right  = 190 / 1920,
		bottom = 153 / 1080,
	),
	filters = [
		Grayscale(),
		Threshold(179, 255),  # 70%
	],
)

# Amount in Game
AMOUNT_PART = PartInfo(
	area = RectF(
		left   = 277 / 1920,
		top    =  98 / 1080,
		right  = 337 / 1920,
		bottom = 148 / 1080,
	),
	filters = [
		HSV(),
		InRange(
			lower=np.array([  0,   0, 204]),  # V=80%
			upper=np.array([180,  77, 255]),
		),
	],
)

# Quota in Game
QUOTA_PART = PartInfo(
	area = RectF(
		left   = 362 / 1920,
		top    =  98 / 1080,
		right  = 422 / 1920,
		bottom = 148 / 1080,
	),
	filters = [
		HSV(),
		InRange(
			lower=np.array([  0,   0, 204]),  # V=80%
			upper=np.array([180,  77, 255]),
		),
	],
)

# Players in game
PLAYERS_PART = PartInfo(
	area = RectF(
		left   =  54 / 1920,
		top    = 172 / 1080,
		right  = 337 / 1920,
		bottom = 257 / 1080,
	),
	filters = [
		HSV(),
	],
)

# Signal in Game
SIGNAL_PART = PartInfo(
	area = RectF(
		left   =   46 / 1920,
		top    = 1015 / 1080,
		right  =  141 / 1920,
		bottom = 1050 / 1080,
	),
	filters = [
		HSV(),
		InRange(
			lower=np.array([  0,   0, 230]),  # V=90%
			upper=np.array([180,  38, 255]),
		),
	],
)

# Golden Egg in Result
GEGG_PART = PartInfo(
	area = RectF(
		left   =  786 / 1920,
		top    =   56 / 1080,
		right  =  886 / 1920,
		bottom =  106 / 1080,
	),
	filters = [
		HSV(),
		InRange(
			lower=np.array([  0,   0, 204]),  # V=80%
			upper=np.array([180,  38, 255]),
		),
	],
)

# Power Egg in Result
PEGG_PART = PartInfo(
	area = RectF(
		left   =  1106 / 1920,
		top    =    56 / 1080,
		right  =  1256 / 1920,
		bottom =   106 / 1080,
	),
	filters = [
		HSV(),
		InRange(
			lower=np.array([  0,   0, 204]),  # V=80%
			upper=np.array([180,  38, 255]),
		),
	],
)

# "Wave 1" in Result
WAVE1_PART = PartInfo(
	area = RectF(
		left   =  450 / 1920,
		top    =  350 / 1080,
		right  =  700 / 1920,
		bottom =  460 / 1080,
	),
	filters = [
		HSV(),
		InRange(
			lower=np.array([  0,   0,   0]),
			upper=np.array([180, 255,  77]),  # V=30%
		),
	],
)

# "Mr. Grizz" in Result
GRIZZ_PART = PartInfo(
	area = RectF(
		left   =  420 / 1920,
		top    =  805 / 1080,
		right  =  590 / 1920,
		bottom =  840 / 1080,
	),
	filters = [
		Grayscale(),
		Threshold(89, 255),  # 35%
	],
)

# Connection Message in Game
UNSTABLE_PART = PartInfo(
	area = RectF(
		left   =  480 / 1920,
		top    =  350 / 1080,
		right  = 1440 / 1920,
		bottom =  440 / 1080,
	),
	filters = [
		Grayscale(),
		Threshold(204, 255),  # 80%
	],
)

# Error Message in Game
ERROR_PART = PartInfo(
	area = RectF(
		left   =  750 / 1920,
		top    =  425 / 1080,
		right  = 1170 / 1920,
		bottom =  480 / 1080,
	),
	filters = [
		HSV(),
		InRange(
			lower=np.array([  0,   0, 204]),  # V=80%
			upper=np.array([180,  38, 255]),
		),
	],
)
