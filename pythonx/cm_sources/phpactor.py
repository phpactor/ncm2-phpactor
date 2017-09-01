# -*- coding: utf-8 -*-

# For debugging, use this command to start neovim:
#
# NVIM_PYTHON_LOG_FILE=nvim.log NVIM_PYTHON_LOG_LEVEL=INFO nvim
#
#
# Please register source before executing any other code, this allow cm_core to
# read basic information about the source without loading the whole module, and
# modules required by this module
from cm import register_source, getLogger, Base

register_source(name='phpactor',
                priority=9,
                abbreviation='php',
                word_pattern=r'[$\w]+',
                scoping=True,
                scopes=['php'],
                early_cache=1,
                cm_refresh_patterns=[r'-\>', r'::'],)

import json
import os
import subprocess
import glob
import re

logger = getLogger(__name__)


class Source(Base):

    def __init__(self, nvim):
        super(Source, self).__init__(nvim)

        self._phpactor = nvim.eval(r"""globpath(&rtp, 'bin/phpactor', 1)""")

        if not self._phpactor:
            self.message('error', 'phpactor not found, please install https://github.com/phpactor/phpactor')

    def cm_refresh(self, info, ctx, *args):

        src = self.get_src(ctx).encode('utf-8')
        lnum = ctx['lnum']
        col = ctx['col']
        filepath = ctx['filepath']
        startcol = ctx['startcol']

        args = ['php', self._phpactor, 'complete', '--format=json', 'stdin', '%s' % self.get_pos(lnum, col, src)]
        proc = subprocess.Popen(args=args,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL,
                                cwd=self.nvim.eval('getcwd()'))

        result, errs = proc.communicate(src, timeout=30)

        result = result.decode()

        logger.debug("args: %s, result: [%s]", args, result)

        result = json.loads(result)

        # {
        #     "suggestions": [
        #         {
        #             "type": "f",
        #             "name": "setFormatter",
        #             "info": "pub setFormatter(OutputFormatterInterface $formatter)"
        #         }
        #     ]
        # }

        matches = []

        for e in result['suggestions']:
            menu = e['info']
            word = e['name']
            t = e['type']

            item = dict(word=word, menu=menu)

            # snippet support
            m = re.search(r'(\w+\s+)?\w+\((.*)\)', menu)

            if m and t == 'f':

                params = m.group(2)

                placeholders = []
                num = 1
                snip_args = ''

                if params != '':

                    params = params.split(',')

                    for param in params:

                        if "=" in param:
                            # skip params with default value
                            break
                        else:
                            param = re.search(r'\$\w+', param).group()
                            ph = self.snippet_placeholder(num, param)
                            placeholders.append(ph)
                            num += 1

                    snip_args = ', '.join(placeholders)

                    if len(placeholders) == 0:
                        # don't jump out of parentheses if function has
                        # parameters
                        snip_args = self.snippet_placeholder(1)

                ph0 = self.snippet_placeholder(0)
                snippet = '%s(%s)%s' % (word, snip_args, ph0)

                item['snippet'] = snippet

            matches.append(item)

        logger.debug("startcol [%s] matches: [%s]", startcol, matches)

        self.complete(info, ctx, startcol, matches)
