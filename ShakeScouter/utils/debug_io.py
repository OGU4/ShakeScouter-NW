import cv2 as cv

from pathlib import Path

from ShakeScouter.utils import debug_flags


def debug_log(message: str) -> None:
	if debug_flags.WAVE_DEBUG:
		print(message)


def debug_save(path: Path, image) -> None:
	if debug_flags.WAVE_DEBUG:
		path.parent.mkdir(parents=True, exist_ok=True)
		cv.imwrite(str(path), image)
