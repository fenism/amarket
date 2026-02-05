from framework.data_loader import BaostockLoader
from core import indicators
import pandas as pd

class MarketAnalyzer:
    def __init__(self):
        self.loader = BaostockLoader()
        
    def analyze_market_status(self):
        """
        Main analysis function returning a dict of signal states for multiple boards.
        """
        try:
            # Define boards to analyze
            boards = {
                "sh": {"code": "sh.000001", "name": "上证指数"},
                "sz": {"code": "sz.399001", "name": "深证成指"},
                "cyb": {"code": "sz.399006", "name": "创业板指"}
            }
            
            results = {}
            latest_date = None
            
            # 1. Fetch Data & Analyze per board
            for key, info in boards.items():
                df = self.loader.fetch_index_data(info["code"], days=400)
                
                if df.empty:
                    results[key] = {"error": "Failed to fetch data"}
                    continue
                    
                # Ensure date index
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                
                if latest_date is None or df.index[-1] > latest_date:
                    latest_date = df.index[-1]
                    
                # --- Per Board Analysis ---
                
                # Step 1: Funding (Water) - Volume
                vol_ma20 = df['volume'].rolling(20).mean()
                current_vol = df['volume'].iloc[-1]
                funding = {
                    "value": current_vol,
                    "ma20": vol_ma20.iloc[-1],
                    "status": "放量" if current_vol > vol_ma20.iloc[-1] else "缩量",
                    "description": "成交量 vs 20日均量"
                }
                
                # Step 2: Sentiment (Temp) - Bias MA20
                price_ma20 = df['close'].rolling(20).mean()
                bias_20 = (df['close'] - price_ma20) / price_ma20 * 100
                score = bias_20.iloc[-1]
                sentiment_status = "过热" if score > 5 else ("冰点" if score < -5 else "中性")
                sentiment = {
                    "score": score,
                    "status": sentiment_status,
                    "description": "乖离率 (20日线)"
                }
                
                # Step 3: Trend (Direction) - EMA200
                ema200 = indicators.calculate_ema(df['close'], span=200)
                current_price = df['close'].iloc[-1]
                trend_status = "牛市" if current_price > ema200.iloc[-1] else "熊市"
                trend = {
                    "current_price": current_price,
                    "ema200": ema200.iloc[-1],
                    "status": trend_status,
                    "series": ema200
                }
                
                # Step 4: Timing (Vol)
                vol_series = indicators.calculate_volatility(df)
                is_contracting, rank = indicators.detect_volatility_contraction(vol_series)
                timing = {
                    "volatility_rank": rank,
                    "is_contracting": is_contracting,
                    "status": "即将变盘" if is_contracting else "波动扩大",
                    "description": "波动率收敛"
                }
                
                results[key] = {
                    "name": info["name"],
                    "data": df,
                    "funding": funding,
                    "sentiment": sentiment,
                    "trend": trend,
                    "timing": timing
                }

            # Step 5: Style (Relative Strength) - Global Calculation
            # Usually Main (Shanghai) vs Growth (ChiNext)
            if "sh" in results and "cyb" in results and "error" not in results["sh"] and "error" not in results["cyb"]:
                df_sh = results["sh"]["data"]
                df_cyb = results["cyb"]["data"]
                
                rs_line, rs_trend = indicators.calculate_relative_strength(df_cyb['close'], df_sh['close'])
                current_rs = rs_line.iloc[-1]
                prev_rs = rs_line.iloc[-2]
                
                direction = "成长/科技 (创业板)" if current_rs > prev_rs else "价值/蓝筹 (沪指)"
                
                style = {
                    "rs_value": current_rs,
                    "trend": "强化" if current_rs > prev_rs else "弱化",
                    "suggestion": direction,
                    "description": "创业板/沪指 相对强弱",
                    "rs_line": rs_line
                }
            else:
                style = {"error": "Insufficient data"}
                
            return {
                "date": latest_date,
                "boards": results,
                "style": style
            }
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}", "boards": {}, "style": {}}
