"""
FastAPI Backend with Direct Databricks Integration
Simplified backend using direct API calls instead of MCP
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import uuid
from datetime import datetime

# Import our direct components
from databricks_connector import DatabricksConnection
from example_queries import DatabricksQueries
from intent_classifier import classify_user_intent
from sql_generator import SQLGenerator
from sql_logger import SQLLogger
from chart_generator import ChartGenerator

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
    data: Optional[List[Dict[str, Any]]] = None
    sql_query: Optional[str] = None
    query_type: Optional[str] = None
    charts: Optional[List[Dict[str, Any]]] = None

class ConsentRequest(BaseModel):
    consent_id: str
    approved: bool

class ConsentResponse(BaseModel):
    response: str
    agent: str
    consent_approved: bool
    data: Optional[List[Dict[str, Any]]] = None
    sql_query: Optional[str] = None
    query_type: Optional[str] = None
    charts: Optional[List[Dict[str, Any]]] = None

# Initialize FastAPI app
app = FastAPI(
    title="Marketing Analytics Platform API",
    description="Direct API integration for Databricks data analysis",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for consent requests
consent_requests = {}

# Initialize query system
query_system = DatabricksQueries()

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Marketing Analytics Platform API",
        "version": "2.0.0",
        "status": "healthy",
        "features": ["Direct API", "Smart Queries", "Charts", "Consent Management"],
        "endpoints": {
            "chat": "/chat",
            "consent": "/consent", 
            "health": "/health",
            "tools": "/tools"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Databricks connection
        with DatabricksConnection() as db:
            test_result = db.execute_query("SELECT 1 as test")
        
        return {
            "status": "healthy",
            "integration": "Direct Databricks API",
            "features": "Smart Queries + Charts + Consent",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/tools")
async def get_available_tools():
    """Get available analysis tools"""
    return {
        "tools": [
            {
                "name": "query_campaigns",
                "description": "Query campaign data with filters",
                "requires_consent": False
            },
            {
                "name": "analyze_performance", 
                "description": "Analyze campaign performance metrics",
                "requires_consent": True
            },
            {
                "name": "budget_analysis",
                "description": "Analyze budget allocation and spending",
                "requires_consent": True
            },
            {
                "name": "trend_analysis",
                "description": "Analyze performance trends over time",
                "requires_consent": True
            }
        ]
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with direct API processing"""
    try:
        user_message = request.message.strip()
        user_id = request.user_id
        
        # Classify user intent
        intent = classify_user_intent(user_message)
        
        if intent == "conversational":
            # Handle conversational queries without data access
            response = handle_conversational_query(user_message)
            return ChatResponse(
                response=response,
                agent="conversational",
                consent_required=False
            )
        
        elif intent == "data_query":
            # Handle data queries with consent management
            return await handle_data_query(user_message, user_id)
        
        else:
            # Default to conversational
            response = handle_conversational_query(user_message)
            return ChatResponse(
                response=response,
                agent="conversational",
                consent_required=False
            )
            
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def handle_conversational_query(message: str) -> str:
    """Handle conversational queries without data access"""
    message_lower = message.lower()
    
    if "ctr" in message_lower:
        return """CTR stands for Click-Through Rate, which is a key digital marketing metric that measures the percentage of people who click on your ad after seeing it.

**Formula:** CTR = (Clicks ÷ Impressions) × 100

**Industry Benchmarks:**
- Search Ads: 1.91% average
- Display Ads: 0.35% average  
- Social Media: 0.9% average

**How to Improve CTR:**
- Write compelling ad copy
- Use relevant keywords
- A/B test different headlines
- Target the right audience
- Use eye-catching visuals"""
    
    elif "cpc" in message_lower or "cost per click" in message_lower:
        return """CPC (Cost Per Click) is the amount you pay each time someone clicks on your ad.

**Industry Benchmarks:**
- Search: $1-2 average
- Display: $0.50-1 average
- Social: $0.50-1.50 average

**Factors Affecting CPC:**
- Keyword competition
- Ad quality score
- Targeting specificity
- Industry competition
- Time of day/day of week

**Tips to Lower CPC:**
- Improve ad relevance
- Use long-tail keywords
- Optimize landing pages
- Improve quality scores"""
    
    elif "optimize" in message_lower or "improve" in message_lower:
        return """Here are proven strategies to improve your campaign performance:

**1. Keyword Optimization**
- Use negative keywords to exclude irrelevant traffic
- Focus on long-tail keywords
- Regular keyword research and updates

**2. Ad Copy Testing**
- A/B test headlines and descriptions
- Use emotional triggers
- Include clear calls-to-action

**3. Landing Page Optimization**
- Match ad copy to landing page content
- Improve page load speed
- Optimize for mobile devices

**4. Audience Targeting**
- Use demographic targeting
- Implement remarketing campaigns
- Create lookalike audiences

**5. Budget Management**
- Allocate budget to top-performing campaigns
- Use bid strategies (target CPA, target ROAS)
- Monitor and adjust daily

Would you like me to analyze your actual campaign data to provide specific recommendations?"""
    
    else:
        return f"""I'm here to help you analyze your marketing data! 

I can help you with:
- Campaign performance analysis
- Budget allocation insights  
- Trend analysis over time
- Channel performance comparison
- ROI and conversion metrics

Just ask me questions like:
- "Show me my top performing campaigns"
- "Analyze my budget allocation"
- "What are my conversion trends?"
- "Compare Display vs Search performance"

What would you like to know about your marketing data?"""

