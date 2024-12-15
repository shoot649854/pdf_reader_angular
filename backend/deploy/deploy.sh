#!/bin/bash

# Exit on any error
set -e

# Get the current working directory
CURRENT_DIR=$(pwd)
PROJECT_ROOT=$(realpath $CURRENT_DIR/..)
NULL="/dev/null"

# Load environment variables from .env file (located in the project root)
if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
  echo "ERROR: .env file not found in the project root."
  exit 1
fi

# Validate if the necessary environment variables are set
export $(grep -v '^#' $PROJECT_ROOT/.env | xargs)
if [[ -z "$PROJECT_ID" || -z "$GCS_BUCKET_NAME" || -z "$GOOGLE_APPLICATION_CREDENTIALS" || -z "$REGION" ]]; then
  echo "ERROR: One or more environment variables are missing from .env file"
  exit 1
fi

# Additional validation for bucket environment variables
export $(grep -v '^#' $PROJECT_ROOT/deploy/.env | xargs)
if [[ -z "$GCS_INPUT_BUCKET" || -z "$GCS_OUTPUT_BUCKET" ]]; then
  echo "ERROR: One or more environment variables (GCS_INPUT_BUCKET, GCS_OUTPUT_BUCKET) are missing."
  exit 1
fi

# Create the service account
IS_SERVICE_ACCOUNT_EXISTS=$(gcloud iam service-accounts list --filter="email:sa-build@${PROJECT_ID}.iam.gserviceaccount.com" --format="value(email)")
if [[ -z "$IS_SERVICE_ACCOUNT_EXISTS" ]]; then
  echo "Creating service account..."
  gcloud beta iam service-accounts create sa-build \
    --display-name="sa-build" \
    --project="${PROJECT_ID}"
else
  echo "Service account 'sa-build' already exists, skipping creation."
fi

# Assign roles to the service account
echo "Assigning roles to the service account..."
gcloud beta projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:sa-build@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin" \
  --condition None > ${NULL} 2>&1

gcloud beta projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:sa-build@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser" \
  --condition None > ${NULL} 2>&1

gcloud beta projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:sa-build@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.admin" \
  --condition None > ${NULL} 2>&1

# Create the service account key for local usage (e.g., for CI/CD)
IS_KEY_EXISTS=$(gcloud iam service-accounts keys list --iam-account "sa-build@${PROJECT_ID}.iam.gserviceaccount.com" --format="value(name)")
if [[ -z "$IS_KEY_EXISTS" ]]; then
  echo "Creating service account key..."
  gcloud iam service-accounts keys create sa-build-key.json \
    --iam-account "sa-build@${PROJECT_ID}.iam.gserviceaccount.com"
else
  echo "Service account key already exists, skipping key creation."
fi

# Enable the necessary APIs (Cloud Functions and others)
echo "Enabling required APIs..."
gcloud services enable cloudfunctions.googleapis.com storage.googleapis.com > ${NULL} 2>&1

# Deploy the Cloud Function
echo "Deploying Cloud Function..."
gcloud functions deploy process_pdf \
    --runtime python310 \
    --gen2 \
    --region=us-central1 \
    --source="$PROJECT_ROOT/deploy" \
    --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
    --trigger-event-filters="bucket=${GCS_INPUT_BUCKET}" \
    --set-env-vars=GCS_INPUT_BUCKET="${GCS_INPUT_BUCKET}",GCS_OUTPUT_BUCKET="${GCS_OUTPUT_BUCKET}" \
    --entry-point=process_pdf \
    --memory=512MB \
    --timeout=120s \
    --service-account="sa-build@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Deployment complete!"
