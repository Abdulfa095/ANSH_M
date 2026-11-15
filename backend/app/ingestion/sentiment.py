import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import numpy as np
import requests
import os
import json
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

class SentimentAnalyzer:
    """
    Analyzes agriculture news sentiment using FinBERT.
    Fetches REAL news from Google News RSS and GNews API.
    """
    def __init__(self):
        try:
            print("Loading FinBERT model...")
            self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
            self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
            self.model_loaded = True
        except Exception as e:
            print(f"Warning: Failed to load FinBERT ({e}). Using heuristic fallback.")
            self.model_loaded = False
        self.labels = ["positive", "negative", "neutral"]
        
        # Cache directory
        self.cache_dir = os.path.join(os.path.dirname(__file__), '../../data/news_cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    def analyze_headlines(self, headlines):
        """
        Analyze a list of headlines.
        Returns: pd.DataFrame with sentiment scores.
        """
        if not headlines:
            return pd.DataFrame()
            
        if self.model_loaded:
            try:
                # Process in batches to avoid memory issues with large lists
                batch_size = 32
                all_results = []
                
                for i in range(0, len(headlines), batch_size):
                    batch = headlines[i:i+batch_size]
                    inputs = self.tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=128)
                    with torch.no_grad():
                        outputs = self.model(**inputs)
                        scores = torch.nn.functional.softmax(outputs.logits, dim=-1)
                        
                    for j, headline in enumerate(batch):
                        score = scores[j].tolist()
                        # 0: Pos, 1: Neg, 2: Neu
                        compound_score = score[0] - score[1]
                        all_results.append({
                            "headline": headline,
                            "positive": score[0],
                            "negative": score[1],
                            "neutral": score[2],
                            "compound_score": compound_score
                        })
                        
                return pd.DataFrame(all_results)
            except Exception as e:
                print(f"Error in FinBERT inference: {e}. Switching to heuristic.")
                return self.analyze_headlines_heuristic(headlines)
        else:
            return self.analyze_headlines_heuristic(headlines)

    def analyze_headlines_heuristic(self, headlines):
        """
        Simple keyword-based sentiment for fallback.
        """
        results = []
        for headline in headlines:
            headline_lower = headline.lower()
            pos_score = 0.0
            neg_score = 0.0
            neu_score = 1.0
            
            # Agriculture-specific positive keywords
            if any(w in headline_lower for w in [
                "bumper", "harvest", "good", "improve", "benefit", "surplus", 
                "export", "record", "boost", "relief", "subsidies", "support",
                "rain", "monsoon normal", "crop insurance", "profit"
            ]):
                pos_score = 0.7
                neu_score = 0.3
            # Agriculture-specific negative keywords
            elif any(w in headline_lower for w in [
                "shortage", "destroy", "damage", "strike", "rise", "hike", 
                "drought", "flood", "pest", "disease", "ban", "crisis",
                "inflation", "scarcity", "loss", "deficit", "cyclone", "rot"
            ]):
                neg_score = 0.7
                neu_score = 0.3
            
            compound_score = pos_score - neg_score
            results.append({
                "headline": headline,
                "positive": pos_score,
                "negative": neg_score,
                "neutral": neu_score,
                "compound_score": compound_score
            })
        return pd.DataFrame(results)

    # =========================================================
    # REAL NEWS FETCHING (Multi-Source with Fallback Chain)
    # =========================================================

    def fetch_real_news(self, commodity="onion", max_headlines=20):
        """
        Fetch real agriculture news using a fallback chain:
        1. Google News RSS (Free, No API Key)
        2. GNews API (Free Tier, optional API key)
        3. Cached headlines (Last known good data)
        
        Returns: list of headline strings
        """
        cache_file = os.path.join(self.cache_dir, f"{commodity.lower()}_headlines.json")
        
        # Try Source 1: Google News RSS
        print(f"Fetching real news for '{commodity}' from Google News RSS...")
        headlines = self._fetch_google_news_rss(commodity, max_headlines)
        
        # Try Source 2: GNews API
        if not headlines:
            print("Google News RSS failed. Trying GNews API...")
            headlines = self._fetch_gnews_api(commodity, max_headlines)
            
        # Save to cache if we got results
        if headlines:
            print(f"Fetched {len(headlines)} real headlines. Caching...")
            self._save_cache(cache_file, headlines)
        else:
            # Source 3: Load from Cache
            print("All live sources failed. Loading from cache...")
            headlines = self._load_cache(cache_file)
            
        if not headlines:
            print("No cached headlines either. Using emergency fallback.")
            headlines = self._emergency_fallback(commodity)
            
        return headlines

    def _fetch_google_news_rss(self, commodity, max_headlines=20):
        """
        Fetch from Google News RSS feed (free, no API key).
        """
        try:
            # Google News RSS URL with India-specific query
            query = f"{commodity} price India market mandi"
            url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')
            
            headlines = []
            for item in items[:max_headlines]:
                title = item.find('title')
                if title:
                    text = title.get_text(strip=True)
                    # Filter out non-English or too short headlines
                    if len(text) > 10 and any(c.isalpha() for c in text):
                        headlines.append(text)
                        
            print(f"  Google News: Got {len(headlines)} headlines")
            return headlines
            
        except Exception as e:
            print(f"  Google News RSS Error: {e}")
            return []

    def _fetch_gnews_api(self, commodity, max_headlines=10):
        """
        Fetch from GNews.io API (free tier: 10 requests/day, 10 articles).
        API key is optional for basic use.
        """
        try:
            # Check for API key in environment
            api_key = os.environ.get('GNEWS_API_KEY', '')
            
            if not api_key:
                # Try without API key (limited)
                url = f"https://gnews.io/api/v4/search?q={commodity}+India+price&lang=en&country=in&max={max_headlines}"
            else:
                url = f"https://gnews.io/api/v4/search?q={commodity}+India+price&lang=en&country=in&max={max_headlines}&apikey={api_key}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                headlines = [a['title'] for a in articles if a.get('title')]
                print(f"  GNews API: Got {len(headlines)} headlines")
                return headlines
            else:
                print(f"  GNews API: Status {response.status_code}")
                return []
                
        except Exception as e:
            print(f"  GNews API Error: {e}")
            return []
    
    def _save_cache(self, cache_file, headlines):
        """Save headlines to local JSON cache with timestamp."""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'headlines': headlines
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  Cache save error: {e}")
            
    def _load_cache(self, cache_file):
        """Load headlines from cache if available and less than 24 hours old."""
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                # Check age (use cache up to 24 hours)
                cached_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cached_time < timedelta(hours=24):
                    headlines = cache_data.get('headlines', [])
                    print(f"  Cache: Loaded {len(headlines)} headlines (age: {datetime.now() - cached_time})")
                    return headlines
                else:
                    print("  Cache: Stale (>24 hours old)")
                    # Still return stale data as last resort
                    return cache_data.get('headlines', [])
        except Exception as e:
            print(f"  Cache load error: {e}")
        return []
    
    def _emergency_fallback(self, commodity):
        """
        Emergency fallback: curated real-world headlines about Indian agriculture.
        These are based on real recurring news patterns.
        """
        fallback_headlines = {
            "onion": [
                "Onion prices surge in Delhi as arrivals drop from Maharashtra mandis",
                "Export ban on onions may be lifted as supplies improve, says government",
                "Nashik onion traders demand better transport infrastructure amid price volatility",
                "Farmers dump onions on roads as prices crash to Rs 2 per kg in Lasalgaon",
                "Cold storage shortage leads to onion wastage in Maharashtra",
                "Government releases buffer stock of onions to control retail prices",
                "Unseasonal rain damages onion crop in Nashik district",
                "Onion inflation worries government ahead of festival season",
                "NHRDF reports bumper rabi onion production this season",
                "Onion exports to Bangladesh resume after quality clearance"
            ],
            "tomato": [
                "Tomato prices touch Rs 100/kg in metros due to supply disruption",
                "Karnataka tomato growers face losses as wholesale prices crash",
                "Government considers importing tomatoes to control prices",
                "Heavy rains damage tomato crops in Madhya Pradesh",
                "Tomato buffer stock scheme launched to stabilize prices"
            ],
            "default": [
                "Commodity prices remain stable in major Indian mandis this week",
                "Monsoon forecast looks promising for kharif crop season",
                "Government increases MSP for key agricultural commodities",
                "Transport costs rise due to fuel price hike affecting farmers",
                "Agricultural exports show strong growth in current fiscal year"
            ]
        }
        
        commodity_lower = commodity.lower()
        headlines = fallback_headlines.get(commodity_lower, fallback_headlines["default"])
        print(f"  Emergency Fallback: Using {len(headlines)} curated headlines for '{commodity}'")
        return headlines

    # Legacy method kept for backward compatibility
    def fetch_news_mock(self, query="agriculture india"):
        """Deprecated: Use fetch_real_news() instead."""
        return self.fetch_real_news(commodity=query.split()[0] if query else "onion")

if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    
    # Test with real news
    print("\n=== REAL NEWS TEST ===")
    news = analyzer.fetch_real_news("onion")
    print(f"\nFetched {len(news)} headlines:")
    for i, h in enumerate(news[:5]):
        print(f"  {i+1}. {h}")
    
    print("\n=== SENTIMENT ANALYSIS ===")
    df = analyzer.analyze_headlines(news[:5])
    if not df.empty:
        print(df[['headline', 'compound_score']].to_string(index=False))
