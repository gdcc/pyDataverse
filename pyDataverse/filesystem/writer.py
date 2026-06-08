import io
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING, Optional, Union

from fsspec.spec import AbstractBufferedFile

from pyDataverse.models.file import UploadBody

if TYPE_CHECKING:
    from .dvfs import DataverseFS

# How long to wait for the background upload thread to finish on close.
_UPLOAD_TIMEOUT_SECONDS = 300


class _UploadStream(io.RawIOBase):
    """File-like source that httpx reads from during a streaming upload.

    Acts as the consumer end of a producer/consumer queue: chunks written by
    the :class:`DataverseFileWriter` are pushed onto the queue, and httpx pulls
    them out via ``read`` as the multipart request body is sent. ``read``
    blocks until either enough bytes are available or the stream is finished,
    so the whole file is never held in memory at once.
    """

    def __init__(self, name: Optional[str] = None):
        self._queue: "Queue[Optional[bytes]]" = Queue()
        self._buffer = b""
        self._eof = False
        if name:
            # httpx uses this attribute as the multipart filename.
            self.name = name

    def put(self, data: bytes) -> None:
        if data:
            self._queue.put(data)

    def finish(self) -> None:
        self._queue.put(None)

    def readable(self) -> bool:
        return True

    def read(self, size: int = -1) -> bytes:
        if size is None or size < 0:
            while not self._eof:
                item = self._queue.get()
                if item is None:
                    self._eof = True
                else:
                    self._buffer += item
            result, self._buffer = self._buffer, b""
            return result

        while len(self._buffer) < size and not self._eof:
            item = self._queue.get()
            if item is None:
                self._eof = True
            else:
                self._buffer += item

        result, self._buffer = self._buffer[:size], self._buffer[size:]
        return result


class DataverseFileWriter(AbstractBufferedFile):
    """
    A write-only fsspec file object that streams uploads to Dataverse.

    Built on :class:`fsspec.spec.AbstractBufferedFile`. fsspec buffers at most
    one ``blocksize`` chunk before calling :meth:`_upload_chunk`, and each chunk
    is handed straight to a background upload thread through an
    :class:`_UploadStream`. This keeps memory bounded by the block size rather
    than the file size, even for very large uploads. If a file already exists at
    the given path it is replaced; otherwise a new file is created.

    Example:
        >>> with fs.open("data/newfile.csv", "wb") as f:
        ...     f.write(b"column1,column2\\n")
        ...     f.write(b"value1,value2\\n")
    """

    def __init__(
        self,
        fs: "DataverseFS",
        path: str,
        metadata: Optional[UploadBody] = None,
        block_size: Union[int, str] = "default",
        **kwargs,
    ):
        """
        Initialize a streaming writer.

        Args:
            fs: The owning DataverseFS instance.
            path: Destination path within the dataset.
            metadata: Optional upload metadata. If omitted, it is derived from
                ``path`` (directory label + filename).
            block_size: Upload chunk size ("default" for the fsspec default).
        """
        self.native_api = fs.native_api
        self.ds_identifier = fs.identifier

        normalized = path.strip("/")
        if "/" in normalized:
            directory_label, filename = normalized.rsplit("/", 1)
        else:
            directory_label, filename = "", normalized

        if metadata is None:
            metadata = UploadBody(
                directory_label=directory_label or None,
                filename=filename,
            )

        self.metadata = metadata
        self._filename = metadata.filename or filename

        # If the file already exists, capture its ID so we replace it.
        self.file_identifier: Optional[Union[str, int]] = None
        try:
            existing = fs._find_file(normalized)
            if existing.data_file is not None:
                self.file_identifier = existing.data_file.id
        except FileNotFoundError:
            pass

        self.file_pid: Optional[str] = None
        self._stream: Optional[_UploadStream] = None
        self._thread: Optional[Thread] = None
        self._error: Optional[Exception] = None
        self._response = None

        super().__init__(fs, path, mode="wb", block_size=block_size, **kwargs)

    @property
    def id(self) -> int:
        assert self.file_identifier is not None, (
            "File identifier is not available until upload is complete"
        )
        return int(self.file_identifier)

    @property
    def persistent_id(self) -> str:
        assert self.file_pid is not None, (
            "File persistent identifier is not available until upload is complete"
        )
        return str(self.file_pid)

    def _initiate_upload(self) -> None:
        """Start the background upload thread on the first flush."""
        self._stream = _UploadStream(name=self._filename)

        def _run() -> None:
            try:
                if self.file_identifier is not None:
                    self._response = self.native_api.replace_datafile(
                        identifier=self.file_identifier,
                        file=self._stream,  # type: ignore[arg-type]
                        metadata=self.metadata,
                    )
                else:
                    self._response = self.native_api.upload_datafile(
                        identifier=self.ds_identifier,
                        file=self._stream,  # type: ignore[arg-type]
                        metadata=self.metadata,
                    )
            except Exception as exc:  # noqa: BLE001 - surfaced on the writer thread
                self._error = exc

        self._thread = Thread(target=_run, daemon=False)
        self._thread.start()

    def _upload_chunk(self, final: bool = False) -> bool:
        """Push the current buffer to the upload stream (fsspec hook)."""
        assert self._stream is not None  # set by _initiate_upload

        if self._error is not None:
            raise IOError(f"Upload failed: {self._error}")

        data = self.buffer.getvalue()
        if data:
            self._stream.put(data)

        if final:
            self._finalize()

        return True

    def _finalize(self) -> None:
        """Signal end-of-stream and wait for the upload to complete."""
        assert self._stream is not None and self._thread is not None

        self._stream.finish()
        self._thread.join(timeout=_UPLOAD_TIMEOUT_SECONDS)

        if self._thread.is_alive():
            raise IOError("Upload did not complete within timeout")
        if self._error is not None:
            raise IOError(f"Upload failed: {self._error}")

        self._capture_result()
        self.fs._cache.clear()

    def _capture_result(self) -> None:
        """Extract the new file's ID/PID from the upload response."""
        response = self._response
        if response is not None and getattr(response, "files", None):
            data_file = response.files[0].data_file
            if data_file is not None:
                self.file_identifier = data_file.id
                self.file_pid = data_file.persistent_id
