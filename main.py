import yfinance as yf
from datetime import datetime
import pytz

# 設定目標股票與起始日期
STOCKS = ['GOOGL', 'SOFI', 'QQQ', 'RKLB']
START_DATE = '2025-06-01'

def get_stock_data():
    table_rows = []
    
    # 取得當前時間 (台北時間)
    tw = pytz.timezone('Asia/Taipei')
    now = datetime.now(tw).strftime('%Y-%m-%d %H:%M:%S')
    
    table_header = f"### 股價監測表 (起始日: {START_DATE})\nUpdated: {now} (Taipei Time)\n\n"
    table_header += "| Stock | Start Price (Jun 2025) | Current Price | Change (%) |\n"
    table_header += "| :--- | :---: | :---: | :---: |\n"

    for symbol in STOCKS:
        try:
            # 下載數據
            ticker = yf.Ticker(symbol)
            # 取得歷史資料，包含 start date 到現在
            hist = ticker.history(start=START_DATE)
            
            if hist.empty:
                table_rows.append(f"| {symbol} | N/A | N/A | N/A |")
                continue

            # 取得起始價格 (2025-06-01 後的第一個交易日收盤價)
            start_price = hist['Close'].iloc[0]
            # 取得最新價格
            current_price = hist['Close'].iloc[-1]
            
            # 計算漲跌幅
            change_percent = ((current_price - start_price) / start_price) * 100
            
            # 格式化顯示 (+號, 顏色標記)
            sign = "+" if change_percent > 0 else ""
            # 在 Markdown 中雖不能直接上色，但可用 emoji 或文字表示
            emoji = "🟢" if change_percent > 0 else "🔴"
            
            row = f"| **{symbol}** | ${start_price:.2f} | ${current_price:.2f} | {emoji} {sign}{change_percent:.2f}% |"
            table_rows.append(row)
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            table_rows.append(f"| {symbol} | Error | Error | Error |")

    return table_header + "\n".join(table_rows)

def update_readme(new_content):
    readme_path = 'README.md'
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        # 如果沒有 README，就創建一個基本的
        content = "# Stock Tracker\n\n\n"

    # 定義標記，我們只替換這兩個標記中間的內容
    start_marker = ""
    end_marker = ""
    
    if start_marker not in content or end_marker not in content:
        # 如果找不到標記，附加在最後面
        final_content = content + f"\n\n{start_marker}\n{new_content}\n{end_marker}"
    else:
        # 替換標記中間的內容
        before = content.split(start_marker)[0]
        after = content.split(end_marker)[1]
        final_content = f"{before}{start_marker}\n{new_content}\n{end_marker}{after}"
        
    with open(readme_path, 'w', encoding='utf-8') as file:
        file.write(final_content)

if __name__ == "__main__":
    table = get_stock_data()
    update_readme(table)
    print("Readme updated successfully.")
