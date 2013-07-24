import time
import signal
import sys
import os

import cherrypy

from scanner.scanner import Scanner
from db import Db
from server.server import Server
from config import Config

class Muckebox(object):
    LOG_TAG = "Muckebox"

    instance = False

    @staticmethod
    def handle_signal_sigint(signal, frame):
        cherrypy.log("Caught SIGINT, trying to exit", Muckebox.LOG_TAG)

        self = Muckebox.instance

        if self.scanner:
            self.scanner.stop()

        if self.server:
            self.server.stop()

        sys.exit(0)

    def register_signal_handler(self):
        signal.signal(signal.SIGINT, Muckebox.handle_signal_sigint)

    def wait_for_signal(self):
        self.register_signal_handler()

        signal.pause()

    def main(self):
        Config.parse_args()

        library_path = Config.get_library_path()
        cache_path = Config.get_cache_path()
        log_path = Config.get_log_path()
        dbpath = Config.get_db_path()

        if not os.path.exists(cache_path):
            os.makedirs(cache_path)

        if not os.path.exists(log_path):
            os.makedirs(log_path)

        self.server = Server()
        self.server.configure()

        Db.open(dbpath, Config.is_verbose())

        if Config.is_scanner_enabled():
            self.scanner = Scanner(library_path)
            self.scanner.start()
        else:
            self.scanner = False

        if Config.is_api_enabled():
            self.server.start()
        else:
            self.server = False

        self.wait_for_signal()

if __name__ == "__main__":
    Muckebox.instance = Muckebox()
    Muckebox.instance.main()

