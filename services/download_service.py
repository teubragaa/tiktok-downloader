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

        # Cada download recebe sua própria pasta temporária
        temp_folder = (
            self.TEMP_ROOT /
            uuid.uuid4().hex
        )

        temp_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        options = {

            "format": "bestvideo+bestaudio/best",

            "outtmpl": str(
                temp_folder /
                "%(title).80s_%(id)s.%(ext)s"
            ),

            "noplaylist": True,

            "restrictfilenames": True,

            "merge_output_format": "mp4",
        }

        with yt_dlp.YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                download_request.url,
                download=True
            )

        # Procura o arquivo final gerado
        files = [
            file
            for file in temp_folder.iterdir()
            if file.is_file()
            and file.suffix not in [
                ".part",
                ".ytdl"
            ]
        ]

        if not files:
            raise Exception(
                "Não foi possível localizar o vídeo baixado."
            )

        downloaded_file = max(
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

            file_name=downloaded_file.name,

            file_path=downloaded_file,

            temp_folder=temp_folder
        )