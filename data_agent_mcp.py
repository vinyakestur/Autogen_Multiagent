"""
Data Agent with MCP Integration
Uses MCP protocol for tool communication with consent management
"""
import json
import logging
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from config import ANTHROPIC_CONFIG
from mcp_client import mcp_client

logger = logging.getLogger(__name__)

class DataAgentWithMCP:
    """Data Agent using MCP protocol for tool communication"""
    
    def __init__(self):
        self.llm = ChatAnthropic(
            anthropic_api_key=ANTHROPIC_CONFIG["api_key"],
            model_name=ANTHROPIC_CONFIG["model"],
            temperature=0.1
        )
        
        self.system_prompt = """You are a marketing analytics expert with access to campaign data tools via MCP protocol.

Available MCP tools:
1. query_campaigns - Query campaign data (no consent needed)
   - query_type: campaigns, reports, performance, summary
   - filters: status, channel, etc.
   - limit: max results

2. analyze_performance - Analyze performance data (consent required)
   - analysis_type: trend, comparison, optimization
   - campaigns: list of campaign IDs
   - metrics: conversions, cost, CTR, etc.

3. execute_campaign_action - Execute actions (high consent required)
   - action: pause, resume, update_budget
   - campaign_ids: list of campaign IDs
   - parameters: action-specific params

Guidelines:
1. Always provide specific numbers and insights from actual data
2. Include actionable recommendations
3. Be transparent about data access and consent requirements
4. Handle consent requests gracefully
5. Provide clear explanations of what the data means"""

    async def process_query(self, user_query: str, user_id: str) -> Dict[str, Any]:
        """Process user query using LLM + MCP tools"""
        
        try:
            # Step 1: LLM determines what tools to use
            tool_plan = await self._plan_tools(user_query)
            
            # Step 2: Execute tools via MCP
            tool_results = []
            for tool_call in tool_plan["tool_calls"]:
                result = await self._execute_tool_via_mcp(tool_call, user_id)
                tool_results.append(result)
            
            # Step 3: LLM synthesizes final response
            final_response = await self._synthesize_response(user_query, tool_results)
            
            return {
                "response": final_response,
                "agent": "data_mcp",
                "consent_required": any("consent" in str(result) for result in tool_results),
                "tool_results": tool_results
            }
            
        except Exception as e:
            logger.error(f"Error in MCP data agent: {e}")
            return {
                "response": f"I encountered an error processing your request: {str(e)}",
                "agent": "data_mcp",
                "consent_required": False,
                "error": str(e)
            }
    
    async def _plan_tools(self, user_query: str) -> Dict[str, Any]:
        """LLM determines which tools to use"""
        
        planning_prompt = f"""
        Based on the user query, determine which MCP tools to call.

        Available tools:
        1. query_campaigns - Query campaign data (no consent needed)
           - query_type: campaigns, campaign_performance, top_performing, channel_summary
           - filters: {{"status": "Active", "channel": "Display", "metric": "conversions"}}
           - limit: 100
           
        IMPORTANT: 
        - Use "top_performing" for general performance queries
        - Use "campaigns" to list campaigns
        - Use "campaign_performance" ONLY when you have a specific campaign_id
        - Use "channel_summary" for channel-level analysis

        2. analyze_performance - Analyze performance data (consent required)
           - analysis_type: trend, comparison, optimization
           - campaigns: ["campaign_id1", "campaign_id2"]
           - metrics: ["conversions", "cost", "CTR", "CVR"]

        3. execute_campaign_action - Execute actions (high consent required)
           - action: pause, resume, update_budget
           - campaign_ids: ["campaign_id1", "campaign_id2"]
           - parameters: {{"new_budget": 5000}}

        Return a JSON with tool_calls array containing tool_name and parameters.
        
        Examples:
        User: "Show me my Display campaigns"
        Response: {{
          "tool_calls": [{{
            "tool_name": "query_campaigns",
            "parameters": {{
              "query_type": "campaigns",
              "filters": {{"channel": "Display"}},
              "limit": 50
            }}
          }}]
        }}
        
        User: "Show me my campaign performance"
        Response: {{
          "tool_calls": [{{
            "tool_name": "query_campaigns",
            "parameters": {{
              "query_type": "top_performing",
              "filters": {{"metric": "conversions"}},
              "limit": 50
            }}
          }}]
        }}
        
        User: "Analyze my campaign trends"
        Response: {{
          "tool_calls": [{{
            "tool_name": "analyze_performance", 
            "parameters": {{
              "analysis_type": "trend",
              "metrics": ["conversions", "cost", "CTR"]
            }}
          }}]
        }}
        
        User: "Show me my top performing campaigns"
        Response: {{
          "tool_calls": [{{
            "tool_name": "query_campaigns",
            "parameters": {{
              "query_type": "top_performing",
              "filters": {{"metric": "conversions"}},
              "limit": 10
            }}
          }}]
        }}
        
        User query: "{user_query}"
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a tool planning expert. Return only valid JSON."),
                HumanMessage(content=planning_prompt)
            ])
            
            # Clean up the response
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error in tool planning: {e}")
            # Fallback: simple query for campaigns
            return {
                "tool_calls": [{
                    "tool_name": "query_campaigns",
                    "parameters": {
                        "query_type": "campaigns",
                        "limit": 50
                    }
                }]
            }
    
    async def _execute_tool_via_mcp(self, tool_call: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute tool via MCP protocol"""
        
        tool_name = tool_call["tool_name"]
        parameters = tool_call["parameters"]
        
        # Add user_id for consent-requiring tools
        if tool_name in ["analyze_performance", "execute_campaign_action"]:
            parameters["user_id"] = user_id
        
        # Call tool via MCP
        try:
            if tool_name == "query_campaigns":
                result = await mcp_client.query_campaigns(**parameters)
            elif tool_name == "analyze_performance":
                result = await mcp_client.analyze_performance(**parameters)
            elif tool_name == "execute_campaign_action":
                result = await mcp_client.execute_action(**parameters)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            return {
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result
            }
        except Exception as e:
            return {
                "tool_name": tool_name,
                "parameters": parameters,
                "result": {"error": f"Tool execution failed: {str(e)}"}
            }
    
    async def _synthesize_response(self, user_query: str, tool_results: List[Dict]) -> str:
        """LLM synthesizes final response from tool results"""
        
        context = f"User Query: {user_query}\n\nTool Results:\n"
        for i, result in enumerate(tool_results):
            context += f"\nTool {i+1} ({result['tool_name']}):\n"
            context += json.dumps(result['result'], indent=2)
        
        synthesis_prompt = f"""
        Based on the user query and tool results, provide a helpful, conversational response.

        Guidelines:
        - If tools returned data, summarize key insights with specific numbers
        - If consent was required, explain what was analyzed
        - If actions were taken, confirm what happened
        - If errors occurred, explain them clearly
        - Be concise but informative
        - Use bullet points for lists
        - Include specific metrics and recommendations
        - Make it conversational and actionable

        User Question: {user_query}
        
        Tool Results:
        {context}
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=synthesis_prompt)
            ])
            return response.content
        except Exception as e:
            logger.error(f"Error in response synthesis: {e}")
            return f"I analyzed your request but encountered an error generating the response: {str(e)}"

# Global MCP data agent
mcp_data_agent = DataAgentWithMCP()



