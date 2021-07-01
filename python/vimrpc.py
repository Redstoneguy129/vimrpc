import socket
import vim
import os
import json
import random
from time import sleep as sleep

DEBUG_MODE = os.getenv("SSH_CONNECTION") is None

if DEBUG_MODE:
    with open("../vimrpc.json", 'r') as config_file:
        config = json.load(config_file)
else:
    with open(os.path.join(vim.eval('s:plugin_root_dir'), '..', 'vimrpc.json'), 'r') as config_file:
        config = json.load(config_file)

has_thumbnail = '_'.join([item['name'] for item in config['filetypes']]).split('_')
has_thumbnail.pop()
remap = {item['icon']: item['name'] for item in config['languages'] if 'icon' in item}

ignored_file_types = -1
ignored_directories = -1


def setPresence(language: str, filePath: str, rpc):
    languageName = language
    for icon in remap:
        if "_" in icon:
            # icon with multiple extensions
            for i in icon.split("_"):
                if i == language:
                    print(i + " == " + language)
                    languageName = remap[icon]
                    language = icon
        else:
            # icon with single extension
            if "*" in icon:
                if icon[1:] in language:
                    languageName = language.title()
                    language = icon[1:]
            else:
                if icon == language:
                    print(icon + " == " + language)
                    languageName = remap[icon]

    print("Language Image: " + language.lower())
    print("Language Name: " + languageName)
    presence = {
        "language": language.lower(),
        "languageName": languageName,
        "filePath": filePath,
        "stop": False
    }
    print(json.dumps(presence))
    rpc.sendall(bytes(json.dumps(presence), encoding="utf-8"))


rpc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rpc_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)


def update():
    global ignored_file_types
    global ignored_directories

    if ignored_file_types == -1:
        # Lazy init
        if vim.eval('exists("g:vimrpc_ignored_file_types")') == '1':
            ignored_file_types = vim.eval('g:vimrpc_ignored_file_types')
        else:
            ignored_file_types = []

        if vim.eval('exists("g:vimrpc_ignored_directories")') == '1':
            ignored_directories = vim.eval('g:vimrpc_ignored_directories')
        else:
            ignored_directories = []

    filename = get_filename()
    directory = get_directory()
    filetype = get_filetype()
    if filetype in has_thumbnail:
        setPresence(filetype, directory+filename+"."+filetype, rpc_socket)


def reconnect():
    try:
        disconnect()
        rpc_socket.connect_ex(((os.getenv("SSH_CONNECTION").split(" ")[0] if os.getenv("SSH_CONNECTION") is not None else "127.0.0.1"), 3500))
    except Exception:
        pass


def disconnect():
    try:
        presence = {
            "language": "null",
            "languageName": "null",
            "filePath": "null",
            "stop": True
        }
        rpc_socket.sendall(bytes(json.dumps(presence), encoding="utf-8"))
        rpc_socket.close()
    except Exception:
        pass


def get_filename():
    return vim.eval('expand("%:t")')


def get_filetype():
    return vim.eval('&filetype')


def get_extension():
    return vim.eval('expand("%:e")')


def get_directory():
    return re.split(r'[\\/]', vim.eval('getcwd()'))[-1]