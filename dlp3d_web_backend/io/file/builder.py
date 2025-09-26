from .filesystem_file_reader import FilesystemFileReader
from .minio_file_reader import MinioFileReader

_FILE_READER = dict(
    FilesystemFileReader=FilesystemFileReader,
    MinioFileReader=MinioFileReader)


def build_file_reader(cfg: dict) -> MinioFileReader | FilesystemFileReader:
    """Build a file reader instance from a configuration dictionary.

    Args:
        cfg (dict):
            Configuration dictionary containing the file reader type and
            initialization parameters.

    Returns:
        MinioFileReader | FilesystemFileReader: File reader instance.

    Raises:
        TypeError: If the specified file reader type is not supported.
    """
    cfg = cfg.copy()
    cls_name = cfg.pop('type')
    if cls_name not in _FILE_READER:
        msg = f'Unknown file reader type: {cls_name}'
        raise TypeError(msg)
    ret_inst = _FILE_READER[cls_name](**cfg)
    return ret_inst
