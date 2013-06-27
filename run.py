import time
import signal
import sys
import os

from scanner.scanner import Scanner
from db import Db
from api.api import API
from config import Config

class Muckebox(object):
    instance = False

    @staticmethod
    def handle_signal_sigint(signal, frame):
        print "Caught SIGINT, trying to exit"

        self = Muckebox.instance

        if self.scanner:
            self.scanner.stop()

        if self.api:
            self.api.stop()

        sys.exit(0)

    def register_signal_handler(self):
        signal.signal(signal.SIGINT, Muckebox.handle_signal_sigint)

    def wait_for_signal(self):
        self.register_signal_handler()

        signal.pause()

    def main(self):
        Config.parse_args()

        path = Config.args.path[0]
        dbpath = Config.args.dbpath

        if not os.path.exists(Config.args.cache_dir):
            os.makedirs(Config.args.cache_dir)

        Db.open(dbpath, Config.args.verbose)

        if not Config.args.no_scanner:
            self.scanner = Scanner(path)
            self.scanner.start()
        else:
            self.scanner = False

        if Config.args.port > 0:
            self.api = API(Config.args.port)
            self.api.start()
        else:
            self.api = False

        self.wait_for_signal()

if __name__ == "__main__":
    Muckebox.instance = Muckebox()
    Muckebox.instance.main()

