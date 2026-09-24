from pathlib import Path
import uuid
import yt_dlp

from models.video import DownloadRequest, DownloadResult


class DownloadService:

    TEMP_ROOT = Path("/tmp/tiktok-downloader")

    def __init__(self):
        self.TEMP_ROOT.mkdir(
            parents=True,
            exist_ok=True
        )

    def download_video(
        self,
        download_request: DownloadRequest
    ) -> DownloadResult:

        temp_folder = (
            self.TEMP_ROOT /
            uuid.uuid4().hex
        )

        temp_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        options = {
            "format": "bestaudio/best",

            "outtmpl": str(
                temp_folder /
                "%(title).80s_%(id)s.%(ext)s"
            ),

            "noplaylist": True,

            "restrictfilenames": True,

            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        with yt_dlp.YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                download_request.url,
                download=True
            )

        files = [
            file
            for file in temp_folder.iterdir()
            if file.is_file()
            and file.suffix.lower() == ".mp3"
        ]

        if not files:
            raise Exception(
                "Não foi possível localizar o áudio."
            )

        audio_file = max(
            files,
            key=lambda file: file.stat().st_mtime
        )

        return DownloadResult(
            title=info.get(
                "title",
                "Sem título"
            ),

            uploader=info.get(
                "uploader",
                "Desconhecido"
            ),

            file_name=audio_file.name,

            file_path=audio_file,

            temp_folder=temp_folder
        )