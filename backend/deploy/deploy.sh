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

# Load environment variables explicitly
export PROJECT_ID=$(grep ^PROJECT_ID= $PROJECT_ROOT/.env | cut -d '=' -f2- | sed 's/"//g')
export GCS_BUCKET_NAME=$(grep ^GCS_BUCKET_NAME= $PROJECT_ROOT/.env | cut -d '=' -f2- | sed 's/"//g')
export GOOGLE_APPLICATION_CREDENTIALS=$(grep ^GOOGLE_APPLICATION_CREDENTIALS= $PROJECT_ROOT/.env | cut -d '=' -f2- | sed 's/"//g')
export REGION=$(grep ^REGION= $PROJECT_ROOT/.env | cut -d '=' -f2- | sed 's/"//g')

if [[ -z "$PROJECT_ID" || -z "$GCS_BUCKET_NAME" || -z "$GOOGLE_APPLICATION_CREDENTIALS" || -z "$REGION" ]]; then
  echo "ERROR: One or more environment variables are missing from .env file"
  exit 1
fi
echo "[DEBUG] PROJECT_ID: $PROJECT_ID"
echo "[DEBUG] GCS_BUCKET_NAME: $GCS_BUCKET_NAME"
echo "[DEBUG] GOOGLE_APPLICATION_CREDENTIALS: $GOOGLE_APPLICATION_CREDENTIALS"
echo "[DEBUG] REGION: $REGION"

# Load additional environment variables from deploy/.env
if [[ -f "$PROJECT_ROOT/deploy/.env" ]]; then
  export GCS_INPUT_BUCKET=$(grep ^GCS_INPUT_BUCKET= $PROJECT_ROOT/deploy/.env | cut -d '=' -f2- | sed 's/"//g')
  export GCS_OUTPUT_BUCKET=$(grep ^GCS_OUTPUT_BUCKET= $PROJECT_ROOT/deploy/.env | cut -d '=' -f2- | sed 's/"//g')
fi

if [[ -z "$GCS_INPUT_BUCKET" || -z "$GCS_OUTPUT_BUCKET" ]]; then
  echo "ERROR: GCS_INPUT_BUCKET or GCS_OUTPUT_BUCKET is missing from deploy/.env."
  exit 1
fi

echo "[DEBUG] GCS_INPUT_BUCKET: $GCS_INPUT_BUCKET"
echo "[DEBUG] GCS_OUTPUT_BUCKET: $GCS_OUTPUT_BUCKET"

# Create the service account
IS_SERVICE_ACCOUNT_EXISTS=$(gcloud iam service-accounts list --filter="email:sa-build@${PROJECT_ID}.iam.gserviceaccount.com" --format="value(email)")
if [[ -z "$IS_SERVICE_ACCOUNT_EXISTS" ]]; then
  echo "Creating service account..."
  gcloud iam service-accounts create sa-build \
    --display-name="sa-build" \
    --project="${PROJECT_ID}"
else
  echo "Service account 'sa-build' already exists, skipping creation."
fi

# Assign roles to the service account
echo "Assigning roles to the service account..."
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:sa-build@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin" \
  --condition=None > ${NULL} 2>&1

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:sa-build@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser" \
  --condition=None > ${NULL} 2>&1

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:sa-build@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.admin" \
  --condition=None > ${NULL} 2>&1

# Create the service account key for local usage (e.g., for CI/CD)
if [[ ! -f "$PROJECT_ROOT/sa-build-key.json" ]]; then
  echo "Creating service account key..."
  gcloud iam service-accounts keys create "$PROJECT_ROOT/sa-build-key.json" \
    --iam-account "sa-build@${PROJECT_ID}.iam.gserviceaccount.com"
else
  echo "Service account key already exists, skipping key creation."
fi

# Enable the necessary APIs (Cloud Functions and others)
echo "Enabling required APIs..."
gcloud services enable cloudfunctions.googleapis.com storage.googleapis.com logging.googleapis.com > ${NULL} 2>&1

# Deploy the Cloud Function
echo "Deploying Cloud Function..."
gcloud functions deploy process_pdf \
    --runtime python312 \
    --gen2 \
    --region="${REGION}" \
    --source="$PROJECT_ROOT/deploy" \
    --trigger-event-filters='type=google.cloud.storage.object.v1.finalized' \
    --trigger-event-filters="bucket=${GCS_INPUT_BUCKET}" \
    --set-env-vars="GCS_INPUT_BUCKET=${GCS_INPUT_BUCKET},GCS_OUTPUT_BUCKET=${GCS_OUTPUT_BUCKET}" \
    --entry-point=process_pdf \
    --memory=512MB \
    --timeout=120s \
    --service-account="sa-build@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Deployment complete!"

# Verify deployment
echo "Verifying the deployed Cloud Function..."
gcloud functions describe process_pdf --region="${REGION}"

# Optional: Fetch logs after deployment
echo "Fetching logs for the Cloud Function..."
gcloud functions logs read process_pdf --region="${REGION}"
