FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && apt-get install -y openssh-client

RUN mkdir -p -m 0700 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts
RUN echo "Host github.com-cosmos\n\tHostname github.com\n\tIdentityFile ~/.ssh/deploy-cosmos\n\tIdentitiesOnly yes" >> ~/.ssh/config
RUN echo "Host github.com-bookt-domain\n\tHostname github.com\n\tIdentityFile ~/.ssh/deploy-domain\n\tIdentitiesOnly yes" >> ~/.ssh/config

WORKDIR /app

COPY ./deploy-cosmos .
RUN cat deploy-cosmos > ~/.ssh/deploy-cosmos && chmod 600 ~/.ssh/deploy-cosmos
COPY ./deploy-domain .
RUN cat deploy-domain > ~/.ssh/deploy-domain && chmod 600 ~/.ssh/deploy-domain
RUN ls -la ~/.ssh

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./api

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
