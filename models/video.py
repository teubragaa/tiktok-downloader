from dataclasses import dataclass
from pathlib import Path


@dataclass
class DownloadRequest:
    url: str


@dataclass
class DownloadResult:
    title: str
    uploader: str
    file_name: str
    file_path: Path
    temp_folder: Path