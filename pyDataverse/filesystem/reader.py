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
        self._known_end: Optional[int] = None

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

    def read(self, length: int = -1) -> bytes:
        """Read ``length`` bytes, or the rest of the file when ``length < 0``.

        A full read streams to the actual end of the HTTP body rather than
        stopping at the metadata-reported ``size``, which can be too small for
        ingested tabular files (see ``_known_end``). Sized reads keep fsspec's
        efficient, cached, range-based behavior.
        """
        if length is None or length < 0:
            if self._known_end is not None and self.loc >= self._known_end:
                return b""
            return self._read_to_end()
        return super().read(length)

    def _read_to_end(self) -> bytes:
        """Stream from the current position to the true end of the file."""
        start = self.loc
        with self.data_access_api.stream_datafile(
            self.file_identifier,
            range_start=start or None,
        ) as response:
            data = b"".join(response.iter_bytes())

        self.loc = start + len(data)
        self._known_end = self.loc
        if self.loc > self.size:
            self.size = self.loc
        return data

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
