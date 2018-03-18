import mock
from unittest import TestCase

from file_loader.file_handler import FileHandler
from file_loader.exceptions import MissingSpecificationFile, InvalidFileNameFormat,\
    UnsupportedBackend, UnsupportedFileType


class FixedWidthTest(TestCase):
    def setUp(self):
        self.file_handler = FileHandler(
            './data',
            './specs',
            './data/failed',
            './data/loaded',
            'sqlite',
            'fixed_width',
            'sqlite////test.db',
            ['file1.txt', 'file2.txt']
        )

    def test_parse_file_name(self):
        # parsing expected file name in expected format
        data_file_name = 'testfile_10-13-2016.txt'
        parsed, drop_date = self.file_handler.parse_file_name(data_file_name)
        self.assertEqual(parsed, 'testfile')
        self.assertEqual(drop_date, '10-13-2016')

        # parsing file name with extra _ characters
        data_file_name = 'my_test_file_10-13-2016.txt'
        parsed, drop_date = self.file_handler.parse_file_name(data_file_name)
        self.assertEqual(parsed, 'my_test_file')
        self.assertEqual(drop_date, '10-13-2016')

        # testings file name that does not fit the convention
        data_file_name = 'testfilewithmissingdate.txt'
        self.assertRaises(InvalidFileNameFormat, self.file_handler.parse_file_name, data_file_name)


    def test_get_spec_file(self):
        data_file_name = 'testfile_10-13-2016.txt'

        # testing file name is returned if the path exists
        with mock.patch('file_loader.file_handler.os.path.exists') as mock_file_exists:
            mock_file_exists.return_value = True
            spec_file = self.file_handler.get_spec_file(data_file_name)

            self.assertEqual(spec_file, './specs/testfile.csv')

        # testing that missing file exception is raised when file does not exist
        with mock.patch('file_loader.file_handler.os.path.exists') as mock_file_exists:
            mock_file_exists.return_value = False
            self.assertRaises(MissingSpecificationFile,self.file_handler.get_spec_file, data_file_name)

    def test_run(self):
        file_handler = FileHandler(
            './data',
            './specs',
            './data/failed',
            './data/loaded',
            'sqlite',
            'fixed_width',
            'sqlite////test.db',
            ['file1.txt', 'file2.txt']
        )
        file_handler.get_spec_file = mock.Mock(return_value='specfile.csv')
        file_handler.move_file = mock.Mock()

        with mock.patch('file_loader.file_handler.Parser') as mock_parser_cls:
            instance = mock_parser_cls.return_value
            instance.run = mock.Mock()
            file_handler.run()

    def test_move_file(self):
        with mock.patch('file_loader.file_handler.os.rename') as mock_rename:
            # Test that file is moved to the target archive directory on success
            self.file_handler.move_file('./data/testfile.txt', True)
            mock_rename.assert_called_once_with(
                './data/testfile.txt',
                './data/loaded/testfile.txt'
            )

        with mock.patch('file_loader.file_handler.os.rename') as mock_rename:
            # Test that file is moved to the target failed directory on failure
            self.file_handler.move_file('./data/testfile.txt', False)
            mock_rename.assert_called_once_with(
                './data/testfile.txt',
                './data/failed/testfile.txt'
            )

    def test_invalid_backend(self):
        unsupported_backend = 'mongodb'

        self.assertRaises(
            UnsupportedBackend,
            FileHandler,
            './data',
            './specs',
            './data/failed',
            './data/loaded',
            unsupported_backend,
            'fixed_width',
            'sqlite////test.db',
            ['file1.txt', 'file2.txt']
        )

    def test_invalid_file_type(self):
        unsupported_file_type = 'json'

        self.assertRaises(
            UnsupportedFileType,
            FileHandler,
            './data',
            './specs',
            './data/failed',
            './data/loaded',
            'sqlite',
            unsupported_file_type,
            'sqlite////test.db',
            ['file1.txt', 'file2.txt']
        )
