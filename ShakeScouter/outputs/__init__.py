# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

from .base import Output
from .console import ConsoleOutput
from .json import JsonOutput
from .websocket import WebSocketOutput

OUTPUT_PLUGINS_KEYLIST = {
	'console': 'ConsoleOutput',
	'json': 'JsonOutput',
	'websocket': 'WebSocketOutput',
}
