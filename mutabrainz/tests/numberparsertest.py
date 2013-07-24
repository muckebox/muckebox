import unittest

from ..numberparser import NumberParser

class NumerParserTest(unittest.TestCase):
    def test_parser(self):
        self.assertEqual(NumberParser.parse(False, False), (1, 1))
        self.assertEqual(NumberParser.parse('', ''), (1, 1))
        self.assertEqual(NumberParser.parse('1', '2'), (1, 2))
        self.assertEqual(NumberParser.parse(1, 2), (1, 2))

        self.assertEqual(NumberParser.parse('2/6', '1/2'), (2, 1))
        self.assertEqual(NumberParser.parse('B7', False), (7, 2))

        self.assertEqual(NumberParser.parse('garbage23foo', 'bla42igitt82'),
                                            (23, 42))

if __name__ == '__main__':
    unittest.main()
