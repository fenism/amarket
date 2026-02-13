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

@st.cache_data(ttl=10) # Cache for 10 seconds for near real-time updates
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
        
        # Margin History Chart
        margin_hist = macro.get('margin', {}).get('history', None)
        if margin_hist is not None and not margin_hist.empty:
            # margin_hist has 'date' and 'total_balance' (in Yuan)
            # Convert to Billion for display consistent with metric
            df_chart = margin_hist.copy()
            df_chart['date'] = pd.to_datetime(df_chart['date'])
            df_chart['DisplayBalance'] = df_chart['total_balance'] / 1e8
            
            fig_margin = px.area(df_chart, x='date', y='DisplayBalance', 
                                 title="两融余额趋势 (近1年)", 
                                 labels={'DisplayBalance': '余额 (亿)', 'date': '日期'},
                                 height=300)
            
            # Add Threshold Line at 20000 (2 Trillion)
            fig_margin.add_hline(y=20000, line_dash="dash", line_color="red", 
                                 annotation_text="2万亿警戒线", annotation_position="top right")
            
            # Customize layout
            fig_margin.update_layout(margin=dict(l=0, r=0, t=30, b=0), hovermode="x unified")
            st.plotly_chart(fig_margin, use_container_width=True)

    with m_col2:
        cutoff = macro.get('money', {}).get('scissors', 0)
        
        # Determine market health status based on scissors gap
        if cutoff > 0:
            health_status = "✅ 健康区域"
            health_color = "green"
            health_desc = "M1>M2，资金活跃，市场健康"
        elif cutoff > -5:
            health_status = "⚠️ 观察区域"
            health_color = "orange"
            health_desc = "剪刀差收窄，关注流动性"
        else:
            health_status = "🚨 风险区域"
            health_color = "red"
            health_desc = "剪刀差倒挂，流动性陷阱风险"
        
        st.metric("M1-M2 剪刀差", f"{cutoff:.2f}%", delta_color="normal" if cutoff > 0 else "inverse", help="M1同比 - M2同比。负值扩大代表流动性陷阱。")
        st.markdown(f"**当前状态**: :{health_color}[{health_status}] - {health_desc}")
        
        # M1-M2 Scissors Historical Chart
        money_hist = macro.get('money', {}).get('history', None)
        if money_hist is not None and not money_hist.empty:
            fig_money = go.Figure()
            
            # Add background shading for zones (without text to avoid overlap)
            # Risk zone (scissors < -5%): Light red
            fig_money.add_hrect(y0=-100, y1=-5, fillcolor="rgba(255,0,0,0.1)", 
                               layer="below", line_width=0)
            
            # Warning zone (-5% to 0%): Light yellow
            fig_money.add_hrect(y0=-5, y1=0, fillcolor="rgba(255,255,0,0.1)", 
                               layer="below", line_width=0)
            
            # Healthy zone (scissors > 0%): Light green
            fig_money.add_hrect(y0=0, y1=100, fillcolor="rgba(0,255,0,0.1)", 
                               layer="below", line_width=0)
            
            # M1 YoY
            fig_money.add_trace(go.Scatter(
                x=money_hist['date'], 
                y=money_hist['m1_yoy'],
                name='M1同比%',
                line=dict(color='blue', width=1.5)
            ))
            
            # M2 YoY
            fig_money.add_trace(go.Scatter(
                x=money_hist['date'], 
                y=money_hist['m2_yoy'],
                name='M2同比%',
                line=dict(color='green', width=1.5)
            ))
            
            # Scissors (M1-M2)
            fig_money.add_trace(go.Scatter(
                x=money_hist['date'], 
                y=money_hist['scissors'],
                name='剪刀差 (M1-M2)',
                line=dict(color='red', width=2),
                fill='tozeroy'
            ))
            
            # Add threshold lines
            fig_money.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.7,
                               annotation_text="0% (健康线)", annotation_position="right")
            fig_money.add_hline(y=-5, line_dash="dot", line_color="orange", opacity=0.7,
                               annotation_text="-5% (警戒线)", annotation_position="right")
            
            fig_money.update_layout(
                title="M1-M2 剪刀差趋势 (资金面健康度)",
                height=300,
                margin=dict(l=0, r=0, t=30, b=0),
                hovermode="x unified",
                yaxis_title="%",
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig_money, use_container_width=True)
    st.caption("数据来源: 两融数据 (沪深交易所 via AkShare) / 货币供应 (中国人民银行 via AkShare)")

    st.divider()

    # Display last update time
    from datetime import datetime
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.subheader(f"2. 市场全景 (Snapshot) - {data['date'].strftime('%Y-%m-%d %H:%M') if data['date'] else 'N/A'}")
    st.caption(f"🔄 最后更新: {current_time} | 数据每10秒自动刷新")
    
    # Grid for Boards
    cols = st.columns(3)
    for i, (key, info) in enumerate(data["boards"].items()):
        if "error" in info: continue
        
        # Real-time Price
        trend = info['trend']
        price = trend['current_price']
        ema = trend['ema200']
        
        # Determine color by Trend (A-Share: Red=Up/Bull, Green=Down/Bear)
        # Streamlit 'inverse': Positive->Red, Negative->Green
        # Streamlit 'normal': Positive->Green, Negative->Red
        # Since our delta is a string, Streamlit usually treats it as positive unless it starts with -?
        # Let's force it by switching mode based on status.
        trend_color = "inverse" if price > ema else "normal"
        
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
            # Vol Up (放量) -> Red ('inverse'), Vol Down (缩量) -> Green ('normal')
            fund_color = "inverse" if fund['status'] == "放量" else "normal"
            i_cols[i].metric(info['name'], fund['status'], f"Vol: {fund['value']/10000:.0f}万手", delta_color=fund_color)
            
    with col2:
        st.info("**恐慌与时机**", icon="⚡")
        i_cols = st.columns(3)
        for i, (key, info) in enumerate(data["boards"].items()):
            if "error" in info: continue
            # Sentiment / Panic
            sent = info['sentiment']
            i_cols[i].metric(info['name'], sent['status'], f"Bias: {sent['score']:.2f}%", delta_color="inverse")
        st.caption("注：Bias (乖离率) = (当前价 - MA20)/MA20。>5%为过热(风险)，<-5%为恐慌(机会)。")
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
            # Convert index to string to avoid gap rendering issues if type=category doesn't work perfectly with datetimes
            # But usually type='category' is enough. 
            # To ensure clean labels, we can filter ticks.
            
            # Colors: Red Up, Green Down (A-Share style)
            fig.add_trace(go.Candlestick(x=df.index.strftime('%Y-%m-%d'), # Use string dates for categorical axis
                            open=df['open'], high=df['high'],
                            low=df['low'], close=df['close'], name='K线',
                            increasing_line_color='red', decreasing_line_color='green'))
                            
            fig.add_trace(go.Scatter(x=df.index.strftime('%Y-%m-%d'), 
                                     y=df['close'].ewm(span=200, adjust=False).mean(), 
                                     name='EMA200', 
                                     line=dict(color='blue', width=2)))
            
            # Layout: Remove gaps using category axis
            fig.update_layout(
                xaxis_rangeslider_visible=False, 
                height=400,
                xaxis=dict(
                    type='category', 
                    nticks=10, # Avoid overcrowding labels
                    tickangle=-45
                )
            )
            st.plotly_chart(fig, use_container_width=True)
        plot_board_charts(chart_trend)
        
    with tab2:
        st.caption("橙色线为20日均量线。显示最近90日成交量。")
        def chart_funding(df, info):
            # Filter to show only recent 90 days for better visualization
            df_display = df.tail(90)
            
            # Debug: Show data info
            if len(df_display) > 0:
                vol_min = df_display['volume'].min()
                vol_max = df_display['volume'].max()
                vol_mean = df_display['volume'].mean()
                zero_count = (df_display['volume'] == 0).sum()
                non_zero_count = (df_display['volume'] > 0).sum()
                
                st.info(f"📊 数据范围: {df_display.index.min().strftime('%Y-%m-%d')} 至 {df_display.index.max().strftime('%Y-%m-%d')} | 共 {len(df_display)} 个交易日")
                st.caption(f"🔍 成交量统计: 最小={vol_min:,.0f}, 最大={vol_max:,.0f}, 均值={vol_mean:,.0f} | 零值天数={zero_count}, 非零天数={non_zero_count}")
                
                # Check if data is problematic
                if zero_count > len(df_display) * 0.9:
                    st.error("❌ 数据异常: 90%以上的交易日成交量为0，请检查数据源")
                    return
            else:
                st.warning("⚠️ 无成交量数据")
                return
            
            # Filter out zero/null values for better visualization
            df_filtered = df_display[df_display['volume'] > 0].copy()
            
            if len(df_filtered) == 0:
                st.error("❌ 所有交易日成交量均为0")
                return
            
            st.caption(f"📈 实际绘制 {len(df_filtered)} 个非零成交量交易日")
            
            fig = go.Figure()
            
            # Volume Colors: Red if Close > Open, Green if Close <= Open
            # Need to iterate or use vector logic. 
            # Simple vector:
            colors = ['red' if c > o else 'green' for c, o in zip(df_filtered['close'], df_filtered['open'])]
            
            # Convert dates to string for categorical axis
            x_dates = df_filtered.index.strftime('%Y-%m-%d').tolist()
            
            fig.add_trace(go.Bar(
                x=x_dates, 
                y=df_filtered['volume'].tolist(), 
                name='成交量', 
                marker_color=colors,
                hovertemplate='日期: %{x}<br>成交量: %{y:,.0f} 手<extra></extra>'
            ))
                                 
            # Calculate MA20 on filtered data
            ma20_values = df_filtered['volume'].rolling(20, min_periods=1).mean()
            
            fig.add_trace(go.Scatter(
                x=x_dates, 
                y=ma20_values.tolist(), 
                name='MA20', 
                line=dict(color='orange', width=2),
                hovertemplate='日期: %{x}<br>MA20: %{y:,.0f}<extra></extra>'
            ))
                                     
            fig.update_layout(
                height=400,
                xaxis=dict(
                    type='category',
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.2)',
                    tickangle=-45,
                    # Ensure all dates are shown
                    tickmode='auto',
                    nticks=20
                ),
                yaxis=dict(
                    title='成交量 (手)',
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.2)',
                    rangemode='tozero'  # Start from zero
                ),
                title=f"成交量 (最近90日: {df_display.index.min().strftime('%Y-%m-%d')} ~ {df_display.index.max().strftime('%Y-%m-%d')}) - 单位: 手",
                hovermode='x unified',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                bargap=0.1  # Small gap between bars
            )
            st.plotly_chart(fig, use_container_width=True)
        plot_board_charts(chart_funding)
        
    with tab3:
        if "error" not in data['style']:
            style = data['style']
            st.metric("当前主线", style['suggestion'], f"趋势: {style['trend']}", delta_color="inverse")
            st.caption("逻辑: 相对强弱(RS) = 创业板/沪指。当RS位于均线(MA20)上方时，视为成长风格占优。")
            
            rs_line = style['rs_line']
            rs_ma20 = style.get('rs_ma20', None)
            
            fig_style = go.Figure()
            fig_style.add_trace(go.Scatter(x=rs_line.index, y=rs_line, name='RS (创业板/沪指)', line=dict(color='blue')))
            
            if rs_ma20 is not None:
                fig_style.add_trace(go.Scatter(x=rs_ma20.index, y=rs_ma20, name='MA20', line=dict(color='orange', width=1)))
                
            fig_style.update_layout(title="风格相对强弱趋势", height=350, hovermode="x unified")
            st.plotly_chart(fig_style, use_container_width=True)
        else:
            st.write("数据不足")

if __name__ == "__main__":
    main()
