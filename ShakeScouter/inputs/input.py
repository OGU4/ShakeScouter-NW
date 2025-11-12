# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import numpy as np

from abc import abstractmethod
from typing import Awaitable, Callable

class Input:
	@abstractmethod
	async def run(self, callback: Callable[[np.ndarray], Awaitable[bool]]) -> None:
		raise NotImplementedError()
