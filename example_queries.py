"""
Example queries for Databricks data access
Contains common query patterns for campaigns and reports data
"""
from databricks_connector import DatabricksConnection
import pandas as pd

class DatabricksQueries:
    """Collection of example queries for campaigns and reports data"""
    
    @staticmethod
    def get_campaigns_overview():
        """Get basic overview of campaigns data"""
        with DatabricksConnection() as db:
            query = """
            SELECT 
                COUNT(*) as total_campaigns,
                COUNT(DISTINCT campaign_id) as unique_campaigns,
                MIN(start_date) as earliest_campaign,
                MAX(end_date) as latest_campaign,
                AVG(budget) as avg_budget,
                SUM(budget) as total_budget
            FROM campaign.silver.campaigns
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
