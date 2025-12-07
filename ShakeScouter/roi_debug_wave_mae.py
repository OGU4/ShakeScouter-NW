import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

import cv2 as cv

from ShakeScouter.constants import screen
from ShakeScouter.scenes.base import Scene
from ShakeScouter.utils import debug_flags
from ShakeScouter.utils.debug_io import debug_log, debug_save
from ShakeScouter.utils.images import Frame, errorMAE

TELEMETRY_DIR = Path(__file__).resolve().parents[1] / '.telemetry'
_YUYV_DETECTED: Optional[bool] = None
THRESHOLD = 0.1  # WaveScene.MIN_ERROR


def fail(message: str) -> None:
	print(json.dumps({'error': message}))
	sys.exit(1)


def capture_frame(device: int, video: Optional[str]):
	source = video if video is not None else device
	cap = cv.VideoCapture(source)
	if not cap.isOpened():
		raise RuntimeError(f'cannot open source: {source}')
	try:
		ret, frame = cap.read()
		if not ret or frame is None:
			raise RuntimeError('failed to read frame')
		return frame
	finally:
		cap.release()


def _try_convert_yuyv(image):
	try:
		converted = cv.cvtColor(image, cv.COLOR_YUV2BGR_YUY2)
		return converted
	except cv.error:
		return None


def ensure_bgr(image):
	global _YUYV_DETECTED
	if _YUYV_DETECTED is None:
		converted = _try_convert_yuyv(image)
		if converted is not None:
			_YUYV_DETECTED = True
			return converted
		_YUYV_DETECTED = False
	elif _YUYV_DETECTED:
		converted = _try_convert_yuyv(image)
		if converted is not None:
			return converted
		raise RuntimeError('expected YUYV frame but conversion failed')

	if image.ndim == 2:
		return cv.cvtColor(image, cv.COLOR_GRAY2BGR)
	if image.ndim == 3 and image.shape[2] == 4:
		return cv.cvtColor(image, cv.COLOR_BGRA2BGR)
	if image.ndim == 3 and image.shape[2] == 3:
		return image
	raise RuntimeError('unsupported image shape')


def save_image(path: Path, image) -> str:
	cv.imwrite(str(path), image)
	return str(path)


def log_image_stats(label: str, image) -> None:
	if not debug_flags.WAVE_DEBUG:
		return
	value_min = int(image.min()) if image.size else 0
	value_max = int(image.max()) if image.size else 0
	value_mean = float(image.mean()) if image.size else 0.0
	if image.size:
		if image.ndim == 2:
			nonzero = int(cv.countNonZero(image))
		else:
			gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
			nonzero = int(cv.countNonZero(gray))
	else:
		nonzero = 0
	debug_log(f'[DEBUG] {label}: dtype={image.dtype}, shape={image.shape}, min={value_min}, max={value_max}, mean={value_mean}, nonzero={nonzero}')


def save_debug_image(name: str, timestamp: str, image) -> None:
	if not debug_flags.WAVE_DEBUG:
		return
	path = TELEMETRY_DIR / f'{name}_{timestamp}.png'
	debug_save(path, image)


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument('--device', type=int, default=0)
	parser.add_argument('--video')
	parser.add_argument('--wave-debug', action='store_true', default=False, help='enable wave debug logs and intermediate image dumps')
	args = parser.parse_args()

	debug_flags.WAVE_DEBUG = args.wave_debug
	timestamp = time.strftime('%Y%m%d-%H%M%S')

	raw = capture_frame(args.device, args.video)
	frame_image = ensure_bgr(raw)

	frame = Frame(raw=frame_image)
	roi_frame = frame.subimage(screen.WAVE_PART['area'])
	roi_color = roi_frame.native.copy()
	wave_image = frame.apply(screen.WAVE_PART)
	wave_text = screen.removeNumberAreaFromWaveImage(wave_image)
	log_image_stats('wave_image stats', wave_image)
	log_image_stats('wave_text stats', wave_text)
	save_debug_image('wave_apply', timestamp, wave_image)

	template = Scene.loadTemplate('wave')

	if wave_text.shape != template.shape:
		raise RuntimeError('processed ROI and template shapes differ')

	mae = errorMAE(wave_text, template)

	TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)
	frame_path = TELEMETRY_DIR / f'wave_mae_frame_{timestamp}.png'
	roi_color_path = TELEMETRY_DIR / f'wave_mae_roi_color_{timestamp}.png'
	roi_path = TELEMETRY_DIR / f'wave_mae_roi_processed_{timestamp}.png'
	tpl_path = TELEMETRY_DIR / f'wave_mae_template_{timestamp}.png'
	save_image(frame_path, frame_image)
	save_image(roi_color_path, roi_color)
	save_image(roi_path, wave_text)
	save_image(tpl_path, template)

	result = {
		'frame_shape': list(frame_image.shape),
		'roi_shape': list(wave_text.shape),
		'template_shape': list(template.shape),
		'mae': mae,
		'below_threshold': bool(mae <= THRESHOLD),
		'frame_path': str(frame_path),
		'roi_color_path': str(roi_color_path),
		'roi_path': str(roi_path),
		'tpl_path': str(tpl_path),
	}
	print(json.dumps(result))


if __name__ == '__main__':
	try:
		main()
	except Exception as exc:
		fail(str(exc))
