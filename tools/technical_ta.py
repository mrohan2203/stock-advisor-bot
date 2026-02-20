# tools/technical_ta.py
import pandas_ta as ta
import pandas as pd

def calculate_advanced_indicators(df):
    """Adds MACD and Bollinger Bands to the dataframe."""
    # Ensure we have enough data
    if len(df) < 30:
        return "Insufficient data for TA"

    # Calculate MACD
    macd = df.ta.macd(fast=12, slow=26, signal=9)
    
    # Calculate Bollinger Bands
    bbands = df.ta.bbands(length=20, std=2)
    
    latest_metrics = {
        "macd_line": macd['MACD_12_26_9'].iloc[-1],
        "macd_signal": macd['MACDs_12_26_9'].iloc[-1],
        "bb_upper": bbands['BBU_20_2.0'].iloc[-1],
        "bb_lower": bbands['BBL_20_2.0'].iloc[-1]
    }
    return latest_metrics