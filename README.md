# Multi-Site Review AI - Akıllı Yorum Asistanı

**Çoklu e-ticaret sitesi yorum analizi yapan yapay zeka destekli Chrome extension**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/Node.js-16+-green.svg)](https://nodejs.org)
[![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-yellow.svg)](https://chrome.google.com)
[![AI](https://img.shields.io/badge/AI-Gemini-purple.svg)](https://ai.google.dev)

## Proje Hakkında

Multi-Site Review AI, e-ticaret sitelerindeki ürün yorumlarını otomatik olarak çekip, yapay zeka ile analiz eden akıllı bir Chrome extension'ıdır. Kullanıcıların sorularını yorumlara dayalı olarak yanıtlar ve ürün hakkında detaylı analiz sunar.

### Desteklenen Siteler
- **Trendyol** - API ve Selenium entegrasyonu
- **Hepsiburada** - Özel web scraper
- *Diğer e-ticaret siteleri için genişletilebilir*

## Özellikler

### Akıllı Yorum Çekme
- **Trendyol API**: Resmi API ile hızlı veri çekimi
- **Selenium Scraping**: Dinamik içerikler için güçlü scraping
- **Çoklu Sayfa Desteği**: Otomatik sayfalama
- **Gerçek Zamanlı**: Anında yorum güncelleme

### AI Destekli Analiz
- **RAG Teknolojisi**: Retrieval-Augmented Generation
- **Gemini AI**: Google'ın en gelişmiş AI modeli
- **Semantic Search**: Anlamlı arama ve analiz
- **Akıllı Soru-Cevap**: Doğal dil işleme

### Kullanıcı Deneyimi
- **Chrome Extension**: Tek tıkla erişim
- **Gerçek Zamanlı**: Anında analiz sonuçları
- **Responsive UI**: Modern ve kullanıcı dostu arayüz
- **Çoklu Dil**: Türkçe destek

## Teknik Mimari

```
multi-site-review-ai/
├── backend/                 # Node.js + Express API
│   ├── ai_core/            # Python AI modülleri
│   │   ├── 1_fetch_reviews.py    # Yorum çekme
│   │   ├── 2_create_rag_index.py # RAG index oluşturma
│   │   ├── 3_query_rag.py        # AI sorgulama
│   │   └── hepsiburada_scraper.py # Hepsiburada scraper
│   ├── server.js           # Express server
│   └── test_system.py      # Test sistemi
├── frontend-extension/      # Chrome extension
│   ├── popup.html          # UI arayüzü
│   ├── popup.js            # Frontend logic
│   └── manifest.json       # Extension manifest
└── README.md               # Bu dosya
```

## Kurulum

### Gereksinimler
- **Python 3.8+**
- **Node.js 16+**
- **Chrome/Chromium** (Selenium için)
- **Gemini API Anahtarı**

### 1. Projeyi Klonlayın
```bash
git clone https://github.com/eniskorkut/multi-site-review-ai.git
cd multi-site-review-ai
```

### 2. Backend Kurulumu
```bash
cd backend

# Python paketlerini yükleyin
pip install -r requirements.txt

# Node.js paketlerini yükleyin
npm install

# Test sistemini çalıştırın
python test_system.py
```

### 3. Gemini API Anahtarı
1. [Google AI Studio](https://makersuite.google.com/app/apikey) adresine gidin
2. Google hesabınızla giriş yapın
3. "Create API Key" butonuna tıklayın
4. API anahtarınızı kopyalayın

```bash
cd backend/ai_core
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
```

**Önemli**: `your_actual_api_key_here` kısmını gerçek API anahtarınızla değiştirin!

### 4. Chrome Extension Kurulumu
1. Chrome'da `chrome://extensions/` adresine gidin
2. "Developer mode" açın
3. "Load unpacked" butonuna tıklayın
4. `frontend-extension` klasörünü seçin

## Kullanım

### 1. Backend'i Başlatın
```bash
cd backend
npm start
```
Server `http://localhost:3000` adresinde çalışacak.

### 2. Extension'ı Kullanın
1. **Trendyol** veya **Hepsiburada**'da bir ürün sayfasına gidin
2. Extension ikonuna tıklayın
3. İstediğiniz soruyu yazın (örn: "Bu ürün kaliteli mi?")
4. "Yorumları Çek ve Sor" butonuna tıklayın

### 3. Manuel Test
```bash
# Yorumları çek
python ai_core/1_fetch_reviews.py --url "https://www.trendyol.com/urun-url"

# RAG index oluştur
python ai_core/2_create_rag_index.py

# Soru sor
python ai_core/3_query_rag.py --question "Bu ürün kaliteli mi?"
```

## API Endpoints

### `POST /fetch-reviews`
Yorumları çeker ve RAG index'ini günceller.

```json
{
  "product_url": "https://www.trendyol.com/urun-url"
}
```

### `POST /analyze`
Mevcut yorumlardan soru yanıtlar.

```json
{
  "question": "Bu ürün kaliteli mi?"
}
```

### `POST /fetch-and-analyze`
Yorumları çeker ve soruyu yanıtlar (tek seferde).

```json
{
  "question": "Bu ürün kaliteli mi?",
  "product_url": "https://www.trendyol.com/urun-url"
}
```

## RAG Sistemi

### 1. Yorum Çekme
- Trendyol API'si veya Selenium ile
- Hepsiburada özel scraper ile
- Çoklu sayfa desteği

### 2. Metin Bölme
- Yorumları anlamlı parçalara bölme
- Cümle bazlı chunking
- Maksimum 200 karakter

### 3. Embedding
- Sentence transformers ile vektörleştirme
- all-MiniLM-L6-v2 modeli
- 384 boyutlu vektörler

### 4. Indexleme
- FAISS ile hızlı arama
- L2 mesafesi kullanımı
- Gerçek zamanlı güncelleme

### 5. Retrieval
- En alakalı parçaları bulma
- Semantic search
- Top-k benzerlik

### 6. Generation
- Gemini AI ile yanıt üretme
- Context-aware responses
- Türkçe dil desteği

## Örnek Kullanım

### Kullanıcı Sorusu:
> "Bu ürün kaliteli mi?"

### AI Yanıtı:
```
**Genel Değerlendirme:** Yorumlara göre bu ürün genellikle kaliteli olarak değerlendiriliyor. 
5 yıldızlı yorumlarda 'çok kaliteli', 'harika ürün' gibi ifadeler kullanılmış. 
Ancak bazı kullanıcılar boyut konusunda sıkıntı yaşamış. 
Genel olarak fiyatına değer bir ürün olduğu belirtiliyor.

**Sonuç:** Ürün, olumlu yorumların ağırlığına bakılırsa denenebilir. 
Ancak, boyut konusunda dikkatli olunmalı ve olası bir sorunla karşılaşma 
ihtimaline karşı satıcının iade politikası kontrol edilmelidir.

---
**Test Bilgisi**: Bu analiz 5/5 yorumdan oluşturulmuştur.
```

## Sorun Giderme

### Yorumlar Çekilmiyor
- URL'nin doğru olduğundan emin olun
- Selenium Chrome driver'ının yüklü olduğunu kontrol edin
- Network bağlantınızı kontrol edin

### AI Yanıt Vermiyor
- Gemini API anahtarınızı kontrol edin
- `.env` dosyasının doğru konumda olduğunu kontrol edin
- API quota limitinizi kontrol edin

### Extension Çalışmıyor
- Backend'in çalıştığından emin olun (`localhost:3000`)
- Extension'ı yeniden yükleyin
- Chrome console'da hata mesajlarını kontrol edin

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## Teşekkürler

- [Google Gemini AI](https://ai.google.dev) - AI modeli
- [Trendyol API](https://www.trendyol.com) - E-ticaret verileri
- [Hepsiburada](https://www.hepsiburada.com) - E-ticaret verileri
- [Sentence Transformers](https://www.sbert.net) - Embedding modeli
- [FAISS](https://github.com/facebookresearch/faiss) - Vektör arama
- [Chrome Extension API](https://developer.chrome.com/docs/extensions/) - Browser extension

## İletişim

- **GitHub**: [@eniskorkut](https://github.com/eniskorkut)
- **Proje**: [multi-site-review-ai](https://github.com/eniskorkut/multi-site-review-ai)

---

**Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!** 