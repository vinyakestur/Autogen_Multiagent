"""
FastAPI Backend with MCP Integration
Main API server for the marketing analytics system
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import logging

# Import our MCP components
from mcp_client import mcp_client
from data_agent_mcp import mcp_data_agent
from conversational_agent import conversational_agent
from intent_classifier import classify_user_intent

logger = logging.getLogger(__name__)

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent: str
    consent_required: bool = False
    consent_id: Optional[str] = None
    tool_results: Optional[List[Dict[str, Any]]] = None

class ConsentRequest(BaseModel):
    consent_id: str
    approved: bool

class ConsentResponse(BaseModel):
    response: str
    agent: str
    consent_approved: bool
    data: Optional[Dict[str, Any]] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect MCP client
    print("🚀 Starting FastAPI with MCP integration...")
    await mcp_client.connect()
    print("✅ MCP client connected")
    
    yield
    
    # Shutdown: Disconnect MCP client
    print("🔌 Disconnecting MCP client...")
    await mcp_client.disconnect()

# Create FastAPI app
app = FastAPI(
    title="Marketing Analytics API with MCP",
    description="AI-powered marketing analytics using MCP protocol",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "Marketing Analytics API with MCP",
        "mcp_status": "connected" if mcp_client.connected else "disconnected",
        "version": "2.0.0",
        "available_tools": await mcp_client.get_available_tools()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mcp_connected": mcp_client.connected
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with MCP integration"""
    
    try:
        logger.info(f"Processing chat request: {request.message}")
        
        # Classify intent
        intent_result = classify_user_intent(request.message)
        intent = intent_result["agent"]
        confidence = intent_result["confidence"]
        
        logger.info(f"Intent classified: {intent} (confidence: {confidence})")
        
        if intent == "conversational":
            # No consent needed - pure LLM response
            response_dict = await conversational_agent.respond(request.message)
            return ChatResponse(
                response=response_dict["response"],
                agent="conversational",
                consent_required=False
            )
        
        elif intent == "data":
            # Consent required - return consent request first
            from intent_classifier import get_consent_info
            consent_info = get_consent_info(request.message)
            
            # Create a consent ID for tracking
            import uuid
            consent_id = str(uuid.uuid4())
            
            # Store the query for later execution
            if not hasattr(app.state, 'pending_consents'):
                app.state.pending_consents = {}
            app.state.pending_consents[consent_id] = {
                "query": request.message,
                "user_id": request.user_id,
                "consent_info": consent_info
            }
            
            return ChatResponse(
                response=f"This query requires access to your campaign data.\n\nAction: {consent_info['action_description']}\nTools: {', '.join(consent_info['tools_required'])}\nData Access: {', '.join(consent_info['data_access'])}\nImpact: {consent_info['impact_analysis']}\n\nPlease approve to continue.",
                agent="data",
                consent_required=True,
                consent_id=consent_id
            )
        
        else:
            return ChatResponse(
                response="I'm not sure how to help with that. Could you please rephrase your question?",
                agent="conversational",
                consent_required=False
            )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.post("/consent", response_model=ConsentResponse)
async def consent_endpoint(request: ConsentRequest):
    """Handle consent approval/denial"""
    
    try:
        # Get the pending consent data
        if not hasattr(app.state, 'pending_consents') or request.consent_id not in app.state.pending_consents:
            raise HTTPException(status_code=404, detail="Consent request not found")
        
        consent_data = app.state.pending_consents[request.consent_id]
        
        if request.approved:
            # Execute the actual query using MCP data agent
            result = await mcp_data_agent.process_query(
                user_query=consent_data["query"],
                user_id=consent_data["user_id"]
            )
            
            # Clean up the pending consent
            del app.state.pending_consents[request.consent_id]
            
            return ConsentResponse(
                response=result["response"],
                agent=result["agent"],
                consent_approved=True,
                data={"tool_results": result.get("tool_results")}
            )
        else:
            # Clean up the pending consent
            del app.state.pending_consents[request.consent_id]
            
            return ConsentResponse(
                response="Consent denied. I can still help you with general marketing questions.",
                agent="conversational",
                consent_approved=False
            )
    
    except Exception as e:
        logger.error(f"Error in consent endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Consent processing failed: {str(e)}")

@app.get("/tools")
async def get_available_tools():
    """Get available MCP tools"""
    try:
        tools = await mcp_client.get_available_tools()
        return tools
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tools: {str(e)}")

@app.post("/tools/query_campaigns")
async def query_campaigns_tool(
    query_type: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100
):
    """Direct tool endpoint for querying campaigns"""
    try:
        result = await mcp_client.query_campaigns(query_type, filters, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

@app.post("/tools/analyze_performance")
async def analyze_performance_tool(
    analysis_type: str,
    campaigns: Optional[List[str]] = None,
    metrics: Optional[List[str]] = None,
    user_id: str = None
):
    """Direct tool endpoint for performance analysis"""
    try:
        result = await mcp_client.analyze_performance(analysis_type, campaigns, metrics, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



