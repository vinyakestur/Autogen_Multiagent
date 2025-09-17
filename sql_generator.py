import anthropic
import json
import logging
from typing import Dict, Any, Optional
from config import ANTHROPIC_CONFIG

logger = logging.getLogger(__name__)

class SQLGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_CONFIG['api_key'])
        
        # Schema information for the AI
        self.schema_info = {
            "tables": {
                "campaigns": {
                    "columns": ["campaign_id", "campaign_name", "status", "budget", "channel", "start_date", "end_date"],
                    "description": "Campaign metadata including budget, status, and channel information"
                },
                "reports": {
                    "columns": ["campaign_id", "CTR", "CVR", "impressions", "conversions", "cost", "date"],
                    "description": "Performance metrics for each campaign including CTR, CVR, and conversions"
                }
            },
            "relationships": {
                "campaigns.campaign_id": "reports.campaign_id"
            },
            "catalog": "campaign",
            "schema": "silver"
        }
    
    def generate_sql(self, user_query: str, query_type: str = "custom") -> Dict[str, Any]:
        """Generate SQL query using Anthropic Claude"""
        try:
            print(f"🔍 Creating prompt for: '{user_query}'")
            # Create the prompt for Claude
            prompt = self._create_prompt(user_query, query_type)
            
            print(f"📤 Sending request to Claude API...")
            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.1,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            print(f"📥 Received response from Claude")
            # Parse the response
            sql_content = response.content[0].text
            print(f"📝 Raw response: {sql_content[:200]}...")
            
            sql_query = self._extract_sql(sql_content)
            print(f"🎯 Extracted SQL: {sql_query[:100]}...")
            
            return {
                "sql": sql_query,
                "explanation": self._extract_explanation(sql_content),
                "query_type": query_type,
                "generated_by": "anthropic_claude"
            }
            
        except Exception as e:
            print(f"❌ Error generating SQL: {e}")
            logger.error(f"Error generating SQL: {e}")
            return {
                "sql": None,
                "explanation": f"Error generating SQL: {str(e)}",
                "query_type": query_type,
                "generated_by": "anthropic_claude"
            }
    
    def _create_prompt(self, user_query: str, query_type: str) -> str:
        """Create a detailed prompt for Claude"""
        return f"""You are a SQL expert for a marketing analytics database. Generate a SQL query based on the user's request.

DATABASE SCHEMA:
- Catalog: {self.schema_info['catalog']}
- Schema: {self.schema_info['schema']}

TABLES:
1. campaigns: {self.schema_info['tables']['campaigns']['description']}
   Columns: {', '.join(self.schema_info['tables']['campaigns']['columns'])}

2. reports: {self.schema_info['tables']['reports']['description']}
   Columns: {', '.join(self.schema_info['tables']['reports']['columns'])}

RELATIONSHIPS:
- campaigns.campaign_id = reports.campaign_id

USER REQUEST: "{user_query}"

IMPORTANT INSTRUCTIONS:
1. Generate a SQL query that EXACTLY matches what the user is asking for
2. If the user mentions specific conditions (like "budget greater than $5000"), include those in WHERE clauses
3. If the user asks for specific fields, only select those fields
4. Use proper JOINs when data from both tables is needed
5. Include appropriate WHERE clauses, GROUP BY, ORDER BY as needed
6. Use the full table names: {self.schema_info['catalog']}.{self.schema_info['schema']}.table_name
7. Make the query efficient and readable
8. If the query needs aggregations, include them appropriately
9. Pay attention to specific values mentioned (like dollar amounts, percentages, etc.)

EXAMPLES:
- "show me campaigns with budget greater than $5000" → SELECT * FROM campaigns WHERE budget > 5000
- "campaigns with high CTR" → SELECT c.*, AVG(r.CTR) as avg_ctr FROM campaigns c JOIN reports r ON c.campaign_id = r.campaign_id GROUP BY c.campaign_id HAVING AVG(r.CTR) > 0.05

RESPONSE FORMAT:
```sql
-- Your SQL query here
SELECT ...
FROM ...
WHERE ...
```

EXPLANATION:
Briefly explain what the query does and why you chose this approach.

Generate the SQL query now:"""
    
    def _extract_sql(self, content: str) -> str:
        """Extract SQL query from Claude's response"""
        try:
            # Look for SQL code blocks
            if "```sql" in content:
                start = content.find("```sql") + 6
                end = content.find("```", start)
                if end != -1:
                    return content[start:end].strip()
            
            # Look for SQL without code blocks
            lines = content.split('\n')
            sql_lines = []
            in_sql = False
            
            for line in lines:
                if any(keyword in line.upper() for keyword in ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE']):
                    in_sql = True
                if in_sql:
                    sql_lines.append(line)
                    if line.strip().endswith(';'):
                        break
            
            return '\n'.join(sql_lines).strip()
            
        except Exception as e:
            logger.error(f"Error extracting SQL: {e}")
            return content
    
    def _extract_explanation(self, content: str) -> str:
        """Extract explanation from Claude's response"""
        try:
            if "EXPLANATION:" in content:
                start = content.find("EXPLANATION:") + 12
                return content[start:].strip()
            return "Query generated by AI based on your request."
        except:
            return "Query generated by AI based on your request."
