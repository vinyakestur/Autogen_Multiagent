"""
Streamlit App with MCP Integration
Updated frontend that can work with both original and MCP systems
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import json
import asyncio
import requests
import logging
from databricks_connector import DatabricksConnection
from example_queries import DatabricksQueries

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Marketing Analytics Chatbot with MCP",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .consent-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .mcp-status {
        padding: 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
        text-align: center;
    }
    .mcp-connected {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .mcp-disconnected {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'show_data' not in st.session_state:
        st.session_state.show_data = None
    if 'use_mcp_system' not in st.session_state:
        st.session_state.use_mcp_system = True
    if 'pending_consent' not in st.session_state:
        st.session_state.pending_consent = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "default_user"
    if 'mcp_backend_url' not in st.session_state:
        st.session_state.mcp_backend_url = "http://localhost:8000"

def load_data():
    """Load sample data for display"""
    try:
        with DatabricksConnection() as db:
            campaigns = db.execute_query("SELECT * FROM campaign.silver.campaigns LIMIT 10")
            reports = db.execute_query("SELECT * FROM campaign.silver.reports LIMIT 10")
            return campaigns, reports
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

def display_chat_message(content, is_user=False):
    """Display a chat message"""
    if is_user:
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong> {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>Bot:</strong> {content}
        </div>
        """, unsafe_allow_html=True)

