"""
Databricks SQL Connector
Provides utilities to connect to and query Databricks data warehouse
"""
import pandas as pd
from databricks import sql
from config import DATABRICKS_CONFIG, TABLES
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabricksConnector:
    """Handles connection to Databricks and data retrieval"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Establish connection to Databricks"""
        try:
            self.connection = sql.connect(
                server_hostname=DATABRICKS_CONFIG["server_hostname"],
                http_path=DATABRICKS_CONFIG["http_path"],
                access_token=DATABRICKS_CONFIG["access_token"]
            )
            self.cursor = self.connection.cursor()
            logger.info("Successfully connected to Databricks")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Databricks: {str(e)}")
            return False
    
    def disconnect(self):
        """Close connection to Databricks"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Disconnected from Databricks")
    
    def execute_query(self, query, fetch_all=True):
        """Execute a SQL query and return results as pandas DataFrame"""
        if not self.connection:
            logger.error("No active connection. Please connect first.")
            return None
            
        try:
            self.cursor.execute(query)
            
            if fetch_all:
                results = self.cursor.fetchall()
                columns = [desc[0] for desc in self.cursor.description]
                df = pd.DataFrame(results, columns=columns)
                logger.info(f"Query executed successfully. Returned {len(df)} rows.")
                return df
            else:
                return self.cursor.fetchone()
                
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            return None
    
    def get_table_info(self, table_name):
        """Get information about a specific table"""
        query = f"""
        DESCRIBE TABLE {DATABRICKS_CONFIG['catalog']}.{DATABRICKS_CONFIG['schema']}.{table_name}
        """
        return self.execute_query(query)
    
    def get_table_sample(self, table_name, limit=10):
        """Get a sample of data from a table"""
        query = f"""
        SELECT * FROM {DATABRICKS_CONFIG['catalog']}.{DATABRICKS_CONFIG['schema']}.{table_name}
        LIMIT {limit}
        """
        return self.execute_query(query)
    
    def get_campaigns_data(self, limit=None):
        """Get data from campaigns table"""
        limit_clause = f"LIMIT {limit}" if limit else ""
        query = f"""
        SELECT * FROM {DATABRICKS_CONFIG['catalog']}.{DATABRICKS_CONFIG['schema']}.{TABLES['campaigns']}
        {limit_clause}
        """
        return self.execute_query(query)
    
    def get_reports_data(self, limit=None):
        """Get data from reports table"""
        limit_clause = f"LIMIT {limit}" if limit else ""
        query = f"""
        SELECT * FROM {DATABRICKS_CONFIG['catalog']}.{DATABRICKS_CONFIG['schema']}.{TABLES['reports']}
        {limit_clause}
        """
        return self.execute_query(query)
    
    def get_available_tables(self):
        """Get list of available tables in the schema"""
        query = f"""
        SHOW TABLES IN {DATABRICKS_CONFIG['catalog']}.{DATABRICKS_CONFIG['schema']}
        """
        return self.execute_query(query)
    
    def custom_query(self, sql_query):
        """Execute a custom SQL query"""
        return self.execute_query(sql_query)

# Context manager for automatic connection management
class DatabricksConnection:
    """Context manager for Databricks connections"""
    
    def __init__(self):
        self.connector = DatabricksConnector()
    
    def __enter__(self):
        if self.connector.connect():
            return self.connector
        else:
            raise ConnectionError("Failed to connect to Databricks")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connector.disconnect()
