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
            # stock_margin_summary_sse/szse
            df_sh = ak.stock_margin_summary_sse()
            df_sz = ak.stock_margin_summary_szse()
            
            # Use the latest date common to both or max date
            latest_sh = df_sh.iloc[-1]
            latest_sz = df_sz.iloc[-1]
            
            # Combine SH + SZ
            # Fields vary slightly by source version, usually '融资余额' (Financing Balance)
            total_margin = float(latest_sh['融资余额']) + float(latest_sz['融资余额'])
            # Net buy is difference or just use balance trend
            
            return {
                "date": str(latest_sh['信用交易日期']),
                "margin_balance": total_margin / 1e8, # Convert to Billion
                "details": f"SH: {latest_sh['融资余额']} + SZ: {latest_sz['融资余额']}"
            }
        except Exception as e:
            print(f"Error fetching margin data: {e}")
            return {"date": "N/A", "margin_balance": 0, "error": str(e)}

    def fetch_money_supply(self):
        """
        Fetch M1/M2 data directly.
        Returns: {
            "date": "2023-12",
            "m1_yoy": 1.3,
            "m2_yoy": 9.7,
            "scissors": -8.4
        }
        """
        try:
            df = ak.macro_china_money_supply()
            # Columns: 统计时间, 货币和准货币(M2)-同比增长, 货币(M1)-同比增长
            latest = df.iloc[0] # Usually sorted descending? Check documentation usage or sort
            
            # Ensure sorting by date descending
            df['统计时间'] = pd.to_datetime(df['统计时间'], format='%Y.%m')
            df.sort_values('统计时间', ascending=False, inplace=True)
            latest = df.iloc[0]
            
            m1_yoy = float(latest['货币(M1)-同比增长'])
            m2_yoy = float(latest['货币和准货币(M2)-同比增长'])
            
            return {
                "date": latest['统计时间'].strftime('%Y-%m'),
                "m1_yoy": m1_yoy,
                "m2_yoy": m2_yoy,
                "scissors": m1_yoy - m2_yoy
            }
        except Exception as e:
            print(f"Error fetching money supply: {e}")
            return {"date": "N/A", "m1_yoy": 0, "m2_yoy": 0, "scissors": 0}
