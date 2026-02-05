import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from core.market_logic import MarketAnalyzer
import pandas as pd

st.set_page_config(page_title="Macro Market Dashboard", layout="wide")

@st.cache_data(ttl=3600)
def get_analysis():
    analyzer = MarketAnalyzer()
    return analyzer.analyze_market_status()

def main():
    st.title("🛡️ 宏观市场战法看板")
    st.markdown("基于 **五步宏观研判法** (资金、情绪、趋势、时机、风格) 的市场全景监测。")
    
    with st.spinner("正在分析市场数据 (Baostock)..."):
        data = get_analysis()
        
    if "error" in data:
        st.error(data["error"])
        return

    st.header(f"📅 分析日期: {data['date'].strftime('%Y-%m-%d')}")

    # Helper to display multi-board metrics
    def display_board_metrics(metric_key, title, formatter=None):
        st.subheader(title)
        cols = st.columns(3)
        for i, (key, info) in enumerate(data["boards"].items()):
            if "error" in info: continue
            
            metric = info[metric_key]
            value = metric['value'] if 'value' in metric else metric['score'] if 'score' in metric else metric.get('status')
            
            # Custom formatting
            display_val = value
            if formatter:
                display_val = formatter(value, metric)
                
            delta_color = "normal"
            if metric_key == "sentiment": # Inverse logic for panic
                delta_color = "inverse"
                
            cols[i].metric(
                label=f"{info['name']}",
                value=metric['status'],
                delta=display_val,
                delta_color=delta_color
            )

    # --- Summary Metrics (Summary Grid) ---
    st.markdown("### 📊 市场核心信号")
    
    # 1. Trend & Funding Row
    col1, col2 = st.columns(2)
    with col1:
        st.info("**1. 趋势 (Trend)**: 价格在EMA200之上为牛，之下为熊。", icon="🧭")
        cols = st.columns(3)
        for i, (key, info) in enumerate(data["boards"].items()):
            cols[i].metric(info['name'], info['trend']['status'], f"现价: {info['trend']['current_price']:.0f}")
            
    with col2:
        st.info("**2. 资金 (Funding)**: 成交量对比20日均量。放量上涨更可靠。", icon="💧")
        cols = st.columns(3)
        for i, (key, info) in enumerate(data["boards"].items()):
            vol_show = f"{info['funding']['value']/1e8:.1f}亿"
            cols[i].metric(info['name'], info['funding']['status'], vol_show)

    st.divider()

    # 2. Sentiment & Timing Row
    col3, col4 = st.columns(2)
    with col3:
        st.info("**3. 情绪 (Sentiment)**: 乖离率(Bias)。>5%过热(风险), <-5%冰点(机会)。", icon="🌡️")
        cols = st.columns(3)
        for i, (key, info) in enumerate(data["boards"].items()):
            cols[i].metric(info['name'], info['sentiment']['status'], f"{info['sentiment']['score']:.1f}%", delta_color="inverse")

    with col4:
        st.info("**4. 时机 (Timing)**: 波动率收敛(变盘点)。K线振幅极度压缩后往往有大行情。", icon="⏱️")
        cols = st.columns(3)
        for i, (key, info) in enumerate(data["boards"].items()):
            cols[i].metric(info['name'], info['timing']['status'], f"排名: {info['timing']['volatility_rank']:.2f}", delta_color="inverse")

    st.divider()

    # 3. Style Row
    st.info("**5. 风格 (Style)**: 创业板指 vs 上证指数。趋势向上代表资金偏好成长/科技，向下代表偏好价值/防守。", icon="⚔️")
    style = data['style']
    if "error" not in style:
        st.metric("本期主线建议", style['suggestion'], f"趋势: {style['trend']} (RS值: {style['rs_value']:.2f})")
    else:
        st.warning("风格数据不足")

    st.divider()
    
    # --- Detailed Charts ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["资金水位", "市场情绪", "趋势方向", "变盘时机", "风格轮动"])
    
    # Chart Helper
    def plot_board_charts(chart_func):
        b_tabs = st.tabs([b['name'] for b in data['boards'].values()])
        for i, (key, info) in enumerate(data['boards'].items()):
            with b_tabs[i]:
                chart_func(info['data'], info)

    with tab1:
        st.markdown("""
        **使用说明**:
        *   **关注点**: 成交量柱状图 (Volume) 是否超过橙色均线 (MA20)。
        *   **含义**: 
            *   **放量**: 市场活跃，资金进场，上涨动力足。
            *   **缩量**: 市场观望，存量博弈，上涨可能乏力。
        """)
        def chart_funding(df, info):
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='成交量', marker_color='teal'))
            fig.add_trace(go.Scatter(x=df.index, y=df['volume'].rolling(20).mean(), name='20日均量', line=dict(color='orange')))
            st.plotly_chart(fig, use_container_width=True)
        plot_board_charts(chart_funding)
        
    with tab2:
        st.markdown("""
        **使用说明**:
        *   **关注点**: 蓝色曲线 (乖离率) 的位置。
        *   **含义**: 
            *   **> 5% (红色虚线)**: 市场**过热**，短期获利盘多，有回调风险 (贪婪时刻)。
            *   **< -5% (蓝色虚线)**: 市场**冰点**，超卖严重，可能有反弹机会 (恐慌时刻)。
            *   **0轴附近**: 情绪平稳。
        """)
        def chart_sentiment(df, info):
            ma20 = df['close'].rolling(20).mean()
            bias = (df['close'] - ma20) / ma20 * 100
            fig = px.line(x=df.index, y=bias, labels={'x': '日期', 'y': '乖离率 (%)'})
            fig.add_hline(y=5, line_dash="dash", line_color="red", annotation_text="过热警戒")
            fig.add_hline(y=-5, line_dash="dash", line_color="blue", annotation_text="冰点机会")
            st.plotly_chart(fig, use_container_width=True)
        plot_board_charts(chart_sentiment)

    with tab3:
        st.markdown("""
        **使用说明**:
        *   **关注点**: K线与蓝色粗线 (EMA200) 的关系。
        *   **含义**: 
            *   **K线在EMA200之上**: **牛市**格局，以持股做多为主，回踩均线是买点。
            *   **K线在EMA200之下**: **熊市**格局，以空仓防守为主，反弹触碰均线是卖点。
        """)
        def chart_trend(df, info):
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index,
                            open=df['open'], high=df['high'],
                            low=df['low'], close=df['close'], name='K线'))
            fig.add_trace(go.Scatter(x=df.index, y=df['close'].ewm(span=200, adjust=False).mean(), name='EMA200牛熊线', line=dict(color='blue', width=2)))
            fig.update_layout(xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        plot_board_charts(chart_trend)

    with tab4:
        st.markdown("""
        **使用说明**:
        *   **关注点**: 波动率曲线 (Volatility) 是否处于历史低位。
        *   **含义**: 
            *   **低位 (波动率收敛)**: 市场经历了长时间横盘，正如“暴风雨前的宁静”，**即将变盘** (选择方向大涨或大跌)。
            *   **高位 (波动率发散)**: 市场正在剧烈波动中，风险较大。
        """)
        def chart_timing(df, info):
            vol = df['pctChg'].rolling(20).std()
            fig = px.area(x=df.index, y=vol, labels={'x': '日期', 'y': '波动率 (标准差)'})
            st.plotly_chart(fig, use_container_width=True)
        plot_board_charts(chart_timing)

    with tab5:
        st.markdown("""
        **使用说明**:
        *   **关注点**: 相对强弱曲线 (RS Line) 的走势。
        *   **含义**: 
            *   **曲线向上**: **创业板 (成长/科技)** 强于大盘，资金在进攻，适合配置科技成长股。
            *   **曲线向下**: **上证 (价值/蓝筹)** 强于创业板，资金在防守，适合配置红利、资源股。
        """)
        if "error" not in data['style']:
            rs = data['style']['rs_line']
            fig_style = px.line(x=rs.index, y=rs, labels={'x': '日期', 'y': '相对强弱 (创业板/上证)'})
            st.plotly_chart(fig_style, use_container_width=True)
        else:
            st.write("暂无数据")

if __name__ == "__main__":
    main()
