# Chargebee Risk Assessment Tool (RiskBee KYB)

A comprehensive Know Your Business (KYB) risk assessment platform built with FastAPI, React, and Supabase. This tool provides automated risk analysis for businesses using AI-powered assessment and real-time data scraping.

## 🚀 Features

### Core Functionality
- **AI-Powered Risk Assessment**: Advanced risk analysis using Google Gemini AI
- **Real-time Data Scraping**: 10+ scrapers for comprehensive business intelligence
- **User Authentication**: Secure login/signup with @chargebee.com domain restriction
- **Email Verification**: Complete email verification workflow
- **Background Processing**: Non-blocking assessment execution
- **Progress Tracking**: Real-time assessment progress monitoring
- **Risk Analytics**: Comprehensive risk distribution and statistics
- **Export Capabilities**: CSV and PDF report generation

### Technical Features
- **Modern Stack**: FastAPI + React + Supabase
- **Responsive UI**: Beautiful, modern interface with Tailwind CSS
- **Real-time Updates**: WebSocket-like polling for live progress
- **Database Integration**: Supabase for data persistence
- **API Documentation**: Auto-generated Swagger/OpenAPI docs
- **Error Handling**: Comprehensive error management and logging

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Supabase)    │
│   Port: 3000    │    │   Port: 8001    │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   AI Services   │
                       │   (Gemini API)  │
                       └─────────────────┘
```

## 🛠️ Prerequisites

- **Python 3.9+**
- **Node.js 16+**
- **npm or yarn**
- **Git**

## 📋 Environment Variables

### Backend (.env)
```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Google AI Configuration
GOOGLE_API_KEY=your_gemini_api_key

# Application Settings
ENVIRONMENT=development
DEBUG=True
JWT_SECRET=your_jwt_secret
```

### Frontend Configuration
The frontend automatically detects the environment and configures the API endpoints.

## 🚀 Local Development Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd ChargebeeRiskTool
```

### 2. Backend Setup
```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your actual values

# Start the backend server
python3 -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Start the development server
npm start
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## 🌐 Hosting Options

### Option 1: Free Hosting (Recommended for Testing)

#### Backend: Render (Free Tier)
1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Deploy Backend**
   ```bash
   # Connect your GitHub repository
   # Create new Web Service
   # Select your repository
   # Configure:
   - Name: chargebee-kyb-backend
   - Environment: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   - Plan: Free
   ```

3. **Environment Variables on Render**
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_supabase_service_key
   GOOGLE_API_KEY=your_gemini_api_key
   ENVIRONMENT=production
   DEBUG=False
   JWT_SECRET=your_jwt_secret
   ```

#### Frontend: Render (Free Tier)
1. **Deploy Frontend**
   ```bash
   # Create new Static Site
   # Configure:
   - Name: chargebee-kyb-frontend
   - Build Command: npm install && npm run build
   - Publish Directory: build
   - Plan: Free
   ```

2. **Update API Configuration**
   - The frontend automatically detects Render hosting
   - Update `frontend/src/services/api.js` if needed

#### Database: Supabase (Free Tier)
1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Note down URL and API keys

2. **Database Schema**
   ```sql
   -- Create risk_assessments table
   CREATE TABLE risk_assessments (
     id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
     domain VARCHAR(255) NOT NULL,
     company_name VARCHAR(255),
     assessment_type VARCHAR(50) DEFAULT 'standard',
     status VARCHAR(50) DEFAULT 'processing',
     risk_assessment_data JSONB,
     scraped_data JSONB,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Create profiles table for user management
   CREATE TABLE profiles (
     id UUID REFERENCES auth.users(id) PRIMARY KEY,
     email VARCHAR(255) UNIQUE NOT NULL,
     full_name VARCHAR(255),
     company_name VARCHAR(255),
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   ```

### Option 2: AWS Complete Infrastructure (Production)

#### 🏗️ AWS Architecture Overview
```
Internet → ALB → EC2 (Frontend + Backend) → RDS PostgreSQL
                    ↓
                S3 Data Lake
```

