"""Backend class for sqlite adapter
"""

from sqlalchemy import create_engine, MetaData, Table, \
    Column, INTEGER, TEXT, BOOLEAN

from file_loader.backends.backend import Backend
from file_loader.logger import logger


class SqlLiteBackend(Backend):
    """Sqlite adapter"""
    types = {
        'TEXT': TEXT,
        'INTEGER': INTEGER,
        'BOOLEAN': BOOLEAN
    }

    def __init__(self, connection_string: str):
        """

        :param connection_string: required for connecting to the db
        """
        self.connection_string = connection_string

        # engine / metadata don't get initialized until explicitly needed
        self.engine = None
        self.metadata = None
        self.table = None
        super().__init__()

    def init_backend(self, table_name: str, fields: list):
        """Initializes the backend by creating a table object and creating
        that table if it doesn't yet exist

        :param table_name: target table for parsed data
        :param fields: list of columns and their data types for the table
        :return:
        """
        logger.info('Initializing backend for table: %s', table_name)
        self.engine = create_engine(self.connection_string)
        self.metadata = MetaData(bind=self.engine)

        columns = self.define_columns(fields)
        self.table = self.get_table(table_name, columns)

        if not self.table_exists(table_name):
            logger.info('Table `%s` does not exist yet; creating now', table_name)
            self.create_table(self.table)
            logger.info('Table `%s` created', table_name)

        return True

    def define_columns(self, fields: list) -> list:
        """Given a list of columns and their data types create a list
        of SqlAlchemy Column objects.
        All tables will have an id identity primary key

        :param fields: list of column names and their data types
        :return:
        """
        id_column = Column('id', INTEGER, primary_key=True, autoincrement=True)
        sql_columns = [id_column]

        for field in fields:
            try:
                sql_type = self.types[field[1]]
            except KeyError as exc:
                logger.error('Key Error: no associated backend type for `%s`', field[1])
                raise exc

            column = Column(field[0], sql_type)
            sql_columns.append(column)
        return sql_columns

    def table_exists(self, table_name: str):
        """Check to see if the table exists in the backend

        :param table_name:
        :return:
        """
        return self.engine.dialect.has_table(self.engine, table_name)

    @staticmethod
    def create_table(table: object):
        """When a table doesn't exist need to create it

        :param table:
        :return:
        """
        table.create(checkfirst=True)
        return table

    def get_table(self, table_name: str, columns: list):
        """given a table name and list of columns create a sqlalchemy table obj

        :param table_name: name of the destination table
        :param columns: list of sqlalchemy Columns
        :return:
        """
        return Table(
            table_name,
            self.metadata,
            *(c for c in columns)
        )

    def insert_rows(self, rows: list, table: object) -> int:
        """Given a list of rows insert it into the database

        :param rows: list of parsed data rows to be inserted
        :param table: table object
        :return: number of rows inserted in the db
        """
        engine = create_engine(self.connection_string)
        conn = engine.connect()
        row_count = 0

        # TODO figure out how to insert rows as a list instead of a dictionary
        # TODO as the number of rows grows it would be nice to have a smaller obj
        try:
            # uses the execute many functionality
            result = conn.execute(table.insert(), rows)
            row_count = result.rowcount
        except Exception as exc:
            raise exc
        finally:
            conn.close()

        return row_count
