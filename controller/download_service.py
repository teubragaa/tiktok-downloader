from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    send_file
)

from urllib.parse import quote
import shutil

from models.video import DownloadRequest
from services.download_service import DownloadService


download_controller = Blueprint(
    "download_controller",
    __name__
)


download_service = DownloadService()


@download_controller.route("/")
def home():

    return render_template(
        "index.html"
    )


@download_controller.route(
    "/api/download",
    methods=["POST"]
)
def download():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Requisição inválida."
        }), 400

    url = data.get(
        "url",
        ""
    ).strip()

    if not url:
        return jsonify({
            "error": "Informe a URL do vídeo."
        }), 400

    download_request = DownloadRequest(
        url=url
    )

    try:

        result = download_service.download_video(
            download_request
        )

        response = send_file(
            result.file_path,
            as_attachment=True,
            download_name=result.file_name
        )

        # Nome do arquivo para o JavaScript
        response.headers["X-Filename"] = quote(
            result.file_name
        )

        # Remove arquivos temporários
        # depois que a resposta terminar
        response.call_on_close(
            lambda: shutil.rmtree(
                result.temp_folder,
                ignore_errors=True
            )
        )

        return response

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500