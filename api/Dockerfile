FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./api

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
