# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from torch import cuda, device

def selectDevice(dev: str) -> device:
	match dev:
		case 'cpu':
			return device('cpu')
		case 'cuda':
			if not cuda.is_available():
				raise TypeError('device "cuda" is not available')
			return device('cuda:0')
		case _:
			return device('cuda:0' if cuda.is_available() else 'cpu')
