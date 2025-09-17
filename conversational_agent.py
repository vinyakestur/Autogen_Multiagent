"""
Conversational Agent - Handles general marketing questions without data access
No consent required - pure LLM responses
"""
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from config import ANTHROPIC_CONFIG
import logging

logger = logging.getLogger(__name__)

class ConversationalAgent:
    """Handles general marketing questions using LLM knowledge only"""
    
    def __init__(self):
        self.llm = ChatAnthropic(
            anthropic_api_key=ANTHROPIC_CONFIG["api_key"],
            model_name=ANTHROPIC_CONFIG["model"],
            temperature=0.3  # Lower temperature for more consistent responses
        )
        
        self.system_prompt = """You are a marketing analytics expert and consultant. You provide helpful, educational responses about marketing concepts, strategies, and best practices.

Your expertise includes:
- Marketing metrics and KPIs (CTR, CPC, CPA, ROI, CVR, etc.)
- Digital marketing channels (Search, Display, Video, Social)
- Campaign optimization strategies
- Marketing attribution and analytics
- Industry benchmarks and best practices
- Marketing automation and tools
- Performance marketing concepts

Guidelines:
1. Provide clear, actionable advice
2. Use specific examples when helpful
3. Include industry benchmarks when relevant
4. Explain complex concepts in simple terms
5. Always be professional and helpful
6. If asked about specific campaigns or data, explain that you'd need access to their actual data to provide specific insights

IMPORTANT: You do NOT have access to the user's actual campaign data. If they ask about their specific campaigns, performance, or data, politely explain that you can provide general guidance but would need access to their actual data for specific insights."""

    async def respond(self, user_query: str) -> Dict[str, Any]:
        """
        Generate a response to a general marketing question
        
        Returns:
            {
                "response": str,
                "agent": "conversational",
                "consent_required": False,
                "response_type": "general_knowledge"
            }
        """
        try:
            logger.info(f"Conversational agent processing: {user_query}")
            
            # Create messages for the LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_query)
            ]
            
            # Get response from LLM
            response = self.llm.invoke(messages)
            
            return {
                "response": response.content,
                "agent": "conversational",
                "consent_required": False,
                "response_type": "general_knowledge",
                "tools_used": []
            }
            
        except Exception as e:
            logger.error(f"Error in conversational agent: {e}")
            return {
                "response": "I apologize, but I'm having trouble processing your request right now. Please try rephrasing your question or ask me about marketing concepts and best practices.",
                "agent": "conversational",
                "consent_required": False,
                "response_type": "error",
                "tools_used": []
            }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return information about what this agent can do"""
        return {
            "agent_type": "conversational",
            "capabilities": [
                "Explain marketing concepts and definitions",
                "Provide best practices and strategies",
                "Share industry benchmarks and standards",
                "Offer campaign optimization advice",
                "Explain marketing metrics and KPIs",
                "Discuss marketing channels and tactics",
                "Provide general marketing guidance"
            ],
            "limitations": [
                "Cannot access your actual campaign data",
                "Cannot analyze your specific performance",
                "Cannot make changes to your campaigns",
                "Cannot provide personalized insights"
            ],
            "consent_required": False
        }

# Global instance
conversational_agent = ConversationalAgent()

async def get_conversational_response(query: str) -> Dict[str, Any]:
    """Convenience function to get conversational response"""
    return await conversational_agent.respond(query)
