# -*- coding: utf-8 -*-

def esc(*codes):
    return "\x1b[%sm" % (";".join([str(c) for c in codes]))


class ColorString(object):
    r"""
    A colorized string-like object that gives correct length
    """

    sep = ""
    fmt = "%s"

    def __init__(self, *items):
        self.items = items

    def __str__(self):
        return self.fmt % (self.sep.join([unicode(s) for s in self.items]))

    def __repr__(self):
        return repr(unicode(self))

    def __len__(self):
        return sum([len(item) for item in self.items])

    def __add__(self, cs):
        if not isinstance(cs, (basestring, ColorString)):
            msg = "Concatenatation failed: %r + %r (Not a ColorString or str)"
            raise TypeError(msg % (type(cs), type(self)))
        return ColorString(self, cs)

    def __radd__(self, cs):
        if not isinstance(cs, (basestring, ColorString)):
            msg = "Concatenatation failed: %r + %r (Not a ColorString or str)"
            raise TypeError(msg % (type(self), type(cs)))
        return ColorString(cs, self)

    @property
    def as_utf8(self):
        """A more readable way to say ``unicode(color).encode('utf8')``
        """
        return unicode(self).encode('utf8')


class ColorString256(ColorString):
    def __init__(self, color, *items):
        (r, g, b) = color
        self.color = self._rgb_to_xterm(r, g, b)
        self.items = items

    def _rgb_to_xterm(self, r, g, b):
        gray_possible = True
        sep = 42.5

        while gray_possible:
            if r < sep or g < sep or b < sep:
                gray = r < sep and g < sep and b < sep
                gray_possible = False
            sep += 42.5

        if gray:
            return (232 + round(float(r + g + b) / 33))
        else: # rgb
            wtf = zip((r, g, b), (36, 6, 1))
            wtf = map(lambda (c, m): int(6 * float(c) / 256) * m, wtf)
            return sum([16] + wtf)

    def __str__(self):
        return self.fmt % (
            self.color, self.sep.join([unicode(s) for s in self.items]))


class fg256(ColorString256):
    fmt = esc(38, 5, "%d") + "%s" + esc(39)
