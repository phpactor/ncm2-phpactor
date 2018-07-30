[phpactor](https://github.com/phpactor/phpactor) integration for
[ncm2](https://github.com/ncm2/ncm2)

![phpactor](https://user-images.githubusercontent.com/4538941/30627852-67643a22-9e05-11e7-90d1-aa75c2d0654c.gif)

## Installation

Assuming you're using [vim-plug](https://github.com/junegunn/vim-plug)

```vim
" Include Phpactor
Plug 'phpactor/phpactor' ,  {'do': 'composer install', 'for': 'php'}

" Require ncm2 and this plugin
Plug 'ncm2/ncm2'
Plug 'roxma/nvim-yarp'
Plug 'phpactor/ncm2-phpactor'
```

Additionally you will need to set the following options:

```vim
autocmd BufEnter * call ncm2#enable_for_buffer()
set completeopt=noinsert,menuone,noselect
```

