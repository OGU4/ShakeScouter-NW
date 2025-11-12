# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from math import ceil

class CounterAnomalyDetector:
	STATE_IDLE_START = 1
	STATE_IDLE_END   = 2
	STATE_COUNTDOWN  = 3

	def __init__(self) -> None:
		self.__state = CounterAnomalyDetector.STATE_IDLE_START
		self.__prevValue     = 100
		self.__prevTimestamp = 0

	@property
	def state(self) -> str:
		match self.__state:
			case CounterAnomalyDetector.STATE_COUNTDOWN:
				return 'COUNTDOWN'
			case CounterAnomalyDetector.STATE_IDLE_START:
				return 'IDLE_START'
			case CounterAnomalyDetector.STATE_IDLE_END:
				return 'IDLE_END'
			case _:
				return 'UNKNOWN'

	def reset(self) -> None:
		self.__state = CounterAnomalyDetector.STATE_IDLE_START
		self.__prevValue     = 100
		self.__prevTimestamp = 0

	def isAnomalous(self, value: int, timestamp: float) -> bool:
		match self.__state:
			case CounterAnomalyDetector.STATE_COUNTDOWN:
				diffValue = self.__prevValue - value
				diffTimestamp = ceil(0.25 + timestamp - self.__prevTimestamp)
				if diffValue < 0 or diffValue > diffTimestamp:
					return True

				if value <= 0 or value >= 1000:
					self.__state = CounterAnomalyDetector.STATE_IDLE_END

			case CounterAnomalyDetector.STATE_IDLE_START:
				if value < 100:
					self.__state = CounterAnomalyDetector.STATE_COUNTDOWN

			case CounterAnomalyDetector.STATE_IDLE_END:
				if 90 <= value and value <= 100:
					self.__state = CounterAnomalyDetector.STATE_IDLE_START
				elif value != 0:
					return True

		# Update values
		self.__prevValue     = value
		self.__prevTimestamp = timestamp

		return False
