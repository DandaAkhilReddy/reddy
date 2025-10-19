#!/bin/bash
# ReddyFit Photo Analysis API - Fly.io Deployment Script

set -e  # Exit on error

echo ""
echo "============================================================"
echo "  ReddyFit Photo Analysis API - Fly.io Deployment"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo -e "${YELLOW}[1/6] Installing Fly.io CLI...${NC}"
    curl -L https://fly.io/install.sh | sh
    export PATH="$HOME/.fly/bin:$PATH"
    echo -e "${GREEN}✅ Fly.io CLI installed${NC}"
else
    echo -e "${GREEN}[1/6] Fly.io CLI already installed${NC}"
    flyctl version
fi

echo ""

# Check if logged in
echo -e "${YELLOW}[2/6] Checking Fly.io authentication...${NC}"
if ! flyctl auth whoami &> /dev/null; then
    echo "Please log in to Fly.io:"
    flyctl auth login
fi
echo -e "${GREEN}✅ Authenticated${NC}"

echo ""

# Check if app exists
echo -e "${YELLOW}[3/6] Checking if app exists...${NC}"
if ! flyctl apps list | grep -q "reddyfit-api"; then
    echo "Creating new Fly.io app..."
    flyctl apps create reddyfit-api
    echo -e "${GREEN}✅ App created: reddyfit-api${NC}"
else
    echo -e "${GREEN}✅ App exists: reddyfit-api${NC}"
fi

echo ""

# Set secrets
echo -e "${YELLOW}[4/6] Setting environment secrets...${NC}"
echo ""
echo "Please provide the following secrets:"
echo ""

# Anthropic API Key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -n "ANTHROPIC_API_KEY: "
    read -s ANTHROPIC_API_KEY
    echo ""
fi

# Firebase Project ID
if [ -z "$FIREBASE_PROJECT_ID" ]; then
    echo -n "FIREBASE_PROJECT_ID (default: reddyfit-dev): "
    read FIREBASE_PROJECT_ID
    FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID:-reddyfit-dev}
fi

# Firebase Storage Bucket
if [ -z "$FIREBASE_STORAGE_BUCKET" ]; then
    echo -n "FIREBASE_STORAGE_BUCKET (default: reddyfit-dev.appspot.com): "
    read FIREBASE_STORAGE_BUCKET
    FIREBASE_STORAGE_BUCKET=${FIREBASE_STORAGE_BUCKET:-reddyfit-dev.appspot.com}
fi

# Set secrets
flyctl secrets set \
  ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  FIREBASE_PROJECT_ID="$FIREBASE_PROJECT_ID" \
  FIREBASE_STORAGE_BUCKET="$FIREBASE_STORAGE_BUCKET" \
  FIREBASE_CREDENTIALS_PATH="./firebase-credentials.json"

echo -e "${GREEN}✅ Secrets configured${NC}"

echo ""

# Deploy
echo -e "${YELLOW}[5/6] Deploying to Fly.io...${NC}"
echo ""
echo "This will:"
echo "  - Build Docker image with Python 3.11"
echo "  - Push to Fly.io registry"
echo "  - Deploy to production"
echo ""
echo "This may take 3-5 minutes..."
echo ""

flyctl deploy --ha=false  # Single instance for free tier

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Deployment successful!${NC}"
else
    echo ""
    echo -e "${RED}❌ Deployment failed!${NC}"
    echo "Check logs with: flyctl logs"
    exit 1
fi

echo ""

# Get app URL
APP_URL=$(flyctl info -j | grep -o '"Hostname":"[^"]*"' | cut -d'"' -f4)

echo -e "${YELLOW}[6/6] Testing deployment...${NC}"
sleep 5  # Wait for app to start

# Test health endpoint
if curl -f "https://$APP_URL/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Health check pending... (app may still be starting)${NC}"
fi

echo ""
echo "============================================================"
echo "  🎉 Deployment Complete!"
echo "============================================================"
echo ""
echo "Your API is now live at:"
echo ""
echo -e "${GREEN}  🌐 Base URL:      https://$APP_URL${NC}"
echo -e "${GREEN}  📚 Swagger Docs:  https://$APP_URL/api/docs${NC}"
echo -e "${GREEN}  💚 Health Check:  https://$APP_URL/api/health${NC}"
echo ""
echo "Useful commands:"
echo "  flyctl logs             - View application logs"
echo "  flyctl status           - Check app status"
echo "  flyctl open /api/docs   - Open Swagger UI in browser"
echo "  flyctl ssh console      - SSH into the container"
echo "  flyctl scale count 2    - Scale to 2 instances"
echo ""
echo "To update the app, run this script again or:"
echo "  flyctl deploy"
echo ""
