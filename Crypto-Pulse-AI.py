```python
import requests
import os
import time
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURATION ---
# The environment provides the API key at runtime.
GEMINI_API_KEY = "" 
genai.configure(api_key=GEMINI_API_KEY)

class CryptoPulseAI:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')

    def fetch_market_data(self, coin_id):
        """Fetches real-time price and market stats from CoinGecko."""
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                "vs_currency": "usd",
                "ids": coin_id.lower(),
                "order": "market_cap_desc",
                "sparkline": False,
                "price_change_percentage": "24h"
            }
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return None
            return data[0]
        except Exception as e:
            print(f"Error fetching data from CoinGecko: {e}")
            return None

    def get_ai_sentiment(self, market_data):
        """Uses Gemini AI to analyze market data and provide a recommendation."""
        coin_name = market_data['name']
        price = market_data['current_price']
        change = market_data['price_change_percentage_24h']
        high_24h = market_data['high_24h']
        low_24h = market_data['low_24h']

        prompt = f"""
        Act as a professional Crypto Data Scientist. Analyze the following market data for {coin_name}:
        - Current Price: ${price}
        - 24h Price Change: {change}%
        - 24h High: ${high_24h}
        - 24h Low: ${low_24h}

        Provide a concise analysis including:
        1. Market Sentiment (Bullish, Bearish, or Neutral).
        2. A brief 'Buy/Sell/Hold' suggestion based on these metrics.
        3. A risk assessment.
        
        Keep the response professional, data-driven, and brief. 
        End with a mandatory disclaimer: "This is AI-generated analysis and NOT financial advice."
        """

        # Exponential backoff implementation for API calls
        retries = 5
        for i in range(retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception:
                if i == retries - 1:
                    return "AI Analysis currently unavailable. Please try again later."
                wait_time = 2 ** i
                time.sleep(wait_time)

    def run(self):
        print("--- Crypto-Pulse-AI: Real-time Market Sentiment ---")
        coin_id = input("Enter Cryptocurrency Name (e.g., bitcoin, ethereum, solana): ").strip().lower()
        
        print(f"\n[1/2] Fetching live data for {coin_id}...")
        market_data = self.fetch_market_data(coin_id)
        
        if not market_data:
            print("Could not find data for that coin. Please check the spelling (e.g., 'bitcoin').")
            return

        print(f"[2/2] Analyzing sentiment with Gemini AI...")
        analysis = self.get_ai_sentiment(market_data)

        print("\n" + "="*50)
        print(f"REPORT: {market_data['name']} ({market_data['symbol'].upper()})")
        print(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        print(f"Current Price: ${market_data['current_price']:,}")
        print(f"24h Change:    {market_data['price_change_percentage_24h']:.2f}%")
        print("-" * 50)
        print("AI ANALYSIS & RECOMMENDATION:")
        print(analysis)
        print("="*50)

if __name__ == "__main__":
    pulse = CryptoPulseAI()
    pulse.run()

```

