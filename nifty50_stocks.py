import requests
from bs4 import BeautifulSoup
import yfinance as yf

# Backup list (in case automatic fetch fails)
BACKUP_NIFTY50 = [
    "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS", "INFY.NS",
    "SBIN.NS", "LT.NS", "ITC.NS", "TCS.NS", "AXISBANK.NS",
    "KOTAKBANK.NS", "BAJFINANCE.NS", "M&M.NS", "SUNPHARMA.NS", "HCLTECH.NS",
    "MARUTI.NS", "TITAN.NS", "HINDUNILVR.NS", "NTPC.NS", "POWERGRID.NS",
    "TATASTEEL.NS", "ONGC.NS", "ADANIPORTS.NS", "WIPRO.NS", "TECHM.NS",
    "BAJAJFINSV.NS", "ADANIENT.NS", "JSWSTEEL.NS", "COALINDIA.NS", "GRASIM.NS",
    "HINDALCO.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS", "EICHERMOT.NS",
    "BAJAJ-AUTO.NS", "INDIGO.NS", "BEL.NS", "TRENT.NS", "ULTRACEMCO.NS",
    "NESTLEIND.NS", "TATACONSUM.NS", "SBILIFE.NS", "HDFCLIFE.NS", "ASIANPAINT.NS",
    "JIOFIN.NS", "SHRIRAMFIN.NS", "MAXHEALTH.NS", "ETERNAL.NS", "BSE.NS"
]

def get_nifty50_stocks():
    """
    Try to get the latest Nifty 50 list.
    If it fails, return the backup list.
    """
    try:
        # Method 1: Using a simple reliable source
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            stocks = []
            for item in data.get("data", []):
                symbol = item.get("symbol")
                if symbol:
                    stocks.append(f"{symbol}.NS")
            
            if len(stocks) >= 40:  # Basic validation
                print(f"Successfully fetched {len(stocks)} Nifty 50 stocks")
                return stocks
                
    except Exception as e:
        print(f"Failed to fetch live Nifty 50 list: {e}")

    print("Using backup Nifty 50 list")
    return BACKUP_NIFTY50
