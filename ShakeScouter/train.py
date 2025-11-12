#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import torch

from argparse import ArgumentParser
from os.path import exists
from torch import nn, optim
from torch.utils.data import DataLoader
from typing import Optional

from constants import env

from recognizers import selectDevice, Trainer
from recognizers.digit.cnn import DigitCNN
from recognizers.digit.dataset import buildDataset
from recognizers.digit.model import DatasetRoot

from utils import forceCwd

# Set current working directory.
forceCwd(__file__)

def train(
	device: torch.device,
	trainLoader: DataLoader,
	testLoader: DataLoader,
	filename: str,
	epochs: int,
):
	# Init trainer
	trainer = Trainer(device, DigitCNN)

	# Define criterion and optimizer
	criterion = nn.CrossEntropyLoss()
	optimizer = optim.Adam(trainer.model.parameters(), lr=0.001)

	# Train model
	trainer.train(trainLoader, criterion, optimizer, epochs)

	# Eval model
	accuracy = trainer.eval(testLoader)
	print(f'Test Accuracy: {accuracy:.4f}')

	# Save model
	with open(filename, 'wb') as fh:
		trainer.save(fh)

def eval(device: torch.device, loader: DataLoader, filename: str):
	# Init trainer
	trainer = Trainer(device, DigitCNN, filename=filename)

	# Eval model
	accuracy = trainer.eval(loader)
	print(f'Test Accuracy: {accuracy:.4f}')

def fileExists(filename: str):
	if exists(filename):
		response = input('Digit model file exists. Overwrite? [y/N]: ').strip().lower()
		if response not in ['y', 'yes']:
			exit(0)

def main(args):
	if not args.eval and not args.force:
		fileExists(args.filename)

	# Load assets
	json: Optional[DatasetRoot] = None
	with open(args.input, 'r') as fh:
		json = DatasetRoot.from_json(fh.read())
	trainDataset, testDataset = buildDataset(json)

	# Init test loader
	testLoader = DataLoader(testDataset, batch_size=args.batch_size)

	device = selectDevice(args.device)
	if args.eval:
		eval(device, testLoader, args.filename)
	else:
		# Init train loader
		trainLoader = DataLoader(trainDataset, batch_size=args.batch_size, shuffle=True)

		train(device, trainLoader, testLoader, args.filename, args.epoch)

if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument('-b', '--batch_size', type=int, default=16, choices=[2, 4, 8, 16, 32, 64])
	parser.add_argument('-i', '--input', type=str, metavar='INPUT')
	parser.add_argument('--filename', type=str, metavar='FILE')
	parser.add_argument('-d', '--device', type=str, default='cpu', choices=['auto', 'cpu', 'cuda'])
	parser.add_argument('-e', '--epoch', type=int, default=30, choices=range(1, 32), metavar='EPOCH')
	parser.add_argument('-f', '--force', action='store_true')
	parser.add_argument('--eval', action='store_true')

	args = parser.parse_args()

	# Set default input
	if args.input is None:
		args.input = env.DEV_DIGIT_DATA_PATH

	# Set default filename
	if args.filename is None:
		args.filename = env.DEV_DIGIT_MODEL_PATH

	main(args)
