from contextlib import suppress, contextmanager
import socket
import json
import os


@contextmanager
def reconnect_on_failure(discord):
    try:
        yield
    except (socket.error, BrokenPipeError, ConnectionResetError):
        discord.reconnect()


class DiscordError(Exception):
    pass


class NoDiscordClientError(DiscordError):
    pass


class ReconnectError(DiscordError):
    pass


class Discord(object):
    def __init__(self, vim, reconnect_threshold=5):
        self.reconnect_threshold = reconnect_threshold
        self.reconnect_counter = 0
        self.sock = None
        with open(os.path.join(vim.eval('g:plugin_root_dir'), '..', 'vimrpc.json'), 'r') as config_file:
            config = json.load(config_file)
        self.remap = {item['icon']: item['name'] for item in config['languages'] if 'icon' in item}

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        try:
            self.sock.connect_ex((str(os.getenv("SSH_CONNECTION").split(" ")[0]), 3500))
        except (ConnectionAbortedError, ConnectionRefusedError):
            raise NoDiscordClientError()

    def disconnect(self):
        presence = {
            "language": "null",
            "languageName": "null",
            "filePath": "null",
            "stop": True
        }
        self.sock.sendall(bytes(json.dumps(presence), encoding="utf-8"))
        with suppress(socket.error, OSError, BrokenPipeError):
            self.sock.close()

    def reconnect(self):
        if self.reconnect_counter > self.reconnect_threshold:
            raise ReconnectError("reconnect_counter > reconnect_threshold")
        self.disconnect()
        self.reconnect_counter += 1
        self.connect()

    def update(self, activity, filePath):
        languageName = activity
        language = activity
        for icon in self.remap:
            if "_" in icon:
                for i in icon.split("_"):
                    if i == language:
                        languageName = self.remap[icon]
                        language = icon
            else:
                if "*" in icon:
                    if icon[1:] in language:
                        languageName = language.title()
                        language = icon[1:]
                else:
                    if icon == language:
                        languageName = self.remap[icon]
        payload = {
            "language": language.lower(),
            "languageName": languageName,
            "filePath": filePath,
            "stop": False
        }
        self.sock.sendall(bytes(json.dumps(presence), encoding="utf-8"))
