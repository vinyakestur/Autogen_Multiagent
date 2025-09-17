# Marketing Analytics Chatbot with MCP Integration

This project provides an AI-powered marketing analytics chatbot that integrates with Databricks data warehouse using the Model Context Protocol (MCP). It features both a web interface and API endpoints for analyzing campaign performance and marketing metrics.

## Quick Start

**For detailed setup instructions, see [SETUP.md](SETUP.md)**

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `env.template` to `.env` and fill in your credentials
4. Run: `python fastapi_backend.py` and `streamlit run streamlit_app_mcp.py --server.port 8502`
5. Access at http://localhost:8502

## Features

- **AI-Powered Chat Interface**: Natural language queries about your marketing data
- **MCP Integration**: Advanced tool integration using Model Context Protocol
- **Real-time Data Analysis**: Direct connection to Databricks data warehouse
- **Consent Management**: Secure data access with user consent workflow
- **Web Interface**: Modern Streamlit-based UI for easy interaction
- **REST API**: FastAPI backend for programmatic access

## Architecture

The project consists of two main components:

1. **FastAPI Backend** (`fastapi_backend.py`) - API server with MCP integration
2. **Streamlit Frontend** (`streamlit_app_mcp.py`) - Web interface for user interaction

## Data Sources

- **Campaign Data**: `campaign.silver.campaigns` (campaign_id, campaign_name, status, channel, budget, start_date, end_date)
- **Reports Data**: `campaign.silver.reports` (report_id, campaign_id, impressions, clicks, conversions, cost, CTR, CVR)

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration:**
   Copy `env.template` to `.env` and fill in your credentials:
   - ANTHROPIC_API_KEY: Your Anthropic API key
   - DATABRICKS_SERVER_HOSTNAME: Your Databricks server
   - DATABRICKS_HTTP_PATH: Your Databricks HTTP path
   - DATABRICKS_ACCESS_TOKEN: Your Databricks access token

## Running the Project

### Option 1: Web Interface (Recommended)

**Terminal 1 - Start Backend:**
```bash
python fastapi_backend.py
```

**Terminal 2 - Start Frontend:**
```bash
streamlit run streamlit_app_mcp.py --server.port 8502
```

**Access the Application:**
- **Web Interface**: http://localhost:8502
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Option 2: Direct API Usage

```python
import requests

# Test the API
response = requests.post("http://localhost:8000/chat", json={
    "message": "Show me my top performing campaigns",
    "user_id": "test_user"
})

print(response.json())
```

### Option 3: Using curl

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is CTR?", "user_id": "test_user"}'
```

## Sample Chat Examples

### General Marketing Questions (No Data Access Required)

These questions are handled by the Conversational Agent and don't require data access:

```
User: "What is CTR?"
Bot: "CTR stands for Click-Through Rate, which is a key digital marketing metric..."

User: "What are industry benchmarks for CPC?"
Bot: "Industry benchmarks for Cost Per Click (CPC) vary by channel and industry..."

User: "How do I improve my campaign performance?"
Bot: "Here are some proven strategies to improve campaign performance..."
```

### Data Analysis Questions (Requires Consent)

These questions access your actual campaign data and require user consent:

```
User: "Show me my campaigns"
Bot: "This query requires access to your campaign data.
      Action: Execute data analysis for your query
      Tools: databricks_query, performance_analyzer
      Data Access: campaign data, reports data
      Impact: This will query and analyze your campaign data for insights.
      Please approve to continue."

[After approval]
Bot: "Here are your campaigns:
      • Campaign A: Display, Active, $5,000 budget
      • Campaign B: Video, Paused, $3,000 budget
      • Campaign C: Search, Active, $7,500 budget
      Total: 15 campaigns, $45,000 total budget"
```

## API Endpoints

- `POST /chat` - Main chat endpoint
- `POST /consent` - Handle data access consent
- `GET /health` - Health check
- `GET /tools` - Available MCP tools
- `GET /` - System status and available tools

## Project Structure

```
LangGraph_MCP/
├── fastapi_backend.py          # FastAPI server with MCP integration
├── streamlit_app_mcp.py        # Streamlit web interface
├── mcp_server.py               # MCP server implementation
├── mcp_server_standalone.py    # Standalone MCP server
├── mcp_client.py               # MCP client for tool integration
├── data_agent_mcp.py           # Data analysis agent
├── conversational_agent.py     # Conversational AI agent
├── intent_classifier.py        # Intent classification
├── databricks_connector.py     # Databricks connection utilities
├── example_queries.py          # Pre-built query examples
├── config.py                   # Configuration settings
├── cursor_mcp_config.json      # MCP server configuration
├── env.template                # Environment variables template
├── SETUP.md                    # Detailed setup instructions
└── requirements.txt            # Python dependencies
```

## Available Tools

The system includes several MCP tools for data analysis:

- `query_campaigns` - Query campaign data with filters
- `analyze_performance` - Analyze campaign performance metrics
- `get_campaign_overview` - Get campaign statistics
- `search_campaigns` - Search campaigns by criteria
- `get_monthly_trends` - Analyze monthly performance trends

## Security Features

- **Consent Management**: Users must approve data access requests
- **Intent Classification**: Automatic detection of data vs conversational queries
- **Environment Variables**: Secure credential management
- **CORS Protection**: Cross-origin request protection

## Troubleshooting

### Common Issues & Solutions

#### 1. Table Not Found Error
```
ERROR: [TABLE_OR_VIEW_NOT_FOUND] The table or view cannot be found
```
**Solution:**
- Ensure table names are correct in your Databricks schema
- Verify catalog and schema names in your `.env` file
- Check Databricks warehouse is running

#### 2. Connection Errors
```
ERROR: Failed to connect to Databricks
```
**Solution:**
- Check Databricks credentials in your `.env` file
- Ensure the warehouse is running
- Verify network connectivity

#### 3. MCP Connection Issues
```
ERROR: MCP client connection failed
```
**Solution:**
- Check MCP server configuration
- Verify Anthropic API key is valid
- Check server logs for detailed errors
- Restart both backend and frontend

### Health Check Commands

```bash
# Check backend health
curl http://localhost:8000/health

# Check if ports are in use
lsof -i :8000
lsof -i :8502

# Check Python processes
ps aux | grep -E "(fastapi_backend|streamlit)"
```

## Performance

- **Query Optimization**: Efficient SQL queries with proper indexing
- **Caching**: Response caching for frequently asked questions
- **Async Processing**: Non-blocking API operations
- **Connection Pooling**: Reusable database connections

## Updates and Maintenance

- **Regular Updates**: Keep dependencies updated
- **Credential Rotation**: Regularly rotate API keys and tokens
- **Monitoring**: Monitor API performance and error rates
- **Backup**: Regular backup of configuration and data

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review server logs for error details
3. Verify configuration settings
4. Test with simple queries first

## Security Note

- API keys are stored in environment variables
- Never commit your `.env` file to version control
- Regularly rotate credentials
- Monitor access logs for suspicious activity

---

**Version**: 2.0.0  
**Last Updated**: 2024  
**Compatibility**: Python 3.8+, Databricks SQL Warehouse