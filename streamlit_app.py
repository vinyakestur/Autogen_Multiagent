"""
Streamlit App with Direct Databricks Integration - Fixed Version
Simplified frontend using direct API calls instead of MCP
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import json
import requests
import logging
import matplotlib.pyplot as plt
import plotly.express as px

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Marketing Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'show_data' not in st.session_state:
        st.session_state.show_data = None
    if 'sql_query' not in st.session_state:
        st.session_state.sql_query = None
    if 'charts' not in st.session_state:
        st.session_state.charts = None
    if 'pending_consent' not in st.session_state:
        st.session_state.pending_consent = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "default_user"
    if 'api_backend_url' not in st.session_state:
        st.session_state.api_backend_url = "http://localhost:8000"

def check_api_health():
    """Check if the API backend is healthy"""
    try:
        response = requests.get(f"{st.session_state.api_backend_url}/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        return False, None

def send_chat_message(message, user_id):
    """Send chat message to API backend"""
    try:
        response = requests.post(
            f"{st.session_state.api_backend_url}/chat",
            json={
                "message": message,
                "user_id": user_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "response": f"API Error: {response.status_code}",
                "agent": "error",
                "consent_required": False
            }
    except Exception as e:
        return {
            "response": f"Connection Error: {str(e)}",
            "agent": "error", 
            "consent_required": False
        }

def display_chat_message(content, is_user):
    """Display a chat message"""
    if is_user:
        st.markdown(f"**You:** {content}")
    else:
        st.markdown(f"**Bot:** {content}")

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Header
    st.title("📊 Marketing Analytics Platform")
    
    # Project Overview
    st.info("Build a comprehensive marketing analytics platform that connects to Databricks for intelligent data querying and visualization using direct API calls.")
    
    # Core Workflow
    st.subheader("🔄 Core Workflow")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **1. Direct Databricks Connection**
        - Establish secure connection to Databricks workspace
        - Access raw data directly through API integration
        - Real-time data processing capabilities
        """)
        
        st.markdown("""
        **2. User Consent Management**
        - Streamlit UI requests user permission before data access
        - Provides approve/deny/cancel options for data queries
        - Granular permission control for different data types
        """)
    
    with col2:
        st.markdown("""
        **3. Intelligent Query System**
        - **Predefined Queries:** Check catalog for existing queries
        - **Dynamic Creation:** Generate new queries if no match exists
        - **Direct Execution:** Execute queries against Databricks automatically
        """)
        
        st.markdown("""
        **4. Automated Report Generation**
        - Streamlit UI generates visual reports
        - Multiple visualization types based on query results
        - Interactive dashboards for data exploration
        """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Configuration")
        
        # API Backend URL
        api_url = st.text_input(
            "API Backend URL",
            value=st.session_state.api_backend_url,
            help="URL of the FastAPI backend with direct Databricks integration"
        )
        if api_url != st.session_state.api_backend_url:
            st.session_state.api_backend_url = api_url
            st.rerun()
        
        # API Health Check
        is_healthy, health_data = check_api_health()
        if is_healthy:
            st.success("✅ API Connected")
            if health_data:
                st.write(f"**Integration:** {health_data.get('integration', 'Unknown')}")
                st.write(f"**Features:** {health_data.get('features', 'Unknown')}")
        else:
            st.error("❌ API Disconnected")
            st.write("Please ensure the API backend is running on port 8000")
        
        # User ID
        user_id = st.text_input("User ID", value=st.session_state.user_id)
        if user_id != st.session_state.user_id:
            st.session_state.user_id = user_id
            st.rerun()
        
        # Clear chat
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.session_state.show_data = None
            st.session_state.pending_consent = None
            st.rerun()
        
        # Sample queries
        st.header("💡 Sample Queries")
        sample_queries = [
            "What is CTR?",
            "Show me my campaigns",
            "Analyze my performance",
            "What's my budget allocation?",
            "Show me trends over time"
        ]
        
        for query in sample_queries:
            if st.button(f"💬 {query}", key=f"sample_{query}"):
                st.session_state.messages.append({"content": query, "is_user": True})
                st.rerun()
    
    # Main chat interface
    st.subheader("💬 Chat Interface")
    
    # Display chat messages
    for message in st.session_state.messages:
        display_chat_message(message["content"], message["is_user"])
    
    # Display data if available
    if hasattr(st.session_state, 'show_data') and st.session_state.show_data:
        st.subheader("📊 Data Analysis Results")
        data_info = st.session_state.show_data
        
        # Display SQL Query if available
        if hasattr(st.session_state, 'sql_query') and st.session_state.sql_query:
            with st.expander("🔍 Generated SQL Query", expanded=False):
                st.code(st.session_state.sql_query, language='sql')
        
        if isinstance(data_info, dict) and 'data' in data_info:
            data = data_info['data']
            
            if isinstance(data, list) and data:
                # Convert list of dicts to DataFrame
                df = pd.DataFrame(data)
                
                # Data overview
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Records", len(df))
                with col2:
                    st.metric("Columns", len(df.columns))
                with col3:
                    if not df.empty:
                        st.metric("Data Types", len(df.dtypes.unique()))
                
                # Enhanced Raw Data Display
                st.subheader("📋 Raw Data Table")
                st.dataframe(df, use_container_width=True, height=400)
                
                # Auto-generated Charts from Backend
        if hasattr(st.session_state, 'charts') and st.session_state.charts:
            st.subheader("🤖 AI-Generated Visualizations")
            for i, chart in enumerate(st.session_state.charts):
                if chart.get('figure_json'):
                    try:
                        # Parse JSON string back to dictionary
                        import json
                        import plotly.graph_objects as go
                        fig_dict = json.loads(chart['figure_json'])
                        fig = go.Figure(fig_dict)
                        st.plotly_chart(fig, use_container_width=True, key=f"ai_chart_{i}")
                    except Exception as e:
                        st.error(f"Error displaying chart {i+1}: {str(e)}")
                        st.json(chart.get('figure_json', 'No chart data'))
                
                # Data Visualizations
                if not df.empty and len(df) > 1:
                    st.subheader("📈 Data Visualizations")
                    
                    # Initialize chart counter with timestamp for uniqueness
                    import time
                    base_time = int(time.time() * 1000)  # milliseconds
                    chart_counter = 0
                    
                    # Determine chart types based on data
                    if 'campaign_id' in df.columns and 'campaign_name' in df.columns:
                        # Campaign data visualizations
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Status distribution pie chart
                            if 'status' in df.columns:
                                status_counts = df['status'].value_counts()
                                st.subheader("📊 Campaign Status Distribution")
                                fig = px.pie(values=status_counts.values, names=status_counts.index, title="Status Distribution")
                                st.plotly_chart(fig, use_container_width=True, key=f"status_pie_{base_time}_{chart_counter}")
                                chart_counter += 1
                        
                        with col2:
                            # Channel distribution pie chart
                            if 'channel' in df.columns:
                                channel_counts = df['channel'].value_counts()
                                st.subheader("📊 Channel Distribution")
                                fig = px.pie(values=channel_counts.values, names=channel_counts.index, title="Channel Distribution")
                                st.plotly_chart(fig, use_container_width=True, key=f"channel_pie_{base_time}_{chart_counter}")
                                chart_counter += 1
                        
                        # Budget analysis
                        if 'budget' in df.columns:
                            st.subheader("💰 Budget Analysis")
                            budget_data = df[['campaign_name', 'budget']].head(10)  # Show top 10 campaigns
                            fig = px.bar(budget_data, x='campaign_name', y='budget', title="Campaign Budgets")
                            fig.update_xaxes(tickangle=45)
                            st.plotly_chart(fig, use_container_width=True, key=f"budget_bar_{base_time}_{chart_counter}")
                            chart_counter += 1
                    
                    elif 'report_id' in df.columns and 'campaign_id' in df.columns:
                        # Reports data visualizations
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # CTR analysis
                            if 'CTR' in df.columns:
                                st.subheader("📈 CTR Analysis")
                                ctr_data = df[['campaign_id', 'CTR']].head(10)
                                fig = px.bar(ctr_data, x='campaign_id', y='CTR', title="CTR by Campaign")
                                fig.update_xaxes(tickangle=45)
                                st.plotly_chart(fig, use_container_width=True, key=f"ctr_bar_{base_time}_{chart_counter}")
                                chart_counter += 1
                        
                        with col2:
                            # CVR analysis
                            if 'CVR' in df.columns:
                                st.subheader("📈 CVR Analysis")
                                cvr_data = df[['campaign_id', 'CVR']].head(10)
                                fig = px.bar(cvr_data, x='campaign_id', y='CVR', title="CVR by Campaign")
                                fig.update_xaxes(tickangle=45)
                                st.plotly_chart(fig, use_container_width=True, key=f"cvr_bar_{base_time}_{chart_counter}")
                                chart_counter += 1
                        
                        # Performance trends
                        if 'report_date' in df.columns and 'impressions' in df.columns:
                            st.subheader("📈 Performance Trends")
                            df['report_date'] = pd.to_datetime(df['report_date'])
                            trend_data = df[['report_date', 'impressions', 'clicks', 'conversions']].head(20)
                            fig = px.line(trend_data, x='report_date', y=['impressions', 'clicks', 'conversions'], 
                                        title="Performance Trends Over Time")
                            st.plotly_chart(fig, use_container_width=True, key=f"trend_line_{base_time}_{chart_counter}")
                            chart_counter += 1
                
                # Download options
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"marketing_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key=f"csv_download_{base_time}"
                )
    
    # Handle pending consent requests
    if st.session_state.pending_consent:
        st.markdown("---")
        st.warning("🔐 Data Access Consent Required")
        
        consent_info = st.session_state.pending_consent
        st.write(f"**Your Query:** {consent_info['original_query']}")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("✅ Approve", type="primary", use_container_width=True):
                # Handle approval by calling the API
                try:
                    response = requests.post(
                        f"{st.session_state.api_backend_url}/consent",
                        json={
                            "consent_id": consent_info['consent_id'],
                            "approved": True
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Consent approved! Processing your request...")
                        
                        # Add the response to chat
                        st.session_state.messages.append({"content": result["response"], "is_user": False})
                        
                        # Store the data for display
                        if result.get("data"):
                            st.session_state.show_data = {"data": result["data"], "agent": result["agent"]}
                        
                        # Store SQL query and charts
                        if result.get("sql_query"):
                            st.session_state.sql_query = result["sql_query"]
                        if result.get("charts"):
                            st.session_state.charts = result["charts"]
                        
                        st.session_state.pending_consent = None
                        st.rerun()
                    else:
                        st.error(f"❌ Error approving consent: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Error approving consent: {str(e)}")
        
        with col2:
            if st.button("❌ Deny", type="secondary", use_container_width=True):
                # Handle denial by calling the API
                try:
                    response = requests.post(
                        f"{st.session_state.api_backend_url}/consent",
                        json={
                            "consent_id": consent_info['consent_id'],
                            "approved": False
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.info("❌ Consent denied. Your data remains protected.")
                        st.session_state.messages.append({"content": result["response"], "is_user": False})
                    else:
                        st.info("❌ Consent denied. Your data remains protected.")
                    
                    st.session_state.pending_consent = None
                    st.rerun()
                except Exception as e:
                    st.info("❌ Consent denied. Your data remains protected.")
                    st.session_state.pending_consent = None
                    st.rerun()
        
        with col3:
            if st.button("🔄 Cancel Request", use_container_width=True):
                st.session_state.pending_consent = None
                st.info("🔄 Request cancelled. You can ask a different question.")
                st.rerun()
    
    # Chat input form
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Ask me about your marketing data:",
            placeholder="e.g., 'Show me my top performing campaigns' or 'What is CTR?'",
            height=100
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_button = st.form_submit_button("Send", type="primary", use_container_width=True)
        
        if submit_button and user_input:
            # Add user message
            st.session_state.messages.append({"content": user_input, "is_user": True})
            
            # Send to API
            with st.spinner("Processing your request..."):
                result = send_chat_message(user_input, st.session_state.user_id)
            
            # Handle response
            if result.get("consent_required") and result.get("consent_id"):
                # Store consent request
                st.session_state.pending_consent = {
                    "consent_id": result["consent_id"],
                    "original_query": user_input
                }
                st.session_state.messages.append({"content": result["response"], "is_user": False})
            else:
                # Direct response
                st.session_state.messages.append({"content": result["response"], "is_user": False})
                if result.get("data"):
                    st.session_state.show_data = {"data": result["data"], "agent": result["agent"]}
                
                # Store SQL query and charts for direct responses too
                if result.get("sql_query"):
                    st.session_state.sql_query = result["sql_query"]
                if result.get("charts"):
                    st.session_state.charts = result["charts"]
            
            st.rerun()

if __name__ == "__main__":
    main()
