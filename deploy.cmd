rem poetry export --format requirements.txt --output requirements.txt --without-hashes
gcloud functions deploy create_session --region europe-west3 --entry-point from_request --runtime python38 --memory 128 --trigger-http --allow-unauthenticated

