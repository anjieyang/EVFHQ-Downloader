FROM python:3.10-alpine

RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev \
    aria2 \
    ffmpeg \
    wget \
    ca-certificates

RUN wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O /usr/local/bin/yt-dlp \
    && chmod a+rx /usr/local/bin/yt-dlp

WORKDIR /data1/EVFHQ/Downloader

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5672

CMD ["python3", "main.py"]
