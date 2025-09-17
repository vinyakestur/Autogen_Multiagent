# Marketing Analytics Platform - Setup Guide

## 🔧 Environment Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Marketing_Analytics_Platform
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

1. Copy the environment template:
```bash
cp env.template .env
```

2. Edit `.env` file with your actual credentials:
```bash
# Anthropic API Configuration
ANTHROPIC_API_KEY=your_actual_anthropic_api_key
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Databricks Configuration
DATABRICKS_SERVER_HOSTNAME=your_actual_databricks_server_hostname
DATABRICKS_HTTP_PATH=your_actual_databricks_http_path
DATABRICKS_ACCESS_TOKEN=your_actual_databricks_access_token
DATABRICKS_CATALOG=campaign
DATABRICKS_SCHEMA=silver
```

### 5. Get Your Credentials

#### Anthropic API Key
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up/Login
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

#### Databricks Credentials
1. Go to your Databricks workspace
2. Navigate to User Settings → Developer → Access Tokens
3. Generate a new token
4. Copy the token to `DATABRICKS_ACCESS_TOKEN` in your `.env` file
5. Get your workspace URL and SQL warehouse path from Databricks SQL

### 6. Run the Application

#### Option 1: FastAPI Backend Only
```bash
python fastapi_direct.py
```
Backend will be available at: http://localhost:8000

#### Option 2: Streamlit Frontend
```bash
streamlit run streamlit_app.py
```
Frontend will be available at: http://localhost:8501

#### Option 3: Both (Recommended)
Terminal 1 (Backend):
```bash
python fastapi_direct.py
```

Terminal 2 (Frontend):
```bash
streamlit run streamlit_app.py
```

## 🔒 Security Notes

- Never commit your `.env` file to version control
- The `.env` file is already included in `.gitignore`
- Use strong, unique API keys
- Rotate your credentials regularly
- Consider using environment-specific configurations for production

## 🚀 Quick Test

1. Start both backend and frontend
2. Open http://localhost:8501 in your browser
3. Try asking: "What is CTR?" or "Show me my campaigns"
4. Check the API health at http://localhost:8000/health

## 📁 Project Structure

```
Marketing_Analytics_Platform/
├── .env                    # Your credentials (create from env.template)
├── .gitignore             # Git ignore rules
├── env.template           # Environment variables template
├── config.py              # Configuration (uses env vars)
├── fastapi_direct.py      # FastAPI backend
├── streamlit_app.py       # Streamlit frontend
├── databricks_connector.py # Databricks integration
├── sql_generator.py       # AI SQL generation
├── intent_classifier.py   # User intent classification
├── chart_generator.py     # Chart generation
├── example_queries.py     # Predefined queries
├── sql_logger.py          # Query logging
└── requirements.txt       # Python dependencies
```
