import unittest

from ..unitconverter import UnitConverter

class UnitConverterTest(unittest.TestCase):
    def test_parser(self):
        self.assertEqual(UnitConverter.string_to_bytes('0'), 0)
        self.assertEqual(UnitConverter.string_to_bytes('23'), 23)
        self.assertEqual(UnitConverter.string_to_bytes('2K'), 2 * 1024)
        self.assertEqual(UnitConverter.string_to_bytes('42M'),
                         42 * 1024 * 1024)
        self.assertEqual(UnitConverter.string_to_bytes('10G'),
                         10 * 1024 * 1024 * 1024)

        with self.assertRaises(ValueError):
            UnitConverter.string_to_bytes('keine zahl')

if __name__ == '__main__':
    unittest.main()
