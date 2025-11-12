# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from os import chdir
from os.path import dirname, realpath

def forceCwd(file: str):
	p = dirname(realpath(file))
	chdir(p)
