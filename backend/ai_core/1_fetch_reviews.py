# Akilli Yorum Asistani - Yorum Çekme Modülü
# Bu dosya Trendyol ve Hepsiburada ürün sayfalarından yorumları çeker
# Web scraping ve API kullanarak yorumları toplar
# Hackathon Projesi - AI Destekli Yorum Analizi

import requests
import json
import argparse
import re
import time
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import bs4
from bs4 import BeautifulSoup

# Hepsiburada scraper modülünü import et
from hepsiburada_scraper import fetch_reviews_hepsiburada

# TRENDYOL API YAKLAŞIMI
# URL'den alınan product_slug ve merchant_id'yi kullanarak sayfa sayfa yorum çeker
# Trendyol'un resmi API'sini kullanarak hızlı ve güvenilir veri çekimi
API_URL = "https://apigw.trendyol.com/discovery-web-socialgw-service/reviews/{product_slug}/yorumlar?merchantId={merchantId}&page={page}&culture=tr-TR&storefrontId=1"

# HTTP istekleri için header bilgileri - Gerçek tarayıcı gibi davranmak için
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
    "Referer": "https://www.trendyol.com/",
    "Origin": "https://www.trendyol.com"
}

def extract_product_info_from_url(url):
    """
    Trendyol URL'sinden ürün slug'ını ve merchant ID'yi güvenilir şekilde çıkarır.
    Bu fonksiyon URL parsing yaparak API çağrıları için gerekli parametreleri elde eder.
    
    Örnek URL: https://www.trendyol.com/harmana/hindiba-kahvesi-p-288620006?boutiqueId=61&merchantId=936059
    """
    try:
        print(f"URL ayrıştırılıyor: {url}")
        parsed_url = urlparse(url)
        
        # product_slug: URL'nin path kısmıdır (örn: /harmana/hindiba-kahvesi-p-288620006)
        product_slug = parsed_url.path.strip('/')
        if not product_slug:
            print("URL'den ürün slug'ı çıkarılamadı.")
            return None, None
            
        # merchantId: URL'nin query parametrelerinden alınır
        query_params = parse_qs(parsed_url.query)
        merchant_id = query_params.get('merchantId', [None])[0]
        
        if not merchant_id:
            print("URL'den merchantId bulunamadı. Sayfa kaynağından alınmaya çalışılacak.")
            # Eğer URL'de merchantId yoksa, bazen ana ürün sayfasında bulunur
            # Bu durumu şimdilik None olarak geçiyoruz, API denemesi başarısız olursa Selenium devreye girer
            pass

        print(f"Bulunan slug: {product_slug}, merchant_id: {merchant_id}")
        return product_slug, merchant_id
        
    except Exception as e:
        print(f"URL ayrıştırma hatası: {e}")
        return None, None

def fetch_reviews_api(product_slug, merchant_id, max_pages=10):
    """
    Trendyol API kullanarak yorumları çeker (YENİ YÖNTEM)
    Bu fonksiyon resmi API'yi kullanarak hızlı ve güvenilir veri çekimi yapar
    """
    reviews = []
    page = 0
    total_pages = 1
    
    # API isteği için merchantId gerekli
    if not merchant_id:
        print("API isteği için merchantId gerekli, bu adım atlanıyor.")
        return []

    print(f"API ile yorumlar çekiliyor: {product_slug} (Merchant: {merchant_id})")
    
    # Sayfa sayfa yorumları çek
    while page < total_pages and page < max_pages:
        try:
            # Sayfa numarasını URL'ye ekle
            url = API_URL.format(product_slug=product_slug, merchantId=merchant_id, page=page)
            print(f"API URL: {url}")
            
            # HTTP session oluştur ve header'ları ayarla
            session = requests.Session()
            session.headers.update(HEADERS)
            
            # API'ye istek gönder
            resp = session.get(url, timeout=30)
            
            # HTTP durum kodunu kontrol et
            if resp.status_code != 200:
                print(f"Sayfa {page} çekilemedi: {resp.status_code}")
                print(f"Response: {resp.text[:200]}")
                break
                
            # JSON yanıtını parse et
            data = resp.json()
            
            # Gelen yanıtta hata olup olmadığını kontrol et
            if not data.get('isSuccess') or 'result' not in data:
                print(f"API'den başarısız yanıt alındı: {data.get('error')}")
                break

            # Yorum verilerini al
            review_data = data['result'].get('productReviews', {})
            
            if page == 0:
                # Toplam sayfa sayısını yanıttan al
                total_pages = min(review_data.get('totalPages', 1), max_pages)
                print(f"Toplam {total_pages} sayfa bulundu.")
            
            # Yorumları işle
            for review in review_data.get('content', []):
                if review.get('comment'):  # Boş yorumları atla
                    reviews.append({
                        'comment': review.get('comment'),
                        'rate': review.get('rate'),
                        'user': review.get('userFullName', 'Anonim'),
                        'date': review.get('commentDateISOtype'),
                        'source': 'api_v2' # Kaynağı yeni API olarak işaretle
                    })
                    
            print(f"{page + 1}/{total_pages} sayfa çekildi. (Toplam {len(reviews)} yorum)")
            page += 1
            time.sleep(1)  # Rate limiting için bekle
            
        except requests.exceptions.RequestException as e:
            print(f"Network hatası sayfa {page}: {e}")
            break
        except Exception as e:
            print(f"Genel hata sayfa {page}: {e}")
            break
    
    return reviews