#### 🗄️ Database Setup (RDS PostgreSQL)
```bash
# Create RDS instance
aws rds create-db-instance \
    --db-instance-identifier riskbee-postgres \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 14.7 \
    --master-username riskbee_admin \
    --master-user-password "YourSecurePassword123!" \
    --allocated-storage 20 \
    --storage-type gp2 \
    --backup-retention-period 7 \
    --multi-az \
    --storage-encrypted

# Database Schema
CREATE DATABASE riskbee_db;
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email_verified BOOLEAN DEFAULT FALSE
);
CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    risk_score DECIMAL(5,4),
    risk_level VARCHAR(50),
    assessment_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 📦 S3 Data Lake Setup
```bash
# Create S3 buckets
aws s3 mb s3://riskbee-datalake-$(date +%Y%m%d)
aws s3 mb s3://riskbee-backups-$(date +%Y%m%d)
aws s3 mb s3://riskbee-static-assets-$(date +%Y%m%d)

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket riskbee-datalake-$(date +%Y%m%d) \
    --versioning-configuration Status=Enabled

# Create folder structure
aws s3api put-object --bucket riskbee-datalake-$(date +%Y%m%d) --key raw-data/
aws s3api put-object --bucket riskbee-datalake-$(date +%Y%m%d) --key processed-data/
aws s3api put-object --bucket riskbee-datalake-$(date +%Y%m%d) --key scraped-data/
```

#### 🖥️ EC2 Instance Setup
```bash
# Create key pair
aws ec2 create-key-pair \
    --key-name riskbee-key-pair \
    --query 'KeyMaterial' \
    --output text > riskbee-key-pair.pem

# Launch EC2 instance
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --count 1 \
    --instance-type t3.medium \
    --key-name riskbee-key-pair \
    --security-group-ids sg-12345678 \
    --subnet-id subnet-12345678 \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=RiskBee-Server}]'
```

#### 🔐 Security Groups
```bash
# EC2 Security Group
aws ec2 create-security-group \
    --group-name riskbee-ec2-sg \
    --description "Security group for RiskBee EC2 instance"

# Allow HTTP/HTTPS/SSH
aws ec2 authorize-security-group-ingress \
    --group-name riskbee-ec2-sg \
    --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress \
    --group-name riskbee-ec2-sg \
    --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress \
    --group-name riskbee-ec2-sg \
    --protocol tcp --port 443 --cidr 0.0.0.0/0

# RDS Security Group
aws ec2 create-security-group \
    --group-name riskbee-rds-sg \
    --description "Security group for RiskBee RDS instance"
aws ec2 authorize-security-group-ingress \
    --group-name riskbee-rds-sg \
    --protocol tcp --port 5432 --source-group riskbee-ec2-sg
```

#### 🐳 Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://riskbee_admin:password@rds-endpoint:5432/riskbee_db
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - S3_BUCKET=${S3_BUCKET}
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    restart: unless-stopped
    depends_on: [backend]

  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    restart: unless-stopped
    depends_on: [frontend, backend]
```

#### 📊 Monitoring & Logging
```bash
# CloudWatch Log Group
aws logs create-log-group --log-group-name /aws/ec2/riskbee

# CloudWatch Dashboard
aws cloudwatch put-dashboard \
    --dashboard-name RiskBee-Dashboard \
    --dashboard-body file://dashboard.json
```

#### 💰 Cost Estimation (Monthly)
- **EC2 t3.medium**: ~$30/month
- **RDS PostgreSQL db.t3.micro**: ~$15/month
- **S3 Storage (100GB)**: ~$2.50/month
- **Data Transfer**: ~$5/month
- **CloudWatch**: ~$5/month
- **Total**: ~$57.50/month

#### 🔄 Scaling Considerations
- **Horizontal**: Use Application Load Balancer (ALB) for multiple EC2 instances
- **Vertical**: Upgrade instance types as needed
- **Database**: Use RDS read replicas for read-heavy workloads
- **Storage**: S3 automatically scales with usage

