import os
from SmartApi import SmartConnect
import pyotp
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

def get_angel_session():
    try:
        obj = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()
        
        data = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
        
        if data['status'] == False:
            print("Angel login failed:", data)
            return None
            
        refreshToken = data['data']['refreshToken']
        feedToken = obj.getfeedToken()
        
        return obj
    except Exception as e:
        print(f"Angel One connection error: {e}")
        return None


def get_option_ltp(tradingsymbol: str, exchange: str = "NFO"):
    """
    Get live LTP of an option
    Example tradingsymbol: BANKNIFTY24OCT55200CE
    """
    try:
        obj = get_angel_session()
        if obj is None:
            return None
            
        ltp_data = obj.ltpData(exchange, tradingsymbol, "")
        
        if ltp_data and ltp_data.get('status'):
            return ltp_data['data']['ltp']
        else:
            print("LTP fetch failed:", ltp_data)
            return None
    except Exception as e:
        print(f"Error fetching option LTP: {e}")
        return None
