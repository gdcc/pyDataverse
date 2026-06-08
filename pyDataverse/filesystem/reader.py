from typing import TYPE_CHECKING, Optional, Union

from fsspec.spec import AbstractBufferedFile

if TYPE_CHECKING:
    from .dvfs import DataverseFS


class DataverseFileReader(AbstractBufferedFile):
    """
    A read-only fsspec file object that streams content from Dataverse.

    Built on :class:`fsspec.spec.AbstractBufferedFile`, so it supports the
    full file protocol (``read``, ``seek``, iteration, context manager) while
    only fetching the bytes that are actually requested. Random access is
    served via HTTP Range requests against the Data Access API, so seeking
    backwards or reading a slice never downloads the whole file.

    Example:
        >>> with fs.open("data/file.csv", "rb") as f:
        ...     header = f.read(1024)
        ...     f.seek(0)
        >>> # Slice notation reads an explicit byte range
        >>> with fs.open("data/file.csv", "rb") as f:
        ...     chunk = f[100:1000]
    """

    def __init__(
        self,
        fs: "DataverseFS",
        path: str,
        file_identifier: Union[str, int],
        size: Optional[int] = None,
        block_size: Union[int, str] = "default",
        cache_type: str = "readahead",
        cache_options: Optional[dict] = None,
        **kwargs,
    ):
        """
        Initialize a reader for a Dataverse file.

        Args:
            fs: The owning DataverseFS instance.
            path: Path to the file within the dataset.
            file_identifier: Database ID or persistent ID of the file.
            size: Optional known file size, to avoid an extra metadata lookup.
            block_size: Read-ahead block size ("default" for the fsspec default).
            cache_type: fsspec read cache policy.
            cache_options: Additional options for the read cache.
        """
        self.data_access_api = fs.data_access_api
        self.file_identifier = file_identifier
        super().__init__(
            fs,
            path,
            mode="rb",
            block_size=block_size,
            cache_type=cache_type,
            cache_options=cache_options,
            size=size,
            **kwargs,
        )

    def _fetch_range(self, start: int, end: int) -> bytes:
        """Fetch a byte range ``[start, end)`` via a Range request.

        fsspec uses an exclusive ``end``, whereas the Data Access API Range
        header is inclusive, hence ``range_end=end - 1``.
        """
        if end <= start:
            return b""

        with self.data_access_api.stream_datafile(
            self.file_identifier,
            range_start=start,
            range_end=end - 1,
        ) as response:
            return b"".join(response.iter_bytes())

    def __getitem__(self, key: Union[int, slice]) -> bytes:
        """
        Read a byte range using indexing/slice notation.

        Examples:
            >>> f[100:1000]  # bytes 100-999
            >>> f[100:]      # byte 100 to end
            >>> f[:1000]     # first 1000 bytes
            >>> f[100]       # single byte at position 100
        """
        if self.closed:
            raise ValueError("Cannot read from closed file")

        if isinstance(key, int):
            data = self._fetch_range(key, key + 1)
            if not data:
                raise IndexError("Index out of range")
            return data

        if isinstance(key, slice):
            if key.step not in (None, 1):
                raise ValueError("Slice steps other than 1 are not supported")

            start = key.start if key.start is not None else 0
            stop = key.stop

            if start < 0 or (stop is not None and stop < 0):
                raise NotImplementedError(
                    "Negative indices are not supported; use positive indices."
                )

            if stop is None:
                stop = self.size

            return self._fetch_range(start, stop)

        raise TypeError(f"Invalid key type: {type(key)}")
