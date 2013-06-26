import argparse
import time
import signal
import sys

from scanner.scanner import Scanner
from db import Db
from api.api import API

class Muckebox(object):
    instance = False

    @staticmethod
    def handle_signal_sigint(signal, frame):
        print "Caught SIGINT, trying to exit"

        self = Muckebox.instance

        if self.scanner:
            self.scanner.stop()
        self.api.stop()

        sys.exit(0)

    def register_signal_handler(self):
        signal.signal(signal.SIGINT, Muckebox.handle_signal_sigint)

    def wait_for_signal(self):
        self.register_signal_handler()

        signal.pause()

    def parse_args(self):
        parser = argparse.ArgumentParser(description = 'mukkebox')
        
        parser.add_argument('path', metavar = 'path', nargs = 1,
                            help = 'Path to music library')
        parser.add_argument('-d', '--dbpath', metavar = 'dbpath',
                            default = '/tmp',
                            help = 'Directory where the database is stored')
        parser.add_argument('-n', '--no-scanner', dest = 'no_scanner',
                            action = 'store_true', default = False,
                            help = 'Disable the scanner')
        parser.add_argument('-v', '--verbose', dest = 'verbose',
                            action = 'store_true', default = False,
                            help = 'Verbose output')
        args = parser.parse_args()

        return args

    def main(self):
        args = self.parse_args()
        path = args.path[0]
        dbpath = args.dbpath

        self.db = Db(dbpath, args.verbose)
        self.api = API()

        if not args.no_scanner:
            self.scanner = Scanner(path)
            self.scanner.start()
        else:
            self.scanner = False

        self.api.start()

        self.wait_for_signal()

if __name__ == "__main__":
    Muckebox.instance = Muckebox()
    Muckebox.instance.main()

