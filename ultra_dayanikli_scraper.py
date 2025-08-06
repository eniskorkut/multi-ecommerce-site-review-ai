import time
import json
import random # Rastgele bekleme süreleri için
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from colorama import init, Fore, Style

init(autoreset=True)

# Kurulum fonksiyonları aynı kalıyor
def setup_driver_for_local():
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def fetch_reviews(url, max_reviews=9999):
    reviews = []
    print(f"Selenium ile yorumlar çekiliyor (Ultra Dayanıklılık Modu): {url}")
    
    driver = None
    try:
        driver = setup_driver_for_local()
        
        if '/yorumlar' not in url:
            base_url = url.split('?')[0]
            url = base_url.strip('/') + "/yorumlar"
        driver.get(url)

        # 1. Adım: Pop-up'ı kapat
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))).click()
            print("Bilgi: Çerez pop-up'ı kapatıldı.")
            time.sleep(1)
        except Exception:
            print("Bilgi: Çerez pop-up'ı bulunamadı, devam ediliyor.")

        # --- ULTRA DAYANIKLILIK SCROLL MANTIĞI ---
        print("Bilgi: Ultra dayanıklılık modunda dinamik kaydırma başlatıldı...")
        
        patience_limit = 7 # Sabrı artırdık
        patience_counter = 0
        last_comment_count = 0
        max_scroll_attempts = 150 # Sonsuz döngüye karşı bir sigorta (150 * 30 yorum = 4500 yorum kapasitesi)

        for attempt in range(max_scroll_attempts):
            
            # --- YENİ ADIM: HEDEFE ODAKLANARAK SCROLL ETME ---
            # Önce en sondaki yorumu bul
            current_comment_elements = driver.find_elements(By.CSS_SELECTOR, "div.comment")
            if current_comment_elements:
                # En son elementin görüş alanına gelmesini sağla
                last_element = current_comment_elements[-1]
                driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'end' });", last_element)
            else:
                # Henüz yorum yoksa, sayfanın dibine git
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # --- YENİ ADIM: DEĞİŞKEN BEKLEME ---
            # Daha insan gibi davranmak için rastgele bir süre bekle
            sleep_time = random.uniform(1.0, 2.5)
            print(f"Bilgi: {sleep_time:.2f} saniye bekleniyor...")
            time.sleep(sleep_time)

            # "Joker" Buton Avcısı hala görevde
            try:
                button_xpath = "//*[contains(text(), 'Daha Fazla Yorum') or contains(text(), 'Daha Fazla Yorum Göster')]"
                load_more_button = driver.find_element(By.XPATH, button_xpath)
                if load_more_button.is_displayed() and load_more_button.is_enabled():
                    print(f"Bilgi: '{load_more_button.text}' butonu bulundu ve tıklandı.")
                    driver.execute_script("arguments[0].click();", load_more_button)
                    time.sleep(random.uniform(2.0, 3.5)) # Buton sonrası ekstra bekleme
            except Exception:
                pass

            # Yorum sayısını tekrar kontrol et
            current_comment_elements = driver.find_elements(By.CSS_SELECTOR, "div.comment")
            current_comment_count = len(current_comment_elements)
            print(f"Bilgi: Şu an ekranda {current_comment_count} yorum görünüyor.")

            if current_comment_count == last_comment_count:
                patience_counter += 1
                if patience_counter >= patience_limit:
                    print("Bilgi: Yorum sayısı artmıyor. Tüm yorumların yüklendiği varsayılıyor.")
                    break
            else:
                last_comment_count = current_comment_count
                patience_counter = 0
        
        print("Bilgi: HTML ayrıştırılıyor ve tüm detaylar toplanıyor...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        review_cards = soup.select("div.comment")
        print(f"Bilgi: Toplam {len(review_cards)} adet yorum kartı bulundu ve işlenecek.")

        for card in review_cards:
            comment_text_element = card.select_one("div.comment-text p")
            comment_text = comment_text_element.text.strip() if comment_text_element else ""
            if comment_text:
                 if not any(r['comment'] == comment_text for r in reviews):
                     reviews.append({'comment': comment_text})

            if len(reviews) >= max_reviews:
                break
        
    except Exception as e:
        print(f"İşlem sırasında bir hata oluştu: {e}")
    finally:
        if driver:
            driver.quit()
    
    print(f"Toplam {len(reviews)} adet yorum başarıyla çekildi.")
    return reviews


def main_process(url):
    print(Fore.CYAN + Style.BRIGHT + "\n=== Yorum Çekme Süreci BAŞLADI ===\n")
    print(f"İşlem başlatıldı: {url}")
    reviews = fetch_reviews(url)
    output_data = {
        "source_url": url, "scraped_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "comment_count": len(reviews), "reviews": reviews
    }
    final_json = json.dumps(output_data, ensure_ascii=False, indent=4)
    print("\n--- SONUÇ ---")
    print(final_json)
    
    with open("son_yorumlar_ultra_dayanikli.json", "w", encoding="utf-8") as f:
        f.write(final_json)
    print(Fore.GREEN + Style.BRIGHT + "\n=== Yorum Çekme Süreci BİTTİ ===\n")
    print("Sonuçlar 'son_yorumlar_ultra_dayanikli.json' dosyasına da kaydedildi.")


# --- ÇALIŞTIRMA ---
# Çok sayıda yoruma sahip bir ürün linkiyle test etmek en doğrusu
target_url = "https://www.trendyol.com/mega-oto-market/oto-araba-guneslik-semsiye-tip-on-cam-gunes-onleyici-katlanabilir-140cm-x-75cm-p-785203759/yorumlar?boutiqueId=61&merchantId=434536&sav=true" 
main_process(target_url) 