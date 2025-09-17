# 🤖 Marketing Analytics Platform

Build a comprehensive marketing analytics platform that connects to Databricks for intelligent data querying and visualization.

## 🎯 Project Overview

This system provides a comprehensive solution for intelligent data analysis with direct Databricks integration, user consent management, and automated report generation.

## 🔄 Core Workflow

### 1. Direct Databricks Connection
- Establish secure connection to Databricks workspace
- Access raw data directly through API integration
- Real-time data processing capabilities

### 2. User Consent Management
- Streamlit UI requests user permission before data access
- Provides approve/deny/cancel options for data queries
- Granular permission control for different data types

### 3. Intelligent Query System
- **Predefined Queries**: Check catalog for existing queries matching user request
- **Dynamic Creation**: Generate new queries if no predefined match exists
- **Direct Execution**: Execute queries against Databricks catalog automatically

### 4. Automated Report Generation
- Streamlit UI generates visual reports including graphs, charts, and analytics
- Multiple visualization types based on query results
- Interactive dashboards for data exploration

## 🏗️ System Components

### API Catalog
- Pre-configured Databricks API endpoints for common analysis tasks
- Standardized query templates for different data types
- Easy configuration and management interface

### Agent Tool Configuration
- Easy setup interface enabling AI agents to interact with Databricks functions
- MCP (Model Context Protocol) integration for intelligent automation
- Configurable tool parameters and permissions

### Graphical UI (Streamlit)
- Visual interface for managing API calls
- Interactive data visualizations and dashboards
- User-friendly consent management system

### Backend API Connector
- Direct integration layer handling Databricks authentication
- Real-time data processing and query execution
- Secure API communication protocols

### Data Visualization Engine
- Automatic conversion of query results into charts and graphs
- Multiple visualization formats (bar, line, pie, scatter, etc.)
- Comprehensive report generation capabilities

## 🔄 Technical Flow

```
User Request → Streamlit UI receives analysis query
     ↓
Consent Check → System requests permission to access data
     ↓
Query Processing → Check catalog for predefined queries or create new ones
     ↓
Data Execution → Execute query against Databricks via API connector
     ↓
Visualization → Generate graphs and reports in Streamlit interface
```

## ✨ Key Features

- **🔒 Secure Access**: Permission-based data access with user consent
- **🧠 Smart Querying**: Hybrid approach using predefined and dynamic queries
- **⚡ Real-time Analysis**: Direct connection for immediate data processing
- **📊 Rich Visualization**: Multiple chart types and report formats
- **👥 User-friendly Interface**: Intuitive Streamlit-based dashboard

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- Databricks SQL Warehouse access
- Internet connection for AI API calls

### 2. Install Dependencies
```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd Marketing_Analytics_Platform

# Install required packages
pip install -r requirements.txt
```

### 3. Configuration
1. Copy the environment template:
```bash
cp env.template .env
```

2. Edit `.env` file with your actual credentials:
- **Server**: Your Databricks workspace URL
- **Catalog**: `campaign` (or your preferred catalog)
- **Schema**: `silver` (or your preferred schema)
- **Access Token**: Your Databricks personal access token
- **AI Model**: Claude-3.5-Sonnet for intelligent query generation

See `SETUP.md` for detailed configuration instructions.

### 4. Run the System

#### Option A: Manual Startup (Recommended for Development)
```bash
# Terminal 1 - Start Backend API
python -m uvicorn fastapi_direct:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Start Frontend UI
streamlit run streamlit_app.py --server.port 8502 --server.address 0.0.0.0
```

#### Option B: Quick Test (Single Command)
```bash
# Test backend only
python fastapi_direct.py

# Test frontend only (requires backend running)
streamlit run streamlit_app.py
```

### 5. Access the Application
- **🎨 Frontend UI**: http://localhost:8502
- **🔧 API Backend**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **❤️ Health Check**: http://localhost:8000/health

### 6. Verify System Health
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check if frontend is accessible
curl http://localhost:8502

