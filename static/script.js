const form =
    document.getElementById("downloadForm");

const status =
    document.getElementById("status");

const downloadButton =
    document.getElementById("downloadButton");


form.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();


        const url =
            document.getElementById("url").value;


        if (!url) {

            status.textContent =
                "Informe uma URL.";

            return;

        }


        let fileHandle = null;


        if ("showSaveFilePicker" in window) {

            try {

                fileHandle =
                    await window.showSaveFilePicker({

                        suggestedName:
                            "video_tiktok.mp4",

                        startIn:
                            "downloads",

                        types: [
                            {
                                description:
                                    "Vídeo MP4",

                                accept: {
                                    "video/mp4": [
                                        ".mp4"
                                    ]
                                }
                            }
                        ]

                    });

            }
            catch (error) {

                if (error.name === "AbortError") {

                    status.textContent =
                        "Download cancelado.";

                    return;
                }

                console.error(error);

            }

        }


        downloadButton.disabled = true;

        downloadButton.textContent =
            "Baixando...";

        status.textContent =
            "Preparando vídeo...";


        try {

            const response =
                await fetch(
                    "/api/download",
                    {

                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            url: url
                        })

                    }
                );


            if (!response.ok) {

                const data =
                    await response.json();

                throw new Error(
                    data.error ||
                    "Erro ao baixar vídeo."
                );

            }


            const encodedFilename =
                response.headers.get(
                    "X-Filename"
                );


            const filename =
                encodedFilename
                    ? decodeURIComponent(
                        encodedFilename
                    )
                    : "video.mp4";


            const blob =
                await response.blob();


            if (fileHandle) {

                const writable =
                    await fileHandle
                        .createWritable();

                await writable.write(
                    blob
                );

                await writable.close();

                status.textContent =
                    "Vídeo salvo com sucesso!";

            }
            else {

                const downloadUrl =
                    URL.createObjectURL(
                        blob
                    );

                const link =
                    document.createElement(
                        "a"
                    );

                link.href =
                    downloadUrl;

                link.download =
                    filename;

                document.body.appendChild(
                    link
                );

                link.click();

                link.remove();

                URL.revokeObjectURL(
                    downloadUrl
                );

                status.textContent =
                    "Download concluído.";

            }

        }
        catch (error) {

            console.error(error);

            status.textContent =
                error.message;

        }
        finally {

            downloadButton.disabled =
                false;

            downloadButton.textContent =
                "Baixar vídeo";

        }

    }
);