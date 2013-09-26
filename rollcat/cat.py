#!/usr/bin/env python

"""
Usage: rollcat [options] [FILE...]

Concatenate FILE(s), or standard input, to standard output.
With no FILE, or when FILE is -, read standard input.

Options:
    --spread, -p <f>   Rainbow spread [default: 3.0]
      --freq, -F <f>   Rainbow frequency [default: 0.1]
      --seed, -S <i>   Rainbow seed, 0 = random [default: 0]
       --animate, -a   Enable psychedelics
  --duration, -d <i>   Animation duration [default: 12]
     --speed, -s <f>   Animation speed [default: 20.0]
         --force, -f   Force color even when stdout is not a tty
       --version, -v   Print version and exit
          --help, -h   Show this message

Examples:
  rollcat f - g      Output f's contents, then stdin, then g's contents.
  rollcat            Copy standard input to standard output.
  fortune | rollcat  Display a rainbow cookie.
"""

import sys
import codecs
import re
import math
from docopt import docopt
from schema import Schema, And, Or, Use, SchemaError
from random import randrange
from time import sleep

def rgb5(r, g, b):
    r, g, b = map(round, [r, g, b])
    return 16 + r * 36 + g * 6 + b

def rgb(r, g, b):
    """ (r, g, b) -> ansi color code """
    r, g, b = map(lambda c: c / 255.0 * 5, [r, g, b])
    return rgb5(r, g, b)

def hex(color):
    """ hex color code -> (r, g, b) """
    c = color[1:] if color[0] is '#' else color
    r, g, b = c[:2], c[2:4], c[4:6]
    return map(lambda c: int(c, 16), [r, g, b])

def paint(s, color):
    return "\x1b[38;5;%dm%s\x1b[39m" % (rgb(*hex(color)), s)

STRIP_ANSI = re.compile(r'\x1b\[(\d+)(;\d+)?(;\d+)?[m|K]')

def rainbow(freq, i):
     red   = math.sin(freq * i + 0) * 127 + 128
     green = math.sin(freq * i + 2 * math.pi / 3) * 127 + 128
     blue  = math.sin(freq * i + 4 * math.pi / 3) * 127 + 128
     return "#%02x%02x%02x" % (red, green, blue)

def println_plain(s, defaults={}, opts={}):
    opts.update(defaults)
    for i, c in enumerate(s.rstrip()):
        # import q; q.d()
        sys.stdout.write(paint(
            c, rainbow(opts['--freq'], opts['--os'] + i / opts['--spread'])))

def println_ani(s, opts={}):
    if not s: return
    for i in xrange(1, opts['--duration'] + 1):
        # sys.stdout.write("\x1b[%dD" % len(s.encode('utf-8')))
        sys.stdout.write("\x1b[1G")
        opts["--os"] += opts["--spread"]
        println_plain(s, opts)
        sys.stdout.flush()
        sleep(1.0 / opts["--speed"])

def println(s, defaults={}, opts={}):
    opts.update(defaults)
    s = s.rstrip()
    if s and (sys.stdout.isatty() or opts['--force']):
        s = STRIP_ANSI.sub('', s)
    if opts['--animate']:
        println_ani(s, opts)
    else:
        println_plain(s, opts)
    print

def cat(fd, opts={}):
    try:
        # hide cursor
        if opts["--animate"]: sys.stdout.write("\x1b[?25l")
        for line in fd:
            line = line.decode('utf-8')
            opts['--os'] += 1
            println(line, opts)
    finally:
        # ensure the cursor apperance
        if opts["--animate"]: sys.stdout.write("\x1b[?25h")

def main(opts):
    opts['--os'] = opts['--seed']
    if opts["--os"] is 0: opts["--os"] = randrange(256)

    files = ['-'] if len(opts['FILE']) is 0 else opts['FILE']
    for file in files:
        try:
            if file is '-':
                fd = sys.stdin
            else:
                fd = open(file)
            if sys.stdout.isatty() or opts['--force']:
                cat(fd, opts)
            else:
                chunk = fd.read(8192)
                sys.stdout.write(chunk)
                if len(chunk) < 8192:
                    break
            fd.close()
        except IOError as e:
            print "rollcat: " + e.strerror
            exit(1)
        except KeyboardInterrupt:
            pass

def print_help(opts={}):

    opts = dict({
        '--animate': False,
        '--duration': 12,
        '--os': 0,
        '--speed': 20,
        '--spread': 8.0,
        '--freq': 0.3
    }.items() + opts.items())

    try:
        i = 20
        o = randrange(256)
        for line in __doc__.splitlines():
            i -= 1
            opts['--os'] = o + i
            println(line, opts)
        print
    except KeyboardInterrupt:
        pass

def entry():
    opts = docopt(__doc__, help=False, version="rollcat 0.2.0")

    if opts['--help']:
        print_help()
        sys.exit()

    schema = Schema({
        '--duration': And(Use(int), lambda n: n > 0, error="duration must be > 0"),
        '--speed': And(Use(float), lambda n: n > 0.1, error="speed must be > 0.1"),
        '--spread': And(Use(float), lambda n: n > 0, error="spread must be > 0"),
        '--freq': Use(float),
        '--seed': Use(int),
        str: object
    })

    try:
        opts = schema.validate(opts)
        main(opts)
    except SchemaError as e:
        exit(e)

if __name__ == '__main__':
    entry()
