function! s:check_nvim()
  if has('nvim')
    call health#report_ok('has("nvim") was successful')
  else
    call health#report_error('has("nvim") was not successful',
        \ 'vimrpc.nvim only works on Neovim')
  endif
endfunction

function! s:check_timers()
  if has('timers')
    call health#report_ok('has("timers") was successful')
  else
    call health#report_error('has("nvim") was not successful',
        \ 'vimrpc.nvim requires timers')
  endif
endfunction

function! s:check_python3()
  if has('python3')
    call health#report_ok('has("python3") was successful')
  else
    call health#report_error('has("python3") was not successful',
        \ 'vimrpc.nvim requires python3')
  endif
endfunction

function! s:issue_info()
  call health#report_info('If you are still having problems, create an issue on https://github.com/Redstoneguy129/vimrpc/issues')
endfunction

function! health#vimrpc#check()
  call health#report_start('vimrpc.nvim')
  call s:check_nvim()
  call s:check_timers()
  call s:check_python3()
  call s:issue_info()
endfunction