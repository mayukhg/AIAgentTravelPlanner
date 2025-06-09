# Installation Guide

This guide will help you set up the Multi-Agent Assistant System on your local development environment.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- AWS account with Bedrock access
- Perplexity AI API key

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd multi-agent-assistant
```

## Step 2: Environment Setup

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or if using the pyproject.toml:

```bash
pip install -e .
```

## Step 3: Database Setup

### PostgreSQL Installation

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download and install from [PostgreSQL official website](https://www.postgresql.org/download/windows/)

### Create Database

```bash
sudo -u postgres psql
CREATE DATABASE assistant_db;
CREATE USER assistant_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE assistant_db TO assistant_user;
\q
```

## Step 4: Environment Configuration

Create a `.env` file in the project root:

```env
# Amazon Bedrock Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Perplexity API (for web search)
PERPLEXITY_API_KEY=your_perplexity_api_key

# Flask Configuration
SESSION_SECRET=your-secret-key-here
FLASK_DEBUG=True

# Database (PostgreSQL)
DATABASE_URL=postgresql://assistant_user:your_password@localhost:5432/assistant_db
```

## Step 5: Database Initialization

Initialize the database tables:

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

Or use Flask-Migrate for more advanced database management:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Step 6: Run the Application

### Development Server

```bash
python main.py
```

The application will be available at `http://localhost:5000`

### Production Server

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

## Verification

### Health Check

Visit `http://localhost:5000/api/health` to verify all services are running correctly.

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-09T15:30:00Z",
  "services": {
    "database": "connected",
    "bedrock": "available",
    "perplexity": "available"
  },
  "agents": {
    "personal_assistant": "active",
    "calendar_agent": "active",
    "search_agent": "active",
    "code_assistant": "active"
  }
}
```

### Test Chat Interface

1. Navigate to `http://localhost:5000/chat`
2. Send a test message: "Hello, can you help me?"
3. Verify you receive a response from the Personal Assistant Agent

## AWS Bedrock Setup

### Enable Model Access

1. Log into AWS Console
2. Navigate to Amazon Bedrock
3. Go to "Model access" in the left sidebar
4. Request access to "Claude 3.5 Sonnet v4"
5. Wait for approval (usually within a few hours)

### IAM Permissions

Ensure your AWS user has the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

## Perplexity API Setup

1. Visit [Perplexity AI](https://www.perplexity.ai/)
2. Sign up for an account
3. Navigate to API settings
4. Generate an API key
5. Add the key to your `.env` file

## Troubleshooting

### Common Issues

**Database Connection Error:**
- Verify PostgreSQL is running
- Check DATABASE_URL format
- Ensure database and user exist

**AWS Bedrock Access Denied:**
- Verify AWS credentials
- Check model access approval status
- Ensure proper IAM permissions

**Perplexity API Error:**
- Verify API key is correct
- Check account billing status
- Ensure API quota is not exceeded

**Port Already in Use:**
```bash
# Find process using port 5000
lsof -i :5000
# Kill the process
kill -9 <PID>
```

### Getting Help

- Check the [Troubleshooting Guide](Troubleshooting)
- Review application logs in the console
- Create an issue in the GitHub repository

## Next Steps

- Read the [User Guide](User-Guide) to learn how to use the system
- Explore the [API Documentation](API-Reference) for integration
- Review [Security Guidelines](Security-Guidelines) for production deployment