#### 🚀 Deployment Script
```bash
#!/bin/bash
# deploy.sh
set -e
echo "🚀 Starting RiskBee AWS deployment..."

# Update system
sudo yum update -y
sudo yum install -y docker git python3 python3-pip nginx

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Deploy containers
cd /opt/riskbee
sudo docker-compose down
sudo docker-compose up -d --build

echo "✅ Deployment completed successfully!"
```

#### 📋 AWS Deployment Checklist
- [ ] AWS account with appropriate permissions
- [ ] Domain name registered and DNS configured
- [ ] SSL certificate (AWS Certificate Manager)
- [ ] Environment variables prepared
- [ ] Database schema ready
- [ ] S3 buckets created with proper permissions
- [ ] EC2 instance launched with user data script
- [ ] RDS PostgreSQL instance configured
- [ ] Security groups configured
- [ ] IAM roles and policies set up
- [ ] Application containers deployed
- [ ] Nginx reverse proxy configured
- [ ] Monitoring and logging configured
- [ ] All endpoints tested and functional

#### Frontend: Vercel/Netlify
1. **Vercel Deployment**
   ```bash
   # Install Vercel CLI
   npm i -g vercel

   # Deploy
   cd frontend
   vercel --prod
   ```

2. **Netlify Deployment**
   ```bash
   # Build locally
   npm run build

   # Deploy to Netlify
   # Drag and drop build folder to Netlify
   ```

#### Database: Supabase Pro
1. **Upgrade to Pro Plan**
   - Better performance
   - More storage
   - Advanced features
   - Priority support

2. **Production Configuration**
   ```bash
   # Enable Row Level Security (RLS)
   ALTER TABLE risk_assessments ENABLE ROW LEVEL SECURITY;
   ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

   # Create policies
   CREATE POLICY "Users can view their own assessments" ON risk_assessments
   FOR SELECT USING (auth.uid() = user_id);
   ```

## 🔧 Configuration

### CORS Settings
Update CORS origins in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend-domain.com",
        "https://your-render-app.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

### Environment Detection
The application automatically detects the environment:
- **Development**: Uses localhost URLs
- **Production**: Uses production URLs
- **Render**: Automatically configured

## 📊 Monitoring & Analytics

### Health Checks
- **Backend**: `GET /health`
- **Auth**: `GET /auth/health`
- **Database**: Automatic connection testing

### Logging
- Application logs in console
- Error tracking with detailed stack traces
- Performance monitoring for assessments

## 🔒 Security Features

- **Domain Restriction**: Only @chargebee.com emails allowed
- **Email Verification**: Required before login
- **JWT Authentication**: Secure token-based auth
- **CORS Protection**: Configured origins only
- **Input Validation**: Pydantic models for all inputs
- **SQL Injection Protection**: Parameterized queries

## 🚀 Deployment Checklist

### Pre-deployment
- [ ] Environment variables configured
- [ ] Database schema created
- [ ] CORS origins updated
- [ ] API keys secured
- [ ] Domain verification set up

### Post-deployment
- [ ] Health checks passing
- [ ] Authentication working
- [ ] Assessment creation functional
- [ ] Email verification working
- [ ] Monitoring configured

## 📈 Performance Optimization

### Backend
- **Caching**: Redis for session storage
- **Async Processing**: Background assessment execution
- **Connection Pooling**: Database connection optimization
- **Rate Limiting**: API request throttling

### Frontend
- **Code Splitting**: Lazy loading of components
- **Optimized Builds**: Production build optimization
- **CDN**: Static asset delivery
- **Caching**: Browser caching strategies

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find and kill process
   lsof -i :8000
   kill -9 <PID>
   ```

2. **Database Connection Issues**
   - Check Supabase credentials
   - Verify network connectivity
   - Check firewall settings

3. **Authentication Problems**
   - Verify email domain restriction
   - Check email verification setup
   - Validate JWT configuration

4. **Assessment Failures**
   - Check API rate limits
   - Verify scraper configurations
   - Monitor error logs

### Debug Mode
Enable debug mode for detailed logging:
```bash
export DEBUG=True
export ENVIRONMENT=development
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check application logs
4. Create an issue in the repository

## 📄 License

This project is proprietary software for Chargebee internal use.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Built with ❤️ for Chargebee Risk Management** 
