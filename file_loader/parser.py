"""Abstract parser class for dumping data from files to a database
"""
from file_loader.logger import logger


class Parser:
    """Running a parser class parses data according to the given parser class
    and inserts data into the given backend class
    """
    def __init__(self, data_file, schema_file, parser_cls: object,
                 backend_cls: object, connection_string: str):
        """

        :param data_file: single data file path to be parsed/dumped
        :param schema_file: schema file path instructs the parser on how to parse the data file
        :param parser_cls: class informs how the lines are parsed according to the schema file
        :param backend_cls: class implements the insert_rows method to dump data
        :param connection_string: needed to initialize the db for the backend cls
        """
        self.data_file = data_file
        # Initialize parser and backend classes
        self.parser = parser_cls(schema_file)
        self.backend = backend_cls(connection_string)
        # list of rows eventually is sent to the backend
        self.rows = []

        # connect to the database and create a new data store if needed
        self.backend.init_backend(self.parser.table_name, self.parser.columns)

    def run(self) -> bool:
        """
        uses the parser class to parse the file
        and then uses the backend class to dump the data to the backend

        :return: returns True if the number of records inserted is equal to the number
        of records supplied from the parser
        """
        rows = self.parse_file(self.data_file)
        num_rows_insert = self.backend.insert_rows(rows, self.backend.table)
        return num_rows_insert == len(rows)

    def parse_file(self, data_file_path) -> list:
        """iterate over the file and parse each row

        :param data_file: str path denotes the location of the data file
        :return: list of rows parsed according to the schema
        """
        rows = []
        logger.info('opening file `%s`', self.data_file)

        with open(data_file_path) as data:
            for line in data:
                values = self.parser.parse(line)
                # each row must have NAMED values so a dict is required instead
                # of a list of values
                rows.append(dict(zip(self.parser.field_names, values)))

        return rows
