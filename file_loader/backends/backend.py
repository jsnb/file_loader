"""Base class for file loading backends
"""
from abc import abstractmethod, ABC


class Backend(ABC):
    """Abstract backend class"""

    def __init__(self):
        """abstract init"""
        pass

    @abstractmethod
    def insert_rows(self, rows: list, table: object) -> int:
        """method for inserting rows"""
        raise NotImplementedError

    @abstractmethod
    def init_backend(self, table_name: str, fields: list):
        """method for initializing the backend"""
        raise NotImplementedError
