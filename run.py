import argparse
import time

from scanner.scanner import Scanner
from db import Db

def parse_args():
    parser = argparse.ArgumentParser(description = 'mukkebox')

    parser.add_argument('path', metavar = 'path', nargs = 1,
                        help = 'Path to music library')
    parser.add_argument('-d', '--dbpath', metavar = 'dbpath', default = '/tmp',
                        help = 'Directory where the database is stored')
    args = parser.parse_args()

    return args

def main():
    args = parse_args()
    path = args.path[0]
    dbpath = args.dbpath

    db = Db(dbpath)
    scanner = Scanner(path)

    scanner.start()

if __name__ == "__main__":
    main()