def fetch_reviews_selenium(url, max_reviews=100):
    """Selenium ile web scraping yaparak yorumları çeker (GÜÇLENDİRİLMİŞ YÖNTEM)"""
    reviews = []
    
    print(f"Selenium ile yorumlar çekiliyor: {url}")
    
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f"user-agent={HEADERS['User-Agent']}")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # URL'yi yorumlar sayfasına çevir
        if '/yorumlar' not in url:
            url = url.replace('?', '/yorumlar?')
        
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        
        # Sayfanın yüklenmesini bekle
        time.sleep(5)
        
        # Yorumları bulmak için farklı selector'ları dene
        review_selectors = [
            '[data-testid="review-card"]',
            '.review-card',
            '.r-card',
            '[class*="review"]',
            '[class*="comment"]',
            '.comment-item',
            '.review-item'
        ]
        
        review_elements = []
        for selector in review_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Yorumlar bulundu: {selector} ile {len(elements)} adet")
                    review_elements = elements
                    break
            except:
                continue
        
        if not review_elements:
            # Sayfayı scroll et ve tekrar dene
            print("İlk denemede yorum bulunamadı, sayfa scroll ediliyor...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            for selector in review_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"Scroll sonrası yorumlar bulundu: {selector} ile {len(elements)} adet")
                        review_elements = elements
                        break
                except:
                    continue
        
        # Yorumları işle
        processed_count = 0
        for element in review_elements:
            try:
                processed_count += 1
                print(f"Element {processed_count}/{len(review_elements)} işleniyor...")
                
                # GÜÇLENDİRİLMİŞ YORUM ÇIKARMA SİSTEMİ
                comment_text = ""
                
                # 1. Adım: Özel Trendyol selector'ları
                trendyol_selectors = [
                    '[data-testid="review-comment"]',
                    '.review-comment',
                    '.comment-text',
                    '.r-card-text',
                    '[class*="comment"]',
                    '[class*="review-text"]',
                    '.review-content',
                    '.comment-content',
                    '[data-testid="comment"]'
                ]
                
                for selector in trendyol_selectors:
                    try:
                        comment_elem = element.find_element(By.CSS_SELECTOR, selector)
                        text = comment_elem.text.strip()
                        if len(text) > 5 and not any(word in text.lower() for word in ['sağlık beyanı', 'fotoğraflı', 'tümü']):
                            comment_text = text
                            print(f"Yorum bulundu ({selector}): {text[:50]}...")
                            break
                    except:
                        continue
                
                # 2. Adım: Genel text elementleri (eğer özel selector'lar başarısızsa)
                if not comment_text:
                    try:
                        # Element içindeki tüm text'leri topla
                        all_texts = element.find_elements(By.CSS_SELECTOR, 'p, span, div, h3, h4, h5')
                        for text_elem in all_texts:
                            text = text_elem.text.strip()
                            if len(text) > 10 and len(text) < 500:  # Makul yorum uzunluğu
                                # Alakasız içerikleri filtrele
                                if not any(word in text.lower() for word in [
                                    'sağlık beyanı', 'fotoğraflı', 'tümü',
                                    'boutique', 'merchant', 'storefront', 'culture', 'logged-in',
                                    'isbuyer', 'channel', 'socialproof', 'abtesting'
                                ]):
                                    comment_text = text
                                    print(f"Genel text bulundu: {text[:50]}...")
                                    break
                    except:
                        pass
                
                # 3. Adım: Element'in kendisinden text çıkar
                if not comment_text:
                    try:
                        full_text = element.text.strip()
                        # Text'i satırlara böl ve en uzun satırı al
                        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                        if lines:
                            longest_line = max(lines, key=len)
                            if len(longest_line) > 5 and len(longest_line) < 500:
                                if not any(word in longest_line.lower() for word in [
                                    'sağlık beyanı', 'fotoğraflı', 'tümü'
                                ]):
                                    comment_text = longest_line
                                    print(f"En uzun satır bulundu: {longest_line[:50]}...")
                    except:
                        pass
                
                if comment_text and len(comment_text) > 3:  # Çok daha gevşek filtreleme
                    # Puanı bul
                    rate = 0
                    try:
                        star_elements = element.find_elements(By.CSS_SELECTOR, '[class*="star"], [class*="rating"]')
                        if star_elements:
                            rate = len([s for s in star_elements if 'filled' in s.get_attribute('class') or 'active' in s.get_attribute('class')])
                    except:
                        pass
                    
                    # Kullanıcı adını bul
                    user_name = "Anonim"
                    try:
                        user_elements = element.find_elements(By.CSS_SELECTOR, '[class*="user"], [class*="author"]')
                        if user_elements:
                            user_name = user_elements[0].text.strip()
                    except:
                        pass
                    
                    # Tekrar eden yorumları kontrol et
                    if not any(r['comment'] == comment_text for r in reviews):
                        reviews.append({
                            'comment': comment_text,
                            'rate': rate,
                            'user': user_name,
                            'date': '',
                            'source': 'selenium_improved'
                        })
                        print(f"Yorum eklendi ({len(comment_text)} karakter): {comment_text[:50]}...")
                
            except Exception as e:
                print(f"Yorum işleme hatası: {e}")
                continue
            
            if len(reviews) >= max_reviews:
                break
        
        # Daha fazla yorum için sayfayı scroll et
        if len(reviews) < max_reviews:
            print("Daha fazla yorum için sayfa scroll ediliyor...")
            last_height = driver.execute_script("return document.body.scrollHeight")
            previous_review_count = len(reviews)
            no_change_count = 0
            
            for scroll_attempt in range(50):  # 50 kez scroll dene (önceki çalışan versiyon)
                print(f"Scroll denemesi {scroll_attempt + 1}/50...")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)  # Daha hızlı scroll
                
                # "Daha Fazla Göster" butonlarını tıkla
                try:
                    load_more_buttons = driver.find_elements(By.CSS_SELECTOR, '[class*="load"], [class*="more"], [class*="show"]')
                    for button in load_more_buttons:
                        if button.is_displayed() and button.is_enabled():
                            driver.execute_script("arguments[0].click();", button)
                            print("Daha fazla göster butonu tıklandı")
                            time.sleep(1)
                except:
                    pass
                
                # Yeni yorumları kontrol et
                for selector in review_selectors:
                    try:
                        new_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if len(new_elements) > len(review_elements):
                            print(f"Yeni yorumlar bulundu: {len(new_elements)} adet")
                            review_elements = new_elements
                            
                            # TÜM elementlerden yorumları çıkar (yeni + eski)
                            for new_element in review_elements:
                                try:
                                    # Aynı güçlendirilmiş yorum çıkarma sistemini kullan
                                    comment_text = ""
                                    
                                    # 1. Adım: Özel Trendyol selector'ları
                                    for selector_name in trendyol_selectors:
                                        try:
                                            comment_elem = new_element.find_element(By.CSS_SELECTOR, selector_name)
                                            text = comment_elem.text.strip()
                                            if len(text) > 5 and not any(word in text.lower() for word in ['sağlık beyanı', 'fotoğraflı', 'tümü']):
                                                comment_text = text
                                                break
                                        except:
                                            continue
                                    
                                    # 2. Adım: Genel text elementleri
                                    if not comment_text:
                                        try:
                                            all_texts = new_element.find_elements(By.CSS_SELECTOR, 'p, span, div, h3, h4, h5')
                                            for text_elem in all_texts:
                                                text = text_elem.text.strip()
                                                if len(text) > 10 and len(text) < 500:
                                                    if not any(word in text.lower() for word in [
                                                        'sağlık beyanı', 'fotoğraflı', 'tümü',
                                                        'boutique', 'merchant', 'storefront', 'culture', 'logged-in',
                                                        'isbuyer', 'channel', 'socialproof', 'abtesting'
                                                    ]):
                                                        comment_text = text
                                                        break
                                        except:
                                            pass
                                    
                                    # 3. Adım: Element'in kendisinden text çıkar
                                    if not comment_text:
                                        try:
                                            full_text = new_element.text.strip()
                                            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                                            if lines:
                                                longest_line = max(lines, key=len)
                                                if len(longest_line) > 5 and len(longest_line) < 500:
                                                    if not any(word in longest_line.lower() for word in [
                                                        'sağlık beyanı', 'fotoğraflı', 'tümü'
                                                    ]):
                                                        comment_text = longest_line
                                        except:
                                            pass
                                    
                                    if comment_text and len(comment_text) > 3:  # Çok daha gevşek filtreleme
                                        # Tekrar eden yorumları kontrol et
                                        if not any(r['comment'] == comment_text for r in reviews):
                                            reviews.append({
                                                'comment': comment_text,
                                                'rate': 0,
                                                'user': 'Anonim',
                                                'date': '',
                                                'source': 'selenium_scroll'
                                            })
                                            print(f"Scroll ile yorum eklendi ({len(comment_text)} karakter): {comment_text[:50]}...")
                                            
                                            # Limit kaldırıldı - tüm yorumları topla
                                            pass
                                except Exception as e:
                                    continue
                            
                            # Limit kaldırıldı - tüm yorumları topla
                            pass
                    except:
                        continue
                
                new_height = driver.execute_script("return document.body.scrollHeight")
                current_review_count = len(reviews)
                print(f"Scroll {scroll_attempt + 1}: {current_review_count} yorum toplandı")
                
                # Eğer son 5 scroll'da yorum sayısı artmadıysa dur
                if scroll_attempt >= 5 and current_review_count == previous_review_count:
                    no_change_count += 1
                    if no_change_count >= 5:
                        print("Yorum sayısı artmıyor, scroll durduruluyor...")
                        break
                else:
                    no_change_count = 0
                
                previous_review_count = current_review_count
                
                if new_height == last_height:
                    print("Sayfa sonuna ulaşıldı, scroll durduruluyor...")
                    break
                last_height = new_height
                
                if len(reviews) >= max_reviews:
                    break

        driver.quit()
        print(f"Selenium ile toplam {len(reviews)} yorum çekildi")
        
    except Exception as e:
        print(f"Selenium başlatma/çalışma hatası: {e}")
        if 'driver' in locals() and driver:
            driver.quit()
    
    return reviews


