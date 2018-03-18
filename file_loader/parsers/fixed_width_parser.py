"""Fixed Width Parsing"""
import csv
import os

from file_loader.exceptions import MalformedLineError
from file_loader.logger import logger


class FixedWidthParser:
    """Parser class defines how to parse a fixed width file"""
    COLUMN_NAME = 'column name'
    WIDTH = 'width'
    DATA_TYPE = 'datatype'

    def __init__(self, schema_file_path):
        """

        :param schema_file_path: path to schema file
        """
        self.field_names = []
        self.widths = []
        self.data_types = []
        self.file_name = schema_file_path
        self.define_schema(schema_file_path)

    @property
    def table_name(self):
        """default table name according to the filename"""
        path = os.path.splitext(self.file_name)[0]
        return os.path.split(path)[-1]

    @property
    def columns(self):
        """needs to be a key value store of name -> data type"""
        return zip(self.field_names, self.data_types)

    def define_schema(self, schema_file_path):
        """according the file spec get a list of widths/field names/data types

        :param schema_file_path: location of the schema file
        :return:
        """
        with open(schema_file_path, 'r') as schema_file:
            reader = csv.DictReader(schema_file)
            for line in reader:
                self.field_names.append(line.get(self.COLUMN_NAME))
                self.widths.append(int(line.get(self.WIDTH)))
                self.data_types.append(line.get(self.DATA_TYPE))

    def parse(self, line: str) -> list:
        """

        :param line: represents a single line in the data file to be parsed
        :return: parsed_values is a parsed list of values to be inserted into the db
        """
        line = line.strip()
        if len(line) != sum(self.widths):
            logger.error('Malformed Line <%s> does not match widths %s', line, self.widths)
            raise MalformedLineError

        parsed_values = []
        position = 0
        # parse AND validating so as to only iterate over the values once
        for index in range(len(self.widths)):
            value = self.convert_type(index, line[position:position + self.widths[index]])
            parsed_values.append(value)
            position += self.widths[index]

        return parsed_values

    def convert_type(self, field_position: int, value: str):
        """Covert the value in the row according to the schema file

        :param field_position: position of the value within the data line
        :param value: the str from the file that needs to be converted
        :return: type depends on the type converson
        """
        data_type = self.data_types[field_position]
        # only supporting these 3 types
        types = {
            'TEXT': str,
            'INTEGER': int,
            'BOOLEAN': lambda x: bool(int(x))
        }
        try:
            converted_value = types[data_type](value.strip())
        except ValueError as exc:
            raise exc
        return converted_value
