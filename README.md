# Marketing Analytics Chatbot with MCP Integration

This project provides an AI-powered marketing analytics chatbot that integrates with Databricks data warehouse using the Model Context Protocol (MCP). It features both a web interface and API endpoints for analyzing campaign performance and marketing metrics.

## 🚀 Quick Start

**For detailed setup instructions, see [SETUP.md](SETUP.md)**

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `env.template` to `.env` and fill in your credentials
4. Run: `python fastapi_backend.py` and `streamlit run streamlit_app_mcp.py --server.port 8502`
5. Access at http://localhost:8502

## 🚀 Features

- **AI-Powered Chat Interface**: Natural language queries about your marketing data
- **MCP Integration**: Advanced tool integration using Model Context Protocol
- **Real-time Data Analysis**: Direct connection to Databricks data warehouse
- **Consent Management**: Secure data access with user consent workflow
- **Web Interface**: Modern Streamlit-based UI for easy interaction
- **REST API**: FastAPI backend for programmatic access

## 🏗️ Architecture

The project consists of two main components:

1. **FastAPI Backend** (`fastapi_backend.py`) - API server with MCP integration
2. **Streamlit Frontend** (`streamlit_app_mcp.py`) - Web interface for user interaction

## 📊 Data Sources

- **Campaign Data**: `campaign.silver.campaigns` (campaign_id, campaign_name, status, channel, budget, start_date, end_date)
- **Reports Data**: `campaign.silver.reports` (report_id, campaign_id, impressions, clicks, conversions, cost, CTR, CVR)

## 🛠️ Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration:**
   Your Databricks credentials are configured in `config.py`:
   - Server: `dbc-f4ba6223-6a9f.cloud.databricks.com`
   - Catalog: `campaign`
   - Schema: `silver`
   - Tables: `campaigns`, `reports`

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Databricks account with SQL Warehouse
- Anthropic API key

### Installation & Setup

1. **Clone and navigate to the project:**
   ```bash
   cd /Users/vinyakestur/Downloads/LangGraph_MCP
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify configuration:**
   - Check `config.py` for correct Databricks credentials
   - Ensure Anthropic API key is valid

### Running the Project

#### Option 1: Web Interface (Recommended)

**Terminal 1 - Start Backend:**
```bash
python fastapi_backend.py
```
Expected output:
```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:mcp_client:✅ Connected to MCP server
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
🚀 Starting FastAPI with MCP integration...
✅ MCP client connected
```

**Terminal 2 - Start Frontend:**
```bash
python -m streamlit run streamlit_app_mcp.py --server.port 8501
```
Expected output:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://10.0.0.110:8501
```

**Access the Application:**
- **Web Interface**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

#### Option 2: Direct API Usage

```python
import requests

# Test the API
response = requests.post("http://localhost:8000/chat", json={
    "message": "Show me my top performing campaigns",
    "user_id": "test_user"
})

print(response.json())
```

#### Option 3: Using curl

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is CTR?", "user_id": "test_user"}'
```

## 💬 Sample Chat Examples

### 🎯 **General Marketing Questions** (No Data Access Required)

These questions are handled by the Conversational Agent and don't require data access:

```
User: "What is CTR?"
Bot: "CTR stands for Click-Through Rate, which is a key digital marketing metric..."

User: "What are industry benchmarks for CPC?"
Bot: "Industry benchmarks for Cost Per Click (CPC) vary by channel and industry..."

User: "How do I improve my campaign performance?"
Bot: "Here are some proven strategies to improve campaign performance..."

User: "What's the difference between CPM and CPC?"
Bot: "CPM (Cost Per Mille) and CPC (Cost Per Click) are different pricing models..."

