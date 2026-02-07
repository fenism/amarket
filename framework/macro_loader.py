import akshare as ak
import pandas as pd
from datetime import datetime

class MacroLoader:
    def __init__(self):
        pass

    def fetch_market_margin(self):
        """
        Fetch margin financing balance (financing + securities lending).
        Returns: {
            "date": str (YYYY-MM-DD),
            "margin_balance": float (in Billion CNY),
            "margin_net_buy": float (in Billion CNY)
        }
        """
        try:
            # AkShare interface for margin summary
            # Updated to match current API: stock_margin_sse / stock_margin_szse
            try:
                # SSE gives a range, so we get the latest valid trading day
                df_sh = ak.stock_margin_sse(start_date="20240101", end_date=datetime.now().strftime("%Y%m%d"))
                latest_sh = df_sh.iloc[-1]
                val_sh = float(latest_sh['融资余额'])
                # '信用交易日期' is usually YYYYMMDD (int or str)
                date_val = str(latest_sh['信用交易日期'])
                date_sh = f"{date_val[:4]}-{date_val[4:6]}-{date_val[6:]}"
            except:
                val_sh = 0
                date_sh = "N/A"
                date_val = datetime.now().strftime("%Y%m%d")

            try:
                # Use the valid date from SSE to query SZSE
                df_sz = ak.stock_margin_szse(date=date_val) 
                val_sz = float(df_sz['融资余额（元）'].sum())
            except:
                 val_sz = 0
            
            # Combine SH + SZ
            total_margin = val_sh + val_sz
            
            return {
                "date": date_sh,
                "margin_balance": total_margin / 1e8, # Convert to Billion
                "details": f"SH: {val_sh/1e8:.2f} + SZ: {val_sz/1e8:.2f}"
            }
        except Exception as e:
            print(f"Error fetching margin data: {e}")
            return {"date": "N/A", "margin_balance": 0, "error": str(e)}

    def fetch_money_supply(self):
        """
        Fetch M1/M2 data directly.
        """
        try:
            df = ak.macro_china_money_supply()
            # Columns: 月份, 货币和准货币(M2)-同比增长, 货币(M1)-同比增长
            # Ensure sorting by date descending
            # 月份 format usually "2023.12" or "2023.12"
            df['月份'] = pd.to_datetime(df['月份'], format='%Y.%m', errors='coerce')
            df.sort_values('月份', ascending=False, inplace=True)
            latest = df.iloc[0]
            
            # Correct column names with dashes
            m1_yoy = float(latest['货币(M1)-同比增长'])
            m2_yoy = float(latest['货币和准货币(M2)-同比增长'])
            
            return {
                "date": latest['月份'].strftime('%Y-%m'),
                "m1_yoy": m1_yoy,
                "m2_yoy": m2_yoy,
                "scissors": m1_yoy - m2_yoy
            }
            
            return {
                "date": latest['统计时间'].strftime('%Y-%m'),
                "m1_yoy": m1_yoy,
                "m2_yoy": m2_yoy,
                "scissors": m1_yoy - m2_yoy
            }
        except Exception as e:
            print(f"Error fetching money supply: {e}")
            return {"date": "N/A", "m1_yoy": 0, "m2_yoy": 0, "scissors": 0}
