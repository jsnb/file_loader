import mock
from io import StringIO
from unittest import TestCase

from file_loader.parsers.fixed_width_parser import FixedWidthParser
from file_loader.exceptions import MalformedLineError

class FixedWidthTest(TestCase):
    def setUp(self):
        test_schema = '''"column name",width,datatype\n
name,10,TEXT\n
valid,1,BOOLEAN\n
count,3,INTEGER\n
'''
        with mock.patch('file_loader.parsers.fixed_width_parser.open') as mock_open:
            mock_open.return_value = StringIO(test_schema)
            self.parser = FixedWidthParser('test/formatname.csv')

    def test_table_name(self):
        self.assertEqual(self.parser.table_name, 'formatname')

    def test_columns(self):
        columns = [
            ('name', 'TEXT'),
            ('valid', 'BOOLEAN'),
            ('count', 'INTEGER'),
        ]
        ix = 0
        for column in self.parser.columns:
            self.assertEqual(column[0], columns[ix][0])
            self.assertEqual(column[1], columns[ix][1])
            ix += 1

    def test_widths(self):
        widths = [10, 1, 3]
        for ix in range(len(self.parser.widths)):
            self.assertEqual(widths[ix], self.parser.widths[ix])

    def test_parse(self):
        # Test 2 successful parses
        line_1 = 'Foonyor   1  0'
        line_2 = 'Barzane   0-12'

        parsed = self.parser.parse(line_1)
        self.assertEqual(parsed[0], 'Foonyor')
        self.assertEqual(parsed[1], True)
        self.assertEqual(parsed[2], 0)

        parsed = self.parser.parse(line_2)
        self.assertEqual(parsed[0], 'Barzane')
        self.assertEqual(parsed[1], False)
        self.assertEqual(parsed[2], -12)

        # Test data that cannot be type casted
        bad_line_1 = 'Foonyor   a  b'
        self.assertRaises(ValueError, self.parser.parse, bad_line_1)

        # Test data that does not match the expected widths
        bad_line_2 = 'Foonyor  '
        self.assertRaises(MalformedLineError, self.parser.parse, bad_line_2)
        bad_line_3 = 'supercalifragilisticexpialidocioussupercalifragilisticexpialidocious'
        self.assertRaises(MalformedLineError, self.parser.parse, bad_line_3)

    def test_convert_type(self):
        self.assertEqual(self.parser.convert_type(0, 'foo'), 'foo')
        self.assertEqual(self.parser.convert_type(1, '0'), False)
        self.assertEqual(self.parser.convert_type(1, '1'), True)
        self.assertEqual(self.parser.convert_type(2, '123'), 123)
        self.assertEqual(self.parser.convert_type(2, '-23'), -23)

        # fails type casting string -> bool
        self.assertRaises(ValueError, self.parser.convert_type, 1, 'a')
        self.assertRaises(ValueError, self.parser.convert_type, 1, 'foo')
        # fails type casting string -> int
        self.assertRaises(ValueError, self.parser.convert_type, 2, 'a')
        self.assertRaises(ValueError, self.parser.convert_type, 2, 'foo')

        # fails by passing a string ('a') as an index
        self.assertRaises(TypeError, self.parser.convert_type, 'a', 20)

