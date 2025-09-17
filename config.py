"""
Configuration for Databricks and LangGraph Integration
"""
import os

# Anthropic API Configuration
ANTHROPIC_CONFIG = {
    "api_key": os.getenv("ANTHROPIC_API_KEY", "your_anthropic_api_key_here"),
    "model": "claude-3-5-sonnet-20241022"
}

# LangSmith API Configuration
LANGSMITH_CONFIG = {
    "api_key": os.getenv("LANGSMITH_API_KEY", "your_langsmith_api_key_here")
}

# Databricks connection settings
DATABRICKS_CONFIG = {
    "server_hostname": os.getenv("DATABRICKS_SERVER_HOSTNAME", "your_databricks_server_here"),
    "http_path": os.getenv("DATABRICKS_HTTP_PATH", "your_http_path_here"),
    "access_token": os.getenv("DATABRICKS_ACCESS_TOKEN", "your_access_token_here"),
    "catalog": os.getenv("DATABRICKS_CATALOG", "main"),
    "schema": os.getenv("DATABRICKS_SCHEMA", "default")
}

# Table names
TABLES = {
    "campaigns": "campaigns",
    "reports": "reports"
}

# LangGraph Configuration
LANGGRAPH_CONFIG = {
    "max_iterations": 10,
    "temperature": 0.1,
    "system_prompt": """You are a marketing analytics assistant with access to Databricks data.
You can help users analyze campaign performance, reports data, and marketing metrics.

Available data sources:
- Campaign data: campaign.silver.campaigns (campaign_id, campaign_name, status, channel, budget, start_date, end_date)
- Reports data: campaign.silver.reports (report_id, campaign_id, impressions, clicks, conversions, cost, CTR, CVR)

Always provide clear, actionable insights based on the actual data."""
}

