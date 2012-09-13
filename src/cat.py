#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re, math, argparse
from roll import fg256
from time import sleep
from gettext import gettext as _
from cStringIO import StringIO

__author__ = "Linjie Ding"
__version__ = "0.1.0"

class RollCatHelpFormatter(argparse.RawTextHelpFormatter):
    SUPPRESS = '==SUPPRESS=='

    def add_usage(self, usage, actions, groups, prefix=_('Usage: ')):
        if usage is not self.SUPPRESS:
            args = usage, actions, groups, prefix
            self._add_item(self._format_usage, args)

    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar

        else:
            parts = []

            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append(option_string)
                return '%s %s' % (', '.join(parts), args_string)

            return ', '.join(parts)

class Roll(object):
    STRIP_ANSI = re.compile('\e\[(\d+)(;\d+)?(;\d+)?[m|K]')

    @classmethod
    def rainbow(cls, freq, i):
        red   = math.sin(freq * i + 0) * 127 + 128
        green = math.sin(freq * i + 2 * math.pi / 3) * 127 + 128
        blue  = math.sin(freq * i + 4 * math.pi / 3) * 127 + 128
        return red, green, blue

    @classmethod
    def cat(cls, fd, opts={}):
        try:
            if opts['animate']: sys.stdout.write("\e[?25l")
            for line in fd:
                opts["os"] += 1
                cls.println(line, opts)
        finally:
            if opts['animate']: sys.stdout.write("\e[?25h")
        
    @classmethod
    def println(cls, s, defaults={}, opts={}):
        opts.update(defaults)
        s.rstrip('\r\n')
        if s and (sys.stdout.isatty() or opts['force']):
            cls.STRIP_ANSI.sub('', s)
        if opts['animate']:
            cls._println_ani(s, opts)
        else:
            cls._println_plain(s, opts)
        print ''
        
    @classmethod
    def _println_plain(cls, s, defaults={}, opts={}):
        opts.update(defaults)
        for i, c in enumerate(s.rstrip('\r\n')):
            sys.stdout.write(str(fg256(cls.rainbow(
                opts['freq'], opts['os'] + i / opts['spread']), c)))
        
    @classmethod
    def _println_ani(cls, s, opts={}):
        if len(s) == 0: return
        for i in range(1, opts['duration']):
            sys.stdout.write('\x1b[%sD' % len(s))
            opts['os'] += opts['spread']
            cls._println_plain(s, opts)
            sleep(1.0 / opts['speed'])            
        

def main():
    parser = argparse.ArgumentParser(
        formatter_class=RollCatHelpFormatter,
        add_help=False,
        usage="""\
rollcat [OPTION]... [FILE]...
""",
        description="""
Concatenate FILE(s), or standard input, to standard output.
With no FILE, or when FILE is -, read standard input.
""",
        epilog="""
Examples:
  rollcat f - g      Output f's content, then stdin, then g's contents.
  rollcat            Copy standard input to standard output.
  fortune | rollcat  Display a rainbow cookie.

Report bugs to <http://www.github.com/metaphysiks/rollcat/issues>
rollcat home page: <http://www.github.com/metaphysiks/rollcat>
"""
    )
    parser.add_argument('-a',
                        '--animate',
                        dest='animate',
                        default=False,
                        action='store_true',
                        help="Enable psychedelics")
    parser.add_argument('-d',
                        '--duration',
                        type=int,
                        default=12,
                        metavar="<i>",
                        help="Animation duration (default: %(default)s)")
    parser.add_argument('-S',
                        '--seed',
                        dest='os',
                        type=int,
                        default=0,
                        metavar="<i>",
                        help="Rainbow seed, 0 = random (default: %(default)s)")
    parser.add_argument('-s',
                        '--speed',
                        type=float,
                        default=20.0,
                        metavar="<f>",
                        help="Animation speed (default: %(default)s)")
    parser.add_argument('-p',
                        '--spread',
                        type=float,
                        default=8.0,
                        metavar="<f>",
                        help="Rainbow spread (default: %(default)s)")
    parser.add_argument('-F',
                        '--freq',
                        type=float,
                        default=0.3,
                        metavar="<f>",
                        help="Rainbow frequency (default: %(default)s)")
    parser.add_argument('-f',
                        '--force',
                        default=False,
                        action='store_true',
                        help="Force color even when stdout is not a tty")
    parser.add_argument('files',
                        metavar='FILE',
                        type=argparse.FileType('r'),
                        nargs='*')
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        help="Print version and exit",
                        version="rollcat %s (c)2012 i@dingstyle.me" % __version__)
    parser.add_argument('-h',
                        '--help',
                        action='store_true',
                        default=False,
                        help="Show this message")

    try:
        opts = vars(parser.parse_args())

        if opts['help']:
            default = {
                'animate': False,
                'duration': 12,
                'os': 0,
                'speed': 20,
                'spread': 8.0,
                'freq': 0.3,
                'force': False,
            }
            Roll.cat(StringIO(parser.format_help()), default)
            sys.exit(0)

        files = opts.pop('files')

        if len(files) == 0:
            files = [sys.stdin]
        for f in files:
            if sys.stdout.isatty() or opts['force']:
                Roll.cat(f, opts)
            else:
                while True:
                    chunk = f.read(8192)
                    sys.stdout.write(chunk)
                    if len(chunk) < 8192: break
    except IOError, ex:
        print "rollcat: %s: %s" % (ex.filename, ex.strerror)

if __name__ == '__main__':
    main()
