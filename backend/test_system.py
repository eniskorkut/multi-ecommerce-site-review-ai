#!/usr/bin/env python3
"""
Akilli Yorum Asistani - Test Sistemi
Bu script sistemin doğru çalışıp çalışmadığını test eder
Hackathon Projesi - AI Destekli Yorum Analizi
"""

import json
import os
import sys
import subprocess
from pathlib import Path

def create_sample_reviews():
    """
    Test için örnek yorumlar oluşturur
    Bu fonksiyon AI sisteminin test edilmesi için gerçekçi yorum verileri oluşturur
    """
    sample_reviews = [
        {
            "comment": "Bu ürün gerçekten çok kaliteli. Fiyatına değer kesinlikle. Kargo da hızlıydı.",
            "rate": 5,
            "user": "TestUser1",
            "date": "2024-01-15",
            "source": "test"
        },
        {
            "comment": "Ürün güzel ama biraz küçük geldi. Kalitesi iyi ama boyut sıkıntısı var.",
            "rate": 4,
            "user": "TestUser2", 
            "date": "2024-01-14",
            "source": "test"
        },
        {
            "comment": "Çok kötü bir ürün. Kırık geldi ve kalitesi berbat. Para israfı.",
            "rate": 1,
            "user": "TestUser3",
            "date": "2024-01-13", 
            "source": "test"
        },
        {
            "comment": "Orta kalitede bir ürün. Fiyatına göre makul. Tavsiye ederim.",
            "rate": 3,
            "user": "TestUser4",
            "date": "2024-01-12",
            "source": "test"
        },
        {
            "comment": "Harika bir ürün! Çok memnun kaldım. Arkadaşlarıma da tavsiye ettim.",
            "rate": 5,
            "user": "TestUser5",
            "date": "2024-01-11",
            "source": "test"
        }
    ]
    
    # AI core dizininde reviews.json oluştur
    ai_core_path = Path('ai_core')
    reviews_path = ai_core_path / 'reviews.json'
    with open(reviews_path, 'w', encoding='utf-8') as f:
        json.dump(sample_reviews, f, ensure_ascii=False, indent=2)
    
    print("✅ Örnek yorumlar oluşturuldu")

def test_rag_index():
    """
    RAG index oluşturmayı test eder
    Bu fonksiyon vektörleştirme ve index oluşturma sürecini test eder
    """
    try:
        print("🔄 RAG index oluşturuluyor...")
        
        # RAG index oluşturma scriptini çalıştır
        result = subprocess.run(['python', 'ai_core/2_create_rag_index.py'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✅ RAG index başarıyla oluşturuldu")
            return True
        else:
            print(f"❌ RAG index oluşturulamadı: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ RAG index test hatası: {e}")
        return False

def test_query():
    """
    Soru sorma işlemini test eder
    Bu fonksiyon AI modelinin yorum analizi yapabilme yeteneğini test eder
    """
    try:
        print("🔄 Test sorusu soruluyor...")
        
        # .env dosyasını kontrol et - Gemini API anahtarı gerekli
        env_path = Path('ai_core/.env')
        if not env_path.exists():
            print("⚠️  .env dosyası bulunamadı. Gemini API anahtarı gerekli.")
            print("   Lütfen backend/ai_core/.env dosyası oluşturun ve API anahtarınızı ekleyin.")
            return False
        
        # Test sorusu sor
        result = subprocess.run(['python', 'ai_core/3_query_rag.py', '--question', 'Bu ürün kaliteli mi?'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✅ Test sorusu başarıyla yanıtlandı")
            print(f"📝 Yanıt:\n{result.stdout}")
            return True
        else:
            print(f"❌ Test sorusu yanıtlanamadı: {result.stderr}")
            if "API anahtarı" in result.stderr:
                print("   Lütfen .env dosyasında geçerli bir Gemini API anahtarı olduğundan emin olun.")
            return False
    except Exception as e:
        print(f"❌ Test sorusu hatası: {e}")
        return False

def test_server():
    """Server'ın çalışıp çalışmadığını test eder"""
    try:
        import requests
        response = requests.get('http://localhost:8080', timeout=5)
        print("✅ Server çalışıyor")
        return True
    except:
        print("❌ Server çalışmıyor (localhost:8080)")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🚀 Akıllı Yorum Asistanı Test Başlatılıyor...\n")
    
    # AI core dizinine geç
    ai_core_path = Path('ai_core')
    if not ai_core_path.exists():
        print("❌ ai_core dizini bulunamadı!")
        return
    
    # 1. Örnek yorumlar oluştur
    create_sample_reviews()
    
    # 2. RAG index test et
    if not test_rag_index():
        print("❌ RAG index testi başarısız!")
        return
    
    # 3. Soru sorma test et
    if not test_query():
        print("❌ Soru sorma testi başarısız!")
        return
    
    # 4. Server test et (opsiyonel)
    print("\n🔄 Server test ediliyor...")
    test_server()
    
    print("\n🎉 Tüm testler tamamlandı!")
    print("\n📋 Kullanım:")
    print("1. Backend'i başlat: npm start")
    print("2. Extension'ı yükle: chrome://extensions/")
    print("3. Trendyol ürün sayfasına git")
    print("4. Extension'ı aç ve yorumları çek")

if __name__ == "__main__":
    main() 