function! s:check_nvim()
  if has('nvim')
    call v:lua.vim.health.ok('has("nvim") was successful')
  else
    call v:lua.vim.health.error('has("nvim") was not successful',
        \ 'vimrpc.nvim only works on Neovim')
  endif
endfunction

function! s:check_timers()
  if has('timers')
    call v:lua.vim.health.ok('has("timers") was successful')
  else
    call v:lua.vim.health.error('has("nvim") was not successful',
        \ 'vimrpc.nvim requires timers')
  endif
endfunction

function! s:check_python3()
  if has('python3')
    call v:lua.vim.health.ok('has("python3") was successful')
  else
    call v:lua.vim.health.error('has("python3") was not successful',
        \ 'vimrpc.nvim requires python3')
  endif
endfunction

function! s:issue_info()
  call v:lua.vim.health.info('If you are still having problems, create an issue on https://github.com/Redstoneguy129/vimrpc/issues')
endfunction

function! health#vimrpc#check()
  call v:lua.vim.health.start('vimrpc.nvim')
  call s:check_nvim()
  call s:check_timers()
  call s:check_python3()
  call s:issue_info()
endfunction
