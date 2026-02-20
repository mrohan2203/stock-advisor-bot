# tools/news_sentiment.py
import yfinance as yf
from textblob import TextBlob

def get_sentiment(ticker):
    """Scrapes news headlines and returns an average sentiment score."""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        if not news:
            return "Neutral (No recent news found)"
        
        # FIX: The new structure stores data inside a 'content' key
        # We use .get() to avoid crashing if a specific article is missing a title
        titles = []
        for n in news[:5]:
            # Try the new structure first, fall back to the old one
            content = n.get('content', n) 
            title = content.get('title', "")
            if title:
                titles.append(title)

        if not titles:
            return "Neutral (Could not parse headlines)"

        sentiments = [TextBlob(t).sentiment.polarity for t in titles]
        avg_score = sum(sentiments) / len(sentiments)
        
        if avg_score > 0.1: return "Positive"
        elif avg_score < -0.1: return "Negative"
        else: return "Neutral"

    except Exception as e:
        # Fallback so the whole bot doesn't crash if news fails
        return f"Neutral (Sentiment Error: {str(e)})"