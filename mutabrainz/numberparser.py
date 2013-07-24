import re
import logging

from cherrypy import log

class NumberParser(object):
    SLASH_RE = re.compile('^(?P<number>[0-9]+)/(?P<total>[0-9]+)$')
    VINYL_RE = re.compile('^(?P<disccode>[A-Za-z])(?P<tracknumber>[0-9]+)$')
    INT_RE = re.compile('[^0-9]*(?P<number>[0-9]+).*')

    @classmethod
    def parse(cls, track_string, disc_string):
        (track_number, track_disc_number) = cls.parse_track_number(track_string)
        disc_number = cls.parse_disc_number(disc_string, track_disc_number)
        
        return (track_number, disc_number)

    @classmethod
    def parse_disc_number(cls, number, default):
        if not number:
            return default

        if (isinstance(number, int)):
            return number

        if not isinstance(number, basestring):
            return default

        if number.isdigit():
            return int(number)

        match = cls.SLASH_RE.match(number)

        if match:
            return int(match.group('number'))

        match = cls.INT_RE.match(number)

        if match:
            return int(match.group('number'))

        log("Could not parse disc number '%s'" % (number), logging.WARNING)

        return default

    @classmethod
    def parse_track_number(cls, number):
        if not number:
            return (1, 1)
        
        if isinstance(number, int):
            return (number, 1)

        if not isinstance(number, basestring):
            log("Unknown number type '%s'" % (number), logging.WARNING)
            return (1, 1)

        if number.isdigit():
            return (int(number), 1)

        match = cls.SLASH_RE.match(number)

        if match:
            return (int(match.group('number')), 1)
        
        match = cls.VINYL_RE.match(number)

        if match:
            return (int(match.group('tracknumber')), \
                        ord(match.group('disccode').upper()) - ord('A') + 1)

        match = cls.INT_RE.match(number)

        if match:
            return (int(match.group('number')), 1)

        log("Could not parse track number '%s'" % (number), logging.WARNING)

        return (1, 1)

