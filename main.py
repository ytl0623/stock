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
    
    table_header = f"**Updated:** {now} (Taipei Time)\n\n"
    table_header += "| Symbol | Start Price | Current Price | Change (%) |\n"
    table_header += "| :--- | :---: | :---: | :---: |\n"

    for symbol in STOCKS:
        try:
            print(f"Fetching {symbol}...")
            stock_data = yf.download(symbol, start=START_DATE, progress=False, auto_adjust=True)

            if stock_data.empty:
                table_rows.append(f"| {symbol} | N/A | N/A | No Data |")
                continue

            stock_data = stock_data.dropna()

            if stock_data.empty:
                table_rows.append(f"| {symbol} | N/A | N/A | No Data (NaN) |")
                continue

            try:
                if isinstance(stock_data['Close'], pd.DataFrame):
                    close_prices = stock_data['Close'].iloc[:, 0]
                else:
                    close_prices = stock_data['Close']
                
                start_price = close_prices.iloc[0]
                current_price = close_prices.iloc[-1]
            except Exception as inner_e:
                print(f"Data structure parsing error for {symbol}: {inner_e}")
                table_rows.append(f"| {symbol} | Error | Error | Structure |")
                continue

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

    return table_header + "\n".join(table_rows)

def update_readme(table_content):
    readme_path = 'README.md'
    markdown_template = f"""{table_content}"""
    
    with open(readme_path, 'w', encoding='utf-8') as file:
        file.write(markdown_template)

if __name__ == "__main__":
    table = get_stock_data()
    update_readme(table)
    print("Readme updated successfully.")