def detect_website_type(url):
    """URL'den hangi web sitesi olduğunu tespit eder"""
    if 'hepsiburada.com' in url:
        return 'hepsiburada'
    elif 'trendyol.com' in url:
        return 'trendyol'
    else:
        return 'unknown'

def fetch_reviews(url=None, max_pages=10, max_reviews=100):
    """Ana yorum çekme fonksiyonu"""
    reviews = []
    
    # 1. Adım: URL'den gerekli bilgileri çıkar
    if not url:
        print("URL parametresi gerekli.")
        return []
    
    # 2. Adım: Web sitesi türünü tespit et
    website_type = detect_website_type(url)
    print(f"Tespit edilen web sitesi: {website_type}")
    
    if website_type == 'hepsiburada':
        print("Hepsiburada için özel scraper kullanılıyor...")
        reviews = fetch_reviews_hepsiburada(url, max_reviews)
    elif website_type == 'trendyol':
        print("Trendyol için mevcut scraper kullanılıyor...")
        product_slug, merchant_id = extract_product_info_from_url(url)
        
        if not product_slug:
            print("URL'den ürün bilgisi alınamadı.")
            return []

        # Trendyol için Selenium ile yorumları çek
        reviews = fetch_reviews_selenium(url, max_reviews)
    else:
        print(f"Desteklenmeyen web sitesi: {website_type}")
        return []

    # Sonuçları kaydet
    if reviews:
        # Tekrar eden yorumları son bir kez temizle
        unique_reviews = list({r['comment']: r for r in reviews}.values())
        print(f"\nToplam {len(unique_reviews)} adet benzersiz yorum bulundu ve kaydediliyor.")
        with open('reviews.json', 'w', encoding='utf-8') as f:
            json.dump(unique_reviews, f, ensure_ascii=False, indent=2)
        print("Yorumlar 'reviews.json' dosyasına başarıyla kaydedildi.")
    else:
        print("\nHiç yorum çekilemedi.")
    
    return reviews

def main():
    parser = argparse.ArgumentParser(description='E-ticaret sitelerinden ürün yorumlarını çeker (Trendyol, Hepsiburada)')
    parser.add_argument('--url', required=True, help='Ürün URL\'si (Trendyol veya Hepsiburada)')
    parser.add_argument('--max-pages', type=int, default=10, help='API için maksimum sayfa sayısı')
    parser.add_argument('--max-reviews', type=int, default=100, help='Selenium için maksimum yorum sayısı')
    
    args = parser.parse_args()
    
    fetch_reviews(
        url=args.url,
        max_pages=args.max_pages,
        max_reviews=args.max_reviews
    )

if __name__ == "__main__":
    main()