async def process_question_with_mcp_system(question):
    """Process user question using MCP system via FastAPI backend"""
    try:
        logger.info(f"Processing query with MCP system: {question}")
        
        # Call FastAPI backend
        response = requests.post(
            f"{st.session_state.mcp_backend_url}/chat",
            json={
                "message": question,
                "user_id": st.session_state.user_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result["response"]
            agent = result.get("agent", "unknown")
            consent_required = result.get("consent_required", False)
            
            # Handle consent requests
            if consent_required and result.get("consent_id"):
                # Extract consent info from response
                st.session_state.pending_consent = {
                    "consent_id": result["consent_id"],
                    "consent_details": result,
                    "original_query": question
                }
            elif consent_required and result.get("tool_results"):
                # Fallback: Extract consent info from tool results (old format)
                for tool_result in result["tool_results"]:
                    if "consent_id" in tool_result.get("result", {}):
                        st.session_state.pending_consent = {
                            "consent_id": tool_result["result"]["consent_id"],
                            "consent_details": tool_result.get("result", {}),
                            "original_query": question
                        }
                        break
            
            show_data = None
            if result.get("tool_results"):
                # Check if any tool returned data
                for tool_result in result["tool_results"]:
                    tool_data = tool_result.get("result", {})
                    if tool_data.get("success") and tool_data.get("data"):
                        show_data = {
                            "type": "mcp_data",
                            "data": tool_data["data"],
                            "tool_name": tool_result["tool_name"],
                            "agent": agent
                        }
                        break
            
            return response_text, show_data, agent, consent_required
        else:
            error_msg = f"Backend error: {response.status_code}"
            return error_msg, None, "error", False
            
    except Exception as e:
        logger.error(f"Error in MCP system processing: {e}")
        return f"I encountered an error processing your request: {str(e)}", None, "error", False

def process_question_with_data(question):
    """Process user question and generate response with data display info"""
    if st.session_state.use_mcp_system:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response, show_data, agent, consent_required = loop.run_until_complete(
                process_question_with_mcp_system(question)
            )
            loop.close()
            return response, show_data
        except Exception as e:
            logger.error(f"MCP system failed: {e}")
            st.session_state.use_mcp_system = False  # Fallback if system fails
            st.error(f"MCP system unavailable: {e}. Falling back to simple mode.")
    
    # Fallback to simple processing
    try:
        with DatabricksConnection() as db:
            queries = DatabricksQueries(db)
            response, data = queries.process_question(question)
            
            if data is not None and not data.empty:
                show_data = {
                    "type": "simple_data",
                    "data": data,
                    "query": question,
                    "agent": "simple"
                }
            else:
                show_data = None
            
            return response, show_data
    except Exception as e:
        logger.error(f"Error in simple processing: {e}")
        return f"I encountered an error: {str(e)}", None

def check_mcp_backend_status():
    """Check if MCP backend is running"""
    try:
        response = requests.get(f"{st.session_state.mcp_backend_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Marketing Analytics Chatbot with MCP</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Configuration")
        
        # MCP Backend URL
        mcp_url = st.text_input(
            "MCP Backend URL",
            value=st.session_state.mcp_backend_url,
            help="URL of the FastAPI backend with MCP integration"
        )
        if mcp_url != st.session_state.mcp_backend_url:
            st.session_state.mcp_backend_url = mcp_url
            st.rerun()
        
        # System Mode Toggle
        use_mcp = st.toggle(
            "Use MCP System",
            value=st.session_state.use_mcp_system,
            help="Enable MCP protocol for advanced tool integration"
        )
        if use_mcp != st.session_state.use_mcp_system:
            st.session_state.use_mcp_system = use_mcp
            st.rerun()
        
        # MCP Status
        if st.session_state.use_mcp_system:
            mcp_status = check_mcp_backend_status()
            if mcp_status:
                st.markdown('<div class="mcp-status mcp-connected">✅ MCP Backend Connected</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="mcp-status mcp-disconnected">❌ MCP Backend Disconnected</div>', unsafe_allow_html=True)
                st.warning("MCP backend is not running. Please start it with: `python fastapi_backend.py`")
        
        # User ID
        user_id = st.text_input("User ID", value=st.session_state.user_id)
        if user_id != st.session_state.user_id:
            st.session_state.user_id = user_id
            st.rerun()
        
        # Clear Chat
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.session_state.show_data = None
            st.session_state.pending_consent = None
            st.rerun()
        
        # Data Preview
        if st.checkbox("📊 Show Sample Data"):
            campaigns_data, reports_data = load_data()
            if campaigns_data is not None:
                st.subheader("Campaign Data")
                st.dataframe(campaigns_data.head())
            if reports_data is not None:
                st.subheader("Reports Data")
                st.dataframe(reports_data.head())
        
        # Pending Consent
        if st.session_state.pending_consent:
            st.header("⚠️ Pending Consent")
            st.warning("You have a pending data access request. Please respond below.")
    
    # Main chat interface
    st.subheader("💬 Chat Interface")
    
    # Display chat messages
    for message in st.session_state.messages:
        display_chat_message(message["content"], message["is_user"])
    
    # Display data tables if requested
    if hasattr(st.session_state, 'show_data') and st.session_state.show_data:
        st.subheader("📊 Data Results")
        data_info = st.session_state.show_data
        
        if data_info["type"] in ["simple_data", "mcp_data"]:
            if isinstance(data_info["data"], list):
                # Convert list of dicts to DataFrame
                df = pd.DataFrame(data_info["data"])
            else:
                df = data_info["data"]
            
            st.dataframe(df)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"marketing_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # Show metadata
            with st.expander("🔍 Data Metadata"):
                st.write(f"**Agent:** {data_info['agent']}")
                st.write(f"**Tool:** {data_info.get('tool_name', 'N/A')}")
                st.write(f"**Rows:** {len(df)}")
                st.write(f"**Columns:** {list(df.columns)}")
    
    # Handle pending consent requests
    if st.session_state.pending_consent:
        st.markdown("---")
        st.subheader("🔐 Data Access Consent Required")
        consent_info = st.session_state.pending_consent
        consent_details = consent_info["consent_details"]
        
        st.info(f"**Query:** {consent_info['original_query']}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Action:**")
            st.write(consent_details.get("action_description", "Access your campaign data"))
            st.write("**Tools Required:**")
            for tool in consent_details.get("tools_required", []):
                st.write(f"• {tool}")
        with col2:
            st.write("**Data Access:**")
            for data_type in consent_details.get("data_access", []):
                st.write(f"• {data_type}")
            st.write("**Impact:**")
            st.write(consent_details.get("impact_analysis", "This will query your campaign data for analysis."))
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("✅ Approve", type="primary"):
                try:
                    # Call consent endpoint
                    response = requests.post(
                        f"{st.session_state.mcp_backend_url}/consent",
                        json={
                            "consent_id": consent_info["consent_id"],
                            "approved": True
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.messages.append({"content": result["response"], "is_user": False})
                        if result.get("data"):
                            st.session_state.show_data = {"type": "consent_data", "data": result["data"], "agent": result["agent"]}
                    else:
                        st.session_state.messages.append({"content": "Error processing consent approval.", "is_user": False})
                    
                    st.session_state.pending_consent = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Error approving consent: {e}")
        
        with col2:
            if st.button("❌ Deny"):
                try:
                    # Call consent endpoint
                    response = requests.post(
                        f"{st.session_state.mcp_backend_url}/consent",
                        json={
                            "consent_id": consent_info["consent_id"],
                            "approved": False
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.messages.append({"content": result["response"], "is_user": False})
                    
                    st.session_state.pending_consent = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Error denying consent: {e}")
        
        with col3:
            if st.button("🔄 Cancel"):
                st.session_state.pending_consent = None
                st.rerun()
    
    # Chat input form
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Ask me about your marketing data:",
            placeholder="e.g., Show me my top performing campaigns, What is CTR?, Compare Display vs Video performance",
            height=100
        )
        submit_button = st.form_submit_button("Send", type="primary")
        
        if submit_button and user_input:
            # Add user message
            st.session_state.messages.append({"content": user_input, "is_user": True})
            
            # Process question
            with st.spinner("Processing your request..."):
                response, show_data = process_question_with_data(user_input)
            
            # Add bot response
            st.session_state.messages.append({"content": response, "is_user": False})
            
            # Set data to show
            if show_data:
                st.session_state.show_data = show_data
            
            st.rerun()
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**System:** Marketing Analytics Chatbot")
    with col2:
        if st.session_state.use_mcp_system:
            st.markdown("**Mode:** MCP Protocol")
        else:
            st.markdown("**Mode:** Simple Processing")
    with col3:
        st.markdown("**Version:** 2.0.0")

if __name__ == "__main__":
    main()



