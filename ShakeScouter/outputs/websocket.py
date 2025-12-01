# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from anyio import sleep_forever, TASK_STATUS_IGNORED
from anyio.abc import TaskGroup, TaskStatus
from json import dumps
from ssl import PROTOCOL_TLS_SERVER, SSLContext
from typing import Any
from websockets import broadcast, serve, WebSocketServerProtocol

from ShakeScouter.outputs.base import Output

class WebSocketOutput(Output):
	def __init__(self, args: Any) -> None:
		self.__connections = set()
		self.__dev  = args.development
		self.__host = args.host
		self.__port = args.port
		self.__sslContext = None

		if args.sslCert is not None and args.sslKey is not None:
			sslContext = SSLContext(PROTOCOL_TLS_SERVER)
			sslContext.load_cert_chain(args.sslCert, args.sslKey)
			self.__sslContext = sslContext
			print(f'Use ssl for WebSocket:', args.sslCert)

	async def setup(self, tg: TaskGroup):
		await tg.start(self.__runLoop)

	async def __onConnected(self, websocket: WebSocketServerProtocol):
		if self.__dev:
			print(f'Connect websocket client:', websocket.id)

		self.__connections.add(websocket)
		try:
			await websocket.wait_closed()
		finally:
			self.__connections.remove(websocket)

			if self.__dev:
				print(f'Disconnect websocket client:', websocket.id)

	async def __runLoop(self, task_status: TaskStatus[None] = TASK_STATUS_IGNORED):
		async with serve(self.__onConnected, self.__host, self.__port, ssl=self.__sslContext):
			task_status.started()
			await sleep_forever()

	def __sendMessage(self, message: Output.Message):
		if not self.__dev and message['event'].startswith('dev_'):
			return

		jsonMessage = dumps(message)
		broadcast(self.__connections, jsonMessage)

	def onMessage(self, message: Output.Message):
		self.__sendMessage(message)