async def handle_data_query(message: str, user_id: str) -> ChatResponse:
    """Handle data queries with consent management"""
    try:
        # Find matching query type
        query_type = query_system.find_matching_query(message)
        
        if query_type:
            # Generate consent request
            consent_id = str(uuid.uuid4())
            
            # Store consent request
            consent_requests[consent_id] = {
                "user_id": user_id,
                "query": message,
                "query_type": query_type,
                "timestamp": datetime.now(),
                "status": "pending"
            }
            
            # Generate consent details
            consent_details = generate_consent_details(query_type, message)
            
            return ChatResponse(
                response=f"""I found a matching analysis for your request: "{message}"

**Action:** {consent_details['action']}
**Tools Required:** {', '.join(consent_details['tools'])}
**Data Access:** {', '.join(consent_details['data_access'])}
**Impact:** {consent_details['impact']}

Please approve this data access request to continue with the analysis.""",
                agent="data_analyst",
                consent_required=True,
                consent_id=consent_id
            )
        else:
            # No predefined query found - use AI to generate custom query
            query_type = "custom"
            consent_id = str(uuid.uuid4())
            
            # Store consent request for custom query
            consent_requests[consent_id] = {
                "user_id": user_id,
                "query": message,
                "query_type": query_type,
                "timestamp": datetime.now(),
                "status": "pending"
            }
            
            # Generate consent details for custom query
            consent_details = generate_consent_details(query_type, message)
            
            return ChatResponse(
                response=f"""I understand you want to analyze: "{message}"

I'll generate a custom SQL query to answer your specific question.

**Action:** {consent_details['action']}
**Tools Required:** {', '.join(consent_details['tools'])}
**Data Access:** {', '.join(consent_details['data_access'])}
**Impact:** {consent_details['impact']}

Please approve this data access request to continue with the custom analysis.""",
                agent="data_analyst",
                consent_required=True,
                consent_id=consent_id
            )
            
    except Exception as e:
        logger.error(f"Error handling data query: {e}")
        return ChatResponse(
            response="I encountered an error processing your request. Please try again.",
            agent="error",
            consent_required=False
        )

def generate_consent_details(query_type: str, message: str) -> Dict[str, Any]:
    """Generate consent details based on query type"""
    consent_templates = {
        'campaigns': {
            'action': 'Query campaign data from Databricks',
            'tools': ['databricks_query', 'campaign_analyzer'],
            'data_access': ['campaign data', 'campaign metadata'],
            'impact': 'This will retrieve and display your campaign information for analysis.'
        },
        'performance': {
            'action': 'Analyze campaign performance metrics',
            'tools': ['performance_analyzer', 'metrics_calculator'],
            'data_access': ['campaign data', 'reports data', 'performance metrics'],
            'impact': 'This will analyze your campaign performance and generate insights.'
        },
        'budget': {
            'action': 'Analyze budget allocation and spending',
            'tools': ['budget_analyzer', 'financial_calculator'],
            'data_access': ['campaign data', 'budget information', 'spending data'],
            'impact': 'This will analyze your budget allocation and provide spending insights.'
        },
        'trends': {
            'action': 'Analyze performance trends over time',
            'tools': ['trend_analyzer', 'time_series_calculator'],
            'data_access': ['reports data', 'historical data', 'time series data'],
            'impact': 'This will analyze trends in your campaign performance over time.'
        }
    }
    
    return consent_templates.get(query_type, {
        'action': 'Query your marketing data',
        'tools': ['databricks_query', 'data_analyzer'],
        'data_access': ['marketing data'],
        'impact': 'This will query your marketing data for analysis.'
    })

