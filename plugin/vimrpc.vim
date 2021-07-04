if !has('nvim')
    echoerr 'This plugin requires Neovim'
    finish
endif
if !has('timers')
    echoerr 'This plugin requires +timers build option'
    finish
endif
if !has('python3')
    echoerr 'This plugin requires python3'
    finish
endif

if !exists('g:vimrpc_activate_on_enter')
    let g:vimrpc_activate_on_enter = 1
endif
if !exists('g:vimrpc_reconnect_threshold')
    let g:vimrpc_reconnect_threshold = 5
endif
if !exists('g:vimrpc_log_debug')
    let g:vimrpc_log_debug = 0
endif
if !exists('g:vimrpc_log_warn')
    let g:vimrpc_log_warn = 1
endif
if !exists('g:vimrpc_trace')
    let g:vimrpc_trace = []
endif
if !exists('g:plugin_root_dir')
    let g:plugin_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')
endif