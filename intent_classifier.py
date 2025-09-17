"""
Intent Classification System for Two-Agent Routing
Routes queries to Conversational Agent (no consent) or Data Agent (requires consent)
"""
import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class IntentClassifier:
    """Classifies user queries to determine which agent should handle them"""
    
    def __init__(self):
        # Keywords that indicate data access is needed
        self.data_keywords = [
            # Possessive indicators
            "my", "our", "show me", "get my", "display my", "fetch my",
            
            # Specific data requests
            "campaign", "campaigns", "performance", "spend", "cost", "budget",
            "conversions", "clicks", "impressions", "ctr", "cvr", "cpc", "cpa",
            "roi", "return", "revenue", "sales", "leads",
            
            # Analysis requests
            "analyze", "analysis", "compare", "comparison", "trends", "trend",
            "insights", "report", "reports", "metrics", "kpi", "kpis",
            "breakdown", "distribution", "summary", "overview",
            
            # Action requests
            "pause", "stop", "resume", "start", "increase", "decrease", 
            "optimize", "optimization", "create", "launch", "modify", 
            "update", "change", "adjust", "set", "configure",
            
            # Specific queries
            "which", "what are my", "how many of my", "find my",
            "list my", "show my", "get my", "pull my"
        ]
        
        # Keywords that indicate general knowledge questions
        self.general_keywords = [
            "what is", "what are", "how to", "how do", "explain", "define",
            "best practice", "best practices", "should i", "recommend",
            "tips", "strategy", "help me understand", "tell me about",
            "difference between", "compare", "vs", "versus",
            "industry", "benchmark", "standard", "typical", "average"
        ]
        
        # Phrases that are definitely general knowledge
        self.general_phrases = [
            "what is ctr", "what is cpc", "what is cpa", "what is roi",
            "how to improve", "how to optimize", "best practices",
            "marketing strategy", "campaign strategy", "advertising tips",
            "digital marketing", "performance marketing", "marketing analytics"
        ]
    
    def classify_intent(self, user_query: str) -> Dict[str, Any]:
        """
        Classify user query and return routing decision
        
        Returns:
            {
                "agent": "conversational" | "data",
                "confidence": float (0-1),
                "reasoning": str,
                "requires_consent": bool
            }
        """
        query_lower = user_query.lower().strip()
        
        # Handle empty or very short queries
        if len(query_lower.split()) < 2:
            return {
                "agent": "conversational",
                "confidence": 0.7,
                "reasoning": "Query too short, defaulting to conversational",
                "requires_consent": False
            }
        
        # Check for explicit general knowledge phrases first
        for phrase in self.general_phrases:
            if phrase in query_lower:
                return {
                    "agent": "conversational",
                    "confidence": 0.95,
                    "reasoning": f"Contains general knowledge phrase: '{phrase}'",
                    "requires_consent": False
                }
        
        # Count data and general keyword matches
        data_matches = sum(1 for keyword in self.data_keywords if keyword in query_lower)
        general_matches = sum(1 for keyword in self.general_keywords if keyword in query_lower)
        
        # Calculate confidence based on keyword matches
        total_keywords = data_matches + general_matches
        
        if total_keywords == 0:
            # No clear keywords - use heuristics
            return self._classify_by_heuristics(query_lower)
        
        # Calculate confidence
        data_confidence = data_matches / total_keywords if total_keywords > 0 else 0
        general_confidence = general_matches / total_keywords if total_keywords > 0 else 0
        
        # Make decision based on confidence
        if data_confidence > general_confidence:
            confidence = data_confidence
            agent = "data"
            reasoning = f"Data keywords: {data_matches}, General keywords: {general_matches}"
            requires_consent = True
        else:
            confidence = general_confidence
            agent = "conversational"
            reasoning = f"General keywords: {general_matches}, Data keywords: {data_matches}"
            requires_consent = False
        
        return {
            "agent": agent,
            "confidence": confidence,
            "reasoning": reasoning,
            "requires_consent": requires_consent
        }
    
    def _classify_by_heuristics(self, query_lower: str) -> Dict[str, Any]:
        """Use heuristics when no clear keywords are found"""
        
        # Check for question words at the beginning
        question_words = ["what", "how", "why", "when", "where", "which", "who"]
        starts_with_question = any(query_lower.startswith(word) for word in question_words)
        
        # Check for possessive pronouns
        has_possessive = any(pronoun in query_lower for pronoun in ["my", "our", "your"])
        
        # Check query length
        word_count = len(query_lower.split())
        
        if has_possessive:
            return {
                "agent": "data",
                "confidence": 0.8,
                "reasoning": "Contains possessive pronoun, likely requesting personal data",
                "requires_consent": True
            }
        
        if starts_with_question and word_count > 4:
            return {
                "agent": "conversational",
                "confidence": 0.7,
                "reasoning": "Complex question without data indicators",
                "requires_consent": False
            }
        
        # Default to conversational for ambiguous cases
        return {
            "agent": "conversational",
            "confidence": 0.6,
            "reasoning": "Ambiguous query, defaulting to conversational",
            "requires_consent": False
        }
    
    def get_consent_details(self, user_query: str) -> Dict[str, Any]:
        """
        Generate detailed consent information for data agent queries
        
        Returns:
            {
                "action_description": str,
                "tools_required": List[str],
                "data_access": List[str],
                "impact_analysis": str
            }
        """
        query_lower = user_query.lower()
        
        # Determine action type
        if any(word in query_lower for word in ["pause", "stop", "resume", "start"]):
            action_type = "campaign_control"
            tools = ["databricks_query", "campaign_controller"]
            data_access = ["campaign status", "campaign performance"]
            impact = "This will modify campaign status and may affect ongoing advertising performance."
        
        elif any(word in query_lower for word in ["increase", "decrease", "change", "adjust", "set"]):
            action_type = "budget_management"
            tools = ["databricks_query", "budget_manager"]
            data_access = ["campaign budgets", "campaign performance"]
            impact = "This will modify campaign budgets and may affect spend allocation."
        
        elif any(word in query_lower for word in ["optimize", "optimization"]):
            action_type = "optimization"
            tools = ["databricks_query", "performance_analyzer", "optimization_engine"]
            data_access = ["campaign performance", "reports data"]
            impact = "This will analyze performance and may suggest or implement optimizations."
        
        else:
            action_type = "data_analysis"
            tools = ["databricks_query", "performance_analyzer"]
            data_access = ["campaign data", "reports data"]
            impact = "This will query and analyze your campaign data for insights."
        
        return {
            "action_description": f"Execute {action_type.replace('_', ' ')} for your query",
            "tools_required": tools,
            "data_access": data_access,
            "impact_analysis": impact
        }

# Global instance
intent_classifier = IntentClassifier()

def classify_user_intent(query: str) -> Dict[str, Any]:
    """Convenience function to classify user intent"""
    return intent_classifier.classify_intent(query)

def get_consent_info(query: str) -> Dict[str, Any]:
    """Convenience function to get consent details"""
    return intent_classifier.get_consent_details(query)



