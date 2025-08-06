#!/usr/bin/env python3
"""
Debug script for Selenium review extraction
"""

import sys
import os
sys.path.append('akilli-yorum-asistani/backend/ai_core')

import importlib.util
spec = importlib.util.spec_from_file_location("fetch_reviews", "akilli-yorum-asistani/backend/ai_core/1_fetch_reviews.py")
fetch_reviews_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch_reviews_module)

def debug_selenium():
    """Debug Selenium functionality"""
    
    url = "https://www.trendyol.com/nutraxin/naturel-sleep-bitkisel-ekstreler-iceren-takviye-edici-gida-60-kapsul-p-6709417"
    
    print(f"Debugging Selenium for URL: {url}")
    
    try:
        # Selenium'u çağır
        reviews = fetch_reviews_module.fetch_reviews_selenium(url, max_reviews=50)
        
        print(f"\nSonuç: {len(reviews)} yorum çekildi")
        
        for i, review in enumerate(reviews[:5], 1):
            print(f"{i}. {review['comment'][:100]}...")
            
    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_selenium() 