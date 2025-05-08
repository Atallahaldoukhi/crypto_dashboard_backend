#!/usr/bin/env python3.11
# /home/ubuntu/crypto_dashboard_backend/scripts/run_daily_crypto_pipeline.py

import sys
sys.path.append("/opt/.manus/.sandbox-runtime")
from data_api import ApiClient

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
import markdown2 # For MD to HTML conversion
from weasyprint import HTML, CSS # For HTML to PDF conversion

# --- Configuration ---
SYMBOLS = ["BTC-USD", "ETH-USD"]
DATA_RANGE = "10d" # Fetch 10 days to have enough data for 7-day SMA and recent analysis
SMA_WINDOW_SHORT = 3
SMA_WINDOW_LONG = 7 # For trend indication
PREDICTION_DAYS = 3 # Predict for next 3 days

BASE_OUTPUT_DIR = "/home/ubuntu/crypto_dashboard_backend"
REPORTS_ARCHIVE_DIR = os.path.join(BASE_OUTPUT_DIR, "reports_archive")
PLOTS_DIR = os.path.join(REPORTS_ARCHIVE_DIR, "plots") # Store plots alongside reports for simplicity
# STATIC_PLOTS_DIR = os.path.join(BASE_OUTPUT_DIR, "app", "static", "plots") # Alternative for serving plots directly

# Ensure output directories exist
os.makedirs(REPORTS_ARCHIVE_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)
# os.makedirs(STATIC_PLOTS_DIR, exist_ok=True)

# Initialize API client
api_client = ApiClient()

TODAY_STR = datetime.now().strftime("%Y-%m-%d")

# --- Helper Functions ---
def fetch_stock_data(symbol, interval="1d", range_val="10d"):
    print(f"Fetching data for {symbol}...")
    try:
        data = api_client.call_api(
            "YahooFinance/get_stock_chart",
            query={
                "symbol": symbol,
                "interval": interval,
                "range": range_val,
                "region": "US",
                "includeAdjustedClose": True,
                "events": "div,split"
            }
        )
        if data and data.get("chart") and data["chart"].get("result") and data["chart"]["result"][0]:
            result = data["chart"]["result"][0]
            timestamps = result["timestamp"]
            prices = result["indicators"]["quote"][0]
            adj_close = result["indicators"]["adjclose"][0]["adjclose"]
            
            df = pd.DataFrame({
                "timestamp": timestamps,
                "open": prices["open"],
                "high": prices["high"],
                "low": prices["low"],
                "close": prices["close"],
                "volume": prices["volume"],
                "adj_close": adj_close
            })
            df["date"] = pd.to_datetime(df["timestamp"], unit="s").dt.date
            df.dropna(subset=["adj_close"], inplace=True) # Ensure adj_close is not null
            return df.tail(10) # Ensure we have enough for 7-day analysis + buffer
        else:
            print(f"No data found for {symbol} or unexpected API response structure.")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

def calculate_sma(data_series, window):
    return data_series.rolling(window=window).mean()

def generate_plot(df, symbol, sma_short, sma_long, predictions_df, filename):
    plt.style.use("seaborn-v0_8-darkgrid") # Using a style that might be available
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(df["date"], df["adj_close"], label="Adjusted Close", color="blue", marker=".")
    ax.plot(df["date"], sma_short, label=f"SMA-{SMA_WINDOW_SHORT}", color="orange")
    ax.plot(df["date"], sma_long, label=f"SMA-{SMA_WINDOW_LONG}", color="green")
    
    if not predictions_df.empty:
        ax.plot(predictions_df["date"], predictions_df["predicted_price"], label="SMA Prediction", color="red", linestyle="--", marker="x")

    ax.set_title(f"{symbol} Price Trend and {SMA_WINDOW_SHORT}-day Prediction", fontsize=16)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Price (USD)", fontsize=12)
    ax.legend()
    ax.grid(True)
    fig.autofmt_xdate()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close(fig)
    print(f"Plot saved: {filename}")

