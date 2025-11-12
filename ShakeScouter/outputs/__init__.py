# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from ShakeScouter.outputs.base import Output
from ShakeScouter.outputs.console import ConsoleOutput
from ShakeScouter.outputs.json import JsonOutput
from ShakeScouter.outputs.websocket import WebSocketOutput

OUTPUT_PLUGINS_KEYLIST = {
	'console': 'ConsoleOutput',
	'json': 'JsonOutput',
	'websocket': 'WebSocketOutput',
}
