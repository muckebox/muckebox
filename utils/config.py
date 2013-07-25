import argparse

class Config(object):
    args = { }

    @classmethod
    def parse_args(cls):
        parser = argparse.ArgumentParser(description = 'muckebox')
        
        parser.add_argument('path', metavar = 'path', nargs = 1,
                            help = 'Path to music library')
        parser.add_argument('-d', '--data-path', dest = 'datapath',
                            default = '/var/muckebox',
                            help = 'Directory where to store our data')
        parser.add_argument('-n', '--no-scanner', dest = 'no_scanner',
                            action = 'store_true', default = False,
                            help = 'Disable the scanner')
        parser.add_argument('-v', '--verbose', dest = 'verbose',
                            action = 'store_true', default = False,
                            help = 'Verbose output')
        parser.add_argument('-p', '--port', dest = 'port',
                            default = 2342, type = int,
                            help = 'Port for the API (0 to disable)')
        parser.add_argument('-c', '--cache-dir', dest = 'cache_dir',
                            default = '',
                            help = 'Cache directory for transcodings')
        parser.add_argument('-V', '--va-artist', dest = 'va_artist',
                            default = 'VA',
                            help = 'Default name for various artist albums')
        parser.add_argument('-r', '--rescan', dest = 'rescan',
                            action = 'store_true', default = False,
                            help = 'Forcefully rescan library')
        parser.add_argument('-f', '--foreground', dest = 'foreground',
                            action = 'store_true', default = False,
                            help = 'Run in foreground')

        cls.args = parser.parse_args()

    @classmethod
    def get_data_path(cls):
        return cls.args.datapath

    @classmethod
    def get_log_path(cls):
        return cls.get_data_path() + "/log"

    @classmethod
    def get_access_log_path(cls):
        return cls.get_log_path() + "/access.log"

    @classmethod
    def get_error_log_path(cls):
        return cls.get_log_path() + "/error.log"

    @classmethod
    def get_db_path(cls):
        return cls.get_data_path() + "/muckebox.db"

    @classmethod
    def get_ssl_path(cls, file_name = False):
        path = cls.get_data_path() + "/ssl"

        if file_name:
            path += "/" + file_name

        return path

    @classmethod
    def get_library_path(cls):
        return cls.args.path[0]

    @classmethod
    def get_cache_path(cls):
        if len(cls.args.cache_dir) > 0:
            return cls.args.cache_dir

        return cls.get_data_path() + "/cache"

    @classmethod
    def is_verbose(cls):
        return cls.args.verbose

    @classmethod
    def get_port(cls):
        return cls.args.port

    @classmethod
    def is_scanner_enabled(cls):
        return not cls.args.no_scanner

    @classmethod
    def is_api_enabled(cls):
        return cls.args.port > 0

    @classmethod
    def get_va_artist(cls):
        return cls.args.va_artist
    
    @classmethod
    def is_rescan_forced(cls):
        return cls.args.rescan

    @classmethod
    def is_foreground(cls):
        return cls.args.foreground
