# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import cv2 as cv
import numpy as np
import time

from numpy.typing import NDArray
from typing import Any, Optional

import ShakeScouter.utils.images.filters as f

from ShakeScouter.constants import Color, screen
from ShakeScouter.recognizers.digit import DigitReader
from ShakeScouter.scenes.base import *
from ShakeScouter.utils.anomaly import CounterAnomalyDetector
from ShakeScouter.utils.images import errorMAE, Frame
from ShakeScouter.utils import debug_flags
from ShakeScouter.utils.debug_io import debug_log, debug_save
from ShakeScouter.utils.images.frame import TELEMETRY_DIR

class WaveScene(Scene):
	MIN_ERROR = 0.1
	ALIVE_THRESHOLD = 600
	GEGG_HUE        = 32
	GEGG_THRESHOLD  = 354  # the half of π×30²
	INITIAL_WAVE_MAX_RETRY = 5

	def __init__(self, reader: DigitReader) -> None:
		self.__reader           = reader
		self.__playersTemplate  = Scene.loadTemplate('players')
		self.__geggTemplate     = Scene.loadTemplate('gegg')
		self.__waveTemplate     = Scene.loadTemplate('wave')
		self.__waveExTemplate   = Scene.loadTemplate('wave_ex')
		self.__unstableTemplate = Scene.loadTemplate('unstable')
		self.__extraWaveCheckId = 0
		self.__timerDebugId     = 0
		self.__lastTimerDebug   = None
		self.__lastTimerImages  = None

	def __captureTimerDebug(self, timestamp: float, count: Optional[int]) -> Optional[dict[str, Any]]:
		if not debug_flags.WAVE_DEBUG:
			return None
		if self.__lastTimerImages is None:
			return None
		rawTimerImage, grayImage, timerImage = self.__lastTimerImages
		self.__timerDebugId += 1
		debug_id = self.__timerDebugId
		ts_str = time.strftime('%Y%m%d-%H%M%S', time.localtime(timestamp))
		raw_path = TELEMETRY_DIR / f'timer_dbg_{ts_str}_{debug_id}_raw.png'
		gray_path = TELEMETRY_DIR / f'timer_dbg_{ts_str}_{debug_id}_gray.png'
		th_path = TELEMETRY_DIR / f'timer_dbg_{ts_str}_{debug_id}_th.png'
		debug_save(raw_path, rawTimerImage)
		debug_save(gray_path, grayImage)
		debug_save(th_path, timerImage)
		debug_log(f'[DEBUG] timer_dbg id={debug_id} ts={timestamp} raw={raw_path} gray={gray_path} th={th_path} count={count}')
		debug_info = {
			'id': debug_id,
			'ts': ts_str,
			'raw': raw_path,
			'gray': gray_path,
			'th': th_path,
		}
		self.__lastTimerDebug = debug_info
		return debug_info

	def setup(self) -> Any:
		data = {
			'end': -1,
			'wave': 0,
			'color': None,
			'quota': -1,
			'detector': CounterAnomalyDetector(),
			'initial_wave_retry_count': 0,
			'initial_wave_last_ocr': None,
		}
		return data

	def reset(self, data: Any) -> None:
		data['end']   = -1
		data['wave']  = 0
		data['color'] = None
		data['quota'] = -1
		data['detector'].reset()
		data['initial_wave_retry_count'] = 0
		data['initial_wave_last_ocr'] = None

	async def __detectAnomalousCount(self, context: SceneContext, data: Any, count: Optional[int]) -> None:
		if count is not None:
			if not data['detector'].isAnomalous(count, context.timestamp):
				# Calc estimated end timestamp
				data['end'] = context.timestamp + (100 - count)
			else:
				if debug_flags.WAVE_DEBUG:
					prev_value = getattr(data['detector'], '_CounterAnomalyDetector__preValue', None)
					prev_timestamp = getattr(data['detector'], '_CounterAnomalyDetector__preTimestamp', None)
					elapsed = None
					if prev_timestamp is not None:
						elapsed = context.timestamp - prev_timestamp
					debug_info = self.__lastTimerDebug
					if debug_info is None:
						debug_info = self.__captureTimerDebug(context.timestamp, count)
					debug_id = debug_info['id'] if debug_info else None
					ts_str = debug_info['ts'] if debug_info else None
					debug_log(f'[DEBUG] timer_anom id={debug_id} ts={context.timestamp} ts_str={ts_str} prev_val={prev_value} elapsed={elapsed} reason=anomalous')
				await context.sendImmediately(SceneEvent.DEV_WARN, {
					'description': f'Anomalous value detected: {count}',
				})

	def __analysisCount(self, frame: Frame) -> Optional[int]:
		# Read "count"
		rawTimerFrame = frame.subimage(screen.TIMER_PART['area'])
		rawTimerImage = rawTimerFrame.native
		filters = screen.TIMER_PART['filters']
		grayImage = filters[0].apply(rawTimerImage) if len(filters) > 0 else rawTimerImage
		timerImage = filters[1].apply(grayImage) if len(filters) > 1 else grayImage
		timerInt = self.__reader.read(timerImage)

		if debug_flags.WAVE_DEBUG:
			self.__lastTimerImages = (rawTimerImage, grayImage, timerImage)
			if timerInt is None or timerInt == 200:
				debug_info = self.__captureTimerDebug(time.time(), timerInt)
				if debug_info is not None:
					rect = screen.TIMER_PART['area']
					full = frame.native
					height, width = full.shape[:2]
					x1 = max(0, int(rect['left'] * width))
					y1 = max(0, int(rect['top'] * height))
					x2 = min(width, int(rect['right'] * width))
					y2 = min(height, int(rect['bottom'] * height))
					annotated = full.copy()
					cv.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 2)
					frame_path = TELEMETRY_DIR / f'timer_dbg_{debug_info["ts"]}_{debug_info["id"]}_frame.png'
					debug_save(frame_path, annotated)
					debug_log(f'[DEBUG] timer_dbg_frame id={debug_info["id"]} path={frame_path}')
			else:
				self.__lastTimerDebug = None

		return timerInt

	def __analysisPlayerStatus(self, color: Color, frame: Frame):
		# Get player image
		playerInfoImage = frame.apply(screen.PLAYERS_PART)

		hue = color.value.hueA
		playersSubimage = playerInfoImage[:55, :]
		playersImage = cv.inRange(
			cv.bitwise_and(playersSubimage, playersSubimage, mask=self.__playersTemplate),
			np.array([hue - 5, 102, 102]),
			np.array([hue + 5, 255, 255]),
		)

		geggSubimage = playerInfoImage[55:, :]
		geggImage = cv.inRange(
			cv.bitwise_and(geggSubimage, geggSubimage, mask=self.__geggTemplate),
			np.array([WaveScene.GEGG_HUE - 5, 102, 102]),
			np.array([WaveScene.GEGG_HUE + 5, 255, 255]),
		)

		# Get player status
		playerStatus = list(map(lambda i: {
			'alive': WaveScene.__getStatus(playersImage, i, WaveScene.ALIVE_THRESHOLD),
			'gegg':  WaveScene.__getStatus(geggImage,    i, WaveScene.GEGG_THRESHOLD),
		}, range(4)))

		return playerStatus

	def __analysisUnstable(self, frame: Frame):
		# Get unstable status
		unstableImage = frame.apply(screen.UNSTABLE_PART)
		unstableError = errorMAE(unstableImage, self.__unstableTemplate)
		unstableStatus = bool(unstableError <= WaveScene.MIN_ERROR)

		return unstableStatus

	async def __analysisXtrawave(self, context: SceneContext, data: Any, frame: Frame, waveImage: Optional[NDArray[np.uint8]] = None) -> SceneStatus:
		if context.timestamp >= data['end']:
			# Debug bookkeeping for every Extra Wave check
			debug_id: Optional[int] = None
			roi_color: Optional[NDArray[np.uint8]] = None
			if debug_flags.WAVE_DEBUG:
				self.__extraWaveCheckId += 1
				debug_id = self.__extraWaveCheckId
				roi_color = frame.subimage(screen.WAVE_PART['area']).native

			if waveImage is None:
				waveImage = frame.apply(screen.WAVE_PART)
			waveExError = errorMAE(waveImage, self.__waveExTemplate)

			if debug_flags.WAVE_DEBUG and debug_id is not None:
				base = f'extra_check_{debug_id}'
				roi_color_name = f'{base}_roi_color.png'
				roi_processed_name = f'{base}_roi_processed.png'
				template_name = f'{base}_template.png'
				if roi_color is not None:
					debug_save(TELEMETRY_DIR / roi_color_name, roi_color)
				debug_save(TELEMETRY_DIR / roi_processed_name, waveImage)
				debug_save(TELEMETRY_DIR / template_name, self.__waveExTemplate)
				below_threshold = waveExError <= WaveScene.MIN_ERROR
				debug_log(f'[DEBUG] extra_check id={debug_id} mae={waveExError} below_threshold={below_threshold} roi_color={roi_color_name} roi={roi_processed_name} tpl={template_name}')

			if waveExError > WaveScene.MIN_ERROR:
				return SceneStatus.FALSE
			else:
				data['wave']  = 'extra'
				data['quota'] = -1

		# Read each part
		count    = self.__analysisCount(frame)
		players  = self.__analysisPlayerStatus(data['color'], frame)
		unstable = self.__analysisUnstable(frame)

		# Detect anomalous count
		await self.__detectAnomalousCount(context, data, count)

		# Send message
		message = {
			'color': data['color'].value.name,
			'wave': 'extra',
			'count': count,
			'players': players,
			'unstable': unstable,
		}
		await context.send(SceneEvent.GAME_UPDATE, message)

		return SceneStatus.CONTINUE

	async def analysis(self, context: SceneContext, data: Any, frame: Frame) -> SceneStatus:
		initial_wave_forced = False

		# In "Xtrawave"
		if data['wave'] == 'extra':
			result = await self.__analysisXtrawave(context, data, frame)
			return result

		if context.timestamp >= data['end']:
			# Detect "Wave"
			waveImage = frame.apply(screen.WAVE_PART)
			waveTextImage = screen.removeNumberAreaFromWaveImage(waveImage)
			waveError = errorMAE(waveTextImage, self.__waveTemplate)

			if waveError > WaveScene.MIN_ERROR:
				data['quota'] = -1

				# Check "Xtrawave"
				result = await self.__analysisXtrawave(context, data, frame, waveImage)
				return result

			# Get nearest hue
			if data['color'] is None:
				playerImage = frame \
					.subimage(screen.PLAYERS_PART['area']) \
					.filter([
						f.Blur((7, 7)),
						f.HSV(),
					])
				data['color'] = WaveScene.__findNearestColor(playerImage)

			# Read "wave"
			waveNumberImage = waveImage[:, self.__waveTemplate.shape[1]:]
			waveNumberInt = self.__reader.read(waveNumberImage)
			initial_wave_retrying = False
			initial_wave_forced = False
			data['initial_wave_last_ocr'] = waveNumberInt
			if data['wave'] == 0:
				if waveNumberInt == 1:
					data['wave'] = 1
					data['initial_wave_retry_count'] = 0
				else:
					if data['initial_wave_retry_count'] < WaveScene.INITIAL_WAVE_MAX_RETRY:
						data['initial_wave_retry_count'] += 1
						initial_wave_retrying = data['initial_wave_retry_count'] < WaveScene.INITIAL_WAVE_MAX_RETRY
					if data['initial_wave_retry_count'] >= WaveScene.INITIAL_WAVE_MAX_RETRY:
						data['wave'] = 1
						initial_wave_forced = True
						debug_log(f'[INFO] initial_wave_forced_to_1 retry_count={data["initial_wave_retry_count"]} last_ocr={waveNumberInt} ts={context.timestamp}')
			else:
				if waveNumberInt is not None:
					data['wave'] = waveNumberInt

			# Read "quota"
			quotaImage = frame.apply(screen.QUOTA_PART)
			quotaInt = self.__reader.read(quotaImage)
			if quotaInt is not None:
				data['quota'] = quotaInt

		# Read "amount"
		amountImage = frame.apply(screen.AMOUNT_PART)
		amountInt = self.__reader.read(amountImage)

		# Read each part
		count    = self.__analysisCount(frame)
		players  = self.__analysisPlayerStatus(data['color'], frame)
		unstable = self.__analysisUnstable(frame)

		# Detect anomalous count
		await self.__detectAnomalousCount(context, data, count)

		# Send message if any of count or amount is not None, or forced wave1 fallback occurred
		if (any([count, amountInt]) or initial_wave_forced) and not (data['wave'] == 0 and 'initial_wave_retry_count' in data and data['initial_wave_retry_count'] > 0 and not initial_wave_forced):
			message = {
				'color': data['color'].value.name,
				'wave': data['wave'],
				'count': count,
				'amount': amountInt,
				'quota': data['quota'],
				'players': players,
				'unstable': unstable,
			}
			await context.send(SceneEvent.GAME_UPDATE, message)

		return SceneStatus.CONTINUE

	@staticmethod
	def __findNearestColor(image: np.ndarray) -> Color:
		# Calc hue histgram
		hueHist = cv.calcHist([image], [0], None, [180], [0, 180])

		# Get dominant hue
		dominantHueIndex = np.argmax(hueHist)

		# Calc hue distance
		hueDistances = np.abs(Color.hues() - dominantHueIndex)

		# Get nearest color index
		nearestIndex = np.argmin(hueDistances)

		# Get nearest color
		nearestColor = Color.all()[nearestIndex]

		return nearestColor

	@staticmethod
	def __getStatus(image: np.ndarray, playerIndex: int, threshold: int) -> bool:
		# Get each player image
		left = playerIndex * 72
		subimage = image[:, left:(left + 67)]

		# Count color pixels
		pixelCount = cv.countNonZero(subimage)

		return pixelCount >= threshold
