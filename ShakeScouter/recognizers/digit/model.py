# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin
from typing import Literal, Optional

@dataclass
class DatasetAssetRange(DataClassJsonMixin):
	stop: int
	start: Optional[int] = None
	step: Optional[int] = None

@dataclass
class DatasetAsset(DataClassJsonMixin):
	filename: str
	range: Optional[DatasetAssetRange] = None
	timer: Optional[int | Literal['range']] = None
	amount: Optional[int | Literal['range']] = None
	quota: Optional[int | Literal['range']] = None

@dataclass
class DatasetRoot(DataClassJsonMixin):
	root_dir: str
	items: list[DatasetAsset]
