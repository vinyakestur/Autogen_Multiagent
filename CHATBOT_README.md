# 🤖 Marketing Analytics Chatbot

A simple Streamlit-based chatbot interface for querying your Databricks marketing data. Ask natural language questions about your campaigns and reports!

## 🚀 Quick Start

### Option 1: Using the Launcher Script
```bash
python run_chatbot.py
```

### Option 2: Direct Streamlit Command
```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## ✨ Features

### 🎯 **Smart Question Processing**
- Natural language understanding
- Pattern matching for common questions
- Context-aware responses

### 📊 **Data Analysis Capabilities**
- Campaign counts and statistics
- Performance metrics and rankings
- Budget analysis
- Channel breakdowns
- Recent activity tracking

### 💬 **Interactive Chat Interface**
- Real-time conversation
- Message history
- Clean, modern UI
- Responsive design

### 🔄 **Real-time Data Loading**
- Connects directly to your Databricks instance
- Loads data on app startup
- Connection status monitoring
- Data refresh capability

## 🗣️ Example Questions

### Campaign Questions
- "How many campaigns do we have?"
- "Show me active campaigns"
- "What's our total budget?"
- "Which campaigns are performing best?"
- "Show me campaigns by channel"

### Reports Questions
- "How many reports do we have?"
- "Show me reports information"

### Analysis Questions
- "What are the recent campaigns?"
- "Show me performance metrics"
- "Help" - Get more examples

## 🏗️ Architecture

### Files Structure
```
├── streamlit_app.py          # Main Streamlit application
├── run_chatbot.py            # Launcher script
├── databricks_connector.py   # Databricks connection utilities
├── example_queries.py        # Pre-built query functions
├── config.py                 # Configuration settings
└── requirements.txt          # Python dependencies
```

### Key Components

1. **Chat Interface** (`streamlit_app.py`)
   - Message display and input handling
   - Question processing logic
   - Response generation

2. **Data Layer** (`databricks_connector.py`)
   - Databricks connection management
   - Query execution
   - Data loading

3. **Question Processing**
   - Pattern matching for question types
   - Response generation functions
   - Error handling

## 🔧 Configuration

Your Databricks credentials are configured in `config.py`:
- Server: `dbc-f4ba6223-6a9f.cloud.databricks.com`
- Catalog: `campaign`
- Schema: `silver`
- Tables: `campaigns`, `reports`

## 📱 UI Features

### Sidebar
- **Connection Status**: Shows Databricks connection state
- **Quick Stats**: Displays campaign and report counts
- **Reload Data**: Button to refresh data from Databricks

### Main Chat Area
- **Message History**: Scrollable conversation
- **Input Box**: Type your questions here
- **Send Button**: Submit your question
- **Enter Key**: Also submits questions

### Message Styling
- **User Messages**: Right-aligned with user avatar
- **Bot Messages**: Left-aligned with bot avatar
- **Rich Formatting**: Markdown support for responses

## 🎨 Customization

### Adding New Question Types
1. Add pattern matching in `process_question()`
2. Create response function
3. Add to help message

### Styling Changes
- Modify CSS in the `st.markdown()` section
- Update colors, fonts, and layout
- Add custom components

### Data Sources
- Extend `load_data()` for additional tables
- Add new query functions
- Update response generation

## 🐛 Troubleshooting

### Common Issues

1. **Connection Errors**
   - Check Databricks credentials in `config.py`
   - Ensure warehouse is running
   - Verify network connectivity

2. **Data Loading Issues**
   - Check table permissions
   - Verify table names and schema
   - Look at error messages in the UI

3. **Question Not Understood**
   - Try rephrasing your question
   - Use keywords from the help examples
   - Check for typos

### Debug Mode
- Check the sidebar for connection status
- Use the "Reload Data" button to refresh
- Look at terminal output for detailed errors

## 🚀 Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python run_chatbot.py
```

### Production Deployment
- Use Streamlit Cloud or similar platform
- Set up environment variables for credentials
- Configure proper security settings

## 📊 Data Requirements

The chatbot expects these tables in your Databricks schema:

### Campaigns Table
- `campaign_id` (string)
- `campaign_name` (string)
- `status` (string)
- `channel` (string)
- `start_date` (date)
- `end_date` (date)
- `budget` (double)

### Reports Table
- `report_id` (string)
- `campaign_id` (string)
- `report_date` (date)
- `impressions` (bigint)
- `clicks` (bigint)
- `conversions` (bigint)
- `cost` (double)
- `CTR` (double)
- `CVR` (double)

## 🎓 Professor Demo Tips

1. **Start with Simple Questions**: "How many campaigns do we have?"
2. **Show Performance Analysis**: "Which campaigns are performing best?"
3. **Demonstrate Budget Analysis**: "What's our total budget?"
4. **Try Channel Analysis**: "Show me campaigns by channel"
5. **Use Help Feature**: Type "help" to show capabilities

## 🔮 Future Enhancements

- Voice input/output
- Advanced NLP processing
- Data visualization charts
- Export capabilities
- Multi-language support
- Advanced analytics queries

---

**Ready to chat with your data!** 🚀
