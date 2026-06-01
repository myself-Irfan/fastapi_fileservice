from dataclasses import dataclass


@dataclass(frozen=True)
class FileMetadata:
    title: str
    file_path: str
    file_size: int
    mime_type: str
    extension: str
    checksum: str