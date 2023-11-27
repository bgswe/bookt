FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./message_relay
EXPOSE 8200

CMD ["python", "-m", "message_relay.main"]
