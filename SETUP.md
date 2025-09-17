# 🚀 Setup Guide for Marketing Analytics MCP System

## Prerequisites

- Python 3.9 or higher
- Access to Databricks workspace
- Anthropic API key
- (Optional) LangSmith API key for tracing

## Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd LangGraph_MCP
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Copy the template file and fill in your credentials:
```bash
cp env.template .env
```

Edit `.env` with your actual credentials:
```bash
# Required
ANTHROPIC_API_KEY=your_actual_anthropic_key_here
DATABRICKS_SERVER_HOSTNAME=your_databricks_server_here
DATABRICKS_HTTP_PATH=your_http_path_here
DATABRICKS_ACCESS_TOKEN=your_access_token_here

# Optional
LANGSMITH_API_KEY=your_langsmith_key_here
DATABRICKS_CATALOG=main
DATABRICKS_SCHEMA=default
```

### 4. Run the System

#### Option A: Run Both Services
```bash
python fastapi_backend.py &
streamlit run streamlit_app_mcp.py --server.port 8502
```

#### Option B: Run Separately
```bash
# Terminal 1 - Backend
python -m uvicorn fastapi_backend:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
streamlit run streamlit_app_mcp.py --server.port 8502
```

### 5. Access the Application

- **Frontend UI**: http://localhost:8502
- **API Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key for Claude |
| `DATABRICKS_SERVER_HOSTNAME` | Yes | Your Databricks server hostname |
| `DATABRICKS_HTTP_PATH` | Yes | Your Databricks HTTP path |
| `DATABRICKS_ACCESS_TOKEN` | Yes | Your Databricks access token |
| `DATABRICKS_CATALOG` | No | Databricks catalog (default: main) |
| `DATABRICKS_SCHEMA` | No | Databricks schema (default: default) |
| `LANGSMITH_API_KEY` | No | LangSmith key for tracing (optional) |

### Databricks Setup

1. Go to your Databricks workspace
2. Navigate to SQL Warehouses
3. Create or select a SQL Warehouse
4. Get the connection details:
   - Server hostname
   - HTTP path
   - Access token

## Features

- 🤖 **AI-Powered Chatbot**: Natural language queries about your data
- 📊 **Marketing Analytics**: Campaign and report analysis
- 🔒 **Consent Management**: Secure data access with user consent
- 🌐 **Web Interface**: Easy-to-use Streamlit frontend
- 🔌 **API Access**: RESTful API for integration
- 📈 **MCP Integration**: Model Context Protocol for advanced AI capabilities

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Verify your Databricks credentials
   - Ensure the SQL Warehouse is running
   - Check network connectivity

2. **API Key Errors**
   - Verify your Anthropic API key is valid
   - Check that the key has sufficient credits

3. **Port Conflicts**
   - Change ports in the startup commands if 8000 or 8502 are in use
   - Update the frontend to use the new backend port

### Getting Help

- Check the logs in the terminal for error messages
- Verify all environment variables are set correctly
- Ensure all dependencies are installed

## Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure
- Use environment variables for all sensitive data
- Regularly rotate your access tokens

## Development

### Project Structure

```
LangGraph_MCP/
├── config.py              # Configuration (uses env vars)
├── fastapi_backend.py     # FastAPI backend server
├── streamlit_app_mcp.py   # Streamlit frontend
├── mcp_server.py          # MCP server implementation
├── databricks_connector.py # Databricks connection logic
├── conversational_agent.py # AI conversation handling
├── data_agent_mcp.py      # Data analysis agent
├── intent_classifier.py   # User intent classification
├── requirements.txt       # Python dependencies
├── env.template          # Environment variables template
├── .gitignore            # Git ignore rules
└── SETUP.md              # This file
```

### Adding New Features

1. Add new tools to `mcp_server.py`
2. Update the frontend in `streamlit_app_mcp.py`
3. Add API endpoints in `fastapi_backend.py`
4. Test with the health check endpoint

## License

[Add your license information here]
