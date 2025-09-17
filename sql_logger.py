import json
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class SQLLogger:
    def __init__(self, log_dir: str = "sql_logs"):
        self.log_dir = log_dir
        self._ensure_log_dir()
    
    def _ensure_log_dir(self):
        """Create log directory if it doesn't exist"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def log_query(self, session_id: str, query_info: Dict[str, Any]) -> str:
        """Log a query to a session-specific file"""
        try:
            # Create session file path
            session_file = os.path.join(self.log_dir, f"session_{session_id}.json")
            
            # Load existing queries or create new list
            queries = self._load_session_queries(session_file)
            
            # Add timestamp and query info
            query_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_query": query_info.get("user_query", ""),
                "sql_query": query_info.get("sql_query", ""),
                "query_type": query_info.get("query_type", "unknown"),
                "generated_by": query_info.get("generated_by", "unknown"),
                "explanation": query_info.get("explanation", ""),
                "execution_time": query_info.get("execution_time", 0),
                "rows_returned": query_info.get("rows_returned", 0),
                "success": query_info.get("success", True)
            }
            
            queries.append(query_entry)
            
            # Save to file
            with open(session_file, 'w') as f:
                json.dump(queries, f, indent=2)
            
            logger.info(f"Query logged to session {session_id}")
            return session_file
            
        except Exception as e:
            logger.error(f"Error logging query: {e}")
            return ""
    
    def _load_session_queries(self, session_file: str) -> List[Dict[str, Any]]:
        """Load existing queries from session file"""
        try:
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading session queries: {e}")
            return []
    
    def get_session_queries(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all queries for a session"""
        session_file = os.path.join(self.log_dir, f"session_{session_id}.json")
        return self._load_session_queries(session_file)
    
    def get_all_sessions(self) -> List[str]:
        """Get list of all session IDs"""
        try:
            files = os.listdir(self.log_dir)
            sessions = []
            for file in files:
                if file.startswith("session_") and file.endswith(".json"):
                    session_id = file.replace("session_", "").replace(".json", "")
                    sessions.append(session_id)
            return sorted(sessions)
        except Exception as e:
            logger.error(f"Error getting sessions: {e}")
            return []
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary statistics for a session"""
        queries = self.get_session_queries(session_id)
        if not queries:
            return {"total_queries": 0, "successful_queries": 0, "failed_queries": 0}
        
        total = len(queries)
        successful = sum(1 for q in queries if q.get("success", True))
        failed = total - successful
        
        return {
            "total_queries": total,
            "successful_queries": successful,
            "failed_queries": failed,
            "success_rate": (successful / total) * 100 if total > 0 else 0
        }
