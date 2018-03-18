from file_loader.logger import logger


class Parser:
    def __init__(self, data_file, schema_file, parser_cls: object, backend_cls: object, connection_string: str):
        self.data_file = data_file
        # Initialize parser and backend classes
        self.parser = parser_cls(schema_file)
        self.backend = backend_cls(connection_string)
        # list of rows eventually is sent to the backend
        self.rows = []

        # connect to the database and create a new data store if needed
        self.backend.init_backend(self.parser.table_name, self.parser.columns)

    def run(self) -> bool:
        rows = self.parse_file(self.data_file)
        num_rows_insert = self.backend.insert_rows(rows, self.backend.table)
        return num_rows_insert == len(rows)

    def parse_file(self, data_file) -> list:
        rows = []
        logger.info('opening file `%s`', self.data_file)
        with open(data_file) as data:
            for line in data:
                values = self.parser.parse(line)
                # each row must have NAMED values so a dict is required instead
                # of a list of values
                rows.append(dict(zip(self.parser.field_names, values)))

        return rows





