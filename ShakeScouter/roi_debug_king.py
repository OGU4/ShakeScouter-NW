#!/usr/bin/env python3
# Usage example:
#   python -m ShakeScouter.roi_debug_king --video /path/to/input.mp4 --out-dir /path/to/out [--step 2] [--limit 100] [--verbose]

import argparse
import sys
from pathlib import Path

import cv2 as cv
import numpy as np

from ShakeScouter.constants import assets, screen
from ShakeScouter.scenes.base import Scene
from ShakeScouter.scenes.ingame.king import KingScene
from ShakeScouter.utils.images import Frame
from ShakeScouter.utils.images.error import errors, getMinErrorKey

EXPECTED_WIDTH = 1920
EXPECTED_HEIGHT = 1080
LOOSE_WHITE_LOWER = 200
LOOSE_WHITE_UPPER = 255


def _parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description='Debug king-name ROI recognition using KingScene logic.')
	parser.add_argument('--video', required=True, help='Input video path (required).')
	parser.add_argument('--out-dir', required=True, help='Directory to save ROI crops (required).')
	parser.add_argument('--step', type=int, default=1, help='Process every Nth frame (default: 1).')
	parser.add_argument('--limit', type=int, help='Maximum number of processed frames.')
	parser.add_argument('--verbose', action='store_true', help='Print per-template error list each processed frame.')
	parser.add_argument('--loose-white', action='store_true', help='Use relaxed white mask (debug only).')
	return parser.parse_args()


def _ensure_output_dirs(base: Path) -> tuple[Path, Path]:
	ok_dir = base / 'ok'
	ng_dir = base / 'ng'
	ok_dir.mkdir(parents=True, exist_ok=True)
	ng_dir.mkdir(parents=True, exist_ok=True)
	return ok_dir, ng_dir


def _format_err(value):
	return f'{value:.3f}' if value is not None else 'None'


def _save_frame_with_roi(image, rect, frame_idx: int, frame_ms: int, out_dir: Path) -> None:
	# rect: (left, top, right, bottom) in absolute pixels
	x1, y1, x2, y2 = rect
	annotated = image.copy()
	cv.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 3)
	filename = out_dir / f'frame_f{frame_idx:06d}_ms{frame_ms:06d}_roi.png'
	cv.imwrite(str(filename), annotated)


def _save_raw_roi(raw_roi, frame_idx: int, frame_ms: int, out_dir: Path) -> None:
	filename = out_dir / f'rawroi_f{frame_idx:06d}_ms{frame_ms:06d}.png'
	if not cv.imwrite(str(filename), raw_roi):
		print(f'warning: failed to save raw ROI to {filename}', file=sys.stderr)


def main() -> int:
	args = _parse_args()
	video_path = Path(args.video)
	out_dir = Path(args.out_dir)

	cap = cv.VideoCapture(str(video_path))
	if not cap.isOpened():
		print(f'error: cannot open video: {video_path}', file=sys.stderr)
		return 1

	width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
	if width != EXPECTED_WIDTH or height != EXPECTED_HEIGHT:
		print(f'warning: expected resolution {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}, got {width}x{height}', file=sys.stderr)

	ok_dir, ng_dir = _ensure_output_dirs(out_dir)

	# Load templates exactly as KingScene does.
	king_templates = {
		key: Scene.loadTemplate(f'kings/{key}')
		for key in assets.kingKeys
	}

	processed = 0
	frame_idx = 0
	try:
		while True:
			ret, frame_bgr = cap.read()
			if not ret or frame_bgr is None:
				break

			if frame_idx % max(args.step, 1) != 0:
				frame_idx += 1
				continue

			frame_ms = int(cap.get(cv.CAP_PROP_POS_MSEC))

			rect = screen.KING_NAME_PART['area']
			x1 = int(rect['left'] * width)
			y1 = int(rect['top'] * height)
			x2 = int(rect['right'] * width)
			y2 = int(rect['bottom'] * height)

			frame = Frame(raw=frame_bgr)
			roi = frame.apply(screen.KING_NAME_PART)

			raw_roi = frame_bgr[y1:y2, x1:x2]
			roi_for_match = roi
			if args.loose_white:
				lower = np.array([LOOSE_WHITE_LOWER, LOOSE_WHITE_LOWER, LOOSE_WHITE_LOWER], dtype=np.uint8)
				upper = np.array([LOOSE_WHITE_UPPER, LOOSE_WHITE_UPPER, LOOSE_WHITE_UPPER], dtype=np.uint8)
				roi_for_match = cv.inRange(raw_roi, lower, upper)

			err_map = errors(roi_for_match, king_templates)
			best_key = getMinErrorKey(roi_for_match, king_templates, minError=KingScene.MIN_ERROR)
			best_error = err_map[best_key] if best_key is not None else None
			passed = 1 if best_key is not None else 0

			err_str = _format_err(best_error)
			key_str = best_key if best_key is not None else 'None'

			subdir = ok_dir if passed else ng_dir
			filename = subdir / f'roi_f{frame_idx:06d}_ms{frame_ms:06d}_key={key_str}_err={err_str}.png'
			cv.imwrite(str(filename), roi)

			if args.loose_white:
				loose_filename = subdir / f'loose_roi_f{frame_idx:06d}_ms{frame_ms:06d}.png'
				cv.imwrite(str(loose_filename), roi_for_match)

			if not passed:
				# Raw ROI stats for debugging InRange threshold.
				b_min, g_min, r_min = [int(raw_roi[:, :, i].min()) for i in range(3)]
				b_max, g_max, r_max = [int(raw_roi[:, :, i].max()) for i in range(3)]
				raw_min = int(raw_roi.min()) if raw_roi.size else 0
				raw_max = int(raw_roi.max()) if raw_roi.size else 0
				print(f'NG raw ROI stats: f={frame_idx:06d} ms={frame_ms:06d} B(min/max)={b_min}/{b_max} G(min/max)={g_min}/{g_max} R(min/max)={r_min}/{r_max} ALL(min/max)={raw_min}/{raw_max}')
				_save_frame_with_roi(frame_bgr, (x1, y1, x2, y2), frame_idx, frame_ms, ng_dir)
				_save_raw_roi(raw_roi, frame_idx, frame_ms, ng_dir)

			print(f'f={frame_idx} ms={frame_ms} best={key_str} err={err_str} pass={passed}')

			if args.verbose:
				sorted_errs = sorted(err_map.items(), key=lambda kv: kv[1])
				err_parts = [f'{k}:{_format_err(v)}' for k, v in sorted_errs]
				print('  errors: ' + ', '.join(err_parts))

			processed += 1
			frame_idx += 1

			if args.limit is not None and processed >= args.limit:
				break

	except KeyboardInterrupt:
		print('interrupted', file=sys.stderr)
	finally:
		cap.release()

	return 0


if __name__ == '__main__':
	sys.exit(main())
