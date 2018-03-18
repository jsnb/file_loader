"""Custom exceptions for file loading application"""


class MalformedLineError(Exception):
    """Raise when a line in a file does not meet parsing expectations"""
    pass


class UnsupportedFileType(Exception):
    """Raise if parser app does not support the format of the file (eg fixed width, csv, etc"""
    pass


class UnsupportedBackend(Exception):
    """Raise if an backend chosen is not supported by the app"""
    pass


class MissingSpecificationFile(Exception):
    """Every file requires a spec file to parse"""
    pass

class InvalidFileNameFormat(Exception):
    """File formats must follow a convention"""
    pass
