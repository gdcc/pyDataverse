from io import IOBase
from typing import Generic, Literal, Optional, TypeVar, Union, overload

from ..api import DataAccessApi

_ModeT = TypeVar("_ModeT", Literal["r"], Literal["rb"])


class DataverseFileReader(IOBase, Generic[_ModeT]):
    """
    A read-only file-like object that streams content from Dataverse.

    Wraps the Dataverse Data Access API streaming response, providing a
    standard Python file interface. Data is fetched in chunks as needed,
    making it memory-efficient for large files.

    Example:
        >>> reader = DataverseFileReader(data_access_api, file_identifier=12345)
        >>> with reader:
        ...     data = reader.read(1024)
        ...     rest = reader.read()
        >>> # Use slice notation to read specific byte ranges
        >>> with reader:
        ...     chunk = reader[100:1000]  # Read bytes 100-1000
    """

    def __init__(
        self,
        data_access_api: DataAccessApi,
        file_identifier: str | int,
        mode: Literal["r", "rb"] = "r",
    ):
        """
        Initialize a reader for a Dataverse file.

        Args:
            data_access_api: API instance for accessing file data
            file_identifier: Database ID or persistent ID of the file
            mode: File mode. Supported modes:
                - 'r', 'rb': Read (default)

        Raises:
            ValueError: If an invalid mode is provided
        """

        self.api = data_access_api
        self.file_identifier = file_identifier
        self._mode = mode

        self._stream_context = None
        self._chunk_iterator = None
        self._buffer = b""
        self._closed = False

    def _initialize_stream(self):
        """Open the streaming connection to Dataverse on first read."""
        if self._stream_context is None:
            self._stream_context = self.api.stream_datafile(self.file_identifier)
            response = self._stream_context.__enter__()
            self._chunk_iterator = response.iter_bytes(chunk_size=8192)

    def _decode_bytes(self, data: bytes) -> str:
        """Decode bytes to string with UTF-8 fallback to latin-1."""
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("latin-1")

    def _read_bytes(self, size: int = -1) -> bytes:
        """Read bytes from the stream."""
        if self._chunk_iterator is None:
            return b""

        if size == -1:
            chunks = [self._buffer]
            try:
                while True:
                    chunks.append(next(self._chunk_iterator))
            except StopIteration:
                pass
            result = b"".join(chunks)
            self._buffer = b""
            return result

        while len(self._buffer) < size:
            try:
                self._buffer += next(self._chunk_iterator)
            except StopIteration:
                break

        result = self._buffer[:size]
        self._buffer = self._buffer[size:]
        return result

    def _read_range(self, start: int, end: Optional[int]) -> bytes:
        """Read a specific byte range using Range header."""
        if self._closed:
            raise ValueError("Cannot read from closed file")

        # Create a new stream context for this range request
        with self.api.stream_datafile(
            self.file_identifier,
            range_start=start,
            range_end=end,
        ) as response:
            # Read all data from the range response
            result = b""
            for chunk in response.iter_bytes():
                result += chunk

        return result

    def __getitem__(self, key: Union[int, slice]) -> Union[bytes, str]:
        """
        Support slice notation for reading byte ranges.

        Args:
            key: Integer index or slice object (e.g., [100:1000])

        Returns:
            Bytes (for 'rb' mode) or string (for 'r' mode) from the specified range

        Examples:
            >>> f[100:1000]  # Read bytes 100-1000
            >>> f[100:]      # Read from byte 100 to end
            >>> f[:1000]     # Read first 1000 bytes
            >>> f[100]       # Read single byte at position 100
        """
        if self._closed:
            raise ValueError("Cannot read from closed file")

        if isinstance(key, int):
            # Single byte access: read one byte
            data = self._read_range(key, key)
            if len(data) == 0:
                raise IndexError("Index out of range")
            result = data[0:1]
        elif isinstance(key, slice):
            # Slice access
            start = key.start if key.start is not None else 0
            stop = key.stop

            # Handle negative indices (would require knowing file size)
            if start < 0 or (stop is not None and stop < 0):
                raise NotImplementedError(
                    "Negative indices require file size information. "
                    "Use positive indices or read the file first."
                )

            # Read the range
            data = self._read_range(start, stop)
            result = data
        else:
            raise TypeError(f"Invalid key type: {type(key)}")

        # Decode if in text mode
        if self._mode == "r":
            return self._decode_bytes(result)
        return result

    def readable(self) -> bool:
        return not self._closed

    def writable(self) -> bool:
        return False

    @overload
    def read(self: "DataverseFileReader[Literal['rb']]", size: int = -1) -> bytes:
        """
        Read bytes when in 'rb' mode.

        Returns:
            bytes: The file content as bytes
        """
        ...

    @overload
    def read(self: "DataverseFileReader[Literal['r']]", size: int = -1) -> str:
        """
        Read string when in 'r' mode.

        Returns:
            str: The file content as a decoded string
        """
        ...

    def read(
        self,
        size: int = -1,
    ) -> Union[bytes, str]:
        """
        Read data from the Dataverse file.

        Args:
            size: Number of bytes/characters to read. -1 reads all remaining data.

        Returns:
            Bytes (for 'rb' mode) or string (for 'r' mode) read from the file
        """
        if self._closed:
            raise ValueError("Cannot read from closed file")

        self._initialize_stream()

        if self._chunk_iterator is None:
            return b"" if self._mode == "rb" else ""

        result = self._read_bytes(size)

        if self._mode == "r":
            return self._decode_bytes(result)
        return result

    def close(self):
        """Close the streaming connection to Dataverse."""
        if self._closed:
            return

        if self._stream_context is not None:
            self._stream_context.__exit__(None, None, None)
        self._closed = True

    @property
    def closed(self) -> bool:
        return self._closed

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
