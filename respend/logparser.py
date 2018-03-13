import re
from pygtail import Pygtail

def regex_match(regex, line):
    m = re.match(regex, line)
    if m is None:
        return m
    return m.group(1);

class RespendTx:
    def __init__(self, time_regex, hex_regex):
        self.time_regex = time_regex
        self.hex_regex = hex_regex

        self.time = None
        self.hex = None

    def parse_line(self, line):
        t = regex_match(self.time_regex, line)
        if t is not None:
            self.time = t
            print("matched %s %s" % (self.time_regex, line))

        h = regex_match(self.hex_regex, line)
        if h is not None:
            self.hex = h
            print("matched %s %s" % (self.hex_regex, line))

    def done(self):
        return self.time != None and self.hex != None

    def clear(self):
        self.time = self.hex = None

class RespendChecker():
    def __init__(self, logpath, on_respend):
        self.logpath = logpath
        self.on_respend = on_respend

    def check(self):
        tx1 = RespendTx(
                time_regex = r'.*tx1: (\d{4}-\d{2}-\d{2} [0-9:]{8})',
                hex_regex = r'.*tx1 hex: ([0-9a-f]+)')

        tx2 = RespendTx(
                time_regex = r'(\d{4}-\d{2}-\d{2} [0-9:]{8}) Respend tx2',
                hex_regex = r'.*tx2 hex: ([0-9a-f]+)')

        found = False
        for line in Pygtail(self.logpath):
            # tx2 is logged before tx1

            if not tx2.done():
                tx2.parse_line(line)

            elif not tx1.done():
                tx1.parse_line(line)

            if tx1.done() and tx2.done():
                print("found double spend")
                self.on_respend(tx1, tx2)
                tx1.clear()
                tx2.clear()
                found = True
        return found
