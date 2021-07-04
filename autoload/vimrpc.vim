function! vimrpc#FindNearestDir(buffer, directory_name)
  let l:buffer_filename = fnamemodify(bufname(a:buffer), ':p')
  let l:relative_path = finddir(a:directory_name, l:buffer_filename . ';')
  if !empty(l:relative_path)
    return fnamemodify(l:relative_path, ':p')
  endif
  return ''
endfunction

function! vimrpc#GetProjectDir(buffer)
  for l:vcs_dir in ['.git', '.hg', '.bzr', '_darcs', '.svn']
    let l:dir = vimrpc#FindNearestDir(a:buffer, l:vcs_dir)
    if !empty(l:dir)
      return fnamemodify(l:dir, ':h:h')
    endif
  endfor
  return ''
endfunction

function! vimrpc#LogDebug(message, trace)
  if a:trace != v:null
    call add(g:vimrpc_trace, a:trace)
  endif
  if g:vimrpc_log_debug
    echomsg '[vimrpc] ' . a:message
  endif
endfunction

function! vimrpc#LogWarn(message, trace)
  if a:trace != v:null
    call add(g:vimrpc_trace, a:trace)
  endif
  if g:vimrpc_log_warn
      echohl WarningMsg | echomsg '[vimrpc] ' . a:message | echohl None
  endif
endfunction

function! vimrpc#LogError(message, trace)
  if a:trace != v:null
    call add(g:vimrpc_trace, a:trace)
  endif
  echohl ErrorMsg | echomsg '[vimrpc] ' . a:message | echohl None
endfunction