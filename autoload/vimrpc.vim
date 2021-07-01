function! vimrpc#update() abort
    python3 import vimrpc
    python3 vimrpc.update()
endfunction

function! vimrpc#reconnect() abort
    python3 import vimrpc
    python3 vimrpc.reconnect()
endfunction

function! vimrpc#disconnect() abort
    python3 import vimrpc
    python3 vimrpc.disconnect()
endfunction