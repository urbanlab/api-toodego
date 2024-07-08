FROM python:3.11-bookworm


WORKDIR /app

COPY requirements.txt /app
COPY src /app/src

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx poppler-utils \
    && rm -rf /var/lib/apt/lists/*


# Installez les dépendances Python de votre application
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

RUN python3 -m spacy download fr_core_news_md

WORKDIR /app/src

ENV OPENCV_SKIP_GUI_SETUP TRUE
ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--debug"]