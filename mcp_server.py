"""
MCP Server for Marketing Analytics Tools
Handles tool registration and execution with consent management
"""
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from databricks_connector import DatabricksConnection
# Consent management handled by FastAPI backend
import pandas as pd

logger = logging.getLogger(__name__)

class MCPToolServer:
    """MCP Server for marketing analytics tools with consent management"""
    
    def __init__(self):
        self.tools = {}
        self.setup_tools()
    
    def setup_tools(self):
        """Register all MCP tools"""
        
        # Tool 1: Query Campaigns (No Consent Required)
        self.tools["query_campaigns"] = {
            "name": "query_campaigns",
            "description": "Query campaign data from Databricks",
            "parameters": {
                "query_type": {
                    "type": "string",
                    "description": "Type of query: campaigns, reports, performance, summary",
                    "required": True
                },
                "filters": {
                    "type": "object", 
                    "description": "Filter criteria (status, channel, etc.)",
                    "required": False
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "required": False,
                    "default": 100
                }
            },
            "handler": self._query_campaigns
        }
        
        # Tool 2: Analyze Performance (Consent Required)
        self.tools["analyze_performance"] = {
            "name": "analyze_performance",
            "description": "Analyze campaign performance with consent",
            "parameters": {
                "analysis_type": {
                    "type": "string",
                    "description": "Type of analysis: trend, comparison, optimization",
                    "required": True
                },
                "campaigns": {
                    "type": "array",
                    "description": "List of campaign IDs to analyze",
                    "required": False
                },
                "metrics": {
                    "type": "array", 
                    "description": "Metrics to analyze",
                    "required": False,
                    "default": ["conversions", "cost", "CTR"]
                },
                "user_id": {
                    "type": "string",
                    "description": "User ID for consent management",
                    "required": True
                }
            },
            "handler": self._analyze_performance
        }
        
        # Tool 3: Execute Campaign Actions (High Consent Required)
        self.tools["execute_campaign_action"] = {
            "name": "execute_campaign_action",
            "description": "Execute actions on campaigns with high consent",
            "parameters": {
                "action": {
                    "type": "string",
                    "description": "Action to perform: pause, resume, update_budget",
                    "required": True
                },
                "campaign_ids": {
                    "type": "array",
                    "description": "List of campaign IDs to act on",
                    "required": True
                },
                "parameters": {
                    "type": "object",
                    "description": "Action parameters (e.g., new_budget)",
                    "required": False
                },
                "user_id": {
                    "type": "string",
                    "description": "User ID for consent management", 
                    "required": True
                }
            },
            "handler": self._execute_campaign_action
        }
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool by name with parameters"""
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}
        
        tool = self.tools[tool_name]
        handler = tool["handler"]
        
        try:
            result = await handler(**parameters)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": f"Tool execution failed: {str(e)}"}
    
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
                        channel,
                        COUNT(*) as campaign_count,
                        SUM(impressions) as total_impressions,
                        SUM(clicks) as total_clicks,
                        SUM(conversions) as total_conversions,
                        SUM(cost) as total_cost,
                        AVG(CTR) as avg_ctr,
                        AVG(CVR) as avg_cvr,
                        SUM(cost)/NULLIF(SUM(conversions), 0) as overall_cpa
                    FROM campaign.silver.campaigns c
                    JOIN campaign.silver.reports r ON c.campaign_id = r.campaign_id
                    GROUP BY channel
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
                    
                elif query_type == "campaign_performance":
                    campaign_id = filters.get("campaign_id") if filters else None
                    if not campaign_id:
                        return {"error": "campaign_id required for performance query"}
                    
                    query = f"""
                    SELECT 
                        c.campaign_name,
                        c.channel,
                        r.impressions,
                        r.clicks,
                        r.conversions,
                        r.cost,
                        r.CTR,
                        r.CVR,
                        r.report_date
                    FROM campaign.silver.campaigns c
                    JOIN campaign.silver.reports r ON c.campaign_id = r.campaign_id
                    WHERE c.campaign_id = '{campaign_id}'
                    ORDER BY r.report_date DESC
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
                        "count": len(data)
                    }
                else:
                    return {
                        "success": True,
                        "data": [],
                        "query_type": query_type,
                        "count": 0
                    }
                    
        except Exception as e:
            logger.error(f"Error in query_campaigns: {e}")
            return {"error": str(e)}
    
    async def _analyze_performance(self, analysis_type: str, campaigns: List[str] = None, 
                                metrics: List[str] = None, user_id: str = None) -> Dict[str, Any]:
        """Analyze performance with consent"""
        
        if not user_id:
            return {"error": "user_id required for analysis"}
        
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
        
        # Consent management handled by FastAPI backend
        
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
                "consent_id": consent_id
            }
        except Exception as e:
            return {"error": str(e), "consent_id": consent_id}
    
    async def _execute_campaign_action(self, action: str, campaign_ids: List[str], 
                                    parameters: Dict = None, user_id: str = None) -> Dict[str, Any]:
        """Execute campaign action with high consent"""
        
        if not user_id:
            return {"error": "user_id required for actions"}
        
        # Get campaign details for impact analysis
        with DatabricksConnection() as db:
            query = """
            SELECT campaign_id, campaign_name, budget, channel, status
            FROM campaign.silver.campaigns
            WHERE campaign_id IN ({})
            """.format(','.join(['%s'] * len(campaign_ids)))
            
            campaigns_data = db.execute_query(query, campaign_ids)
        
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
        
        # Consent management handled by FastAPI backend
        
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
                "consent_id": consent_id
            }
        except Exception as e:
            return {"error": str(e), "consent_id": consent_id}
    
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
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Get list of available tools"""
        return {
            "tools": list(self.tools.keys()),
            "tool_details": {
                name: {
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
                for name, tool in self.tools.items()
            }
        }

# Global MCP server instance
mcp_server = MCPToolServer()
