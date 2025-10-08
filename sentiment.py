
import requests
from datetime import datetime
import google_sheets  # Your separate module

SHEET_ID = "1YkTXNX5LAhANICxzu4Tj4Hr6aFMoXdufH_ev1gmRx7c"
WORKSHEET_NAME = "SEMENT"

def get_sentiment_for_ticker(ticker):
    url = "https://api.marketaux.com/v1/news/all"
    params = {
        "api_token": "GHvX2fU3SlWfely31ktchdIGv7bGqVVr0AhGQwpC",
        "symbols": ticker
    }

    response = requests.get(url, params=params)
    data = response.json()

    sentiments = []
    if "data" in data:
        for article in data["data"]:
            entities = article.get("entities", [])
            for e in entities:
                if e.get("symbol") == ticker and "sentiment_score" in e:
                    sentiments.append(e["sentiment_score"])
    
    
    if sentiments:
        avg_sentiment = sum(sentiments) / len(sentiments)
        if avg_sentiment > 0:
            sentiment_label = "Positive"
        elif avg_sentiment < 0:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"
        return round(avg_sentiment, 4), sentiment_label
    else:
        return None, None

def main():
    tickers = ["^NSEI", "NIFTY_BANK"]
    headers = ["NSE", "SENTIMENT_SCORE", "SENTIMENT", "VALUE"]
    rows = []

    # Get sentiment data
    for ticker in tickers:
        sentiment_score, sentiment_label = get_sentiment_for_ticker(ticker)
        if sentiment_score is not None:
            rows.append([ticker, sentiment_score, sentiment_label, sentiment_score])
        else:
            rows.append([ticker, "NO DATA FOUND", "NO DATA FOUND", "NO DATA FOUND"])

    # Append rows to Google Sheet
    google_sheets.update_google_sheet_by_name(SHEET_ID, WORKSHEET_NAME, headers, rows)

    # Append timestamp as a separate row at the end
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, [now])

if __name__ == "__main__":
    main()
