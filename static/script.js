let selectedDirectory = null;


const form = document.getElementById("downloadForm");

const chooseFolderButton =
    document.getElementById("chooseFolder");

const folderInfo =
    document.getElementById("folderInfo");

const status =
    document.getElementById("status");

const downloadButton =
    document.getElementById("downloadButton");


const supportsDirectoryPicker =
    "showDirectoryPicker" in window;


// Selecionar pasta
chooseFolderButton.addEventListener(
    "click",
    async () => {

        if (!supportsDirectoryPicker) {

            status.textContent =
                "Seu navegador não permite selecionar pastas diretamente. O download convencional será utilizado.";

            return;
        }

        try {

            selectedDirectory =
                await window.showDirectoryPicker({
                    mode: "readwrite",
                    startIn: "downloads"
                });


            folderInfo.textContent =
                `Pasta selecionada: ${selectedDirectory.name}`;

        }
        catch (error) {

            if (error.name !== "AbortError") {

                console.error(error);

                status.textContent =
                    "Não foi possível acessar a pasta.";

            }

        }

    }
);


// Download
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


        downloadButton.disabled = true;

        downloadButton.textContent =
            "Baixando...";

        status.textContent =
            "Preparando vídeo...";


        try {

            const response = await fetch(
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


            /*
             * Se o navegador suporta escolha
             * de diretório e uma pasta foi
             * selecionada.
             */
            if (
                selectedDirectory &&
                supportsDirectoryPicker
            ) {

                const fileHandle =
                    await selectedDirectory
                        .getFileHandle(
                            filename,
                            {
                                create: true
                            }
                        );


                const writable =
                    await fileHandle
                        .createWritable();


                await writable.write(
                    blob
                );


                await writable.close();


                status.textContent =
                    `Vídeo salvo em ${selectedDirectory.name}`;

            }

            else {

                /*
                 * Fallback:
                 *
                 * Chrome antigo,
                 * Firefox,
                 * Safari etc.
                 */

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