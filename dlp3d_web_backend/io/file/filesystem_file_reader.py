import os

from .base_file_reader import BaseFileReader


class FilesystemFileReader(BaseFileReader):
    """File reader implementation for local filesystem storage.

    This class provides functionality to read files from the local filesystem
    using a mapping of file keys to file paths.
    """

    def __init__(self,
                 name: str,
                 file_paths: dict[str, str],
                 root_dir: str | None = None,
                 logger_cfg: None | dict = None) -> None:
        """Initialize the filesystem file reader.

        Args:
            name (str):
                Name identifier for this file reader instance.
            file_paths (dict[str, str]):
                Dictionary mapping file keys to their corresponding file paths
                on the local filesystem.
            root_dir (str | None, optional):
                Root directory path for relative file paths.
                If provided, all file paths will be resolved relative
                to this directory. If None, file paths are used as-is.
                Defaults to None.
            logger_cfg (None | dict, optional):
                Logger configuration, see `setup_logger` for detailed description.
                Logger name will use the class name. Defaults to None.
        """
        BaseFileReader.__init__(self, name, logger_cfg)
        self.file_paths = file_paths
        self.root_dir = root_dir
        self.version = 'one_version'

    async def get_version(self) -> str:
        """Get the version of the file reader.

        Returns:
            str: Version string.
        """
        return self.version

    async def get_file_keys(self) -> list[str]:
        """Get all file keys in the library.

        Returns:
            list[str]: List of file keys.
        """
        return list(self.file_paths.keys())


    async def get_file_by_key(self, key: str) -> bytes:
        """Get file data by key.

        Args:
            key (str):
                File key.

        Returns:
            bytes: File data.
        """
        file_path = self.file_paths.get(key, None)
        if file_path is None:
            msg = f'No file data record about key={key}.'
            self.logger.error(msg)
            raise KeyError(msg)
        if self.root_dir is not None:
            file_path = os.path.join(self.root_dir, file_path)
        with open(file_path, 'rb') as f:
            return f.read()
