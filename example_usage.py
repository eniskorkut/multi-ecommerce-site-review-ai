#!/usr/bin/env python3
"""
Akıllı Yorum Asistanı - Örnek Kullanım
Bu script gerçek bir Trendyol ürün URL'si ile sistemi test eder.
"""

import requests
import json
import time

def test_fetch_reviews():
    """Yorum çekme işlemini test eder"""
    print("🔄 Yorumlar çekiliyor...")
    
    # Örnek Trendyol ürün URL'si (gerçek bir ürün URL'si ile değiştirin)
    product_url = "https://www.trendyol.com/trendyol-man/trendyol-man-basic-oversize-fit-pamuklu-triko-kazak-p-12345678"
    
    try:
        response = requests.post('http://localhost:8080/fetch-reviews', 
                               json={'product_url': product_url},
                               timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Yorumlar başarıyla çekildi!")
            print(f"📊 Sonuç: {data.get('message', '')}")
            return True
        else:
            print(f"❌ Hata: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return False

def test_ask_question():
    """Soru sorma işlemini test eder"""
    print("\n🔄 Soru soruluyor...")
    
    questions = [
        "Bu ürün kaliteli mi?",
        "Fiyatına değer mi?",
        "Hangi renk daha popüler?",
        "Kargo hızlı mı?",
        "Boyut sıkıntısı var mı?"
    ]
    
    for question in questions:
        try:
            print(f"\n❓ Soru: {question}")
            
            response = requests.post('http://localhost:8080/analyze', 
                                   json={'question': question},
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"🤖 Cevap: {data.get('answer', '')}")
            else:
                print(f"❌ Hata: {response.status_code}")
                
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"❌ Hata: {e}")

def test_fetch_and_ask():
    """Yorumları çek ve soru sor (tek seferde)"""
    print("\n🔄 Yorumları çek ve soru sor...")
    
    # Gerçek bir Trendyol URL'si ile değiştirin
    product_url = "https://www.trendyol.com/trendyol-man/trendyol-man-basic-oversize-fit-pamuklu-triko-kazak-p-12345678"
    question = "Bu ürün kaliteli mi ve fiyatına değer mi?"
    
    try:
        response = requests.post('http://localhost:8080/fetch-and-analyze', 
                               json={
                                   'question': question,
                                   'product_url': product_url
                               },
                               timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ İşlem başarılı!")
            print(f"🤖 Cevap: {data.get('answer', '')}")
            print(f"📊 Detaylar: {data.get('fetchOutput', '')[:200]}...")
        else:
            print(f"❌ Hata: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Hata: {e}")

def main():
    """Ana test fonksiyonu"""
    print("🚀 Akıllı Yorum Asistanı - Örnek Kullanım\n")
    
    # Server'ın çalışıp çalışmadığını kontrol et
    try:
        response = requests.get('http://localhost:8080', timeout=5)
        print("✅ Server çalışıyor")
    except:
        print("❌ Server çalışmıyor! Önce 'npm start' ile backend'i başlatın.")
        return
    
    print("\n" + "="*50)
    print("1. YORUM ÇEKME TESTİ")
    print("="*50)
    test_fetch_reviews()
    
    print("\n" + "="*50)
    print("2. SORU SORMA TESTİ")
    print("="*50)
    test_ask_question()
    
    print("\n" + "="*50)
    print("3. ÇEKTİR VE SOR TESTİ")
    print("="*50)
    test_fetch_and_ask()
    
    print("\n" + "="*50)
    print("🎉 Test tamamlandı!")
    print("="*50)
    
    print("\n📋 Kullanım İpuçları:")
    print("- Gerçek bir Trendyol ürün URL'si kullanın")
    print("- Extension'ı Chrome'da yükleyin")
    print("- Trendyol ürün sayfasında extension'ı açın")
    print("- Sorularınızı yazın ve 'Yorumları Çek ve Sor' butonuna tıklayın")

if __name__ == "__main__":
    main() 