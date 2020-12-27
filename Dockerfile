FROM python:3.8 as builder
WORKDIR /usr/src/app
RUN python -m pip install "poetry==1.1.4"
COPY pyproject.toml .
COPY poetry.lock .
RUN poetry export --format requirements.txt --output requirements.txt --without-hashes



FROM gcr.io/google.com/cloudsdktool/cloud-sdk:321.0.0-slim as deployer
WORKDIR /usr/src/app
COPY --from=builder /usr/src/app/requirements.txt .
COPY main.py .
RUN gcloud functions deploy auth0-firebase-token-exchange --project trentiemeciel --source=. --trigger-http --region=europe-west3 --entry-point=from_request --runtime=python38 --memory=128 --allow-unauthenticated

