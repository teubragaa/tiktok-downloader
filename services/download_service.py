from pathlib import Path
import uuid
import re
import asyncio
import subprocess

import yt_dlp
import requests
import edge_tts

from faster_whisper import WhisperModel

from models.video import (
    DownloadRequest,
    DownloadResult
)


class DownloadService:

    TEMP_ROOT = Path("/tmp/tiktok-downloader")

    OLLAMA_URL = (
        "http://host.docker.internal:11434/api/generate"
    )

    OLLAMA_MODEL = "qwen3:30b"

    VOICE = "pt-BR-AntonioNeural"

    def __init__(self):

        self.TEMP_ROOT.mkdir(
            parents=True,
            exist_ok=True
        )

        print("Carregando Whisper large-v3...")

        self.whisper = WhisperModel(
            "large-v3",
            device="cpu",
            compute_type="float32"
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

        video_file, info = self._download(
            download_request.url,
            temp_folder
        )

        audio_file = self._extract_audio(
            video_file,
            temp_folder
        )

        text = self._transcribe(
            audio_file
        )

        rewritten_text = self._rewrite(
            text
        )

        final_audio = (
            temp_folder /
            "novo_audio.mp3"
        )

        asyncio.run(
            self._generate_audio(
                rewritten_text,
                final_audio
            )
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

            file_name="novo_audio.mp3",

            file_path=final_audio,

            temp_folder=temp_folder
        )


    def _download(
        self,
        url,
        temp_folder
    ):

        options = {

            "format":
                "bestvideo+bestaudio/best",

            "outtmpl": str(
                temp_folder /
                "%(title).80s_%(id)s.%(ext)s"
            ),

            "noplaylist": True,

            "restrictfilenames": True,

            "merge_output_format": "mp4",
        }

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

        files = [
            file
            for file in temp_folder.iterdir()
            if file.is_file()
            and file.suffix.lower()
            in [
                ".mp4",
                ".webm",
                ".mkv",
                ".mov"
            ]
        ]

        if not files:

            raise Exception(
                "Não foi possível localizar "
                "o vídeo baixado."
            )

        video_file = max(
            files,
            key=lambda file:
                file.stat().st_mtime
        )

        return video_file, info


    def _extract_audio(
        self,
        video_file,
        temp_folder
    ):

        print("Extraindo áudio...")

        audio_file = (
            temp_folder /
            "audio_original.wav"
        )

        subprocess.run(
            [
                "ffmpeg",
                "-y",

                "-i",
                str(video_file),

                "-vn",

                "-ac",
                "1",

                "-ar",
                "16000",

                "-c:a",
                "pcm_s16le",

                str(audio_file)
            ],
            check=True
        )

        return audio_file


    def _transcribe(
        self,
        audio_file
    ):

        print("Transcrevendo...")

        segments, info = (
            self.whisper.transcribe(
                str(audio_file),

                language="pt",

                beam_size=10,

                vad_filter=True
            )
        )

        text = " ".join(

            segment.text.strip()

            for segment in segments
        )

        if not text:

            raise Exception(
                "Não foi possível "
                "transcrever o áudio."
            )

        print(
            "\nTRANSCRIÇÃO:\n",
            text
        )

        return text


    def _rewrite(
        self,
        text
    ):

        print(
            "Reescrevendo com Ollama..."
        )

        word_count = len(
            text.split()
        )

        prompt = f"""
Crie um NOVO roteiro curto
para TikTok usando apenas
a ideia central do texto abaixo.

Regras:

- escreva completamente do zero;
- não copie frases;
- não faça apenas troca de sinônimos;
- mantenha aproximadamente
  {word_count} palavras;
- preserve a ideia principal;
- mantenha o mesmo tipo de assunto;
- comece com um gancho forte;
- use português brasileiro natural;
- escreva pensando em narração;
- não coloque título;
- não explique sua resposta;
- devolva somente o novo roteiro.

Texto de referência:

{text}
"""

        response = requests.post(
            self.OLLAMA_URL,

            json={
                "model":
                    self.OLLAMA_MODEL,

                "prompt":
                    prompt,

                "stream":
                    False,

                "options": {

                    "temperature":
                        0.8,

                    "top_p":
                        0.9
                }
            },

            timeout=1800
        )

        response.raise_for_status()

        rewritten = (
            response
            .json()
            ["response"]
        )

        rewritten = re.sub(
            r"<think>.*?</think>",
            "",
            rewritten,
            flags=re.DOTALL
        )

        rewritten = (
            rewritten.strip()
        )

        print(
            "\nNOVO TEXTO:\n",
            rewritten
        )

        return rewritten


    async def _generate_audio(
        self,
        text,
        output_file
    ):

        print(
            "Gerando novo áudio..."
        )

        communicate = (
            edge_tts.Communicate(
                text,
                self.VOICE
            )
        )

        await communicate.save(
            str(output_file)
        )