# 🚀 Deployment Guide - GenAI Email Processing System

## 📋 Overview

This guide provides step-by-step instructions for deploying the GenAI Email Processing System in various environments, from local development to production cloud deployment.

## 🎯 Deployment Options

### 1. 📓 Jupyter Notebook (Interactive/Analysis)
**Best for:** Research, analysis, one-time processing, demonstrations

### 2. 🚀 FastAPI Production Service
**Best for:** Production deployments, real-time processing, integration with other systems

### 3. ☁️ Cloud Deployment
**Best for:** Scalable production environments, high availability

## 📓 Jupyter Notebook Deployment

### Google Colab (Recommended for Notebooks)

1. **Upload Notebook**
   ```
   1. Go to colab.research.google.com
   2. Upload fashion_store_email_processor.ipynb
   3. Open the notebook
   ```

2. **Configure API Key**
   ```
   1. Click the key icon (🔑) in left sidebar
   2. Add secret: Name = OPENAI_API_KEY, Value = your_api_key
   3. Ensure the secret is accessible to the notebook
   ```

3. **Run the Notebook**
   ```
   1. Runtime → Run all
   2. Monitor progress in each cell
   3. Download results when complete
   ```

### Local Jupyter Deployment

1. **Install Dependencies**
   ```bash
   pip install jupyter pandas numpy openai langchain chromadb
   pip install gspread oauth2client openpyxl xlsxwriter
   ```

2. **Configure Environment**
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```

3. **Launch Jupyter**
   ```bash
   jupyter notebook fashion_store_email_processor.ipynb
   ```

## 🚀 FastAPI Production Deployment

### Local Development

1. **Setup Environment**
   ```bash
   # Clone repository
   git clone <repository_url>
   cd crossover_genai_assessment
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   ```bash
   # Copy template
   cp .env.template .env
   
   # Edit .env file with your settings
   nano .env
   ```

3. **Start the Server**
   ```bash
   python -m src.main
   ```

4. **Verify Deployment**
   ```bash
   # Health check
   curl http://localhost:8000/api/v1/health
   
   # API documentation
   open http://localhost:8000/docs
   ```

### Docker Deployment

1. **Build Docker Image**
   ```bash
   docker build -t genai-email-processor .
   ```

2. **Run Container**
   ```bash
   docker run -d \
     --name email-processor \
     -p 8000:8000 \
     -e OPENAI_API_KEY=your_api_key \
     genai-email-processor
   ```

3. **Using Docker Compose**
   ```bash
   # Start services
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   
   # Stop services
   docker-compose down
   ```

## ☁️ Cloud Deployment

### AWS Deployment

#### EC2 Deployment

1. **Launch EC2 Instance**
   ```bash
   # Choose Ubuntu 22.04 LTS
   # Instance type: t3.medium or larger
   # Security group: Allow HTTP (80), HTTPS (443), SSH (22)
   ```

