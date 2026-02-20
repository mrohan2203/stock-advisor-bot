import os
from groq import Groq
from dotenv import load_dotenv
from tools.stock_data import get_stock_stats
from tools.news_sentiment import get_sentiment
from agents.prompts import SYSTEM_PROMPT, get_analysis_prompt

load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_stock(ticker):
    # 1. Fetch data from your existing tools
    stats = get_stock_stats(ticker)
    sentiment = get_sentiment(ticker)
    
    if "error" in stats:
        return "I couldn't find data for that ticker. Please check the symbol."

    # 2. Call Groq (OpenAI-compatible syntax)
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": get_analysis_prompt(ticker, stats, sentiment)}
            ],
            temperature=0.2, # Low temperature for factual financial analysis
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error connecting to Groq: {str(e)}"