# Test Databricks connection
python -c "from databricks_connector import DatabricksConnection; print('✅ Connection test:', DatabricksConnection().connect())"
```

## 📁 Project Structure

```
Marketing_Analytics_Platform/
├── 🎨 Frontend
│   └── streamlit_app.py              # Main Streamlit UI with consent management
├── 🔧 Backend
│   ├── fastapi_direct.py             # FastAPI backend with direct Databricks integration
│   ├── databricks_connector.py       # Direct Databricks connection utilities
│   └── sql_logger.py                 # SQL query logging and audit trail
├── 🧠 Intelligence Layer
│   ├── example_queries.py            # Hybrid query system (predefined + AI)
│   ├── sql_generator.py              # AI-powered SQL generation (Claude)
│   └── intent_classifier.py          # Intent classification (conversational vs data)
├── 📊 Visualization
│   └── chart_generator.py            # Automated chart generation (Plotly)
├── ⚙️ Configuration
│   ├── config.py                     # System configuration and credentials
│   └── requirements.txt              # Python dependencies
├── 📝 Documentation
│   ├── README.md                     # This file
│   └── ARCHITECTURE_USER_FLOW.md    # Detailed technical documentation
└── 📊 Data & Logs
    └── sql_logs/                     # Query execution logs and audit trail
        ├── session_default_user.json
        └── session_test_user.json
```

### **Key Files Explained:**

- **`streamlit_app.py`**: Main user interface with chat, consent management, and data visualization
- **`fastapi_direct.py`**: REST API backend handling requests, consent, and data processing
- **`databricks_connector.py`**: Direct connection to Databricks SQL Warehouse
- **`example_queries.py`**: Hybrid query system combining predefined templates with AI generation
- **`sql_generator.py`**: Claude AI integration for custom SQL query generation
- **`intent_classifier.py`**: Determines if queries are conversational or require data access
- **`chart_generator.py`**: Automatically creates interactive visualizations from data
- **`config.py`**: Contains Databricks credentials and AI model configuration

## 🔧 Advanced Features

### Consent Management
- Granular permission requests for different data types
- User-friendly approval interface
- Audit trail for data access

### Intelligent Query Processing
- Natural language to SQL conversion
- Query optimization and validation
- Caching for improved performance

### Visualization Engine
- Automatic chart type selection based on data
- Interactive filtering and drilling down
- Export capabilities for reports

## 🛡️ Security

- Secure Databricks authentication
- User consent tracking and management
- API key protection and rotation
- Audit logging for compliance

## 📊 Supported Data Types

- Campaign performance metrics
- Marketing analytics data
- Financial reports and KPIs
- Custom business metrics
- Real-time operational data

## 💬 Sample Chat Examples

### 🗣️ **Conversational Queries (No Data Access Required)**

These queries provide educational content without accessing your data:

#### **Marketing Metrics Education**
```
👤 User: "What is CTR?"
🤖 Bot: "CTR stands for Click-Through Rate, which is a key digital marketing metric that measures the percentage of people who click on your ad after seeing it.

Formula: CTR = (Clicks ÷ Impressions) × 100

Industry Benchmarks:
- Search Ads: 1.91% average
- Display Ads: 0.35% average  
- Social Media: 0.9% average

How to Improve CTR:
- Write compelling ad copy
- Use relevant keywords
- A/B test different headlines
- Target the right audience"
```

#### **Performance Optimization Advice**
```
👤 User: "How do I improve campaign performance?"
🤖 Bot: "Here are proven strategies to improve campaign performance:

1. Keyword Optimization
   - Use negative keywords to exclude irrelevant traffic
   - Focus on long-tail keywords
   - Regular keyword research and updates

2. Ad Copy Testing
   - A/B test headlines and descriptions
   - Use emotional triggers
   - Include clear calls-to-action

3. Landing Page Optimization
   - Match ad copy to landing page content
   - Improve page load speed
   - Optimize for mobile devices

