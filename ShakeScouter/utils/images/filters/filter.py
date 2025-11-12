# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import numpy as np

from abc import abstractmethod

class Filter:
	@abstractmethod
	def apply(self, image: np.ndarray) -> np.ndarray:
		raise NotImplementedError()