# --- Main Pipeline Logic ---
def run_pipeline():
    all_reports_data = []

    for symbol in SYMBOLS:
        print(f"\nProcessing {symbol}...")
        df_data = fetch_stock_data(symbol, range_val=DATA_RANGE)

        if df_data.empty or len(df_data) < SMA_WINDOW_LONG:
            print(f"Not enough data for {symbol} to process. Skipping.")
            all_reports_data.append(f"## {symbol}\n\nInsufficient data to generate analysis.\n")
            continue

        # Analysis
        df_data[f"sma_{SMA_WINDOW_SHORT}"] = calculate_sma(df_data["adj_close"], SMA_WINDOW_SHORT)
        df_data[f"sma_{SMA_WINDOW_LONG}"] = calculate_sma(df_data["adj_close"], SMA_WINDOW_LONG)
        df_data["daily_change_pct"] = df_data["adj_close"].pct_change() * 100
        
        latest_data = df_data.iloc[-1]
        current_price = latest_data["adj_close"]
        daily_change = latest_data["daily_change_pct"]
        trend_sma_short = latest_data[f"sma_{SMA_WINDOW_SHORT}"]
        trend_sma_long = latest_data[f"sma_{SMA_WINDOW_LONG}"]

        trend_direction = "Neutral"
        if trend_sma_short > trend_sma_long:
            trend_direction = "Upward"
        elif trend_sma_short < trend_sma_long:
            trend_direction = "Downward"

        # Prediction (Simple SMA extension)
        predictions = []
        last_sma_value = df_data[f"sma_{SMA_WINDOW_SHORT}"].iloc[-1]
        last_date = df_data["date"].iloc[-1]
        
        # For simplicity, let's assume the last SMA value is the prediction for the next day
        # A more robust prediction would extrapolate the trend or use a more complex model
        # For this example, we will just use the last SMA value for all prediction days
        # or a very simple linear extrapolation of the last two SMA points.
        
        if len(df_data[f"sma_{SMA_WINDOW_SHORT}"].dropna()) >= 2:
            sma_series = df_data[f"sma_{SMA_WINDOW_SHORT}"].dropna()
            last_sma_val = sma_series.iloc[-1]
            second_last_sma_val = sma_series.iloc[-2]
            sma_slope = last_sma_val - second_last_sma_val
        else:
            sma_slope = 0 # Default to no change if not enough data for slope
            last_sma_val = df_data[f"sma_{SMA_WINDOW_SHORT}"].dropna().iloc[-1] if not df_data[f"sma_{SMA_WINDOW_SHORT}"].dropna().empty else current_price

        for i in range(1, PREDICTION_DAYS + 1):
            predicted_date = last_date + timedelta(days=i)
            predicted_price = last_sma_val + (sma_slope * i) # Linear extrapolation of SMA
            predictions.append({"date": predicted_date, "predicted_price": predicted_price})
        
        predictions_df = pd.DataFrame(predictions)
        if not predictions_df.empty:
             predictions_df["date"] = pd.to_datetime(predictions_df["date"]).dt.date

        # Plotting
        plot_filename = os.path.join(PLOTS_DIR, f"{symbol.lower().replace('-usd', '')}_price_trend_{TODAY_STR}.png")
        generate_plot(df_data, symbol, df_data[f"sma_{SMA_WINDOW_SHORT}"], df_data[f"sma_{SMA_WINDOW_LONG}"], predictions_df, plot_filename)

        # Report Content for this symbol
        report_symbol_md = f"## {symbol} Analysis ({TODAY_STR})\n\n"
        report_symbol_md += f"**Current Price:** ${current_price:,.2f}\n"
        report_symbol_md += f"**Daily Change:** {daily_change:.2f}%\n"
        report_symbol_md += f"**Trend (SMA {SMA_WINDOW_SHORT} vs SMA {SMA_WINDOW_LONG}):** {trend_direction}\n\n"
        report_symbol_md += f"**Price Data (Last 7 days):**\n"
        report_symbol_md += df_data.tail(7)[["date", "open", "high", "low", "close", "adj_close", "volume"]].to_markdown(index=False) + "\n\n"
        report_symbol_md += f"**Predicted Prices (SMA-{SMA_WINDOW_SHORT} based, next {PREDICTION_DAYS} days):**\n"
        if not predictions_df.empty:
            report_symbol_md += predictions_df[["date", "predicted_price"]].to_markdown(index=False) + "\n\n"
        else:
            report_symbol_md += "Prediction data not available.\n\n"
        report_symbol_md += f"![{symbol} Price Trend]({os.path.basename(plot_filename)})\n\n"
        # Note: For PDF, image path needs to be absolute or resolvable by WeasyPrint
        # For simplicity, we assume the markdown renderer for the website can handle relative paths if plots are in a subfolder.
        # For PDF, we might need to adjust path or embed. For now, using basename.

        all_reports_data.append(report_symbol_md)

    # Combine reports into one master markdown file
    final_md_content = f"# Daily Crypto Market Report - {TODAY_STR}\n\n"
    final_md_content += "This report provides a summary of recent market activity and price trends for selected cryptocurrencies.\n\n"
    final_md_content += "**Disclaimer:** This information is for educational purposes only and should not be considered financial advice. Cryptocurrency markets are highly volatile.\n\n"
    final_md_content += "---\n\n"
    final_md_content += "\n\n".join(all_reports_data)

    md_report_filename = os.path.join(REPORTS_ARCHIVE_DIR, f"daily_crypto_report_{TODAY_STR}.md")
    pdf_report_filename = os.path.join(REPORTS_ARCHIVE_DIR, f"daily_crypto_report_{TODAY_STR}.pdf")

    with open(md_report_filename, "w", encoding="utf-8") as f:
        f.write(final_md_content)
    print(f"Markdown report saved: {md_report_filename}")

    # Convert Markdown to PDF
    try:
        html_content = markdown2.markdown(final_md_content, extras=["tables", "fenced-code-blocks"])
        # Add some basic CSS for better PDF formatting, including handling Arabic if needed
        # The plot paths in markdown are relative, for WeasyPrint they need to be absolute or base_url set.
        # We will use an absolute path for the plots in the HTML for PDF generation.
        html_with_abs_plot_paths = html_content.replace("![BTC-USD Price Trend](btc_price_trend", f"![BTC-USD Price Trend]({os.path.join(PLOTS_DIR, 'btc_price_trend')}")
        html_with_abs_plot_paths = html_with_abs_plot_paths.replace("![ETH-USD Price Trend](eth_price_trend", f"![ETH-USD Price Trend]({os.path.join(PLOTS_DIR, 'eth_price_trend')}")
        
        # More robust replacement for any plot image
        import re
        def replace_plot_path(match):
            alt_text = match.group(1)
            img_filename = match.group(2)
            # Construct absolute path, assuming img_filename is just the basename like 'btc_price_trend_2025-05-08.png'
            abs_img_path = os.path.join(PLOTS_DIR, img_filename)
            return f'<img src="file://{abs_img_path}" alt="{alt_text}" style="max-width:100%; height:auto;" />'

        # Replace markdown image syntax with HTML img tags with absolute file paths
        html_for_pdf = re.sub(r"!\[([^\]]+)\]\(([^)]+)\)", replace_plot_path, final_md_content)
        html_content_for_pdf = markdown2.markdown(html_for_pdf, extras=["tables", "fenced-code-blocks"])
        
        # Basic CSS, including font for Arabic if report text was in Arabic
        # For this report, content is mostly English tables and plot titles.
        css = CSS(string="""
            @page { size: A4; margin: 2cm; }
            body { font-family: sans-serif; direction: rtl; text-align: right; }
            h1, h2, h3 { color: #333; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 1em; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            img { max-width: 100%; height: auto; display: block; margin-left: auto; margin-right: auto; margin-bottom:1em; }
        """)
        HTML(string=html_content_for_pdf, base_url=REPORTS_ARCHIVE_DIR).write_pdf(pdf_report_filename, stylesheets=[css])
        print(f"PDF report saved: {pdf_report_filename}")
    except Exception as e:
        print(f"Error converting Markdown to PDF: {e}")
        print("PDF generation failed. Markdown report is available.")

if __name__ == "__main__":
    print("Starting daily crypto processing pipeline...")
    run_pipeline()
    print("\nPipeline finished.")
    print(f"Reports and plots saved in: {REPORTS_ARCHIVE_DIR}")
    print("To run this pipeline again for a new day, simply execute this script.")
    print("Automatic daily execution is not enabled in the current environment.")
    print("You can trigger it manually or via an external scheduler if you set one up.")

