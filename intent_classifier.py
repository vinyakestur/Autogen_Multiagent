"""
Simple Intent Classifier for Direct API
Classifies user queries as conversational or data-related
"""
import re

def classify_user_intent(message: str) -> str:
    """
    Classify user intent based on message content
    
    Args:
        message: User's input message
        
    Returns:
        'conversational' or 'data_query'
    """
    message_lower = message.lower().strip()
    
    # Conversational patterns (no data access needed)
    conversational_patterns = [
        r'\bwhat is\b',
        r'\bhow to\b',
        r'\bexplain\b',
        r'\btell me about\b',
        r'\bdefine\b',
        r'\bmeaning of\b',
        r'\bhelp\b',
        r'\bhow do i\b',
        r'\bwhat are\b',
        r'\bctr\b',
        r'\bcpc\b',
        r'\bcpm\b',
        r'\bcvr\b',
        r'\broi\b',
        r'\boptimize\b',
        r'\bimprove\b',
        r'\bbest practices\b',
        r'\btips\b',
        r'\badvice\b'
    ]
    
    # Data query patterns (requires data access)
    data_patterns = [
        r'\bshow me\b',
        r'\bdisplay\b',
        r'\blist\b',
        r'\bget\b',
        r'\bfind\b',
        r'\bsearch\b',
        r'\banalyze\b',
        r'\bcompare\b',
        r'\bmy\b.*\bcampaigns?\b',
        r'\bmy\b.*\bdata\b',
        r'\bmy\b.*\bperformance\b',
        r'\bmy\b.*\bbudget\b',
        r'\bmy\b.*\bmetrics\b',
        r'\btop\b.*\bperforming\b',
        r'\bbest\b.*\bcampaigns?\b',
        r'\bworst\b.*\bcampaigns?\b',
        r'\btrends?\b',
        r'\bover time\b',
        r'\bmonthly\b',
        r'\bweekly\b',
        r'\bdaily\b',
        r'\bbreakdown\b',
        r'\bsummary\b',
        r'\boverview\b',
        r'\bstatistics\b',
        r'\binsights\b',
        r'\bresults\b',
        r'\bgive me\b.*\bsummary\b',
        r'\bgive me\b.*\boverview\b',
        r'\bprovide\b.*\bsummary\b',
        r'\bprovide\b.*\boverview\b',
        r'\bmarketing\b.*\bdata\b',
        r'\bmarketing\b.*\bsummary\b',
        r'\bmarketing\b.*\boverview\b',
        r'\bmarketing\b.*\binsights\b',
        r'\bmarketing\b.*\banalysis\b',
        r'\bmarketing\b.*\bperformance\b',
        r'\bmarketing\b.*\bmetrics\b',
        r'\bmarketing\b.*\bstatistics\b'
    ]
    
    # Check for data patterns first (more specific)
    for pattern in data_patterns:
        if re.search(pattern, message_lower):
            return 'data_query'
    
    # Check for conversational patterns
    for pattern in conversational_patterns:
        if re.search(pattern, message_lower):
            return 'conversational'
    
    # Default to conversational for unclear intent
    return 'conversational'
