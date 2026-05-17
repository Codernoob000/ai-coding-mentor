#!/bin/bash

# Hardened Deployment Script for AI Coding Mentor Agent
# Target: Google Cloud Run (Production)

# Exit on any error, undefined variable, or pipe failure
set -euo pipefail

# --- Configuration ---
PROJECT_ID="second-brain-496517"
REGION="us-central1"
SERVICE_NAME="ai-coding-mentor"
AR_REPO="mentor-artifacts"
SERVICE_ACCOUNT="ai-mentor-runner"
SA_EMAIL="${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com"
# Using Artifact Registry (GCR is deprecated)
IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/${SERVICE_NAME}:v1"

echo "--------------------------------------------------------"
echo "HARDENING DEPLOYMENT: $SERVICE_NAME"
echo "--------------------------------------------------------"

# 1. Enable Required Infrastructure APIs
echo "[1/6] Enabling secure GCP APIs..."
gcloud services enable run.googleapis.com \
                       artifactregistry.googleapis.com \
                       secretmanager.googleapis.com \
                       cloudbuild.googleapis.com \
                       --project "$PROJECT_ID"

# 2. Setup Artifact Registry Repository
if ! gcloud artifacts repositories describe "$AR_REPO" --location="$REGION" --project="$PROJECT_ID" &>/dev/null; then
    echo "[2/6] Creating Artifact Registry repository..."
    gcloud artifacts repositories create "$AR_REPO" \
        --repository-format=docker \
        --location="$REGION" \
        --description="Hardened images for AI Mentor" \
        --project "$PROJECT_ID"
else
    echo "[2/6] Artifact Registry exists."
fi

# 3. Build Image securely via Cloud Build
echo "[3/6] Building optimized image..."
gcloud builds submit --tag "$IMAGE_TAG" --project "$PROJECT_ID"

# 4. Create Least-Privilege Service Account
if ! gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
    echo "[4/6] Creating least-privilege service account..."
    gcloud iam service-accounts create "$SERVICE_ACCOUNT" \
        --display-name="AI Mentor Runner (Least Privilege)" \
        --project "$PROJECT_ID"
else
    echo "[4/6] Service account exists."
fi

# 5. Bind Minimal IAM Roles
echo "[5/6] Hardening IAM permissions..."
# Grant access to Secret Manager
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None --quiet

# 6. Deploy Hardened Service to Cloud Run
echo "[6/6] Deploying hardened service..."
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_TAG" \
    --service-account "$SA_EMAIL" \
    --region "$REGION" \
    --project "$PROJECT_ID" \
    --no-allow-unauthenticated \
    --update-secrets="GEMINI_API_KEY=GEMINI_API_KEY:1" \
    --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=INFO" \
    --startup-probe-type=http \
    --startup-probe-path=/api/v1/health \
    --startup-probe-initial-delay-seconds=10 \
    --timeout=300 \
    --min-instances=0 \
    --max-instances=10 \
    --cpu=1 \
    --memory=512Mi

echo "--------------------------------------------------------"
echo "DEPLOYMENT COMPLETE"
echo "Note: Use 'gcloud run services proxy' to test authenticated endpoint."
echo "--------------------------------------------------------"
