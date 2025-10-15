# Deployment Guide - Content Analysis Platform

Complete guide for deploying the Content Analysis Platform to various environments.

## Table of Contents

- [Overview](#overview)
- [Local Deployment](#local-deployment)
- [Docker Deployment](#docker-deployment)
- [Streamlit Cloud](#streamlit-cloud)
- [AWS Deployment](#aws-deployment)
- [Azure Deployment](#azure-deployment)
- [Google Cloud Deployment](#google-cloud-deployment)
- [Production Best Practices](#production-best-practices)
- [Monitoring & Maintenance](#monitoring--maintenance)

---

## Overview

### Deployment Options

| Option | Best For | Difficulty | Cost |
|--------|----------|------------|------|
| Local | Development, testing | Easy | Free |
| Docker | Consistent environments | Medium | Free |
| Streamlit Cloud | Quick prototypes | Easy | Free tier |
| AWS | Enterprise, scalability | Medium | Pay-as-you-go |
| Azure | Microsoft ecosystem | Medium | Pay-as-you-go |
| GCP | Google ecosystem | Medium | Pay-as-you-go |

### Prerequisites

- Python 3.8+ installed
- Git installed
- API keys for OpenAI or Anthropic
- (Optional) Docker installed
- (Optional) Cloud account (AWS/Azure/GCP)

---

## Local Deployment

### Standard Installation

**1. Clone Repository**

```bash
git clone https://github.com/yourusername/content-analyzer.git
cd content-analyzer
```

**2. Create Virtual Environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**3. Install Dependencies**

```bash
# Core dependencies
pip install -r backend/requirements.txt

# UI dependencies
pip install streamlit plotly

# Optional: PDF support
pip install weasyprint
```

**4. Configure Environment**

Create `.env` file:

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_AI_PROVIDER=openai
DEFAULT_AI_MODEL=gpt-4
```

**5. Run Application**

```bash
# From project root
streamlit run frontend/streamlit_app.py

# Or specify port
streamlit run frontend/streamlit_app.py --server.port 8501
```

**6. Access Application**

Open browser: `http://localhost:8501`

### Production Local Server

For production-like local deployment:

**1. Install Production Server**

```bash
pip install gunicorn uvicorn
```

**2. Run with Gunicorn**

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

**3. Reverse Proxy (Nginx)**

```nginx
# /etc/nginx/sites-available/content-analyzer

server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Docker Deployment

### Dockerfile

Create `Dockerfile` in project root:

```dockerfile
# Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install streamlit plotly weasyprint

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
# docker-compose.yml
version: '3.8'

services:
  content-analyzer:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DEFAULT_AI_PROVIDER=openai
      - DEFAULT_AI_MODEL=gpt-4
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Build and Run

```bash
# Build image
docker build -t content-analyzer:latest .

# Run container
docker run -d \
  -p 8501:8501 \
  -e OPENAI_API_KEY=sk-... \
  --name content-analyzer \
  content-analyzer:latest

# Or use docker-compose
docker-compose up -d

# View logs
docker logs -f content-analyzer

# Stop container
docker stop content-analyzer
```

### Docker Hub Deployment

```bash
# Tag image
docker tag content-analyzer:latest yourusername/content-analyzer:latest

# Push to Docker Hub
docker push yourusername/content-analyzer:latest

# Pull and run on any machine
docker pull yourusername/content-analyzer:latest
docker run -d -p 8501:8501 \
  -e OPENAI_API_KEY=sk-... \
  yourusername/content-analyzer:latest
```

---

## Streamlit Cloud

### Setup

**1. Prepare Repository**

Ensure your repo has:
- `frontend/streamlit_app.py` (main app)
- `requirements.txt` in root or `backend/`
- `.streamlit/config.toml` (optional)

**2. Create Streamlit Config**

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor="#FF6B6B"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#262730"
font="sans serif"

[server]
maxUploadSize=200
enableXsrfProtection=true
enableCORS=false
```

**3. Create secrets.toml Template**

Create `.streamlit/secrets.toml.example`:

```toml
# DO NOT commit this file with real values
# Copy to secrets.toml and add real keys

OPENAI_API_KEY = "sk-..."
ANTHROPIC_API_KEY = "sk-ant-..."
DEFAULT_AI_PROVIDER = "openai"
DEFAULT_AI_MODEL = "gpt-4"
```

**4. Deploy to Streamlit Cloud**

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select repository and branch
5. Set main file path: `frontend/streamlit_app.py`
6. Add secrets in dashboard (Settings → Secrets)
7. Click "Deploy"

**5. Access Your App**

URL: `https://yourusername-content-analyzer-app-hash.streamlit.app`

### Secrets Configuration

In Streamlit Cloud dashboard, add secrets:

```toml
OPENAI_API_KEY = "sk-..."
ANTHROPIC_API_KEY = "sk-ant-..."
DEFAULT_AI_PROVIDER = "openai"
DEFAULT_AI_MODEL = "gpt-4"
```

Access in code:

```python
import streamlit as st

api_key = st.secrets["OPENAI_API_KEY"]
```

---

## AWS Deployment

### Option 1: AWS Elastic Beanstalk

**1. Install EB CLI**

```bash
pip install awsebcli
```

**2. Initialize EB**

```bash
eb init -p python-3.10 content-analyzer --region us-east-1
```

**3. Create Environment**

```bash
eb create content-analyzer-env
```

**4. Configure Environment Variables**

```bash
eb setenv OPENAI_API_KEY=sk-... ANTHROPIC_API_KEY=sk-ant-...
```

**5. Deploy**

```bash
eb deploy
```

**6. Open Application**

```bash
eb open
```

### Option 2: AWS ECS (Docker)

**1. Create ECR Repository**

```bash
aws ecr create-repository --repository-name content-analyzer
```

**2. Build and Push Image**

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t content-analyzer .
docker tag content-analyzer:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/content-analyzer:latest

# Push
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/content-analyzer:latest
```

**3. Create Task Definition**

`task-definition.json`:

```json
{
  "family": "content-analyzer",
  "networkMode": "awsvpc",
  "containerDefinitions": [
    {
      "name": "content-analyzer",
      "image": "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/content-analyzer:latest",
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "DEFAULT_AI_PROVIDER", "value": "openai"},
        {"name": "DEFAULT_AI_MODEL", "value": "gpt-4"}
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:openai-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/content-analyzer",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048"
}
```

**4. Create ECS Service**

```bash
aws ecs create-service \
  --cluster content-analyzer-cluster \
  --service-name content-analyzer-service \
  --task-definition content-analyzer \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Option 3: AWS Lambda + API Gateway

For serverless deployment (API mode only):

**1. Create Lambda Function**

```python
# lambda_function.py
import json
from src.ai import create_ai_analysis_service

async def lambda_handler(event, context):
    body = json.loads(event['body'])
    
    service = await create_ai_analysis_service()
    result = await service.analyze(
        content=body['content'],
        title=body['title']
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'quality_score': result.overall_quality_score,
            'summary': result.content_summary.short_summary
        })
    }
```

**2. Package and Deploy**

```bash
# Create deployment package
pip install -r requirements.txt -t package/
cd package && zip -r ../deployment.zip . && cd ..
zip -g deployment.zip lambda_function.py

# Upload to Lambda
aws lambda create-function \
  --function-name content-analyzer \
  --runtime python3.10 \
  --role arn:aws:iam::ACCOUNT:role/lambda-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://deployment.zip \
  --timeout 300 \
  --memory-size 1024
```

---

## Azure Deployment

### Azure App Service

**1. Install Azure CLI**

```bash
# Windows
winget install Microsoft.AzureCLI

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

**2. Login**

```bash
az login
```

**3. Create Resource Group**

```bash
az group create --name content-analyzer-rg --location eastus
```

**4. Create App Service Plan**

```bash
az appservice plan create \
  --name content-analyzer-plan \
  --resource-group content-analyzer-rg \
  --sku B1 \
  --is-linux
```

**5. Create Web App**

```bash
az webapp create \
  --resource-group content-analyzer-rg \
  --plan content-analyzer-plan \
  --name content-analyzer-app \
  --runtime "PYTHON|3.10"
```

**6. Configure Environment**

```bash
az webapp config appsettings set \
  --resource-group content-analyzer-rg \
  --name content-analyzer-app \
  --settings OPENAI_API_KEY=sk-... ANTHROPIC_API_KEY=sk-ant-...
```

**7. Deploy Code**

```bash
# Configure deployment
az webapp deployment source config-local-git \
  --name content-analyzer-app \
  --resource-group content-analyzer-rg

# Add Azure remote
git remote add azure <deployment-url>

# Deploy
git push azure main
```

### Azure Container Instances

**1. Create Container Registry**

```bash
az acr create \
  --resource-group content-analyzer-rg \
  --name contentanalyzeracr \
  --sku Basic
```

**2. Build and Push Image**

```bash
# Login to ACR
az acr login --name contentanalyzeracr

# Build and push
az acr build --registry contentanalyzeracr --image content-analyzer:latest .
```

**3. Deploy Container**

```bash
az container create \
  --resource-group content-analyzer-rg \
  --name content-analyzer-container \
  --image contentanalyzeracr.azurecr.io/content-analyzer:latest \
  --cpu 2 \
  --memory 4 \
  --registry-login-server contentanalyzeracr.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --ip-address Public \
  --ports 8501 \
  --environment-variables OPENAI_API_KEY=sk-...
```

---

## Google Cloud Deployment

### Cloud Run

**1. Install gcloud CLI**

```bash
# Follow: https://cloud.google.com/sdk/docs/install
```

**2. Configure Project**

```bash
gcloud init
gcloud config set project YOUR_PROJECT_ID
```

**3. Build Container**

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/content-analyzer
```

**4. Deploy to Cloud Run**

```bash
gcloud run deploy content-analyzer \
  --image gcr.io/YOUR_PROJECT_ID/content-analyzer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=sk-...,ANTHROPIC_API_KEY=sk-ant-...
```

**5. Access Application**

Service URL will be provided in output.

### App Engine

**1. Create `app.yaml`**

```yaml
runtime: python310

env_variables:
  OPENAI_API_KEY: "sk-..."
  ANTHROPIC_API_KEY: "sk-ant-..."

automatic_scaling:
  min_instances: 1
  max_instances: 10

resources:
  cpu: 2
  memory_gb: 4
  disk_size_gb: 10
```

**2. Deploy**

```bash
gcloud app deploy
```

---

## Production Best Practices

### Security

**1. Environment Variables**

```python
# Never commit API keys
# Use environment variables
import os

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not set")
```

**2. Secrets Management**

- AWS: AWS Secrets Manager
- Azure: Azure Key Vault
- GCP: Secret Manager
- Docker: Docker Secrets

**3. HTTPS/SSL**

Always use HTTPS in production:

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8501;
    }
}
```

### Performance

**1. Caching**

```python
import functools
from cachetools import TTLCache

cache = TTLCache(maxsize=100, ttl=3600)

@functools.lru_cache(maxsize=128)
def get_analysis(url: str):
    # Analysis logic
    pass
```

**2. Rate Limiting**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
async def analyze_endpoint():
    pass
```

**3. Connection Pooling**

```python
import aiohttp

async with aiohttp.ClientSession() as session:
    # Reuse session for multiple requests
    pass
```

### Monitoring

**1. Logging**

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Analysis started")
```

**2. Health Checks**

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
```

**3. Metrics**

```python
from prometheus_client import Counter, Histogram

analysis_counter = Counter('analyses_total', 'Total analyses')
analysis_duration = Histogram('analysis_duration_seconds', 'Analysis duration')

@analysis_duration.time()
async def analyze():
    analysis_counter.inc()
    # Analysis logic
```

---

## Monitoring & Maintenance

### Application Monitoring

**CloudWatch (AWS)**:

```bash
# View logs
aws logs tail /aws/elasticbeanstalk/content-analyzer-env/var/log/web.stdout.log

# Create alarm
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --threshold 80
```

**Azure Monitor**:

```bash
# Enable diagnostics
az monitor diagnostic-settings create \
  --resource content-analyzer-app \
  --name diagnostics \
  --logs '[{"category": "AppServiceConsoleLogs", "enabled": true}]'
```

**Google Cloud Logging**:

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision"
```

### Backup Strategy

**1. Database Backups** (if using):

```bash
# Automated daily backups
0 2 * * * /usr/bin/pg_dump mydb > /backups/db_$(date +\%Y\%m\%d).sql
```

**2. Configuration Backups**:

```bash
# Version control all configs
git add .env.example docker-compose.yml
git commit -m "Update configuration"
```

### Update Procedures

**1. Zero-Downtime Updates**:

```bash
# Blue-green deployment
docker-compose -f docker-compose.blue.yml up -d
# Test blue environment
docker-compose -f docker-compose.green.yml down
```

**2. Rolling Updates**:

```bash
# Kubernetes rolling update
kubectl set image deployment/content-analyzer content-analyzer=image:v2
```

---

## Troubleshooting

### Common Issues

**Port already in use**:

```bash
# Find process
lsof -i :8501

# Kill process
kill -9 <PID>
```

**Module not found**:

```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**API key errors**:

```bash
# Verify environment variable
echo $OPENAI_API_KEY

# Check .env file
cat .env
```

---

## Summary

### Deployment Checklist

- [ ] Choose deployment platform
- [ ] Set up environment
- [ ] Configure API keys (secrets)
- [ ] Install dependencies
- [ ] Test locally first
- [ ] Deploy to staging
- [ ] Run tests on staging
- [ ] Deploy to production
- [ ] Configure monitoring
- [ ] Set up backups
- [ ] Document deployment process
- [ ] Create runbook for incidents

### Quick Commands

```bash
# Local
streamlit run frontend/streamlit_app.py

# Docker
docker-compose up -d

# AWS EB
eb deploy

# Azure
git push azure main

# GCP
gcloud run deploy
```

---

**For more help**, see:
- Main README.md
- TROUBLESHOOTING.md
- Platform-specific documentation

**Happy deploying!** 🚀
