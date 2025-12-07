# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import ShakeScouter.utils.images.filters as f

from typing import Any, Optional

from ShakeScouter.constants import screen
from ShakeScouter.scenes.base import SceneContext, SceneEvent, SceneStatus
from ShakeScouter.scenes.ingame.wave import WaveScene
from ShakeScouter.utils.debug_io import debug_log
from ShakeScouter.utils import debug_flags
from ShakeScouter.utils.images import Frame, errorMAE


class DebugWaveScene(WaveScene):
	def __init__(self, reader) -> None:
		from ShakeScouter.utils import debug_flags
		debug_flags.WAVE_DEBUG = True
		super().__init__(reader)

	# Copy of WaveScene.analysis with additional debug logs.
	async def analysis(self, context: SceneContext, data: Any, frame: Frame) -> SceneStatus:
		debug_log(f'[DEBUG] analysis enter: wave={data["wave"]}, ts={context.timestamp}, end={data["end"]}')

		# In "Xtrawave"
		if data['wave'] == 'extra':
			result = await self._WaveScene__analysisXtrawave(context, data, frame)
			return result

		debug_log(f'[DEBUG] check_wave_block: ts={context.timestamp}, end={data["end"]}')

		if context.timestamp >= data['end']:
			debug_log(f'[DEBUG] enter_wave_block: ts={context.timestamp}, end={data["end"]}')
			# Detect "Wave"
			waveImage = frame.apply(screen.WAVE_PART)
			waveTextImage = screen.removeNumberAreaFromWaveImage(waveImage)
			waveError = errorMAE(waveTextImage, self._WaveScene__waveTemplate)

			# Debug point (1): after computing MAE
			debug_log(f'[DEBUG] wave_error={waveError}')

			if waveError > WaveScene.MIN_ERROR:
				# Debug point (2): entering extra branch
				debug_log('[DEBUG] ENTER_EXTRA_BRANCH')
				data['quota'] = -1

				# Debug point (3): before calling __analysisXtrawave
				debug_log('[DEBUG] CALL_analysisXtrawave')

				# Check "Xtrawave"
				result = await self._WaveScene__analysisXtrawave(context, data, frame, waveImage)
				return result

			# Get nearest hue
			if data['color'] is None:
				playerImage = frame \
					.subimage(screen.PLAYERS_PART['area']) \
					.filter([
						f.Blur((7, 7)),
						f.HSV(),
					])
				data['color'] = WaveScene._WaveScene__findNearestColor(playerImage)

			# Read "wave"
			waveNumberImage = waveImage[:, self._WaveScene__waveTemplate.shape[1]:]
			waveNumberInt = self._WaveScene__reader.read(waveNumberImage)
			if waveNumberInt is not None:
				data['wave'] = waveNumberInt

			# Read "quota"
			quotaImage = frame.apply(screen.QUOTA_PART)
			quotaInt = self._WaveScene__reader.read(quotaImage)
			if quotaInt is not None:
				data['quota'] = quotaInt

		# Read "amount"
		amountImage = frame.apply(screen.AMOUNT_PART)
		amountInt = self._WaveScene__reader.read(amountImage)

		# Read each part
		count    = self._WaveScene__analysisCount(frame)
		if debug_flags.WAVE_DEBUG and (count is None or count == 200):
			debug_log(f'[DEBUG] extra_probe timestamp={context.timestamp} end={data["end"]} count={count}')
		players  = self._WaveScene__analysisPlayerStatus(data['color'], frame)
		unstable = self._WaveScene__analysisUnstable(frame)

		# Detect anomalous count
		await self._WaveScene__detectAnomalousCount(context, data, count)

		# Send message if any of count or amount is not None
		if any([count, amountInt]):
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
