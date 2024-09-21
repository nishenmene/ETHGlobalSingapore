from flask import Flask, jsonify, request
import requests
import openai
import os

# Initialize Flask app
app = Flask(__name__)

# OpenAI API Key from environment variable
openai.api_key = "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"

# CoinGecko API URL (for latest crypto coins data)
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"
CURRENCY = "usd"

# Function to get latest launched coins from CoinGecko
def get_latest_coins():
    try:
        response = requests.get(COINGECKO_API_URL, params={
            "vs_currency": CURRENCY,
            "order": "market_cap_desc",
            "per_page": 5,
            "page": 1
        })
        response.raise_for_status()  # Raise error for bad HTTP status codes
        coins = response.json()
        return coins
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Function to query OpenAI API for trust score
def get_chatgpt_insights(coin_name):
    prompt = f"Analyze the cryptocurrency {coin_name}. What is its potential for future growth? What factors make it trustworthy? Provide a score for trustworthiness and explain."
    
    # OpenAI GPT-4 completion request
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=150
    )
    
    return response.choices[0].text.strip()

# Route to get latest coins with insights from ChatGPT
@app.route('/api/latest-coins', methods=['GET'])
def latest_coins_with_insights():
    # Fetch the latest coins from CoinGecko
    coins = get_latest_coins()

    # Check if there was an error in fetching the coins
    if "error" in coins:
        return jsonify({"error": coins["error"]}), 500

    # Prepare the results list
    results = []
    
    # For each coin, get ChatGPT insights
    for coin in coins:
        coin_name = coin['name']
        trust_insight = get_chatgpt_insights(coin_name)
        
        results.append({
            "coin_name": coin_name,
            "coin_symbol": coin['symbol'],
            "current_price": coin['current_price'],
            "market_cap": coin['market_cap'],
            "trust_insight": trust_insight
        })
    
    # Return the results as JSON
    return jsonify(results)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
