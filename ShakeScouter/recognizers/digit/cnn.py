# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import torch.nn as nn

from constants import env

class DigitCNN(nn.Module):
	def __init__(self):
		super(DigitCNN, self).__init__()
		self.__layers = nn.Sequential(
			nn.Conv2d( 1, 32, 3, padding=1),  #  1ch -> 32ch (3x3 kernel)
			nn.ReLU(),
			nn.Conv2d(32, 64, 3, padding=1),  # 32ch -> 64ch (3x3 kernal)
			nn.ReLU(),
			nn.MaxPool2d(2, 2),

			nn.Flatten(),

			nn.Linear(64 * (env.DIGIT_WIDTH // 2) * (env.DIGIT_HEIGHT // 2), 128), # 64ch * image size
			nn.ReLU(),
			nn.Linear(128, 10), # 128ch -> 10ch (digits [0-9])
			nn.LogSoftmax(1),
		)

	def forward(self, x):
		output = self.__layers(x)
		return output
