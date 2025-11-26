import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

STOCKS = ['GOOGL', 'SOFI', 'QQQ', 'RKLB', 'BTC-USD']
START_DATE = '2025-06-09'

def get_stock_data():
    table_rows = []
    tw = pytz.timezone('Asia/Taipei')
    now = datetime.now(tw).strftime('%Y-%m-%d %H:%M:%S')
    
    table_header = f"### 📊 Asset Performance (Base: {START_DATE})\n**Updated:** {now} (Taipei Time)\n\n"
    table_header += "| Symbol | Start Price | Current Price | Change (%) |\n"
    table_header += "| :--- | :---: | :---: | :---: |\n"

    print(f"Downloading data for: {STOCKS}...")
    
    try:
        data = yf.download(STOCKS, start=START_DATE, group_by='ticker', auto_adjust=True, threads=True)
        
        if data.empty:
            return table_header + "| All | N/A | N/A | Error |"

        for symbol in STOCKS:
            try:
                if len(STOCKS) == 1:
                    stock_data = data
                else:
                    stock_data = data[symbol]

                stock_data = stock_data.dropna()

                if stock_data.empty:
                    table_rows.append(f"| {symbol} | N/A | N/A | No Data |")
                    continue

                start_price = stock_data['Close'].iloc[0]
                current_price = stock_data['Close'].iloc[-1]
                change_percent = ((current_price - start_price) / start_price) * 100
                
                sign = "+" if change_percent > 0 else ""
                emoji = "🟢" if change_percent > 0 else "🔴"
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

def update_readme(table_content):
    readme_path = 'README.md'

    markdown_template = f"""{table_content}"""

    with open(readme_path, 'w', encoding='utf-8') as file:
        file.write(markdown_template)

if __name__ == "__main__":
    table = get_stock_data()
    update_readme(table)
