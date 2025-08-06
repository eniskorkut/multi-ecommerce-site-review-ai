#!/usr/bin/env python3
"""
Test script for review fetching
"""

import sys
import os
sys.path.append('backend/ai_core')

# Import the function directly
import importlib.util
spec = importlib.util.spec_from_file_location("fetch_reviews", "backend/ai_core/1_fetch_reviews.py")
fetch_reviews_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch_reviews_module)

def test_review_fetching():
    """Test review fetching with a real Trendyol URL"""
    
    # Test URL'leri
    test_urls = [
        "https://www.trendyol.com/nutraxin/naturel-sleep-bitkisel-ekstreler-iceren-takviye-edici-gida-60-kapsul-p-6709417",
        "https://www.trendyol.com/trendyol-man/trendyol-man-basic-oversize-fit-pamuklu-triko-kazak-p-12345678",
        "https://www.trendyol.com/samsung/samsung-galaxy-a15-128-gb-samsung-turkiye-garantili-p-12345678"
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing URL: {url}")
        print(f"{'='*60}")
        
        try:
            reviews = fetch_reviews_module.fetch_reviews(url=url, max_pages=2, max_reviews=10)
            
            if reviews:
                print(f"✅ Başarılı! {len(reviews)} yorum çekildi.")
                for i, review in enumerate(reviews[:3], 1):
                    print(f"{i}. {review['comment'][:100]}...")
            else:
                print("❌ Hiç yorum çekilemedi.")
                
        except Exception as e:
            print(f"❌ Hata: {e}")

if __name__ == "__main__":
    test_review_fetching() 