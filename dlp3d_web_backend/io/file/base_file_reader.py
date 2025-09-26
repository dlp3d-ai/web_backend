from abc import ABC, abstractmethod

from ...utils.log import setup_logger
from ...utils.super import Super


class BaseFileReader(Super, ABC):
    """Base class for file reading operations.

    This abstract base class provides the interface for reading files from various
    storage backends. Subclasses must implement the abstract methods to provide
    specific file reading functionality.
    """

    def __init__(self,
                 name: str,
                 logger_cfg: None | dict = None) -> None:
        """Initialize the file reader.

        Args:
            name (str):
                Reader name.
            logger_cfg (None | dict, optional):
                Logger configuration, see `setup_logger` for detailed description.
                Logger name will use the class name. Defaults to None.
        """
        ABC.__init__(self)
        Super.__init__(self, logger_cfg)
        self.name = name
        self.logger_cfg['logger_name'] = self.name
        self.logger = setup_logger(**self.logger_cfg)

    @abstractmethod
    async def get_version(self) -> str:
        """Get the version of the reader.

        Returns:
            str: Version string.
        """
        pass

    @abstractmethod
    async def get_file_keys(self) -> list[str]:
        """Get all file names in the library.

        Returns:
            list[str]: List of file names.
        """
        pass

    @abstractmethod
    async def get_file_by_key(self, key: str) -> bytes:
        """Get file data by key.

        Args:
            key (str):
                File key/name.

        Returns:
            bytes: File data.
        """
        pass
