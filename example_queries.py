"""
Intelligent Query System for Databricks Analysis
Contains predefined queries and dynamic query generation capabilities
"""
from databricks_connector import DatabricksConnection
import pandas as pd
from config import DATABRICKS_CONFIG
from sql_generator import SQLGenerator

class DatabricksQueries:
    """Intelligent Query System with predefined and dynamic query capabilities"""
    
    def __init__(self):
        self.catalog = DATABRICKS_CONFIG["catalog"]
        self.schema = DATABRICKS_CONFIG["schema"]
        self.sql_generator = SQLGenerator()
    
    def get_table_name(self, table):
        """Get fully qualified table name"""
        return f"{self.catalog}.{self.schema}.{table}"
    
    def find_matching_query(self, user_query):
        """Find predefined query that matches user request - only for very basic queries"""
        # Only match very basic, generic queries to predefined patterns
        basic_patterns = {
            'campaigns': ['show me all campaigns', 'list all campaigns', 'campaigns list'],
            'performance': ['show me performance', 'performance metrics', 'show metrics'],
            'budget': ['show me budget', 'budget overview', 'budget allocation'],
            'trends': ['show me trends', 'trends over time', 'monthly trends'],
            'summary': ['summary', 'overview', 'insights', 'marketing data summary']
        }
        
        user_query_lower = user_query.lower().strip()
        
        # Check for exact matches or very basic patterns only
        for query_type, patterns in basic_patterns.items():
            if any(pattern == user_query_lower for pattern in patterns):
                return query_type
        
        # For any query with specific conditions, filters, or complex requirements, use AI
        complex_indicators = [
            'greater than', 'less than', 'more than', 'above', 'below',
            'with', 'where', 'having', 'filter', 'sort', 'order',
            'top', 'best', 'worst', 'highest', 'lowest',
            'by', 'group by', 'average', 'sum', 'count',
            'between', 'from', 'to', 'since', 'until',
            'active', 'completed', 'paused', 'status',
            'channel', 'source', 'medium', 'budget greater',
            'budget less', 'budget more', 'budget above'
        ]
        
        if any(indicator in user_query_lower for indicator in complex_indicators):
            return None  # Use AI generation
        
        return None  # Default to AI generation for most queries
    
    def generate_dynamic_query(self, user_query, query_type):
        """Generate dynamic query based on user request"""
        if query_type == 'campaigns':
            return self._generate_campaigns_query(user_query)
        elif query_type == 'performance':
            return self._generate_performance_query(user_query)
        elif query_type == 'budget':
            return self._generate_budget_query(user_query)
        elif query_type == 'trends':
            return self._generate_trends_query(user_query)
        elif query_type == 'summary':
            return self._generate_summary_query(user_query)
        else:
            # Use AI to generate custom SQL for non-predefined queries
            return self._generate_ai_query(user_query, query_type)
    
    def _generate_ai_query(self, user_query, query_type):
        """Generate AI-powered custom SQL query"""
        try:
            print(f"🤖 Generating AI query for: '{user_query}' (type: {query_type})")
            ai_result = self.sql_generator.generate_sql(user_query, query_type)
            
            if ai_result.get('sql') and ai_result['sql'].strip():
                print(f"✅ AI generated SQL: {ai_result['sql'][:100]}...")
                return ai_result['sql']
            else:
                print("⚠️ AI returned empty SQL, using intelligent fallback")
                return self._generate_intelligent_fallback(user_query)
        except Exception as e:
            print(f"❌ Error generating AI query: {e}")
            return self._generate_intelligent_fallback(user_query)
    
    def _generate_campaigns_query(self, user_query):
        """Generate campaigns-specific query"""
        return f"""
        SELECT 
            campaign_id,
            campaign_name,
            status,
            channel,
            budget,
            start_date,
            end_date
        FROM {self.get_table_name('campaigns')}
        ORDER BY start_date DESC
        LIMIT 50
        """
    
    def _generate_performance_query(self, user_query):
        """Generate performance analysis query"""
        return f"""
        SELECT 
            c.campaign_name,
            c.channel,
            c.status,
            AVG(r.impressions) as avg_impressions,
            AVG(r.clicks) as avg_clicks,
            AVG(r.conversions) as avg_conversions,
            AVG(r.cost) as avg_cost,
            AVG(r.CTR) as avg_ctr,
            AVG(r.CVR) as avg_cvr
        FROM {self.get_table_name('campaigns')} c
        LEFT JOIN {self.get_table_name('reports')} r ON c.campaign_id = r.campaign_id
        GROUP BY c.campaign_id, c.campaign_name, c.channel, c.status
        ORDER BY avg_conversions DESC
        LIMIT 20
        """
    
    def _generate_budget_query(self, user_query):
        """Generate budget analysis query"""
        return f"""
        SELECT 
            channel,
            status,
            COUNT(*) as campaign_count,
            SUM(budget) as total_budget,
            AVG(budget) as avg_budget,
            MIN(budget) as min_budget,
            MAX(budget) as max_budget
        FROM {self.get_table_name('campaigns')}
        GROUP BY channel, status
        ORDER BY total_budget DESC
        """
    
    def _generate_trends_query(self, user_query):
        """Generate trends analysis query"""
        return f"""
        SELECT 
            DATE_TRUNC('month', r.report_date) as month,
            c.channel,
            SUM(r.impressions) as total_impressions,
            SUM(r.clicks) as total_clicks,
            SUM(r.conversions) as total_conversions,
            SUM(r.cost) as total_cost,
            AVG(r.CTR) as avg_ctr,
            AVG(r.CVR) as avg_cvr
        FROM {self.get_table_name('reports')} r
        JOIN {self.get_table_name('campaigns')} c ON r.campaign_id = c.campaign_id
        WHERE r.report_date >= DATE_SUB(CURRENT_DATE(), 12)
        GROUP BY DATE_TRUNC('month', r.report_date), c.channel
        ORDER BY month DESC, total_conversions DESC
        """
    
    def _generate_intelligent_fallback(self, user_query):
        """Generate intelligent fallback query based on user input keywords"""
        query_lower = user_query.lower()
        
        # Extract budget conditions
        budget_condition = None
        if 'budget greater than' in query_lower or 'budget >' in query_lower:
            # Extract the number after "greater than" or ">"
            import re
            match = re.search(r'budget\s+(?:greater\s+than|>)\s*(\d+)', query_lower)
            if match:
                amount = match.group(1)
                budget_condition = f"budget > {amount}"
        elif 'budget less than' in query_lower or 'budget <' in query_lower:
            match = re.search(r'budget\s+(?:less\s+than|<)\s*(\d+)', query_lower)
            if match:
                amount = match.group(1)
                budget_condition = f"budget < {amount}"
        elif 'budget between' in query_lower:
            match = re.search(r'budget\s+between\s+(\d+)\s+and\s+(\d+)', query_lower)
            if match:
                min_amount, max_amount = match.group(1), match.group(2)
                budget_condition = f"budget BETWEEN {min_amount} AND {max_amount}"
        
        # Check for specific keywords to generate more relevant queries
        if any(word in query_lower for word in ['campaign', 'campaigns']):
            if budget_condition:
                return f"""
                SELECT 
                    campaign_id,
                    campaign_name,
                    status,
                    channel,
                    budget,
                    start_date,
                    end_date
                FROM {self.get_table_name('campaigns')}
                WHERE {budget_condition}
                ORDER BY budget DESC
                """
            elif any(word in query_lower for word in ['status', 'active', 'completed', 'paused']):
                return f"""
                SELECT 
                    status,
                    COUNT(*) as count,
                    AVG(budget) as avg_budget
                FROM {self.get_table_name('campaigns')}
                GROUP BY status
                ORDER BY count DESC
                """
            else:
                return f"""
                SELECT 
                    campaign_id,
                    campaign_name,
                    status,
                    channel,
                    budget,
                    start_date,
                    end_date
                FROM {self.get_table_name('campaigns')}
                ORDER BY start_date DESC
                LIMIT 20
                """
        
        elif any(word in query_lower for word in ['performance', 'metrics', 'ctr', 'cvr', 'conversion']):
            return f"""
            SELECT 
                c.campaign_name,
                AVG(r.CTR) as avg_ctr,
                AVG(r.CVR) as avg_cvr,
                SUM(r.conversions) as total_conversions,
                AVG(r.cost) as avg_cost
            FROM {self.get_table_name('campaigns')} c
            LEFT JOIN {self.get_table_name('reports')} r ON c.campaign_id = r.campaign_id
            GROUP BY c.campaign_name
            ORDER BY total_conversions DESC
            LIMIT 20
            """
        
        elif any(word in query_lower for word in ['budget', 'cost', 'spend']):
            if budget_condition:
                return f"""
                SELECT 
                    campaign_id,
                    campaign_name,
                    budget,
                    channel,
                    status
                FROM {self.get_table_name('campaigns')}
                WHERE {budget_condition}
                ORDER BY budget DESC
                """
            else:
                return f"""
                SELECT 
                    campaign_name,
                    budget,
                    channel,
                    status
                FROM {self.get_table_name('campaigns')}
                ORDER BY budget DESC
                LIMIT 20
                """
        
        else:
            # Generic overview query
            return f"""
            SELECT 
                'campaigns' as table_name,
                COUNT(*) as record_count,
                'Campaign data' as description
            FROM {self.get_table_name('campaigns')}
            UNION ALL
            SELECT 
                'reports' as table_name,
                COUNT(*) as record_count,
                'Performance reports' as description
            FROM {self.get_table_name('reports')}
            """
    
    def _generate_generic_query(self, user_query):
        """Generate generic query for unknown requests (deprecated - use intelligent fallback)"""
        return self._generate_intelligent_fallback(user_query)
    
    def get_campaigns_overview(self):
        """Get basic overview of campaigns data"""
        with DatabricksConnection() as db:
            query = f"""
            SELECT 
                COUNT(*) as total_campaigns,
                COUNT(DISTINCT campaign_id) as unique_campaigns,
                MIN(start_date) as earliest_campaign,
                MAX(end_date) as latest_campaign,
                AVG(budget) as avg_budget,
                SUM(budget) as total_budget
            FROM {self.get_table_name('campaigns')}
            """
            return db.execute_query(query)
    
    @staticmethod
    def get_reports_overview():
        """Get basic overview of reports data"""
        with DatabricksConnection() as db:
            query = """
            SELECT 
                COUNT(*) as total_reports,
                COUNT(DISTINCT report_id) as unique_reports,
                MIN(report_date) as earliest_report,
                MAX(report_date) as latest_report,
                AVG(impressions) as avg_impressions,
                AVG(clicks) as avg_clicks,
                AVG(conversions) as avg_conversions,
                AVG(cost) as avg_cost
            FROM campaign.silver.reports
            """
            return db.execute_query(query)
    
    @staticmethod
    def get_campaigns_by_status():
        """Get campaigns grouped by status"""
        with DatabricksConnection() as db:
            query = """
            SELECT 
                status,
                COUNT(*) as campaign_count,
                AVG(budget) as avg_budget
            FROM campaign.silver.campaigns
            GROUP BY status
            ORDER BY campaign_count DESC
            """
            return db.execute_query(query)
    
    @staticmethod
    def get_reports_by_campaign():
        """Get reports grouped by campaign"""
        with DatabricksConnection() as db:
            query = """
            SELECT 
                c.campaign_name,
                COUNT(r.report_id) as report_count,
                AVG(r.impressions) as avg_impressions,
                AVG(r.clicks) as avg_clicks,
                AVG(r.conversions) as avg_conversions,
                AVG(r.cost) as avg_cost
            FROM campaign.silver.reports r
            LEFT JOIN campaign.silver.campaigns c ON r.campaign_id = c.campaign_id
            GROUP BY c.campaign_name
            ORDER BY report_count DESC
            """
            return db.execute_query(query)
    
    @staticmethod
    def get_campaign_performance():
        """Get campaign performance metrics"""
        with DatabricksConnection() as db:
            query = """
            SELECT 
                c.campaign_id,
                c.campaign_name,
                c.status,
                c.budget,
                COUNT(r.report_id) as report_count,
                AVG(r.impressions) as avg_impressions,
                SUM(r.impressions) as total_impressions,
                AVG(r.clicks) as avg_clicks,
                SUM(r.clicks) as total_clicks,
                AVG(r.conversions) as avg_conversions,
                SUM(r.conversions) as total_conversions,
                AVG(r.cost) as avg_cost,
                SUM(r.cost) as total_cost
            FROM campaign.silver.campaigns c
            LEFT JOIN campaign.silver.reports r ON c.campaign_id = r.campaign_id
            GROUP BY c.campaign_id, c.campaign_name, c.status, c.budget
            ORDER BY total_impressions DESC
            """
            return db.execute_query(query)
    
    @staticmethod
    def get_top_performing_campaigns(limit=10):
        """Get top performing campaigns by impressions"""
        with DatabricksConnection() as db:
            query = f"""
            SELECT 
                c.campaign_name,
                c.status,
                c.budget,
                SUM(r.impressions) as total_impressions,
                SUM(r.clicks) as total_clicks,
                SUM(r.conversions) as total_conversions,
                COUNT(r.report_id) as report_count,
                ROUND(SUM(r.impressions) / c.budget, 2) as impressions_per_dollar
            FROM campaign.silver.campaigns c
            LEFT JOIN campaign.silver.reports r ON c.campaign_id = r.campaign_id
            WHERE c.budget > 0
            GROUP BY c.campaign_id, c.campaign_name, c.status, c.budget
            HAVING total_impressions > 0
            ORDER BY impressions_per_dollar DESC
            LIMIT {limit}
            """
            return db.execute_query(query)
    
    @staticmethod
    def get_recent_activity(days=30):
        """Get recent activity for both campaigns and reports"""
        with DatabricksConnection() as db:
            query = f"""
            SELECT 
                'campaign' as type,
                campaign_id as id,
                campaign_name as name,
                start_date as activity_date,
                status
            FROM campaign.silver.campaigns
            WHERE start_date >= CURRENT_DATE - INTERVAL {days} DAYS
            
            UNION ALL
            
            SELECT 
                'report' as type,
                report_id as id,
                CONCAT('Report for ', c.campaign_name) as name,
                report_date as activity_date,
                'Report' as status
            FROM campaign.silver.reports r
            LEFT JOIN campaign.silver.campaigns c ON r.campaign_id = c.campaign_id
            WHERE report_date >= CURRENT_DATE - INTERVAL {days} DAYS
            
            ORDER BY activity_date DESC
            """
            return db.execute_query(query)
    
    @staticmethod
    def search_campaigns(search_term):
        """Search campaigns by name or channel"""
        with DatabricksConnection() as db:
            query = f"""
            SELECT 
                campaign_id,
                campaign_name,
                channel,
                status,
                budget,
                start_date,
                end_date
            FROM campaign.silver.campaigns
            WHERE LOWER(campaign_name) LIKE LOWER('%{search_term}%')
               OR LOWER(channel) LIKE LOWER('%{search_term}%')
            ORDER BY start_date DESC
            """
            return db.execute_query(query)
    
    def _generate_summary_query(self, user_query):
        """Generate comprehensive summary query"""
        return f"""
        SELECT 
            'Campaigns' as data_type,
            COUNT(*) as total_count,
            COUNT(CASE WHEN status = 'Active' THEN 1 END) as active_count,
            COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed_count,
            COUNT(CASE WHEN status = 'Paused' THEN 1 END) as paused_count,
            ROUND(AVG(budget), 2) as avg_budget,
            ROUND(SUM(budget), 2) as total_budget,
            COUNT(DISTINCT channel) as channel_count
        FROM {self.get_table_name('campaigns')}
        
        UNION ALL
        
        SELECT 
            'Reports' as data_type,
            COUNT(*) as total_count,
            COUNT(CASE WHEN impressions > 0 THEN 1 END) as active_count,
            COUNT(CASE WHEN conversions > 0 THEN 1 END) as completed_count,
            COUNT(CASE WHEN cost > 0 THEN 1 END) as paused_count,
            ROUND(AVG(CTR), 2) as avg_budget,
            ROUND(AVG(CVR), 2) as total_budget,
            COUNT(DISTINCT campaign_id) as channel_count
        FROM {self.get_table_name('reports')}
        """
    
    @staticmethod
    def get_monthly_trends():
        """Get monthly trends for campaigns and reports"""
        with DatabricksConnection() as db:
            query = """
            SELECT 
                DATE_TRUNC('month', start_date) as month,
                'campaigns' as type,
                COUNT(*) as count
            FROM campaign.silver.campaigns
            GROUP BY DATE_TRUNC('month', start_date)
            
            UNION ALL
            
            SELECT 
                DATE_TRUNC('month', report_date) as month,
                'reports' as type,
                COUNT(*) as count
            FROM campaign.silver.reports
            GROUP BY DATE_TRUNC('month', report_date)
            
            ORDER BY month DESC, type
            """
            return db.execute_query(query)