@app.post("/consent", response_model=ConsentResponse)
async def handle_consent(request: ConsentRequest):
    """Handle consent approval/denial"""
    try:
        consent_id = request.consent_id
        approved = request.approved
        
        if consent_id not in consent_requests:
            raise HTTPException(status_code=404, detail="Consent request not found")
        
        consent_request = consent_requests[consent_id]
        
        if approved:
            # Execute the query
            try:
                result = await execute_data_query(
                    consent_request['query'],
                    consent_request['query_type'],
                    session_id=consent_request.get('user_id', 'default')
                )
                
                # Update consent status
                consent_requests[consent_id]['status'] = 'approved'
                
                return ConsentResponse(
                    response=f"✅ Analysis completed! Here are your results:\n\n{result['summary']}",
                    agent="data_analyst",
                    consent_approved=True,
                    data=result.get('data'),
                    sql_query=result.get('sql_query'),
                    query_type=result.get('query_type'),
                    charts=result.get('charts')
                )
                
            except Exception as e:
                logger.error(f"Error executing approved query: {e}")
                return ConsentResponse(
                    response=f"❌ Error executing your request: {str(e)}",
                    agent="error",
                    consent_approved=False
                )
        else:
            # Consent denied
            consent_requests[consent_id]['status'] = 'denied'
            return ConsentResponse(
                response="❌ Data access denied. Your data remains protected. You can ask other questions that don't require data access.",
                agent="data_analyst",
                consent_approved=False
            )
            
    except Exception as e:
        logger.error(f"Error handling consent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def execute_data_query(query: str, query_type: str, session_id: str = None) -> Dict[str, Any]:
    """Execute data query and return results with hybrid system"""
    try:
        with DatabricksConnection() as db:
            # Generate and execute query using hybrid system
            sql_query = query_system.generate_dynamic_query(query, query_type)
            data_df = db.execute_query(sql_query)
            
            # Convert DataFrame to list of dictionaries for frontend
            if data_df is not None and not data_df.empty:
                data = data_df.to_dict('records')
            else:
                data = []
            
            # Generate charts using auto-detection (with error handling)
            charts = []
            try:
                chart_generator = ChartGenerator()
                charts = chart_generator.generate_charts(data, query_type)
                # Ensure all charts are JSON serializable
                for chart in charts:
                    if 'figure_json' not in chart:
                        charts = []  # If any chart is not properly serialized, disable all
                        break
            except Exception as e:
                logger.error(f"Error generating charts: {e}")
                charts = []  # Fallback to empty charts
            
            # Generate summary
            summary = generate_analysis_summary(query_type, data)
            
            # Log the query if session_id is provided
            if session_id:
                sql_logger = SQLLogger()
                query_info = {
                    'user_query': query,
                    'sql_query': sql_query,
                    'query_type': query_type,
                    'generated_by': 'predefined' if query_type in ['campaigns', 'performance', 'budget', 'trends', 'summary'] else 'ai_generated',
                    'explanation': f"Query executed for {query_type} analysis",
                    'execution_time': 0,  # Could add timing if needed
                    'rows_returned': len(data),
                    'success': True
                }
                sql_logger.log_query(session_id, query_info)
            
            return {
                'summary': summary,
                'data': data,
                'query_type': query_type,
                'sql_query': sql_query,
                'charts': charts,
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error executing data query: {e}")
        raise e

def generate_analysis_summary(query_type: str, data: List[Dict]) -> str:
    """Generate human-readable summary of analysis results"""
    if not data:
        return "No data found for your query."
    
    if query_type == 'campaigns':
        return f"Found {len(data)} campaigns. Here are the key details from your campaign data."
    
    elif query_type == 'performance':
        return f"Performance analysis complete. Analyzed {len(data)} campaign performance records with detailed metrics."
    
    elif query_type == 'budget':
        total_budget = sum(row.get('total_budget', 0) for row in data if isinstance(row.get('total_budget'), (int, float)))
        return f"Budget analysis complete. Total budget analyzed: ${total_budget:,.2f} across {len(data)} categories."
    
    elif query_type == 'trends':
        return f"Trend analysis complete. Analyzed {len(data)} time periods showing performance trends over time."
    
    elif query_type == 'summary':
        if len(data) >= 2:
            campaigns_data = data[0] if data[0]['data_type'] == 'Campaigns' else data[1]
            reports_data = data[1] if data[1]['data_type'] == 'Reports' else data[0]
            
            return f"""📊 **Marketing Data Summary**
            
**Campaigns Overview:**
• Total Campaigns: {campaigns_data['total_count']}
• Active: {campaigns_data['active_count']} | Completed: {campaigns_data['completed_count']} | Paused: {campaigns_data['paused_count']}
• Total Budget: ${campaigns_data['total_budget']:,.2f} | Average Budget: ${campaigns_data['avg_budget']:,.2f}
• Channels: {campaigns_data['channel_count']} different channels

**Performance Overview:**
• Total Reports: {reports_data['total_count']}
• Average CTR: {reports_data['avg_budget']:.2f}% | Average CVR: {reports_data['total_budget']:.2f}%
• Campaigns with Data: {reports_data['channel_count']}

This gives you a comprehensive overview of your marketing data performance."""
        else:
            return f"Summary analysis complete. Retrieved {len(data)} summary records of your marketing data."
    
    else:
        return f"Analysis complete. Retrieved {len(data)} records of data for your query."

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Direct Databricks Analysis API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
