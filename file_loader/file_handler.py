"""Handler for routing files to parsers and moving them in the file system
"""
import os

from file_loader.exceptions import UnsupportedBackend, UnsupportedFileType,\
    MissingSpecificationFile, InvalidFileNameFormat
from file_loader.logger import logger
from file_loader.parser import Parser
from file_loader.parsers.fixed_width_parser import FixedWidthParser
from file_loader.backends.sqlite import SqlLiteBackend


class FileHandler:
    """Utility for dealing with files before and after they have been parsed

    FileHandler class is the main entry point for the application
    In it's initialization it creates a parser object and parses the file
    Moves the file out of the initial data directory and sends it to the archive or failed dir
    """

    FILE_TYPES = {
        'fixed_width': FixedWidthParser
    }

    BACKENDS = {
        'sqlite': SqlLiteBackend
    }

    def __init__(self, data_dir: str, specs_dir: str, failed_dir: str, archive_dir: str,
                 backend: str, file_type: str, connection_string: str, files: str):
        """
        :param data_dir: location of target files
        :param specs_dir: directory containing specification files
        :param failed_dir: send failed parsed files here
        :param archive_dir: successfully parsed files go here
        :param backend: key that maps to a backend class eg // `sqlite`
        :param file_type: key that maps to a file type parser class eg// `fixed_width`
        :param connection_string: target data store
        :param files: list of files to be loaded into the database
        """
        self.data_dir = data_dir
        self.specs_dir = specs_dir
        self.failed_dir = failed_dir
        self.archive_dir = archive_dir
        self.files = files
        self.connection_string = connection_string
        self.files = files

        self.backend_cls = self.BACKENDS.get(backend)
        if self.backend_cls is None:
            logger.error('Backend `%s` is not supported. Choose from supported backends %s',
                         backend, self.BACKENDS.keys())
            raise UnsupportedBackend

        self.parser_type_cls = self.FILE_TYPES.get(file_type)
        if self.parser_type_cls is None:
            logger.error('File type `%s` is not supported. Choose from supported file types %s',
                         backend, self.FILE_TYPES.keys())
            raise UnsupportedFileType

    def run(self):
        """
        Iterate over the list of files and attempt to parse them
        :return:
        """
        for data_file_name in self.files:
            spec_file = self.get_spec_file(data_file_name)
            data_file_path = os.path.join(self.data_dir, data_file_name)
            parser = Parser(
                data_file_path,
                spec_file,
                self.parser_type_cls,
                self.backend_cls,
                self.connection_string)
            load_success = parser.run()

            self.move_file(data_file_path, load_success)

    def move_file(self, file_path: str, success: bool):
        """

        :param file_path: path of the original file
        :param success: success determines where the file ends up
        :return:
        """
        if success:
            target_dir = self.archive_dir
        else:
            target_dir = self.failed_dir
        file_name = os.path.split(file_path)[-1]
        os.rename(file_path, os.path.join(target_dir, file_name))

    @staticmethod
    def parse_file_name(path: str):
        """
        Parsing the file based on the conventions laid out in the assignment
        filename_YYYY-MM-dd

        :param path:
        :return:
        """
        file_name = os.path.splitext(path)[0]
        file_name_parts = file_name.split('_')

        if len(file_name_parts) < 2:
            logger.error(
                'File name `%s` does not conform to expected file format filename_YYYY-MM-dd',
                file_name)
            raise InvalidFileNameFormat

        # TODO raise if the date format is incorrect? Not doing anything with this date yet
        drop_date = file_name_parts[-1]

        file_type = '_'.join(file_name_parts[0:-1])
        return file_type, drop_date

    def get_spec_file(self, data_file_name):
        """
        Given a data file name grab the location of the spec file

        :param data_file_name:
        :return:
        """
        file_type, drop_date = self.parse_file_name(data_file_name)
        spec_file = os.path.join(self.specs_dir, file_type + '.csv')

        if os.path.exists(spec_file):
            return spec_file
        else:
            logger.error('No spec file found for %s', data_file_name)
            raise MissingSpecificationFile
