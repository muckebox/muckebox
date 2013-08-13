import argparse
import imp
import os

class Settings(object):
    args = { }
    config = False
    config_path = False

    @classmethod
    def parse_args(cls):
        parser = argparse.ArgumentParser(description = 'muckebox')

        parser.add_argument('-c', '--config-file', dest = 'config_file',
                            default = [ '~/.config/muckebox/config.py',
                                        '/etc/muckebox/config.py' ],
                            help = 'Path to the config file')
        parser.add_argument('-n', '--no-scanner', dest = 'no_scanner',
                            action = 'store_true', default = False,
                            help = 'Disable the scanner')
        parser.add_argument('-v', '--verbose', dest = 'verbose',
                            action = 'store_true', default = False,
                            help = 'Verbose output')
        parser.add_argument('-r', '--rescan', dest = 'rescan',
                            action = 'store_true', default = False,
                            help = 'Forcefully rescan library')
        parser.add_argument('-f', '--foreground', dest = 'foreground',
                            action = 'store_true', default = False,
                            help = 'Run in foreground')

        cls.args = parser.parse_args()

        cls.load_config_file()

    @classmethod
    def load_config_file(cls):
        files = cls.args.config_file

        if isinstance(files, basestring):
            files = [ files ]

        for fn in files:
            try:
                fn = os.path.expanduser(fn)
                cls.config = imp.load_source('config', fn).config
                cls.config_path = os.path.dirname(os.path.abspath(fn))

                return
            except:
                pass

        print "WARNING: could not load config file, using built-in defaults"

        (fn, path, descr) = imp.find_module('default_configuration')

        cls.config = imp.load_module('default_configuration',
                                     fn, path, descr).config
        cls.config_path = path

    @classmethod
    def get_log_path(cls):
        return cls.config['log_path']

    @classmethod
    def get_access_log_path(cls):
        return cls.get_log_path() + "/access.log"

    @classmethod
    def get_error_log_path(cls):
        return cls.get_log_path() + "/error.log"

    @classmethod
    def get_db_path(cls):
        return cls.config['db_path']

    @classmethod
    def get_config_path(cls, filename):
        if not os.path.isabs(filename):
            filename = cls.config_path + "/" + filename

        return os.path.abspath(filename)

    @classmethod
    def get_ssl_key_path(cls):
        return cls.get_config_path(cls.config['ssl_key_path'])

    @classmethod
    def get_ssl_cert_path(cls):
        return cls.get_config_path(cls.config['ssl_certificate_path'])

    @classmethod
    def get_library_path(cls):
        return cls.config['library_path']

    @classmethod
    def get_cache_path(cls):
        return cls.config['cache_path']

    @classmethod
    def get_password(cls):
        return cls.config['password']

    @classmethod
    def get_port(cls):
        return cls.config['port']

    @classmethod
    def get_va_artist(cls):
        return cls.config['va_artist']

    @classmethod
    def is_verbose(cls):
        return cls.args.verbose

    @classmethod
    def is_scanner_enabled(cls):
        return not cls.args.no_scanner

    @classmethod
    def is_api_enabled(cls):
        return cls.get_port() > 0
    
    @classmethod
    def is_rescan_forced(cls):
        return cls.args.rescan

    @classmethod
    def is_foreground(cls):
        return cls.args.foreground