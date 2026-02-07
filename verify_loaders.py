from framework.tencent_loader import TencentLoader
from framework.macro_loader import MacroLoader
import pandas as pd

def test_loaders():
    print("Testing TencentLoader...")
    t_loader = TencentLoader()
    
    # Test Realtime
    codes = ["sh000001", "sz399001"]
    try:
        df = t_loader.fetch_realtime_quotes(codes)
        print(f"Realtime Data:\n{df}")
    except Exception as e:
        print(f"Realtime Data Failed: {e}")

    # Test K-Line
    try:
        kline = t_loader.fetch_k_line("sh000001")
        print(f"K-Line Data (Last 5):\n{kline.tail()}")
    except Exception as e:
        print(f"K-Line Data Failed: {e}")

    print("\nTesting MacroLoader...")
    m_loader = MacroLoader()
    
    # Test Margin
    try:
        margin = m_loader.fetch_market_margin()
        print(f"Margin Data: {margin}")
    except Exception as e:
        print(f"Margin Data Failed: {e}")
        
    # Test Money Supply
    try:
        import akshare as ak
        df = ak.macro_china_money_supply()
        print(f"Money Supply Columns: {df.columns.tolist()}")
        # money = m_loader.fetch_money_supply()
        # print(f"Money Supply: {money}")
    except Exception as e:
        print(f"Money Supply Failed: {e}")

if __name__ == "__main__":
    test_loaders()
