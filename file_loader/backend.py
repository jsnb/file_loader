from sqlalchemy import create_engine, MetaData, Table, \
    Column, INTEGER, TEXT, BOOLEAN

from file_loader.logger import logger

class SqlLiteBackend:
    types = {
        'TEXT': TEXT,
        'INTEGER': INTEGER,
        'BOOLEAN': BOOLEAN
    }

    def __init__(self, connection_string):
        self.connection_string = connection_string

        # engine / metadata don't get initialized until explicitly needed
        self.engine = None
        self.metadata = None
        self.table = None

    def init_backend(self, table_name: str, fields: list):
        logger.info('Initializing backend for table: %s' % table_name)
        self.engine = create_engine(self.connection_string)
        self.metadata = MetaData(bind=self.engine)

        columns = self.define_columns(fields)
        self.table = self.get_table(table_name, columns)

        if not self.table_exists(table_name):
            logger.info('Table `%s` does not exist yet; creating now', table_name)
            self.create_table(self.table)
            logger.info('Table `%s` created', table_name)

        return True

    def define_columns(self, fields):
        id_column = Column('id', INTEGER, primary_key=True, autoincrement=True)
        sql_columns = [id_column]

        for field in fields:
            try:
                sql_type = self.types[field[1]]
            except KeyError as e:
                logger.error('Key Error: no associated backend type for `%s`', field[1])
                raise e

            column = Column(field[0], sql_type)
            sql_columns.append(column)
        return sql_columns

    def table_exists(self, table_name: str):
        return self.engine.dialect.has_table(self.engine, table_name)

    def create_table(self, table: object):
        table.create(checkfirst=True)
        return table

    def get_table(self, table_name: str, columns: list):
        return Table(
            table_name,
            self.metadata,
            *(c for c in columns)
        )

    def insert_rows(self, rows: list, table: object) -> int:
        engine = create_engine(self.connection_string)
        conn = engine.connect()
        row_count = 0

        # TODO figure out how to insert rows as a list instead of a dictionary
        # TODO as the number of rows grows it would be nice to have a smaller obj
        try:
            result = conn.execute(table.insert(), rows)
            row_count = result.rowcount
        except Exception as e:
            raise e
        finally:
            conn.close()

        return row_count
