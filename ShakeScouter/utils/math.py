# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from math import log10

def calcDigits(n: int) -> int:
	if n == 0:
		return 1
	return int(log10(n)) + 1

def getDigit(n: int, index: int) -> int:
	return (n // 10 ** index) % 10
