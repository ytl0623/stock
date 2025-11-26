import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# 設定目標股票與起始日期
STOCKS = ['GOOGL', 'SOFI', 'QQQ', 'RKLB']
START_DATE = '2025-06-09'

def get_stock_data():
    table_rows = []
    
    # 取得當前時間 (台北時間)
    tw = pytz.timezone('Asia/Taipei')
    now = datetime.now(tw).strftime('%Y-%m-%d %H:%M:%S')
    
    table_header = f"### 股價監測表 (起始日: {START_DATE})\nUpdated: {now} (Taipei Time)\n\n"
    table_header += "| Stock | Start Price | Current Price | Change (%) |\n"
    table_header += "| :--- | :---: | :---: | :---: |\n"

    print(f"Downloading data for: {STOCKS}...")
    
    try:
        # 使用 bulk download，這比迴圈抓取更穩定
        # auto_adjust=True 會自動處理除權息，讓比較更準確
        data = yf.download(STOCKS, start=START_DATE, group_by='ticker', auto_adjust=True, threads=True)
        
        if data.empty:
            print("Error: No data downloaded.")
            return table_header + "| All | N/A | N/A | Error |"

        for symbol in STOCKS:
            try:
                # 處理單一股票數據
                # 如果只有一支股票，dataframe 結構會不同，需要判斷
                if len(STOCKS) == 1:
                    stock_data = data
                else:
                    stock_data = data[symbol]

                # 移除 NaN 值 (非交易日)
                stock_data = stock_data.dropna()

                if stock_data.empty:
                    table_rows.append(f"| {symbol} | N/A | N/A | No Data |")
                    continue

                # 取得起始與最新價格 ('Close' 已經是調整後收盤價)
                start_price = stock_data['Close'].iloc[0]
                current_price = stock_data['Close'].iloc[-1]
                
                # 計算漲跌幅
                change_percent = ((current_price - start_price) / start_price) * 100
                
                # 格式化顯示
                sign = "+" if change_percent > 0 else ""
                emoji = "🟢" if change_percent > 0 else "🔴"
                
                # 判斷是否持平
                if change_percent == 0:
                    emoji = "⚪"
                    sign = ""

                row = f"| **{symbol}** | ${start_price:.2f} | ${current_price:.2f} | {emoji} {sign}{change_percent:.2f}% |"
                table_rows.append(row)

            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                table_rows.append(f"| {symbol} | Error | Error | Parse Fail |")

    except Exception as e:
        print(f"Critical Download Error: {e}")
        return table_header + f"\nError downloading data: {e}"

    return table_header + "\n".join(table_rows)

def update_readme(new_content):
    readme_path = 'README.md'
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        content = "# Stock Tracker\n\n\n"

    start_marker = ""
    end_marker = ""
    
    if start_marker not in content or end_marker not in content:
        final_content = content + f"\n\n{start_marker}\n{new_content}\n{end_marker}"
    else:
        before = content.split(start_marker)[0]
        after = content.split(end_marker)[1]
        final_content = f"{before}{start_marker}\n{new_content}\n{end_marker}{after}"
        
    with open(readme_path, 'w', encoding='utf-8') as file:
        file.write(final_content)

if __name__ == "__main__":
    table = get_stock_data()
    update_readme(table)
    print("Readme updated successfully.")
