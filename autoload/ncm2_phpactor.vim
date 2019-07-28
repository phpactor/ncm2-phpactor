if get(s:, 'loaded', 0)
    finish
endif
let s:loaded = 1

let g:ncm2_phpactor_timeout = get(g:, 'ncm2_phpactor_timeout', 5)

let g:ncm2_phpactor#proc = yarp#py3({
    \ 'module': 'ncm2_phpactor',
    \ 'on_load': { -> ncm2#set_ready(g:ncm2_phpactor#source)}
    \ })

let g:ncm2_phpactor#source = extend(get(g:, 'ncm2_phpactor#source', {}), {
            \ 'name': 'phpactor',
            \ 'ready': 0,
            \ 'priority': 9,
            \ 'mark': 'b',
            \ 'scope': ['php'],
            \ 'word_pattern': '[\$\w][\w]*',
            \ 'complete_pattern': ['\$', '-\>', '::'],
            \ 'subscope_enable': 1,
            \ 'on_complete': 'ncm2_phpactor#on_complete',
            \ 'on_warmup': 'ncm2_phpactor#on_warmup',
            \ }, 'keep')

func! ncm2_phpactor#init()
    call ncm2#register_source(g:ncm2_phpactor#source)
endfunc

func! ncm2_phpactor#on_warmup(ctx)
    call g:ncm2_phpactor#proc.jobstart()
endfunc

func! ncm2_phpactor#on_complete(ctx)
    " g:phpactorPhpBin and g:phpactorbinpath, g:phpactorInitialCwd is defined in
    " phpactor plugin
    call g:ncm2_phpactor#proc.try_notify('on_complete',
                \ a:ctx,
                \ getline(1, '$'),
                \ getcwd(),
                \ [g:phpactorPhpBin,
                \       g:phpactorbinpath,
                \       'complete', '-d', g:phpactorInitialCwd,
                \       '--format=json', '--', 'stdin'
                \       ])
endfunc

function! ncm2_phpactor#_completeImportClassFromNcm2(completedItem)

    if !has_key(a:completedItem, "word") || !has_key(a:completedItem, "user_data")
        return
    endif

    let user_data = json_decode(a:completedItem['user_data'])

    if (user_data['source'] !=# "phpactor")
        return
    endif

    if !empty(get(a:completedItem, "info", ""))
        call phpactor#rpc("import_class", {
                    \ "qualified_name": a:completedItem['info'],
                    \ "offset": phpactor#_offset(),
                    \ "source": phpactor#_source(),
                    \ "path": expand('%:p')})
    endif

endfunction

if g:phpactorOmniAutoClassImport == v:true
    autocmd CompleteDone *.php call ncm2_phpactor#_completeImportClassFromNcm2(v:completed_item)
endif