Would you like me to analyze your actual campaign data to provide specific recommendations?"
```

#### **Marketing Concepts**
```
👤 User: "What is CPC?"
🤖 Bot: "CPC (Cost Per Click) is the amount you pay each time someone clicks on your ad.

Industry Benchmarks:
- Search: $1-2 average
- Display: $0.50-1 average
- Social: $0.50-1.50 average

Factors Affecting CPC:
- Keyword competition
- Ad quality score
- Targeting specificity
- Industry competition

Tips to Lower CPC:
- Improve ad relevance
- Use long-tail keywords
- Optimize landing pages"
```

### 📊 **Data Analysis Queries (Requires Consent)**

These queries access your actual Databricks data and require approval:

#### **Basic Campaign Queries**
```
👤 User: "Show me my campaigns"
🤖 Bot: [🔐 Consent Request]
       "I found a matching analysis for your request: 'Show me my campaigns'

Action: Query campaign data from Databricks
Tools Required: databricks_query, campaign_analyzer
Data Access: campaign data, campaign metadata
Impact: This will retrieve and display your campaign information for analysis.

Please approve this data access request to continue with the analysis."

[After Approval] ✅
🤖 Bot: "✅ Analysis completed! Here are your results:

Found 50 campaigns. Here are the key details from your campaign data.

[Interactive Data Table with Campaigns]
[Pie Chart: Status Distribution]
[Bar Chart: Channel Distribution]
[Budget Analysis Chart]"
```

#### **Performance Analysis**
```
👤 User: "Analyze my performance"
🤖 Bot: [🔐 Consent Request]
       "I understand you want to analyze: 'Analyze my performance'

I'll generate a custom SQL query to answer your specific question.

Action: Query your marketing data
Tools Required: databricks_query, data_analyzer
Data Access: marketing data
Impact: This will query your marketing data for analysis.

Please approve this data access request to continue with the custom analysis."

[After Approval] ✅
🤖 Bot: "✅ Analysis completed! Here are your results:

Performance analysis complete. Analyzed 20 campaign performance records with detailed metrics.

[Performance Metrics Table]
[CTR Analysis Chart]
[CVR Analysis Chart]
[Performance Trends Line Chart]"
```

#### **Budget Analysis**
```
👤 User: "Show me budget allocation"
🤖 Bot: [🔐 Consent Request] → [After Approval] ✅
       "✅ Analysis completed! Here are your results:

Budget analysis complete. Total budget analyzed: $1,250,000.00 across 9 categories.

[Budget Allocation Table]
[Channel Budget Pie Chart]
[Budget vs Performance Scatter Plot]"
```

#### **AI-Powered Complex Queries**
```
👤 User: "Show me campaigns with budget greater than $5000"
-show me campaigns with budget greater than $30000"
-"find campaigns with budget less than $10000"
🤖 Bot: [🔐 Consent Request] → [After Approval] ✅
       "✅ Analysis completed! Here are your results:

Analysis complete. Retrieved 35 records of data for your query.

[Generated SQL Query Display]
[Filtered Campaigns Table]
[Budget Distribution Chart]"
```

#### **Trend Analysis**
```
👤 User: "Show me trends over time"
🤖 Bot: [🔐 Consent Request] → [After Approval] ✅
       "✅ Analysis completed! Here are your results:

Trend analysis complete. Analyzed 12 time periods showing performance trends over time.

[Monthly Trends Table]
[Performance Trends Line Chart]
[Channel Performance Over Time]"
```

#### **Summary Overview**
```
👤 User: "Give me a summary"
🤖 Bot: [🔐 Consent Request] → [After Approval] ✅
       "✅ Analysis completed! Here are your results:

📊 Marketing Data Summary

Campaigns Overview:
• Total Campaigns: 150
• Active: 45 | Completed: 80 | Paused: 25
• Total Budget: $2,500,000.00 | Average Budget: $16,666.67
• Channels: 5 different channels

Performance Overview:
• Total Reports: 1,200
• Average CTR: 2.15% | Average CVR: 3.42%
• Campaigns with Data: 120

