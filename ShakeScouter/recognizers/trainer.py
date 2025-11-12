# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import torch

from torch import nn, optim
from torch.utils.data import DataLoader
from typing import BinaryIO, IO, Type

class Trainer:
	def __init__(
		self,
		device: torch.device,
		model: Type[nn.Module],
		**kwargs
	):
		self.__device = device

		if 'filename' in kwargs:
			# Load model
			filename = kwargs['filename']
			modelInstance = model()
			modelInstance.load_state_dict(torch.load(filename, map_location=device))
			self.__model = modelInstance
		else:
			# Create model
			self.__model = model().to(device)

	@property
	def model(self) -> nn.Module:
		return self.__model

	def train(
		self,
		dataLoader: DataLoader,
		criterion: nn.Module,
		optimizer: optim.Optimizer,
		epochs: int,
	):
		self.__model.train()
		for epoch in range(epochs):
			runningLoss = 0.0

			for data in dataLoader:
				inputs = data[0].unsqueeze(1).to(self.__device)
				labels = data[1].to(self.__device)

				# Compute prediction error
				outputs = self.__model(inputs)
				loss = criterion(outputs, labels)

				# Backpropagation
				optimizer.zero_grad()
				loss.backward()
				optimizer.step()

				runningLoss += loss.item() * inputs.size(0)

			dataSize = len(dataLoader)
			epochLoss = runningLoss / dataSize
			print(f'Epoch {epoch + 1}/{epochs}, Loss: {epochLoss:.4f}')

	def eval(self, dataLoader: DataLoader) -> float:
		self.__model.eval()

		correct: int = 0
		total: int = 0
		with torch.no_grad():
			for data in dataLoader:
				inputs = data[0].unsqueeze(1).to(self.__device)
				labels = data[1].to(self.__device)
				outputs = self.__model(inputs)

				_, predicted = torch.max(outputs.data, 1)
				total += labels.size(0)
				correct += (predicted == labels).sum().item()

		accuracy = float(correct) / total
		return accuracy

	def save(self, file: str | BinaryIO | IO[bytes]):
		torch.save(self.__model.state_dict(), file)
