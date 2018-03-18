import mock
from pathlib import Path
from unittest import TestCase
from sqlalchemy import MetaData
from sqlalchemy.sql.sqltypes import INTEGER, TEXT, BOOLEAN
from sqlalchemy.exc import StatementError

from file_loader.backend import SqlLiteBackend


class BackendTest(TestCase):
    def setUp(self):
        self.backend = SqlLiteBackend('mock_connection_str')

    def test_define_columns(self):
        fields = [
            ('Foo', 'TEXT'),
            ('Bar', 'INTEGER'),
            ('Baz', 'BOOLEAN'),
        ]

        columns = self.backend.define_columns(fields)

        # the number of columns returned should be 1 more than the fields supplied
        # the `id` primary key column is prepended to the list of columns
        num_columns = len(columns)
        self.assertEqual(num_columns, len(fields)+1)

        self.assertEqual(columns[0].name, 'id')
        self.assertEqual(type(columns[0].type), INTEGER)
        self.assertEqual(columns[1].name, 'Foo')
        self.assertEqual(type(columns[1].type), TEXT)
        self.assertEqual(columns[2].name, 'Bar')
        self.assertEqual(type(columns[2].type), INTEGER)
        self.assertEqual(columns[3].name, 'Baz')
        self.assertEqual(type(columns[3].type), BOOLEAN)

        # Testing that unsupported fields raise a KeyError
        bad_fields = [
            ('Foo', 'DECIMAL'),
            ('Bar', 'INTEGER'),
            ('Baz', 'BOOLEAN'),
        ]

        self.assertRaises(KeyError, self.backend.define_columns, bad_fields)

    def test_get_table(self):
        fields = [
            ('Foo', 'TEXT'),
            ('Bar', 'INTEGER'),
            ('Baz', 'BOOLEAN'),
        ]
        # metadata obj has to be initialized to create a table obj
        self.backend.metadata = MetaData()

        columns = self.backend.define_columns(fields)
        table = self.backend.get_table('test_table', columns)

        # assert basic attributes of the resulting table
        self.assertEqual(table.name, 'test_table')
        self.assertEqual(len(table.columns), 4)

        # look for primary key column `id`
        self.assertEqual(table.primary_key.columns.get('id').name, 'id')
        self.assertEqual(type(table.primary_key.columns.get('id').type), INTEGER)

        # verify that all the fields from the columns arg are in the resulting table obj
        self.assertEqual(table.columns.get('Foo').name, 'Foo')
        self.assertEqual(type(table.columns.get('Foo').type), TEXT)
        self.assertEqual(table.columns.get('Bar').name, 'Bar')
        self.assertEqual(type(table.columns.get('Bar').type), INTEGER)
        self.assertEqual(table.columns.get('Baz').name, 'Baz')
        self.assertEqual(type(table.columns.get('Baz').type), BOOLEAN)


class BackendIntegrationTest(TestCase):
    def setUp(self):
        # create a temp db file to be deleted in self.tearDown()
        self.db_file = 'test.db'
        self.p = Path(self.db_file)
        self.p.touch()
        connection_string = 'sqlite:///%s' % str(self.p.absolute())

        self.backend = SqlLiteBackend(connection_string)

        self.table_name = 'test_table'
        self.fields = [
            ('Foo', 'TEXT'),
            ('Bar', 'INTEGER'),
            ('Baz', 'BOOLEAN'),
        ]

        # For now have to initialize the backend in self.setUp() in order to test
        # all the methods with a valid sqlalchemy engine
        self.init_success = self.backend.init_backend(self.table_name, self.fields)

    def tearDown(self):
        # delete sqlite database file
        self.p.unlink()
        pass

    def test_init(self):
        # assert that init completed and that the resulting table exists
        self.assertEqual(self.init_success, True)
        self.assertEqual(self.backend.table_exists(self.table_name), True)

    def test_table_exists(self):
        # ensure that the initialized table exists
        self.assertEqual(self.backend.table_exists(self.table_name), True)
        # make sure that an arbitrary table returns false
        self.assertEqual(self.backend.table_exists('fake_table'), False)

    def test_insert_rows(self):
        rows = [
            {'Foo': 'Testing', 'Bar': 1, 'Baz': True},
            {'Foo': 'Insert', 'Bar': 2, 'Baz': False},
            {'Foo': 'Rows', 'Bar': 3, 'Baz': True},
            {'Foo': 'Testing', 'Bar': 4, 'Baz': False},
            {'Foo': 'Insert', 'Bar': 5, 'Baz': True},
            {'Foo': 'Rows', 'Bar': 6, 'Baz': False},
            {'Foo': 'Testing', 'Bar': 7, 'Baz': True},
        ]

        inserted = self.backend.insert_rows(rows, self.backend.table)
        # assert that 7 rows were inserted
        self.assertEqual(inserted, 7)

        # inconsistent keys in the rows dicts will raise an error on insert
        bad_rows = [
            {'Foo': 'Testing', 'Bar': 'hello', 'Baz': 0},
            {'FakeColumn': 'Testing', 'Bazzz': 'hello', 'Barrr': 0},
        ]

        self.assertRaises(StatementError, self.backend.insert_rows, bad_rows, self.backend.table)
