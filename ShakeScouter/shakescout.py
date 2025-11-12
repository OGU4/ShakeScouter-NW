#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from anyio import create_task_group, create_memory_object_stream, run
from argparse import ArgumentParser
from dotenv import load_dotenv
from os import getenv
from typing import Any

from inputs.cv import CVInput
from outputs import OUTPUT_PLUGINS_KEYLIST, Output
from scenes import getDefaultPipeline, SceneStatus
from scenes.context import SceneContextImpl

from utils import forceCwd, PluginLoader
from utils.images import Frame

# Set current working directory.
forceCwd(__file__)

async def main(args):
	targetOutputPlugins = map(lambda o: OUTPUT_PLUGINS_KEYLIST[o], args.outputs)

	outputLoader = PluginLoader('outputs')
	outputs: list[Output] = [
		outputLoader.load(plugin)(args)
		for plugin in targetOutputPlugins
	]

	async with create_task_group() as tg:
		streams = [create_memory_object_stream[Any]() for _ in outputs]

		# Setup output plugins
		for i, output in enumerate(outputs):
			await output.setup(tg)
			tg.start_soon(output.onReceive, streams[i][1])

		# Init context and pipeline
		context = SceneContextImpl(list(map(lambda ss: ss[0], streams)))
		scene = getDefaultPipeline(args.device, args.development)
		data = scene.setup()
		input = CVInput(args)

		async def callback(frame: Frame) -> bool:
			result = await scene.analysis(context, data, frame)
			return result == SceneStatus.DONE

		# Start input
		async def run():
			await input.run(callback)
			tg.cancel_scope.cancel()
		tg.start_soon(run)

if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument('--development', action='store_true', help='Run the program in development mode.')
	parser.add_argument('-d', '--device', type=str, metavar='DEVICE', default='auto', choices=['auto', 'cpu', 'cuda'], help='Specify the device to use in PyTorch. Available options are "auto", "cpu", and "cuda."')
	parser.add_argument('-o', '--outputs', type=str, metavar='OUTPUTS', nargs='+', default=['console', 'websocket'], choices=['console', 'json', 'websocket'], help='Specify the output types. Available options are "console", "json", and "websocket."')

	# CVInput options
	parser.add_argument('-i', '--input', type=int, metavar='INPUT', help='Specify the device ID of the OpenCV input.')
	parser.add_argument('--width', type=int, default=1920, choices=range(640, 8192), metavar='WIDTH', help='Specify the width of the OpenCV input.')
	parser.add_argument('--height', type=int, default=1080, choices=range(360, 4320), metavar='HEIGHT', help='Specify the height of the OpenCV input.')

	# JsonOutput options
	parser.add_argument('-t', '--timestamp', action='store_true', help='Use timestamp as json filename.')

	# WebSocketOutput options
	parser.add_argument('-H', '--host', type=str, metavar='HOST', help='Specify the hostname for the WebSocket connection.')
	parser.add_argument('-p', '--port', type=int, choices=range(1024, 65536), metavar='PORT', help='Specify the port number for the WebSocket connection.')

	args = parser.parse_args()
	load_dotenv()

	# Set torch device
	if args.device == 'auto':
		args.device = getenv('TORCH_DEVICE') or 'cpu'

	# Set device ID
	if args.input is None:
		envDevice = getenv('CV_DEVICE')
		args.input = int(envDevice) if envDevice else 0

	# Set hostname
	if args.host is None:
		args.host = getenv('WS_HOST') or 'localhost'

	# Set port number
	if args.port is None:
		envPort = getenv('WS_PORT')
		args.port = int(envPort) if envPort else 4649

	args.sslCert = getenv('WS_SSLCERT')
	args.sslKey = getenv('WS_SSLKEY')

	run(main, args)