User: "What are best practices for digital marketing?"
Bot: "Here are the key best practices for digital marketing success..."
```

### 📊 **Data Analysis Questions** (Requires Consent)

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

User: "Show me my top performing campaigns"
Bot: [Consent request] → [After approval]
     "Top performing campaigns by conversions:
      1. Campaign C: 1,250 conversions, 3.2% CTR
      2. Campaign A: 980 conversions, 2.8% CTR
      3. Campaign D: 750 conversions, 2.1% CTR"

User: "Analyze my campaign performance trends"
Bot: [Consent request] → [After approval]
     "Performance trends over the last 30 days:
     • Conversions: +15% increase
     • CTR: +8% improvement
     • Cost per conversion: -12% decrease
     • Top performing channel: Search (3.1% CTR)"

User: "Compare Display vs Video performance"
Bot: [Consent request] → [After approval]
     "Channel Performance Comparison:
     Display:
     • CTR: 2.3%
     • Conversions: 1,200
     • Cost: $8,500
     
     Video:
     • CTR: 1.8%
     • Conversions: 950
     • Cost: $12,000
     
     Recommendation: Display is more cost-effective for your campaigns"

User: "What's my total budget across all campaigns?"
Bot: [Consent request] → [After approval]
     "Total budget allocation:
     • Active campaigns: $35,000
     • Paused campaigns: $10,000
     • Total: $45,000
     • By channel: Search (40%), Display (35%), Video (25%)"
```

### 🔧 **Campaign Management Actions** (High Consent Required)

These actions modify campaign settings and require high-level consent:

```
User: "Pause my Display campaigns"
Bot: [High consent request] → [After approval]
     "Successfully paused 3 Display campaigns:
     • Campaign A: Paused
     • Campaign B: Paused  
     • Campaign C: Paused
     Total budget freed: $15,000"

User: "Increase budget for Campaign A by $2,000"
Bot: [High consent request] → [After approval]
     "Campaign A budget updated:
     • Previous: $5,000
     • New: $7,000
     • Increase: +40%"
```

### 🧪 **Testing Commands**

Use these commands to test different aspects of the system:

```bash
# Test general questions (no consent)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is CTR?", "user_id": "test_user"}'

# Test data questions (requires consent)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "show my campaigns", "user_id": "test_user"}'

# Test health check
curl http://localhost:8000/health

# Test available tools
curl http://localhost:8000/tools
```

### 🎮 **Interactive Testing Script**

Create a test script to try different queries:

```python
import requests
import json

def test_chat(message, user_id="test_user"):
    response = requests.post("http://localhost:8000/chat", json={
        "message": message,
        "user_id": user_id
    })
    return response.json()

# Test different types of queries
queries = [
    "What is CTR?",
    "How do I optimize campaigns?",
    "show my campaigns",
    "analyze my performance",
    "what's my total budget?",
    "pause my display campaigns"
]

for query in queries:
    print(f"\nQuery: {query}")
    result = test_chat(query)
    print(f"Response: {result['response'][:100]}...")
    print(f"Agent: {result['agent']}")
    print(f"Consent Required: {result.get('consent_required', False)}")
```

## 🔗 **API Endpoints**

- `POST /chat` - Main chat endpoint
- `POST /consent` - Handle data access consent
- `GET /health` - Health check
- `GET /tools` - Available MCP tools
- `GET /` - System status and available tools

## 🔧 Advanced Configuration

### MCP Server Configuration
The MCP server configuration is in `cursor_mcp_config.json`:

```json
{
  "mcpServers": {
    "marketing-analytics-mcp": {
      "command": "python",
      "args": ["/path/to/mcp_server_standalone.py"],
      "env": {
        "DATABRICKS_TOKEN": "your_token",
        "DATABRICKS_URL": "https://your-databricks-url",
        "ANTHROPIC_API_KEY": "your_anthropic_key"
      }
    }
  }
}
```

### Environment Variables
You can also use environment variables instead of hardcoded credentials:

```bash
export ANTHROPIC_API_KEY="your_key"
export DATABRICKS_SERVER_HOSTNAME="your_hostname"
export DATABRICKS_HTTP_PATH="your_path"
export DATABRICKS_ACCESS_TOKEN="your_token"
```

