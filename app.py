import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from core.market_logic import MarketAnalyzer
import pandas as pd
import os

st.set_page_config(page_title="Macro Market Dashboard (Real-time + AI)", layout="wide", page_icon="📈")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Try to get from secrets first
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("API Key loaded from Secrets")
    else:
        api_key = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API Key for smart analysis.")
    
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key

    # Model Selection: Hardcoded to Gemini 3 Pro as requested
    model_name = "gemini-3-pro-preview"
    
    st.info("Data Sources:\n- Quotes: Tencent Finance (Real-time)\n- Macro: AkShare (Daily/Monthly)\n- Analysis: Gemini 3 Pro")

@st.cache_data(ttl=60) # Cache for 60 seconds for real-time feel
def get_analysis(key=None, model="gemini-3-pro-preview"):
    # Pass key to analyzer
    analyzer = MarketAnalyzer(api_key=key, model_name=model)
    return analyzer.analyze_market_status()

def main():
    st.title("🛡️ A股宏观战法看板 (Live)")
    st.markdown("### 💡 智能宏观点评 (AI Insight)")
    
    with st.spinner("正在拉取实时数据并进行AI分析..."):
        # Use session state to store key if needed, or just pass from sidebar
        data = get_analysis(
            key=api_key if 'api_key' in locals() and api_key else None, 
            model=model_name if 'model_name' in locals() and model_name else "gemini-3-pro-preview"
        )
        
    if "error" in data:
        st.error(data["error"])
        return

    # AI Section
    if "ai_commentary" in data:
        st.success(data["ai_commentary"], icon="🤖")

    st.divider()

    # Macro & Liquidity Section
    st.subheader("1. 宏观流动性 (Liquidity)")
    macro = data.get("macro", {})
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric("两融余额 (Margin Balance)", f"{macro.get('margin', {}).get('margin_balance', 0):.2f}亿", help="融资+融券余额，代表杠杆资金情绪")
    with m_col2:
        st.metric("M1-M2 剪刀差", f"{cutoff:.2f}%", delta_color="normal" if cutoff > 0 else "inverse", help="M1同比 - M2同比。负值扩大代表流动性陷阱。")
    st.caption("数据来源: 两融数据 (沪深交易所 via AkShare) / 货币供应 (中国人民银行 via AkShare)")

    st.divider()

    st.subheader(f"2. 市场全景 (Snapshot) - {data['date'].strftime('%Y-%m-%d %H:%M') if data['date'] else 'N/A'}")
    
    # Grid for Boards
    cols = st.columns(3)
    for i, (key, info) in enumerate(data["boards"].items()):
        if "error" in info: continue
        
        # Real-time Price
        trend = info['trend']
        price = trend['current_price']
        ema = trend['ema200']
        
        # Determine color by Trend
        trend_color = "normal" if price > ema else "inverse"
        
        cols[i].metric(
            label=f"{info['name']}",
            value=f"{price:.2f}",
            delta=f"EMA200: {ema:.2f} ({trend['status']})",
            delta_color=trend_color
        )

    # --- Indicators Grid ---
    st.markdown("### 📊 核心指标矩阵")
    
    # 1. Funding & Sentiment
    col1, col2 = st.columns(2)
    with col1:
        st.info("**资金与情绪**", icon="🌊")
        i_cols = st.columns(3)
        for i, (key, info) in enumerate(data["boards"].items()):
            if "error" in info: continue
            # Funding
            fund = info['funding']
            i_cols[i].metric(info['name'], fund['status'], f"Vol: {fund['value']/10000:.0f}万手")
            
    with col2:
        st.info("**恐慌与时机**", icon="⚡")
        i_cols = st.columns(3)
        for i, (key, info) in enumerate(data["boards"].items()):
            if "error" in info: continue
            # Sentiment / Panic
            sent = info['sentiment']
            i_cols[i].metric(info['name'], sent['status'], f"Bias: {sent['score']:.2f}%", delta_color="inverse")

    st.divider()
    
    # --- Detailed Charts ---
    tab1, tab2, tab3 = st.tabs(["趋势与K线", "资金成交量", "风格轮动"])
    
    # Chart Helper
    def plot_board_charts(chart_func):
        # Only create tabs for valid boards
        valid_boards = [info for key, info in data['boards'].items() if "error" not in info]
        if not valid_boards:
            st.warning("暂无有效市场数据")
            return
            
        b_tabs = st.tabs([b['name'] for b in valid_boards])
        for i, info in enumerate(valid_boards):
            with b_tabs[i]:
                chart_func(info['data'], info)

    with tab1:
        st.caption("蓝色线为EMA200牛熊分界线。线上做多，线下防守。")
        def chart_trend(df, info):
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index,
                            open=df['open'], high=df['high'],
                            low=df['low'], close=df['close'], name='K线'))
            fig.add_trace(go.Scatter(x=df.index, y=df['close'].ewm(span=200, adjust=False).mean(), name='EMA200', line=dict(color='blue', width=2)))
            fig.update_layout(xaxis_rangeslider_visible=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        plot_board_charts(chart_trend)
        
    with tab2:
        st.caption("橙色线为20日均量线。")
        def chart_funding(df, info):
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='成交量', marker_color='teal'))
            fig.add_trace(go.Scatter(x=df.index, y=df['volume'].rolling(20).mean(), name='MA20', line=dict(color='orange')))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        plot_board_charts(chart_funding)
        
    with tab3:
        if "error" not in data['style']:
            style = data['style']
            st.metric("当前主线", style['suggestion'], f"趋势: {style['trend']}")
            rs = style['rs_line']
            fig_style = px.line(x=rs.index, y=rs, labels={'x': '日期', 'y': '相对强弱 (创业板/沪指)'})
            st.plotly_chart(fig_style, use_container_width=True)
        else:
            st.write("数据不足")

if __name__ == "__main__":
    main()
