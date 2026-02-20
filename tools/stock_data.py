import yfinance as yf

def get_stock_stats(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo")
    if hist.empty: return {"error": "Invalid Ticker"}
    
    current_price = hist['Close'].iloc[-1]
    ma_20 = hist['Close'].mean()
    
    return {
        "symbol": ticker.upper(),
        "price": round(current_price, 2),
        "ma_20": round(ma_20, 2),
        "trend": "Bullish" if current_price > ma_20 else "Bearish"
    }