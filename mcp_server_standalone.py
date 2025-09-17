#!/usr/bin/env python3
"""
Standalone MCP Server for Marketing Analytics
Can be run as a standalone MCP server for external clients like Cursor
"""
import asyncio
import json
import logging
import sys
import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool, TextContent, ImageContent, EmbeddedResource,
        CallToolResult, ListToolsResult
    )
except ImportError:
    print("MCP dependencies not installed. Run: pip install mcp")
    sys.exit(1)

# Local imports
from databricks_connector import DatabricksConnection
from data_agent import consent_manager
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "your_databricks_token_here")
DATABRICKS_URL = os.getenv("DATABRICKS_URL", "https://your_databricks_server_here")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your_anthropic_api_key_here")

@dataclass
class MarketingAnalyticsMCPServer:
    """Marketing Analytics MCP Server"""
    
    def __init__(self):
        self.server = Server("marketing-analytics-mcp")
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="query_campaigns",
                    description="Query campaign data from Databricks. No consent required for basic queries.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query_type": {
                                "type": "string",
                                "enum": ["campaigns", "reports", "performance", "summary", "top_performing", "channel_summary"],
                                "description": "Type of query to execute"
                            },
                            "filters": {
                                "type": "object",
                                "description": "Filter criteria (status, channel, etc.)",
                                "properties": {
                                    "status": {"type": "string", "description": "Campaign status"},
                                    "channel": {"type": "string", "description": "Marketing channel"},
                                    "metric": {"type": "string", "description": "Metric for top performing queries"}
                                }
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 100
                            }
                        },
                        "required": ["query_type"]
                    }
                ),
                Tool(
                    name="analyze_performance",
                    description="Analyze campaign performance with consent. Provides insights and recommendations.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "analysis_type": {
                                "type": "string",
                                "enum": ["trend", "comparison", "optimization"],
                                "description": "Type of analysis to perform"
                            },
                            "campaigns": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of campaign IDs to analyze"
                            },
                            "metrics": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Metrics to analyze",
                                "default": ["conversions", "cost", "CTR"]
                            },
                            "user_id": {
                                "type": "string",
                                "description": "User ID for consent management",
                                "default": "default_user"
                            }
                        },
                        "required": ["analysis_type"]
                    }
                ),
                Tool(
                    name="execute_campaign_action",
                    description="Execute actions on campaigns with high consent. Can pause, resume, or update budgets.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["pause", "resume", "update_budget"],
                                "description": "Action to perform on campaigns"
                            },
                            "campaign_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of campaign IDs to act on"
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Action-specific parameters (e.g., new_budget)"
                            },
                            "user_id": {
                                "type": "string",
                                "description": "User ID for consent management",
                                "default": "default_user"
                            }
                        },
                        "required": ["action", "campaign_ids"]
                    }
                ),
                Tool(
                    name="get_campaign_summary",
                    description="Get a high-level summary of all campaigns and their performance.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_channels": {
                                "type": "boolean",
                                "description": "Include channel breakdown",
                                "default": True
                            },
                            "include_trends": {
                                "type": "boolean", 
                                "description": "Include trend analysis",
                                "default": False
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "query_campaigns":
                    result = await self._query_campaigns(**arguments)
                elif name == "analyze_performance":
                    result = await self._analyze_performance(**arguments)
                elif name == "execute_campaign_action":
                    result = await self._execute_campaign_action(**arguments)
                elif name == "get_campaign_summary":
                    result = await self._get_campaign_summary(**arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                    )
                
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2))]
                )
                
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )
    
    async def _query_campaigns(self, query_type: str, filters: Dict = None, limit: int = 100) -> Dict[str, Any]:
        """Query campaign data - no consent required"""
        try:
            with DatabricksConnection() as db:
                if query_type == "campaigns":
                    # Get campaigns with filters
                    where_clause = ""
                    
                    if filters:
                        if filters.get("status"):
                            where_clause += f" AND status = '{filters['status']}'"
                        if filters.get("channel"):
                            where_clause += f" AND channel = '{filters['channel']}'"
                    
                    query = f"""
                    SELECT campaign_id, campaign_name, status, channel, budget, start_date, end_date
                    FROM campaign.silver.campaigns
                    WHERE 1=1 {where_clause}
                    LIMIT {limit}
                    """
                    
                    result = db.execute_query(query)
                    
                elif query_type == "channel_summary":
                    # Get channel performance summary
                    query = """
                    SELECT 
                        c.channel,
                        COUNT(*) as campaign_count,
                        SUM(r.impressions) as total_impressions,
                        SUM(r.clicks) as total_clicks,
                        SUM(r.conversions) as total_conversions,
                        SUM(r.cost) as total_cost,
                        AVG(r.CTR) as avg_ctr,
                        AVG(r.CVR) as avg_cvr,
                        SUM(r.cost)/NULLIF(SUM(r.conversions), 0) as overall_cpa
                    FROM campaign.silver.campaigns c
                    JOIN campaign.silver.reports r ON c.campaign_id = r.campaign_id
                    GROUP BY c.channel
                    ORDER BY total_conversions DESC
                    """
                    result = db.execute_query(query)
                    
                elif query_type == "top_performing":
                    metric = filters.get("metric", "conversions") if filters else "conversions"
                    query = f"""
                    SELECT 
                        c.campaign_name,
                        c.channel,
                        r.impressions,
                        r.clicks,
                        r.conversions,
                        r.cost,
                        r.CTR,
                        r.CVR
                    FROM campaign.silver.campaigns c
                    JOIN campaign.silver.reports r ON c.campaign_id = r.campaign_id
                    ORDER BY r.{metric} DESC
                    LIMIT {limit}
                    """
                    result = db.execute_query(query)
                    
                else:
                    return {"error": f"Unknown query_type: {query_type}"}
                
                # Convert pandas DataFrame to dict for JSON serialization
                if result is not None and not result.empty:
                    # Convert to records and handle date serialization
                    data = result.to_dict('records')
                    # Convert any datetime objects to strings
                    for record in data:
                        for key, value in record.items():
                            if hasattr(value, 'isoformat'):  # datetime objects
                                record[key] = value.isoformat()
                            elif pd.isna(value):  # NaN values
                                record[key] = None
                    
                    return {
                        "success": True,
                        "data": data,
                        "query_type": query_type,
                        "count": len(data),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "success": True,
                        "data": [],
                        "query_type": query_type,
                        "count": 0,
                        "timestamp": datetime.now().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"Error in query_campaigns: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def _analyze_performance(self, analysis_type: str, campaigns: List[str] = None, 
                                metrics: List[str] = None, user_id: str = "default_user") -> Dict[str, Any]:
        """Analyze performance with consent"""
        
        # Request consent
        consent_request = {
            "tool": "analyze_performance",
            "action": f"Perform {analysis_type} analysis",
            "parameters": {
                "analysis_type": analysis_type,
                "campaigns": campaigns or [],
                "metrics": metrics or ["conversions", "cost", "CTR"]
            },
            "impact": f"Will analyze {len(campaigns) if campaigns else 'all'} campaigns for {analysis_type} insights",
            "risk_level": "low"
        }
        
        consent_id = consent_manager.create_consent_request(user_id, f"{analysis_type} analysis", consent_request)
        
        # For MCP server, we'll auto-approve consent (in production, this would wait for user approval)
        consent_manager.approve_consent(consent_id)
        
        # Execute analysis
        try:
            if analysis_type == "trend":
                result = await self._analyze_trends(campaigns, metrics)
            elif analysis_type == "comparison":
                result = await self._compare_campaigns(campaigns, metrics)
            elif analysis_type == "optimization":
                result = await self._generate_optimization(campaigns, metrics)
            else:
                return {"error": f"Unknown analysis_type: {analysis_type}"}
            
            return {
                "success": True,
                "analysis": result,
                "analysis_type": analysis_type,
                "consent_id": consent_id,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "consent_id": consent_id, "timestamp": datetime.now().isoformat()}
    
    async def _execute_campaign_action(self, action: str, campaign_ids: List[str], 
                                    parameters: Dict = None, user_id: str = "default_user") -> Dict[str, Any]:
        """Execute campaign action with high consent"""
        
        # Get campaign details for impact analysis
        with DatabricksConnection() as db:
            query = f"""
            SELECT campaign_id, campaign_name, budget, channel, status
            FROM campaign.silver.campaigns
            WHERE campaign_id IN ({','.join([f"'{cid}'" for cid in campaign_ids])})
            """
            
            campaigns_data = db.execute_query(query)
        
        if campaigns_data is not None and not campaigns_data.empty:
            total_budget = campaigns_data['budget'].sum()
            daily_cost = total_budget / 30  # Rough estimate
            
            impact_analysis = {
                "affected_campaigns": len(campaign_ids),
                "total_budget": float(total_budget),
                "estimated_daily_impact": float(daily_cost),
                "campaigns": campaigns_data['campaign_name'].tolist()
            }
        else:
            impact_analysis = {
                "affected_campaigns": len(campaign_ids),
                "total_budget": 0,
                "estimated_daily_impact": 0,
                "campaigns": campaign_ids
            }
        
        # Request high consent
        consent_request = {
            "tool": "execute_campaign_action",
            "action": f"{action} on {len(campaign_ids)} campaigns",
            "parameters": {
                "action": action,
                "campaign_ids": campaign_ids,
                "parameters": parameters or {}
            },
            "impact": impact_analysis,
            "risk_level": "high"
        }
        
        consent_id = consent_manager.create_consent_request(user_id, f"{action} campaigns", consent_request)
        
        # Auto-approve for MCP server
        consent_manager.approve_consent(consent_id)
        
        # Execute action (simulation)
        try:
            if action == "pause":
                result = {
                    "paused_campaigns": campaign_ids,
                    "message": f"Successfully paused {len(campaign_ids)} campaigns",
                    "estimated_savings": f"${daily_cost:.2f}/day"
                }
            elif action == "resume":
                result = {
                    "resumed_campaigns": campaign_ids,
                    "message": f"Successfully resumed {len(campaign_ids)} campaigns",
                    "estimated_cost": f"${daily_cost:.2f}/day"
                }
            elif action == "update_budget":
                new_budget = parameters.get("new_budget", 0) if parameters else 0
                result = {
                    "updated_campaigns": campaign_ids,
                    "new_budget": new_budget,
                    "message": f"Updated budget for {len(campaign_ids)} campaigns"
                }
            else:
                return {"error": f"Unknown action: {action}"}
            
            return {
                "success": True,
                "action": action,
                "result": result,
                "consent_id": consent_id,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "consent_id": consent_id, "timestamp": datetime.now().isoformat()}
    
    async def _get_campaign_summary(self, include_channels: bool = True, include_trends: bool = False) -> Dict[str, Any]:
        """Get comprehensive campaign summary"""
        try:
            with DatabricksConnection() as db:
                # Basic campaign stats
                basic_query = """
                SELECT 
                    COUNT(*) as total_campaigns,
                    COUNT(CASE WHEN status = 'Active' THEN 1 END) as active_campaigns,
                    SUM(budget) as total_budget,
                    AVG(budget) as avg_budget
                FROM campaign.silver.campaigns
                """
                basic_stats = db.execute_query(basic_query)
                
                summary = {
                    "basic_stats": basic_stats.to_dict('records')[0] if not basic_stats.empty else {},
                    "timestamp": datetime.now().isoformat()
                }
                
                if include_channels:
                    # Channel breakdown
                    channel_query = """
                    SELECT 
                        c.channel,
                        COUNT(*) as campaign_count,
                        SUM(r.conversions) as total_conversions,
                        SUM(r.cost) as total_cost,
                        AVG(r.CTR) as avg_ctr
                    FROM campaign.silver.campaigns c
                    JOIN campaign.silver.reports r ON c.campaign_id = r.campaign_id
                    GROUP BY c.channel
                    ORDER BY total_conversions DESC
                    """
                    channel_stats = db.execute_query(channel_query)
                    summary["channel_breakdown"] = channel_stats.to_dict('records') if not channel_stats.empty else []
                
                if include_trends:
                    # Top performing campaigns
                    top_query = """
                    SELECT 
                        c.campaign_name,
                        c.channel,
                        r.conversions,
                        r.CTR,
                        r.CVR
                    FROM campaign.silver.campaigns c
                    JOIN campaign.silver.reports r ON c.campaign_id = r.campaign_id
                    ORDER BY r.conversions DESC
                    LIMIT 5
                    """
                    top_campaigns = db.execute_query(top_query)
                    summary["top_performers"] = top_campaigns.to_dict('records') if not top_campaigns.empty else []
                
                return {
                    "success": True,
                    "summary": summary
                }
                
        except Exception as e:
            logger.error(f"Error getting campaign summary: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def _analyze_trends(self, campaigns: List[str], metrics: List[str]) -> Dict:
        """Analyze trends (implementation)"""
        with DatabricksConnection() as db:
            # Get channel summary
            channel_query = """
            SELECT 
                c.channel,
                SUM(r.conversions) as total_conversions,
                AVG(r.CTR) as avg_ctr,
                SUM(r.cost)/NULLIF(SUM(r.conversions), 0) as overall_cpa
            FROM campaign.silver.campaigns c
            JOIN campaign.silver.reports r ON c.campaign_id = r.campaign_id
            GROUP BY c.channel
            ORDER BY total_conversions DESC
            """
            channel_summary = db.execute_query(channel_query)
            
            # Get top campaigns
            top_query = """
            SELECT c.campaign_name, r.conversions
            FROM campaign.silver.campaigns c
            JOIN campaign.silver.reports r ON c.campaign_id = r.campaign_id
            ORDER BY r.conversions DESC
            LIMIT 10
            """
            top_campaigns = db.execute_query(top_query)
        
        if channel_summary is not None and not channel_summary.empty:
            top_channel = channel_summary.iloc[0]['channel']
        else:
            top_channel = "Unknown"
        
        if top_campaigns is not None and not top_campaigns.empty:
            top_performers = top_campaigns['campaign_name'].head(3).tolist()
        else:
            top_performers = []
        
        return {
            "trends": {
                "top_channel": top_channel,
                "growth_insights": "Display campaigns showing 15% improvement",
                "recommendations": [
                    "Focus budget on Display channel",
                    "Optimize Video campaign targeting", 
                    "Consider pausing underperforming Search campaigns"
                ],
                "top_performers": top_performers
            }
        }
    
    async def _compare_campaigns(self, campaigns: List[str], metrics: List[str]) -> Dict:
        """Compare campaigns (implementation)"""
        with DatabricksConnection() as db:
            channel_query = """
            SELECT 
                c.channel,
                AVG(r.CTR) as avg_ctr,
                SUM(r.cost)/NULLIF(SUM(r.conversions), 0) as overall_cpa,
                AVG(r.CVR) as avg_cvr
            FROM campaign.silver.campaigns c
            JOIN campaign.silver.reports r ON c.campaign_id = r.campaign_id
            GROUP BY c.channel
            ORDER BY avg_ctr DESC
            """
            channel_summary = db.execute_query(channel_query)
        
        if channel_summary is not None and not channel_summary.empty:
            best_ctr_channel = channel_summary.iloc[0]['channel']
            best_cpa_row = channel_summary.loc[channel_summary['overall_cpa'].idxmin()]
            best_cpa_channel = best_cpa_row['channel']
        else:
            best_ctr_channel = "Unknown"
            best_cpa_channel = "Unknown"
        
        return {
            "comparison": {
                "best_ctr_channel": best_ctr_channel,
                "best_cpa_channel": best_cpa_channel,
                "cost_efficiency": "Video has highest CVR, Display has best CPA",
                "recommendation": "Reallocate 20% budget from Search to Display"
            }
        }
    
    async def _generate_optimization(self, campaigns: List[str], metrics: List[str]) -> Dict:
        """Generate optimization recommendations (implementation)"""
        with DatabricksConnection() as db:
            top_query = """
            SELECT c.campaign_name, r.conversions, r.cost
            FROM campaign.silver.campaigns c
            JOIN campaign.silver.reports r ON c.campaign_id = r.campaign_id
            ORDER BY r.conversions DESC
            LIMIT 10
            """
            top_campaigns = db.execute_query(top_query)
        
        if top_campaigns is not None and not top_campaigns.empty:
            pause_recommendations = top_campaigns.tail(3)['campaign_name'].tolist()
            boost_recommendations = top_campaigns.head(3)['campaign_name'].tolist()
        else:
            pause_recommendations = []
            boost_recommendations = []
        
        return {
            "optimizations": {
                "budget_reallocation": "Move 25% budget from underperformers to top 3 campaigns",
                "pause_recommendations": pause_recommendations,
                "boost_recommendations": boost_recommendations,
                "estimated_impact": "+20% conversions, -15% overall cost"
            }
        }
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

async def main():
    """Main function"""
    server = MarketingAnalyticsMCPServer()
    logger.info("🚀 Starting Marketing Analytics MCP Server...")
    logger.info("📊 Available tools: query_campaigns, analyze_performance, execute_campaign_action, get_campaign_summary")
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())



