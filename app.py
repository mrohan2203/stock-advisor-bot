import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import re
import io
from fpdf import FPDF
from agents.orchestrator import analyze_stock
from tools.stock_data import get_stock_stats
from tools.news_sentiment import get_sentiment

# --- 1. PDF GENERATION UTILITIES ---
def clean_text(text):
    """Removes emojis and non-Latin-1 characters to prevent FPDF errors."""
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.replace("#", "").replace("*", "").strip()

def generate_pdf_report(ticker, stats, sentiment, report_text, fig):
    """Creates a clean PDF with metrics, AI summary, and the price chart."""
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, f"Executive Stock Report: {ticker}", ln=True, align='C')
    pdf.ln(5)
    
    # Key Metrics Table
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "Market Snapshot", ln=True)
    pdf.set_font("Helvetica", size=10)
    
    metrics = [
        f"Current Price: ${stats['price']}",
        f"20-Day MA: ${stats['ma_20']}",
        f"Technical Signal: {stats['trend']}",
        f"Sentiment: {sentiment}"
    ]
    for metric in metrics:
        pdf.cell(0, 7, f"- {metric}", ln=True)
    
    pdf.ln(5)
    
    # Extract 'The Bottom Line' from AI report
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "The Bottom Line", ln=True)
    pdf.set_font("Helvetica", size=10)
    
    if "Bottom Line" in report_text:
        bottom_line = report_text.split("Bottom Line")[-1].split("Key Drivers")[0]
        pdf.multi_cell(0, 7, clean_text(bottom_line))
    else:
        pdf.multi_cell(0, 7, clean_text(report_text[:300]) + "...")

    # Embed the Chart
    try:
        img_bytes = fig.to_image(format="png")
        pdf.image(io.BytesIO(img_bytes), x=10, y=pdf.get_y() + 10, w=190)
    except:
        pdf.cell(0, 10, "(Visual chart could not be embedded)", ln=True)
    
    return bytes(pdf.output())

# --- 2. STREAMLIT UI SETUP ---
st.set_page_config(page_title="AI Market Intelligence", layout="wide")

# Initialize Session State
if 'ai_report' not in st.session_state:
    st.session_state.ai_report = None
if 'current_ticker' not in st.session_state:
    st.session_state.current_ticker = None
if 'stats' not in st.session_state:
    st.session_state.stats = None

with st.sidebar:
    st.title("🎯 Controls")
    # Manual input or Selectbox
    ticker = st.text_input("Enter Ticker:", value="AAPL").upper()
    analyze_btn = st.button("Generate Full Analysis", use_container_width=True)
    st.divider()
    st.caption("⚡ Engine: Groq Llama 3.3 70B")

st.title(f"📊 {ticker} Intelligence Dashboard")

# Execute Full Analysis Only on Button Click
if analyze_btn:
    with st.spinner("Fetching data and generating AI insights..."):
        st.session_state.stats = get_stock_stats(ticker)
        st.session_state.sentiment = get_sentiment(ticker)
        st.session_state.ai_report = analyze_stock(ticker)
        st.session_state.current_ticker = ticker

# Only display if data exists in state and matches current ticker
if st.session_state.ai_report and st.session_state.current_ticker == ticker:
    stats = st.session_state.stats
    sentiment_label = st.session_state.sentiment
    
    # --- ROW 1: PRIMARY KPI BANNER ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Current Price", f"${stats['price']}")
    ma_diff = round(stats['price'] - stats['ma_20'], 2)
    m2.metric("vs 20-Day MA", f"${stats['ma_20']}", f"{ma_diff}")
    trend_color = "green" if stats['trend'] == "Bullish" else "red"
    m3.metric("Technical Signal", stats['trend'])
    m4.metric("Sentiment", sentiment_label)

    st.divider()

    # --- ROW 2: VISUALS (DYNAMIC) & REPORT (STATIC) ---
    left_col, right_col = st.columns([1.5, 1])

    with left_col:
        # Time Range Selector: Updates Chart ONLY
        time_range = st.radio(
            "Chart Timeframe:", 
            ["1D", "1W", "1M", "6M", "1Y", "5Y"], 
            horizontal=True, 
            index=2
        )
        
        range_map = {
            "1D": {"p": "1d", "i": "1m"}, "1W": {"p": "5d", "i": "30m"},
            "1M": {"p": "1mo", "i": "1d"}, "6M": {"p": "6mo", "i": "1d"},
            "1Y": {"p": "1y", "i": "1wk"}, "5Y": {"p": "5y", "i": "1mo"}
        }
        
        config = range_map[time_range]
        hist_data = yf.Ticker(ticker).history(period=config["p"], interval=config["i"])
        
        # Enhanced Subplot Chart
        hist_data['SMA20'] = hist_data['Close'].rolling(window=20).mean()
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.05, row_heights=[0.7, 0.3])

        fig.add_trace(go.Candlestick(
            x=hist_data.index, open=hist_data['Open'],
            high=hist_data['High'], low=hist_data['Low'],
            close=hist_data['Close'], name="Price"
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=hist_data.index, y=hist_data['SMA20'],
            line=dict(color='orange', width=2), name="20-Day SMA"
        ), row=1, col=1)

        vol_colors = ['#26a69a' if c >= o else '#ef5350' for o, c in zip(hist_data['Open'], hist_data['Close'])]
        fig.add_trace(go.Bar(
            x=hist_data.index, y=hist_data['Volume'],
            marker_color=vol_colors, name="Volume"
        ), row=2, col=1)

        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500, margin=dict(t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.subheader("🤖 Advisor's Take")
        st.markdown(f"### **Outlook: :{trend_color}[{stats['trend'].upper()}]**")
        
        with st.container(border=True):
            st.markdown(st.session_state.ai_report)
        
        # PDF Generation
        pdf_data = generate_pdf_report(ticker, stats, sentiment_label, st.session_state.ai_report, fig)
        st.download_button(
            label="📄 Download PDF Summary",
            data=pdf_data,
            file_name=f"{ticker}_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        with st.expander("ℹ️ Risk Assessment & Disclaimers"):
            st.caption("Investment involves risk. Analysis for educational purposes only.")
else:
    st.info("👈 Enter a ticker and click 'Generate Full Analysis' to load the dashboard.")
