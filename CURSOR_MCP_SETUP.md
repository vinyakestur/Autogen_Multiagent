# 🎯 **Cursor MCP Integration Setup Guide**

## 🚀 **Quick Setup**

### **1. Add MCP Configuration to Cursor**

Copy the contents of `cursor_mcp_config.json` and add it to your Cursor settings:

**Cursor Settings → Features → MCP Servers**

```json
{
  "mcpServers": {
    "marketing-analytics-mcp": {
      "command": "python",
      "args": [
        "/Users/vibhakestur/Downloads/LangGraph_MCP/mcp_server_standalone.py"
      ],
      "env": {
        "DATABRICKS_TOKEN": "${DATABRICKS_ACCESS_TOKEN}",
        "DATABRICKS_URL": "https://${DATABRICKS_SERVER_HOSTNAME}",
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

### **2. Restart Cursor**

After adding the configuration, restart Cursor to load the MCP server.

### **3. Test the Integration**

Open a new chat in Cursor and try these commands:

```
@marketing-analytics-mcp get_campaign_summary
```

```
@marketing-analytics-mcp query_campaigns
```

---

## 🛠️ **Available MCP Tools**

### **1. get_campaign_summary**
Get a comprehensive overview of all campaigns.

**Usage:**
```
@marketing-analytics-mcp get_campaign_summary
```

**Parameters:**
- `include_channels` (boolean): Include channel breakdown
- `include_trends` (boolean): Include trend analysis

**Example:**
```
Show me a summary of all my campaigns with channel breakdown
```

### **2. query_campaigns**
Query specific campaign data with filters.

**Usage:**
```
@marketing-analytics-mcp query_campaigns
```

**Parameters:**
- `query_type`: 
  - `campaigns` - List campaigns with filters
  - `top_performing` - Top campaigns by metric
  - `channel_summary` - Channel performance summary
  - `campaign_performance` - Individual campaign details
- `filters`: Filter criteria (status, channel, metric)
- `limit`: Maximum results (default: 100)

**Examples:**
```
Show me my top 10 performing campaigns by conversions
Show me all Display campaigns
Get a summary of all channels
Show me campaign performance for campaign_id_123
```

### **3. analyze_performance**
Analyze campaign performance with advanced insights.

**Usage:**
```
@marketing-analytics-mcp analyze_performance
```

**Parameters:**
- `analysis_type`:
  - `trend` - Performance trends over time
  - `comparison` - Compare campaigns/channels
  - `optimization` - Generate optimization recommendations
- `campaigns`: List of campaign IDs to analyze
- `metrics`: Metrics to analyze (conversions, cost, CTR, CVR)
- `user_id`: User ID for consent management

**Examples:**
```
Analyze trends across all my campaigns
Compare Display vs Video performance
Generate optimization recommendations for my campaigns
```

### **4. execute_campaign_action**
Execute actions on campaigns (high consent required).

**Usage:**
```
@marketing-analytics-mcp execute_campaign_action
```

**Parameters:**
- `action`: 
  - `pause` - Pause campaigns
  - `resume` - Resume campaigns
  - `update_budget` - Update campaign budgets
- `campaign_ids`: List of campaign IDs to act on
- `parameters`: Action-specific parameters
- `user_id`: User ID for consent management

**Examples:**
```
Pause my underperforming campaigns
Resume my paused campaigns
Update budget for campaign_123 to $5000
```

---

## 💬 **Example Conversations with Cursor**

### **Campaign Overview**
```
User: "Give me an overview of my marketing campaigns"
Cursor: Uses @marketing-analytics-mcp get_campaign_summary
Result: Shows total campaigns, active campaigns, budget, channel breakdown
```

### **Performance Analysis**
```
User: "Which campaigns are performing best?"
Cursor: Uses @marketing-analytics-mcp query_campaigns with query_type="top_performing"
Result: Lists top performing campaigns with metrics
```

### **Channel Comparison**
```
User: "How are my Display campaigns doing compared to Video?"
Cursor: Uses @marketing-analytics-mcp analyze_performance with analysis_type="comparison"
Result: Comparative analysis of channel performance
```

### **Optimization Recommendations**
```
User: "How can I optimize my campaign performance?"
Cursor: Uses @marketing-analytics-mcp analyze_performance with analysis_type="optimization"
Result: Specific optimization recommendations
```

---

## 🔧 **Troubleshooting**

### **MCP Server Not Loading**
1. Check that the path to `mcp_server_standalone.py` is correct
2. Verify Python is in your PATH
3. Ensure all dependencies are installed: `pip install mcp`
4. Check Cursor logs for error messages

### **Tool Execution Errors**
1. Verify Databricks credentials are correct
2. Check that the database tables exist
3. Test the server manually: `python test_mcp_server.py`

### **Permission Issues**
1. Ensure the Python script has execute permissions
2. Check that the directory is accessible
3. Verify environment variables are set correctly

---

## 📊 **Data Access & Privacy**

### **Consent Management**
- **Basic queries** (campaign lists, summaries): No consent required
- **Performance analysis**: Low consent (auto-approved in MCP mode)
- **Campaign actions**: High consent (auto-approved in MCP mode)

### **Data Security**
- All queries go through your Databricks connection
- No data is stored locally by the MCP server
- All operations are logged for audit purposes

---

## 🎯 **Advanced Usage**

### **Custom Queries**
You can ask Cursor to combine multiple tools for complex analysis:

```
"Analyze my top 5 campaigns, then compare their performance across channels, and give me optimization recommendations"
```

### **Data Export**
```
"Show me my campaign summary and export the data to CSV"
```

### **Real-time Monitoring**
```
"Monitor my active campaigns and alert me if any are underperforming"
```

---

## 🚀 **Next Steps**

1. **Test the integration** with simple queries
2. **Explore the available tools** using the examples above
3. **Create custom workflows** combining multiple tools
4. **Set up monitoring** for regular campaign analysis
5. **Share insights** with your team using Cursor's export features

---

## 📞 **Support**

If you encounter issues:
1. Run `python test_mcp_server.py` to verify server functionality
2. Check the Cursor logs for MCP-related errors
3. Verify your Databricks connection is working
4. Ensure all environment variables are correctly set

---

**🎉 Your Marketing Analytics MCP Server is now integrated with Cursor!**

You can now ask Cursor to analyze your marketing data using natural language, and it will automatically use the appropriate MCP tools to provide insights and recommendations.



