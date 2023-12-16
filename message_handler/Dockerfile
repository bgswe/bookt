FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && apt-get install -y openssh-client

RUN mkdir -p -m 0700 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts

WORKDIR /app
COPY ./requirements.txt ./
RUN --mount=type=ssh pip install --no-cache-dir -r requirements.txt
COPY . ./message_handler

CMD ["python", "-m", "message_handler.main"]
