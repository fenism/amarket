import baostock as bs
import pandas as pd

def test_baostock():
    lg = bs.login()
    print(f"Login respond error_code: {lg.error_code}")
    print(f"Login respond  error_msg: {lg.error_msg}")

    # 1. Test Index Data (Shanghai Composite)
    print("\n--- Testing Index Data (sh.000001) ---")
    rs = bs.query_history_k_data_plus("sh.000001",
        "date,code,open,high,low,close,volume,amount,pctChg",
        start_date='2024-01-01', end_date='2024-01-10',
        frequency="d", adjustflag="3")
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    print(f"Index data count: {len(result)}")
    print(result.head())

    # 2. Test Margin Data (if available via query_history_k_data_plus or special query)
    # Baostock doc says 'query_history_k_data_plus' fields include 'turn' (turnover).
    # It does NOT explicitly have 'financing balance' (margin) in k-line data.
    # Let's check typical fields.
    print("\n--- Testing Stock Data (sh.600000) ---")
    rs_stock = bs.query_history_k_data_plus("sh.600000",
        "date,code,close,volume,amount,turn,pctChg,peTTM,pbMRQ",
        start_date='2024-01-01', end_date='2024-01-10',
        frequency="d", adjustflag="3")
    stock_data_list = []
    while (rs_stock.error_code == '0') & rs_stock.next():
        stock_data_list.append(rs_stock.get_row_data())
    result_stock = pd.DataFrame(stock_data_list, columns=rs_stock.fields)
    print(f"Stock data count: {len(result_stock)}")
    print(result_stock.head())

    bs.logout()

if __name__ == "__main__":
    test_baostock()
