import json
import random

# Mock sentiment options for testing
SENTIMENT_OPTIONS = ["positive", "negative", "neutral"]

def build_prompt(content):
    """Build a prompt to send to an LLM."""
    return f"""
    Analyze the following article and return a JSON array of topics discussed and the sentiment for each.

    Example format:
    [
      {{"topic": "example topic", "sentiment": "positive | negative | neutral"}}
    ]

    Sample Topics:
    [
        "Politics", "Economy", "Healthcare", "Technology", "Climate Change"
    ]
    
    Article:
    {content}
    """

def mock_llm_response(content):
    """Simulate an LLM API response based on the input content."""
    # For mocking, picking a few fake topics
    sample_topics = ["Politics", "Economy", "Healthcare", "Technology", "Climate Change"]
    selected = random.sample(sample_topics, k=random.randint(1, 3))
    
    result = [{"topic": topic, "sentiment": random.choice(SENTIMENT_OPTIONS)} for topic in selected]
    return json.dumps(result)

def analyze_content_with_llm(content):
    """
    Main entry function:
    - Prepares prompt
    - Sends to LLM (mocked for now)
    - Parses the response into structured data
    """
    prompt = build_prompt(content)

    # Replace with real API call when needed
    response_str = mock_llm_response(content)

    try:
        analysis_result = json.loads(response_str)
        assert isinstance(analysis_result, list)
        return analysis_result
    except Exception as e:
        print(f"[LLM] Error parsing response: {e}")
        return []
