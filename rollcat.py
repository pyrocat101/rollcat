#!/usr/bin/env python

import sys, re, math, argparse
from color import fg256
from time import sleep

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
            sys.stdout.write('\e[%sD' % len(s))
            opts['os'] += opts['spread']
            cls._println_plain(s, opts)
            sleep(1.0 / opts['speed'])            
        

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="""
    Concatenate FILE(s), or standard input, to standard output.
    With no FILE, or when FILE is -, read standard input.
    """)
    parser.add_argument('-a',
                        '--animate',
                        dest='animate',
                        default=False,
                        action='store_true')
    parser.add_argument('-d',
                        '--duration',
                        type=int,
                        default=12)
    parser.add_argument('-S',
                        '--seed',
                        dest='os',
                        type=int,
                        default=0)
    parser.add_argument('-s',
                        '--speed',
                        type=float,
                        default=20.0)
    parser.add_argument('-p',
                        '--spread',
                        type=float,
                        default=8.0)
    parser.add_argument('-F',
                        '--freq',
                        type=float,
                        default=0.3)
    parser.add_argument('-f',
                        '--force',
                        default=False,
                        action='store_true')
    parser.add_argument('files',
                        metavar='FILE',
                        nargs='*')

    opts = vars(parser.parse_args())

    files = opts.pop('files')

#    opts = {
#        'animate': False,
#        'duration': 12,
#        'os': 0,
#        'speed': 20,
#        'spread': 8.0,
#        'freq': 0.3,
#        'force': False,
#    }

    if len(files) == 0:
        files = [sys.stdin]
    for f in files:
        try:
            if f == '-' or f is sys.stdin:
                fd = sys.stdin
            else:
                fd = open(f, 'r')
            
            if sys.stdout.isatty() or opts['force']:
                Roll.cat(fd, opts)
            else:
                while True:
                    chunk = fd.read(8192)
                    sys.stdout.write(chunk)
                    if len(chunk) < 8192: break
        except IOError, ex:
            print "rollcat: %s: %s" % (ex.filename, ex.strerror)

