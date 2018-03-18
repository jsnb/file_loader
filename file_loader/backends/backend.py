"""Base class for file loading backends
"""


class Backend:
    """Abstract backend class"""
    def insert_rows(self, rows: list, table: object) -> int:
        """method for inserting rows"""
        raise NotImplementedError

    def init_backend(self, table_name: str, fields: list):
        """method for initializing the backend"""
        raise NotImplementedError
