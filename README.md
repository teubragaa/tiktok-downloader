# TikTok Downloader

Como utilizo com frequência a opção de baixar vídeos do TikTok, desenvolvi minha própria ferramenta para tornar esse processo mais rápido, 
simples e livre de anúncios encontrados em muitas plataformas online. A aplicação foi desenvolvida em Python e permite o download de vídeos públicos do TikTok por meio de uma interface web simples e prática.

O projeto utiliza Flask no backend, yt-dlp para extração dos vídeos, FFmpeg para processamento de mídia e Docker para criar um ambiente isolado e facilmente reproduzível.

O usuário informa a URL do vídeo pelo navegador e escolhe onde deseja salvar o arquivo através da interface do sistema operacional.

---

## Tecnologias utilizadas

- Python 3.12
- Flask
- yt-dlp
- FFmpeg
- Gunicorn
- HTML
- CSS
- JavaScript
- Docker
- Docker Compose

---

## Funcionalidades

- Download de vídeos públicos do TikTok
- Interface web simples
- Seleção do local onde o arquivo será salvo
- Processamento de vídeo com FFmpeg
- Backend estruturado com Controller, Service e Model
- Execução totalmente através de Docker
- Não necessita instalar Python ou FFmpeg localmente
- Tratamento básico de erros
