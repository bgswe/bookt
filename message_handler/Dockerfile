FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./message_handler

CMD ["python", "-m", "message_handler.main"]