## 📁 Project Structure

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
└── requirements.txt            # Python dependencies
```

## 🔍 Available Tools

The system includes several MCP tools for data analysis:

- `query_campaigns` - Query campaign data with filters
- `analyze_performance` - Analyze campaign performance metrics
- `get_campaign_overview` - Get campaign statistics
- `search_campaigns` - Search campaigns by criteria
- `get_monthly_trends` - Analyze monthly performance trends

## 🛡️ Security Features

- **Consent Management**: Users must approve data access requests
- **Intent Classification**: Automatic detection of data vs conversational queries
- **Secure Credentials**: API keys stored in configuration files
- **CORS Protection**: Cross-origin request protection

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. **Table Not Found Error**
```
ERROR: [TABLE_OR_VIEW_NOT_FOUND] The table or view `campaign`.`silver`.`campaign` cannot be found
```
**Solution:**
- Ensure table names are correct (`campaigns` not `campaign`)
- Verify catalog and schema names in `config.py`
- Check Databricks warehouse is running

#### 2. **Connection Errors**
```
ERROR: Failed to connect to Databricks
```
**Solution:**
- Check Databricks credentials in `config.py`
- Ensure the warehouse is running
- Verify network connectivity
- Test connection: `python -c "from databricks_connector import DatabricksConnection; DatabricksConnection().connect()"`

#### 3. **MCP Connection Issues**
```
ERROR: MCP client connection failed
```
**Solution:**
- Check MCP server configuration in `cursor_mcp_config.json`
- Verify Anthropic API key is valid
- Check server logs for detailed errors
- Restart both backend and frontend

#### 4. **Frontend Not Loading**
```
Streamlit app not accessible at http://localhost:8501
```
**Solution:**
- Ensure both backend and frontend are running
- Check port availability (8000 for backend, 8501 for frontend)
- Try different ports: `streamlit run streamlit_app_mcp.py --server.port 8502`
- Check firewall settings

#### 5. **Consent Errors**
```
ERROR: Consent request not found
```
**Solution:**
- Clear browser cache and refresh
- Restart the backend server
- Check consent ID generation in logs

#### 6. **API Timeout Errors**
```
ERROR: Request timeout
```
**Solution:**
- Check Databricks warehouse performance
- Increase timeout settings
- Monitor server resources

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Check Commands

```bash
# Check backend health
curl http://localhost:8000/health

# Check if ports are in use
lsof -i :8000
lsof -i :8501

# Check Python processes
ps aux | grep -E "(fastapi_backend|streamlit)"

# Test Databricks connection
python -c "from databricks_connector import DatabricksConnection; print('Connection test:', DatabricksConnection().connect())"
```

### Log Analysis

Check logs for specific error patterns:

```bash
# Backend logs
python fastapi_backend.py 2>&1 | grep ERROR

# Frontend logs  
python -m streamlit run streamlit_app_mcp.py --server.port 8501 2>&1 | grep ERROR
```

## 📈 Performance

- **Query Optimization**: Efficient SQL queries with proper indexing
- **Caching**: Response caching for frequently asked questions
- **Async Processing**: Non-blocking API operations
- **Connection Pooling**: Reusable database connections

## 🔄 Updates and Maintenance

- **Regular Updates**: Keep dependencies updated
- **Credential Rotation**: Regularly rotate API keys and tokens
- **Monitoring**: Monitor API performance and error rates
- **Backup**: Regular backup of configuration and data

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review server logs for error details
3. Verify configuration settings
4. Test with simple queries first

## 🔐 Security Note

- API keys are stored in configuration files
- In production, use environment variables or secure key management
- Regularly rotate credentials
- Monitor access logs for suspicious activity

---

**Version**: 2.0.0  
**Last Updated**: 2024  
**Compatibility**: Python 3.8+, Databricks SQL Warehouse