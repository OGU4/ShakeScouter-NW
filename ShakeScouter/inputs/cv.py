# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import cv2 as cv

from anyio import sleep
from logging import getLogger
from typing import Awaitable, Callable

from ShakeScouter.inputs.input import Input
from ShakeScouter.utils.images import Frame

# Set up logger
logger = getLogger(__name__)

class CVInput(Input):
	def __init__(self, args) -> None:
		self.__device = args.input
		self.__width  = args.width
		self.__height = args.height

	async def run(self, callback: Callable[[Frame], Awaitable[bool]]) -> None:
		device = cv.VideoCapture(self.__device)

		if not device.isOpened():
			logger.warn('Could not open video capture device.')
			return

		device.set(cv.CAP_PROP_FRAME_WIDTH,  self.__width)
		device.set(cv.CAP_PROP_FRAME_HEIGHT, self.__height)

		try:
			# frameCount = 0
			# startTime = cv.getTickCount()
			while device.isOpened():
				ret, image = device.read()
				if ret:
					frame = Frame(raw=image)
					result = await callback(frame)
					if result:
						break
					await sleep(0)
				else:
					break

				# frameCount += 1
				# currentTime = cv.getTickCount()
				# elapsedTime = (currentTime - startTime) / cv.getTickFrequency()
				# framerate = frameCount / elapsedTime
				# print('FPS:', framerate)
		finally:
			device.release()
