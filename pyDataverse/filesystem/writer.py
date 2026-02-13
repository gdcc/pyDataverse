from io import IOBase
from queue import Queue
from threading import Thread
from time import sleep
from typing import Optional, Union

from pyDataverse.api import NativeApi
from pyDataverse.models.file import UploadBody


class DataverseFileWriter(IOBase):
    """
    A write-only file-like object that streams uploads to Dataverse.

    Implements a producer-consumer pattern where writes are immediately
    queued and uploaded by a background thread. This enables streaming
    uploads without loading the entire file into memory.

    The upload begins immediately when the object is created and continues
    as data is written, making it efficient for large files.

    Example:
        >>> writer = DataverseFileWriter(
        ...     native_api,
        ...     ds_identifier="doi:10.123/456",
        ...     metadata={"label": "data.csv"}
        ... )
        >>> with writer:
        ...     writer.write(b"header\\n")
        ...     writer.write(b"data\\n")
    """

    def __init__(
        self,
        native_api: NativeApi,
        ds_identifier: Union[str, int],
        metadata: UploadBody,
        file_identifier: Optional[Union[str, int]] = None,
    ):
        """
        Initialize a writer and start the upload.

        Args:
            native_api: API instance for uploading files
            ds_identifier: Dataset identifier to upload to
            metadata: File metadata (label, description, directoryLabel, etc.)
            file_identifier: If provided, replaces existing file

        Note:
            Upload begins immediately in a background thread.
        """
        self.native_api = native_api
        self.ds_identifier = ds_identifier
        self.file_identifier = file_identifier
        self.file_pid = None
        self.metadata = metadata

        # Set name attribute for httpx to use as filename in multipart form
        # httpx uses this attribute to determine the filename in the upload
        if metadata and metadata.filename:
            self.name = metadata.filename

        self._queue = Queue()
        self._closed = False
        self._upload_error = None
        self._upload_complete = False

        self._upload_thread = Thread(target=self._run_upload, daemon=False)
        self._upload_thread.start()

    @property
    def id(self) -> int:
        assert self.file_identifier and self._upload_complete, (
            "File identifier is not available until upload is complete"
        )
        return int(self.file_identifier)

    @property
    def persistent_id(self) -> str:
        assert self.file_identifier and self._upload_complete, (
            "File persistent identifier is not available until upload is complete"
        )
        return str(self.file_pid)

    def _run_upload(self):
        """Background thread that performs the upload."""
        try:
            if self.file_identifier:
                self.native_api.replace_datafile(
                    identifier=self.file_identifier,
                    file=self,  # type: ignore[arg-type]
                    metadata=self.metadata,
                )
            else:
                response = self.native_api.upload_datafile(
                    identifier=self.ds_identifier,
                    file=self,  # type: ignore[arg-type]
                    metadata=self.metadata,
                )

                if hasattr(response, "files") and response.files:
                    if response.files and len(response.files) > 0:
                        data_file = response.files[0].data_file
                        if data_file:
                            self.file_identifier = data_file.id
                            self.file_pid = data_file.persistent_id
                    else:
                        raise ValueError("No files returned from upload")

        except Exception as e:
            self._upload_error = e
        finally:
            self._upload_complete = True

    def readable(self) -> bool:
        """Return True so httpx can read from this object during upload."""
        return True

    def writable(self) -> bool:
        return not self._closed

    def read(self, size: int = -1) -> bytes:
        """
        Read data from the queue (called by httpx during upload).

        Args:
            size: Number of bytes to read. -1 reads all available.

        Returns:
            Data to upload, or empty bytes when done
        """
        if self._closed and self._queue.empty():
            return b""

        chunks = []
        bytes_read = 0

        while size == -1 or bytes_read < size:
            if self._queue.empty():
                if self._closed:
                    break
                sleep(0.01)
                continue

            chunk = self._queue.get()

            if chunk is None:
                break

            chunks.append(chunk)
            bytes_read += len(chunk)

            if size != -1 and bytes_read >= size:
                break

        return b"".join(chunks)

    def write(self, data: Union[bytes, str]) -> int:
        """
        Write data to the upload stream.

        Data is immediately queued and available for upload.

        Args:
            data: Bytes or string to write

        Returns:
            Number of bytes written

        Raises:
            IOError: If upload thread encountered an error
        """
        if not self.writable():
            raise ValueError("Cannot write to closed file")

        if isinstance(data, str):
            data = data.encode("utf-8")

        self._queue.put(data)

        if self._upload_error:
            raise IOError(f"Upload failed: {self._upload_error}")

        return len(data)

    def close(self):
        """
        Close the writer and wait for upload to complete.

        Raises:
            IOError: If upload failed or timed out
        """
        if self._closed:
            return

        self._closed = True
        self._queue.put(None)

        timeout_seconds = 60
        elapsed = 0

        while not self._upload_complete and elapsed < timeout_seconds:
            sleep(0.1)
            elapsed += 0.1

        if not self._upload_complete:
            raise IOError("Upload did not complete within timeout")

        if self._upload_error:
            raise IOError(f"Upload failed: {self._upload_error}")

    @property
    def closed(self) -> bool:
        return self._closed

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
