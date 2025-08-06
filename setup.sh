#!/bin/bash

echo "🚀 Akıllı Yorum Asistanı Kurulum Scripti"
echo "========================================"

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Python kontrolü
echo -e "${BLUE}📋 Python kontrol ediliyor...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python $PYTHON_VERSION bulundu${NC}"
else
    echo -e "${RED}❌ Python3 bulunamadı! Lütfen Python 3.8+ yükleyin.${NC}"
    exit 1
fi

# Node.js kontrolü
echo -e "${BLUE}📋 Node.js kontrol ediliyor...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js $NODE_VERSION bulundu${NC}"
else
    echo -e "${RED}❌ Node.js bulunamadı! Lütfen Node.js 16+ yükleyin.${NC}"
    exit 1
fi

# Backend dizinine geç
cd backend

# Python paketlerini yükle
echo -e "${BLUE}📦 Python paketleri yükleniyor...${NC}"
if pip3 install -r requirements.txt; then
    echo -e "${GREEN}✅ Python paketleri yüklendi${NC}"
else
    echo -e "${RED}❌ Python paketleri yüklenemedi${NC}"
    exit 1
fi

# Node.js paketlerini yükle
echo -e "${BLUE}📦 Node.js paketleri yükleniyor...${NC}"
if npm install; then
    echo -e "${GREEN}✅ Node.js paketleri yüklendi${NC}"
else
    echo -e "${RED}❌ Node.js paketleri yüklenemedi${NC}"
    exit 1
fi

# Test sistemini çalıştır
echo -e "${BLUE}🧪 Sistem test ediliyor...${NC}"
if python3 test_system.py; then
    echo -e "${GREEN}✅ Sistem testi başarılı${NC}"
else
    echo -e "${YELLOW}⚠️  Sistem testi başarısız, manuel kontrol gerekebilir${NC}"
fi

# .env dosyası kontrolü
echo -e "${BLUE}🔑 .env dosyası kontrol ediliyor...${NC}"
if [ ! -f "ai_core/.env" ]; then
    echo -e "${YELLOW}⚠️  .env dosyası bulunamadı${NC}"
    echo -e "${BLUE}📝 .env dosyası oluşturuluyor...${NC}"
    echo "GEMINI_API_KEY=your_api_key_here" > ai_core/.env
    echo -e "${YELLOW}⚠️  Lütfen ai_core/.env dosyasına Gemini API anahtarınızı ekleyin${NC}"
else
    echo -e "${GREEN}✅ .env dosyası mevcut${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Kurulum tamamlandı!${NC}"
echo ""
echo -e "${BLUE}📋 Kullanım Adımları:${NC}"
echo "1. Gemini API anahtarınızı ai_core/.env dosyasına ekleyin"
echo "2. Backend'i başlatın: cd backend && npm start"
echo "3. Chrome'da chrome://extensions/ adresine gidin"
echo "4. 'Developer mode' açın"
echo "5. 'Load unpacked' ile frontend-extension klasörünü yükleyin"
echo "6. Trendyol ürün sayfasına gidin ve extension'ı kullanın"
echo ""
echo -e "${BLUE}🧪 Test için:${NC}"
echo "python3 example_usage.py"
echo ""
echo -e "${GREEN}🚀 İyi kullanımlar!${NC}" 