This gives you a comprehensive overview of your marketing data performance."
```

### 🧪 **Testing Commands**

#### **Test Conversational Queries (No Data Access)**
```bash
# Test via API
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is CTR?", "user_id": "test_user"}'

# Expected: Direct response without consent request
```

#### **Test Data Queries (Requires Consent)**
```bash
# Test via API
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me my campaigns", "user_id": "test_user"}'

# Expected: Consent request with detailed explanation
```

#### **Test Consent Approval**
```bash
# First get consent_id from the above response, then:
curl -X POST "http://localhost:8000/consent" \
  -H "Content-Type: application/json" \
  -d '{"consent_id": "your-consent-id-here", "approved": true}'

# Expected: Data analysis results with charts and tables
```

## 🔗 API Endpoints

### **Core Endpoints**
- **`POST /chat`** - Main chat endpoint for user queries
- **`POST /consent`** - Handle data access consent approval/denial
- **`GET /health`** - System health check with Databricks connection test
- **`GET /tools`** - Available analysis tools and their requirements
- **`GET /`** - System status and available endpoints

### **API Usage Examples**

#### **Chat Endpoint**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me my campaigns",
    "user_id": "user123",
    "session_id": "session456"
  }'
```

#### **Consent Endpoint**
```bash
curl -X POST "http://localhost:8000/consent" \
  -H "Content-Type: application/json" \
  -d '{
    "consent_id": "uuid-here",
    "approved": true
  }'
```

#### **Health Check**
```bash
curl http://localhost:8000/health
```

### **Response Formats**

#### **Chat Response (Conversational)**
```json
{
  "response": "CTR stands for Click-Through Rate...",
  "agent": "conversational",
  "consent_required": false
}
```

#### **Chat Response (Data Query)**
```json
{
  "response": "I found a matching analysis for your request...",
  "agent": "data_analyst",
  "consent_required": true,
  "consent_id": "uuid-here"
}
```

#### **Consent Response (Approved)**
```json
{
  "response": "✅ Analysis completed! Here are your results...",
  "agent": "data_analyst",
  "consent_approved": true,
  "data": [...],
  "sql_query": "SELECT ...",
  "charts": [...]
}
```

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. **Connection Errors**
```
ERROR: Failed to connect to Databricks
```
**Solution:**
- Check Databricks credentials in `config.py`
- Ensure the warehouse is running
- Verify network connectivity

#### 2. **Frontend Not Loading**
```
Streamlit app not accessible at http://localhost:8502
```
**Solution:**
- Ensure both backend and frontend are running
- Check port availability
- Try different ports if needed

#### 3. **Consent Errors**
```
ERROR: Consent request not found
```
**Solution:**
- Clear browser cache and refresh
- Restart the backend server
- Check consent ID generation in logs

### Health Check Commands

```bash
# Check backend health
curl http://localhost:8000/health

# Check if ports are in use
lsof -i :8000
lsof -i :8502

# Test Databricks connection
python -c "from databricks_connector import DatabricksConnection; print('✅ Connection test:', DatabricksConnection().connect())"

# Test AI query generation
python -c "from sql_generator import SQLGenerator; sg = SQLGenerator(); print('✅ AI test:', sg.generate_sql('test query', 'custom'))"

# Check system status
curl http://localhost:8000/
```

### **Quick System Test**
```bash
# Complete system test script
#!/bin/bash
echo "🧪 Testing Marketing Analytics Platform..."

# Test 1: Backend Health
echo "1. Testing backend health..."
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✅ Backend healthy" || echo "❌ Backend unhealthy"

# Test 2: Conversational Query
echo "2. Testing conversational query..."
curl -s -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is CTR?", "user_id": "test"}' | grep -q "conversational" && echo "✅ Conversational working" || echo "❌ Conversational failed"

# Test 3: Data Query (should require consent)
echo "3. Testing data query..."
curl -s -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me my campaigns", "user_id": "test"}' | grep -q "consent_required" && echo "✅ Data query working" || echo "❌ Data query failed"

echo "🎉 System test complete!"
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