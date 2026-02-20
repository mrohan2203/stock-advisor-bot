import subprocess
import sys
from textblob import TextBlob

# --- 1. CLOUD INITIALIZATION ---
# This block handles the "hidden" corpora download required by Streamlit Cloud
try:
    # Attempt a basic sentiment call to check if corpora are present
    TextBlob("test").sentiment
except Exception:
    # If missing, trigger the download via a subprocess
    print("Downloading TextBlob corpora for cloud environment...")
    subprocess.run([sys.executable, "-m", "textblob.download_corpora"])

# --- 2. SENTIMENT ANALYSIS LOGIC ---
def get_sentiment(ticker):
    """
    Fetches news sentiment for a given ticker. 
    In a production app, you would fetch real news here.
    """
    # Example mock news for analysis (replace with real news API calls if needed)
    mock_news = [
        f"{ticker} hits all-time high as demand surges.",
        f"Analysts upgrade {ticker} following strong quarterly earnings.",
        f"Investors cautious about {ticker}'s exposure to supply chain issues."
    ]
    
    # Calculate polarity
    total_polarity = 0
    for headline in mock_news:
        blob = TextBlob(headline)
        total_polarity += blob.sentiment.polarity
    
    avg_polarity = total_polarity / len(mock_news)
    
    # Map polarity to human-readable labels
    if avg_polarity > 0.1:
        return "Positive"
    elif avg_polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"
