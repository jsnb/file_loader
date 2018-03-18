import os

from file_loader.exceptions import UnsupportedBackend, UnsupportedFileType,\
    MissingSpecificationFile, InvalidFileNameFormat
from file_loader.logger import logger
from file_loader.parser import Parser
from file_loader.parsers.fixed_width_parser import FixedWidthParser
from file_loader.backend import SqlLiteBackend


class FileHandler:
    FILE_TYPES = {
        'fixed_width': FixedWidthParser
    }

    BACKENDS = {
        'sqlite': SqlLiteBackend
    }

    def __init__(self, data_dir, specs_dir, failed_dir, archive_dir, backend, file_type,
                 connection_string, files):
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
        for data_file_name in self.files:
            spec_file = self.get_spec_file(data_file_name)
            data_file_path = os.path.join(self.data_dir, data_file_name)
            p = Parser(
                data_file_path,
                spec_file,
                self.parser_type_cls,
                self.backend_cls,
                self.connection_string)
            load_success = p.run()

            self.move_file(data_file_path, load_success)

    def move_file(self, file_path: str, success: bool):
        if success:
            target_dir = self.archive_dir
        else:
            target_dir = self.failed_dir
        file_name = os.path.split(file_path)[-1]
        os.rename(file_path, os.path.join(target_dir, file_name))

    def parse_file_name(self, path):
        file_name, ext = os.path.splitext(path)
        file_name_parts = file_name.split('_')

        if len(file_name_parts) < 2:
            logger.error('File name `%s` does not conform to expected file format filename_YYYY-MM-dd', file_name)
            raise InvalidFileNameFormat

        # TODO raise if the date format is incorrect? Not doing anything with this date yet
        drop_date = file_name_parts[-1]

        file_type = '_'.join(file_name_parts[0:-1])
        return file_type, drop_date

    def get_spec_file(self, data_file_name):
        file_type, drop_date = self.parse_file_name(data_file_name)
        spec_file = os.path.join(self.specs_dir, file_type + '.csv')

        if os.path.exists(spec_file):
            return spec_file
        else:
            logger.error('No spec file found for %s', data_file_name)
            raise MissingSpecificationFile


