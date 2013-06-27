import argparse

class Config(object):
    args = { }

    @classmethod
    def parse_args(cls):
        parser = argparse.ArgumentParser(description = 'muckebox')
        
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
        parser.add_argument('-p', '--port', dest = 'port',
                            default = 2342, type = int,
                            help = 'Port for the API (0 to disable)')

        cls.args = parser.parse_args()
