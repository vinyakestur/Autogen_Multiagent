"""
MCP Client Manager for Marketing Analytics
Handles communication with MCP server tools
"""
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from mcp_server import mcp_server

logger = logging.getLogger(__name__)

class MCPClientManager:
    """MCP Client Manager for tool communication"""
    
    def __init__(self):
        self.connected = True  # Direct connection to local server
        self.server = mcp_server
    
    async def connect(self):
        """Connect to MCP server (simulated for local server)"""
        try:
            self.connected = True
            logger.info("✅ Connected to MCP server")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to MCP server: {e}")
            return False
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool via MCP protocol"""
        if not self.connected:
            await self.connect()
        
        try:
            result = await self.server.call_tool(tool_name, parameters)
            return result
        except Exception as e:
            logger.error(f"Tool call failed for {tool_name}: {e}")
            return {"error": f"Tool call failed: {e}"}
    
    async def query_campaigns(self, query_type: str, filters: Dict = None, limit: int = 100) -> Dict:
        """Query campaigns via MCP"""
        return await self.call_tool("query_campaigns", {
            "query_type": query_type,
            "filters": filters or {},
            "limit": limit
        })
    
    async def analyze_performance(self, analysis_type: str, campaigns: List[str] = None, 
                                metrics: List[str] = None, user_id: str = None) -> Dict:
        """Analyze performance via MCP"""
        return await self.call_tool("analyze_performance", {
            "analysis_type": analysis_type,
            "campaigns": campaigns or [],
            "metrics": metrics or ["conversions", "cost", "CTR"],
            "user_id": user_id
        })
    
    async def execute_action(self, action: str, campaign_ids: List[str], 
                           parameters: Dict = None, user_id: str = None) -> Dict:
        """Execute campaign action via MCP"""
        return await self.call_tool("execute_campaign_action", {
            "action": action,
            "campaign_ids": campaign_ids,
            "parameters": parameters or {},
            "user_id": user_id
        })
    
    async def get_available_tools(self) -> Dict[str, Any]:
        """Get available tools from MCP server"""
        return self.server.get_available_tools()
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.connected:
            self.connected = False
            logger.info("🔌 Disconnected from MCP server")

# Global MCP client
mcp_client = MCPClientManager()



