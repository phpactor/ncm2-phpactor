# -*- coding: utf-8 -*-

import vim
from ncm2 import Ncm2Source, getLogger
import re

import subprocess
from ncm2 import Popen
import json

logger = getLogger(__name__)


class Source(Ncm2Source):

    def __init__(self, nvim):
        super(Source, self).__init__(nvim)
        self.completion_timeout = self.nvim.eval('g:ncm2_phpactor_timeout') or 5

    def on_complete(self, ctx, lines, cwd, phpactor_complete):
        src = "\n".join(lines)
        src = self.get_src(src, ctx)

        lnum = ctx['lnum']

        # use byte addressing
        bcol = ctx['bcol']
        src = src.encode()

        pos = self.lccol2pos(lnum, bcol, src)
        args = phpactor_complete
        args += [str(pos)]

        proc = Popen(args=args,
                     stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.DEVNULL)

        result, errs = proc.communicate(src, timeout=self.completion_timeout)

        result = result.decode()

        logger.debug("args: %s, result: [%s]", args, result)

        result = json.loads(result)

        if not result or not result.get('suggestions', None):
            return

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
            menu = e['short_description']
            word = e['name']
            t = e['type']

            item = dict(word=word, menu=menu, info=menu)

            # snippet support
            m = re.search(r'(\w+\s+)?\w+\((.*)\)', menu)

            if m and (t == 'function' or t == 'method'):

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

                item['user_data'] = {'snippet': snippet, 'is_snippet': 1}

            matches.append(item)

        self.complete(ctx, ctx['startccol'], matches)

    def snippet_placeholder(self, num, txt=''):
        txt = txt.replace('\\', '\\\\')
        txt = txt.replace('$', r'\$')
        txt = txt.replace('}', r'\}')
        if txt == '':
            return '${%s}' % num
        return '${%s:%s}' % (num, txt)


source = Source(vim)

on_complete = source.on_complete
