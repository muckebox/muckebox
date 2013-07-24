import unittest

def run():
    loader = unittest.TestLoader()
    tests = loader.discover('.', '*test.py')
    testRunner = unittest.runner.TextTestRunner()
    testRunner.run(tests)

if __name__ == '__main__':
    run()
