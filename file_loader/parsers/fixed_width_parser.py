import csv
import os
from file_loader.exceptions import MalformedLineError
from file_loader.logger import logger

class FixedWidthParser:
    COLUMN_NAME = 'column name'
    WIDTH = 'width'
    DATA_TYPE = 'datatype'

    def __init__(self, schema_file):
        self.field_names = []
        self.widths = []
        self.data_types = []
        self.file_name = schema_file
        self.define_schema(schema_file)

    @property
    def table_name(self):
        path = os.path.splitext(self.file_name)[0]
        return os.path.split(path)[-1]

    @property
    def columns(self):
        return zip(self.field_names, self.data_types)

    def define_schema(self, schema_file):
        with open(schema_file, 'r') as schema:
            reader = csv.DictReader(schema)
            for line in reader:
                self.field_names.append(line.get(self.COLUMN_NAME))
                self.widths.append(int(line.get(self.WIDTH)))
                self.data_types.append(line.get(self.DATA_TYPE))

    def parse(self, line: str) -> list:
        '''

        :param line: represents a single line in the data file to be parsed
        :return: parsed_values is a parsed list of values to be inserted into the db
        '''
        line = line.strip()
        if len(line) != sum(self.widths):
            logger.error('Malformed Line <%s> does not match widths %s', line, self.widths)
            raise MalformedLineError

        parsed_values = []
        position = 0
        # parse AND validating so as to only iterate over the values once
        for ix in range(len(self.widths)):
            value = self.convert_type(ix, line[position:position + self.widths[ix]])
            parsed_values.append(value)
            position += self.widths[ix]

        return parsed_values

    def convert_type(self, field_position: int, value: str):
        data_type = self.data_types[field_position]
        types = {
            'TEXT': str,
            'INTEGER': int,
            'BOOLEAN': lambda x: bool(int(x))
        }
        try:
            converted_value = types[data_type](value.strip())
        except ValueError as e:
            raise e
        return converted_value

