import mock
from io import StringIO
from unittest import TestCase

from file_loader.parser import Parser
from file_loader.parsers.fixed_width_parser import FixedWidthParser
from file_loader.backends.sqlite import SqlLiteBackend


class ParserTest(TestCase):
    def setUp(self):
        self.test_data = '''Foonyor   1  0\nBarzane   0-12\nQuuxitude 1103\n'''

        test_schema = '''"column name",width,datatype\n
name,10,TEXT\n
valid,1,BOOLEAN\n
count,3,INTEGER'''

        with mock.patch('file_loader.parsers.fixed_width_parser.open') as schema_open:
            schema_open.return_value = StringIO(test_schema)

            data_file = 'testdata_10-31-2017.txt'
            schema_file = 'testdata.csv'
            mock_connection = 'fakeconnection'
            with mock.patch('file_loader.backends.sqlite.SqlLiteBackend.init_backend') as mock_backend:
                mock_backend.return_value(True)
                self.parser = Parser(data_file, schema_file, FixedWidthParser, SqlLiteBackend, mock_connection)

    def test_parse_file(self):
        expected_rows = [
            {'name': 'Foonyor', 'valid': True, 'count': 0},
            {'name': 'Barzane', 'valid': False, 'count': -12},
            {'name': 'Quuxitude', 'valid': True, 'count': 103}
        ]

        with mock.patch('file_loader.parser.open') as data_open:
            # mock the data file with StringIO obj
            data_open.return_value = StringIO(self.test_data)
            # call parse on the mocked data file
            rows = self.parser.parse_file('mock_data_path.csv')

            for ix in range(len(rows)):
                self.assertEqual(rows[ix].get('name'), expected_rows[ix].get('name'))
                self.assertEqual(rows[ix].get('valid'), expected_rows[ix].get('valid'))
                self.assertEqual(rows[ix].get('count'), expected_rows[ix].get('count'))

    def test_run(self):
        rows = [
            {'name': 'Foonyor', 'valid': True, 'count': 0},
        ]

        self.parser.parse_file = mock.MagicMock(return_value=rows)
        self.parser.backend.insert_rows = mock.MagicMock(return_value=True)

        self.parser.run()

        self.parser.parse_file.assert_called_once_with(self.parser.data_file)
        self.parser.backend.insert_rows.assert_called_once_with(rows, self.parser.backend.table)