2. **Setup Application**
   ```bash
   # SSH into instance
   ssh -i your_key.pem ubuntu@your_instance_ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and dependencies
   sudo apt install python3-pip python3-venv nginx -y
   
   # Clone and setup application
   git clone <repository_url>
   cd crossover_genai_assessment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Nginx**
   ```nginx
   # /etc/nginx/sites-available/email-processor
   server {
       listen 80;
       server_name your_domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Setup Systemd Service**
   ```ini
   # /etc/systemd/system/email-processor.service
   [Unit]
   Description=GenAI Email Processor
   After=network.target
   
   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/crossover_genai_assessment
   Environment=PATH=/home/ubuntu/crossover_genai_assessment/venv/bin
   EnvironmentFile=/home/ubuntu/crossover_genai_assessment/.env
   ExecStart=/home/ubuntu/crossover_genai_assessment/venv/bin/python -m src.main
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

5. **Start Services**
   ```bash
   sudo systemctl enable email-processor
   sudo systemctl start email-processor
   sudo systemctl enable nginx
   sudo systemctl start nginx
   ```

#### AWS Lambda Deployment

1. **Prepare Lambda Package**
   ```bash
   # Create deployment package
   pip install -r requirements.txt -t lambda_package/
   cp -r src/ lambda_package/
   cd lambda_package && zip -r ../lambda_deployment.zip .
   ```

2. **Deploy with AWS CLI**
   ```bash
   aws lambda create-function \
     --function-name genai-email-processor \
     --runtime python3.9 \
     --role arn:aws:iam::your_account:role/lambda-execution-role \
     --handler src.lambda_handler.handler \
     --zip-file fileb://lambda_deployment.zip \
     --environment Variables='{OPENAI_API_KEY=your_key}'
   ```

### Google Cloud Platform

#### Cloud Run Deployment

1. **Prepare for Cloud Run**
   ```bash
   # Build container
   gcloud builds submit --tag gcr.io/your_project/email-processor
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy email-processor \
     --image gcr.io/your_project/email-processor \
     --platform managed \
     --region us-central1 \
     --set-env-vars OPENAI_API_KEY=your_key \
     --allow-unauthenticated
   ```

#### App Engine Deployment

1. **Configure app.yaml**
   ```yaml
   runtime: python39
   
   env_variables:
     OPENAI_API_KEY: your_api_key
   
   automatic_scaling:
     min_instances: 1
     max_instances: 10
   ```

2. **Deploy**
   ```bash
   gcloud app deploy
   ```

### Microsoft Azure

#### Container Instances

1. **Create Resource Group**
   ```bash
   az group create --name email-processor-rg --location eastus
   ```

2. **Deploy Container**
   ```bash
   az container create \
     --resource-group email-processor-rg \
     --name email-processor \
     --image your_registry/email-processor:latest \
     --environment-variables OPENAI_API_KEY=your_key \
     --dns-name-label email-processor-unique \
     --ports 8000
   ```

## 🔧 Configuration Management

### Environment Variables

**Required:**
```bash
OPENAI_API_KEY=your_openai_api_key
```

**Optional:**
```bash
# Server configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Database
DATABASE_URL=sqlite:///./emails.db

# Logging
LOG_LEVEL=INFO
```

### Configuration Files

1. **Copy Template**
   ```bash
   cp .env.template .env
   ```

2. **Customize Settings**
   ```bash
   # Edit configuration
   nano .env
   
   # Validate configuration
   python -c "from src.config.settings import settings; print('Config OK')"
   ```

## 🔍 Monitoring & Maintenance

### Health Checks

```bash
# Basic health check
curl http://your_domain/api/v1/health

# Detailed status
curl http://your_domain/api/v1/status
```

### Logging

```bash
# View application logs
tail -f logs/email_processor.log

# View error logs
tail -f logs/errors.log

# System logs (systemd)
sudo journalctl -u email-processor -f
```

### Performance Monitoring

```bash
# Check resource usage
htop

# Monitor API performance
curl -w "@curl-format.txt" http://your_domain/api/v1/health

# View metrics (if enabled)
curl http://your_domain/metrics
```

## 🔒 Security Configuration

### API Authentication

1. **Enable Authentication**
   ```bash
   # In .env file
   ENABLE_API_AUTHENTICATION=true
   API_KEY_HEADER=X-API-Key
   SECRET_KEY=your_secret_key
   ```

2. **Create API Keys**
   ```bash
   python scripts/create_api_key.py
   ```

### SSL/TLS Configuration

1. **Obtain SSL Certificate**
   ```bash
   # Using Let's Encrypt
   sudo certbot --nginx -d your_domain.com
   ```

2. **Configure HTTPS Redirect**
   ```nginx
   # Update nginx configuration
   server {
       listen 80;
       server_name your_domain.com;
       return 301 https://$server_name$request_uri;
   }
   ```

## 📊 Scaling Considerations

### Horizontal Scaling

1. **Load Balancer Configuration**
   ```nginx
   upstream email_processors {
       server 127.0.0.1:8000;
       server 127.0.0.1:8001;
       server 127.0.0.1:8002;
   }
   
   server {
       location / {
           proxy_pass http://email_processors;
       }
   }
   ```

2. **Multiple Instances**
   ```bash
   # Start multiple instances
   python -m src.main --port 8000 &
   python -m src.main --port 8001 &
   python -m src.main --port 8002 &
   ```

### Vertical Scaling

1. **Resource Requirements**
   ```
   Minimum: 2 CPU cores, 4GB RAM
   Recommended: 4 CPU cores, 8GB RAM
   High Load: 8+ CPU cores, 16GB+ RAM
   ```

2. **Database Scaling**
   ```bash
   # PostgreSQL for production
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   
   # Redis for caching
   REDIS_URL=redis://host:6379/0
   ```

## 🚨 Troubleshooting

### Common Issues

1. **API Key Issues**
   ```bash
   # Test API key
   python test_openai_key.py
   
   # Validate environment
   python pre_assessment_check.py
   ```

2. **Port Conflicts**
   ```bash
   # Check port usage
   sudo netstat -tulpn | grep :8000
   
   # Use different port
   python -m src.main --port 8001
   ```

3. **Memory Issues**
   ```bash
   # Monitor memory usage
   free -h
   
   # Increase swap if needed
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### Performance Issues

1. **Slow Response Times**
   ```bash
   # Enable caching
   ENABLE_RESPONSE_CACHE=true
   
   # Increase worker processes
   uvicorn src.main:app --workers 4
   ```

2. **High Memory Usage**
   ```bash
   # Reduce model size or use quantized models
   # Implement request queuing
   # Monitor ChromaDB memory usage
   ```

## 📋 Deployment Checklist

### Pre-deployment

- [ ] API keys configured
- [ ] Environment variables set
- [ ] Dependencies installed
- [ ] Configuration validated
- [ ] Tests passing
- [ ] Security settings reviewed

### Post-deployment

- [ ] Health checks passing
- [ ] API endpoints responding
- [ ] Logging working
- [ ] Monitoring configured
- [ ] SSL certificate installed
- [ ] Backup strategy implemented

### Production Readiness

- [ ] Load testing completed
- [ ] Error handling verified
- [ ] Fallback mechanisms tested
- [ ] Monitoring alerts configured
- [ ] Documentation updated
- [ ] Team training completed

---

**🎉 Deployment Complete! Your GenAI Email Processing System is now ready for production use.**
