# Akilli Yorum Asistani - RAG Sorgulama Modülü
# Bu dosya kullanıcı sorularını RAG sistemi ile yanıtlar
# Gemini AI kullanarak akıllı yorum analizi yapar
# Hackathon Projesi - AI Destekli Yorum Analizi

import argparse
import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import google.generativeai as genai

def load_index_and_chunks():
    """
    FAISS index'ini ve metin parçalarını yükler
    Bu fonksiyon önceden oluşturulmuş vektör index'ini ve metin parçalarını okur
    """
    # Script'in bulunduğu dizini al
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Index ve chunks dosya yollarını belirle
    index_path = os.path.join(script_dir, 'index.faiss')
    chunks_path = os.path.join(script_dir, 'chunks.json')
    
    # FAISS index'ini yükle
    index = faiss.read_index(index_path)
    
    # Metin parçalarını JSON'dan yükle
    with open(chunks_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    return index, chunks

def get_top_chunks(question, model, index, chunks, top_k=5):
    """
    Soruya en uygun metin parçalarını bulur
    Bu fonksiyon semantic search ile en alakalı yorum parçalarını döndürür
    """
    # Soruyu vektörleştir
    q_vec = model.encode([question], convert_to_numpy=True)
    
    # FAISS ile en yakın parçaları ara
    D, I = index.search(q_vec, top_k)
    
    # En alakalı parçaları döndür
    top_chunks = [chunks[i] for i in I[0]]
    return top_chunks

def build_improved_prompt(question, top_chunks, product_stats):
    """
    Gemini için geliştirilmiş bir prompt oluşturur
    Bu fonksiyon AI modeline gönderilecek detaylı ve yapılandırılmış prompt hazırlar
    
    Args:
        question (str): Kullanıcının sorusu
        top_chunks (list): RAG ile çekilmiş en ilgili yorum parçaları
        product_stats (dict): Ortalama puan, yorum sayısı gibi istatistiksel veriler
    """
    # Tüm yorumları numaralandırarak göster
    context = '\n'.join(f'{i+1}. {c}' for i, c in enumerate(top_chunks))
    
    # Detaylı prompt oluştur
    prompt = (
        "Sen, e-ticaret sitelerindeki ürün yorumlarını analiz eden uzman bir yapay zeka asistanısın. "
        "Görevin, kullanıcı yorumlarını analiz ederek kısa ve öz bir genel değerlendirme sunmaktır.\n\n"
        "**ÜRÜNÜN GENEL PUAN DURUMU:**\n"
        f"- Ortalama Puan: {product_stats.get('ortalamaPuan', 'N/A')} / 5\n"
        f"- Toplam Değerlendirme Sayısı: {product_stats.get('toplamDegerlendirme', 'N/A')}\n"
        f"- Pozitif Yorumlar: {product_stats.get('pozitifYorumlar', 'N/A')}\n"
        f"- Negatif Yorumlar: {product_stats.get('negatifYorumlar', 'N/A')}\n\n"
        "**KULLANICI YORUMLARI:**\n"
        f"{context}\n\n"
        f"**TOPLAM YORUM SAYISI:** {len(top_chunks)} adet yorum bulunmaktadır.\n\n"
        "--- GÖREV ve KURALLAR ---\n"
        "1. **Sadece Sağlanan Bilgiyi Kullan:** Cevabını SADECE yukarıdaki bilgilere dayandır.\n"
        "2. **Kısa ve Öz Ol:** Maksimum 3-4 paragraf yaz.\n"
        "3. **Dengeli Bakış Açısı:** Hem olumlu hem olumsuz yönleri kısaca belirt.\n"
        "4. **Genel Değerlendirme Formatı:**\n"
        "    - **Genel Değerlendirme:** Yorumların genel havasını özetleyen kısa bir paragraf (olumlu/olumsuz yönler dahil).\n"
        "    - **Sonuç:** Kısa bir tavsiye veya özet.\n"
        "5. **Gereksiz Detaylardan Kaçın:** Uzun listeler ve çok fazla alıntı yapma.\n"
        "-----------------------------------\n\n"
        f"**KULLANICININ SORUSU:** {question}\n\n"
        "**GENEL DEĞERLENDİRME (Kısa ve öz, Türkçe):**"
    )
    return prompt

def build_prompt(question, top_chunks):
    """Eski prompt fonksiyonu - geriye uyumluluk için"""
    return build_improved_prompt(question, top_chunks, {})

def extract_product_stats(chunks):
    """
    Yorumlardan ürün istatistiklerini çıkarır
    Bu fonksiyon yorumların tonunu ve puanlarını analiz eder
    """
    stats = {
        'ortalamaPuan': 0,
        'toplamDegerlendirme': len(chunks),
        'pozitifYorumlar': 0,
        'negatifYorumlar': 0,
        'nötrYorumlar': 0
    }
    
    total_rating = 0
    rating_count = 0
    
    # Her yorum parçasını analiz et
    for chunk in chunks:
        # Rating bilgisi varsa topla
        if 'rate' in chunk and chunk['rate'] > 0:
            total_rating += chunk['rate']
            rating_count += 1
        
        # Yorum tonunu analiz et - Basit kelime tabanlı analiz
        text = chunk.lower()
        positive_words = ['güzel', 'iyi', 'beğendim', 'memnun', 'kaliteli', 'tavsiye', 'harika', 'mükemmel']
        negative_words = ['kötü', 'berbat', 'memnun değil', 'kırık', 'bozuk', 'iade']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        # Yorum tonunu sınıflandır
        if positive_count > negative_count:
            stats['pozitifYorumlar'] += 1
        elif negative_count > positive_count:
            stats['negatifYorumlar'] += 1
        else:
            stats['nötrYorumlar'] += 1
    
    if rating_count > 0:
        stats['ortalamaPuan'] = round(total_rating / rating_count, 1)
    
    return stats

def add_review_count_to_response(response_text, total_chunks, used_chunks):
    """AI cevabının sonuna yorum sayısını ekler"""
    review_count_info = f"\n\n---\n📊 **Test Bilgisi**: Bu analiz {used_chunks}/{total_chunks} yorumdan oluşturulmuştur."
    return response_text + review_count_info

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--question', required=True, help='Kullanıcı sorusu')
    args = parser.parse_args()

    # .env'den API anahtarını yükle
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print('Gemini API anahtarı .env dosyasında bulunamadı.', flush=True)
        exit(1)
    genai.configure(api_key=api_key)

    # Model ve indexleri yükle
    model = SentenceTransformer('all-MiniLM-L6-v2')
    index, chunks = load_index_and_chunks()

    # Tüm yorumları detaylı formatla
    all_reviews = []
    for i, chunk in enumerate(chunks):
        if isinstance(chunk, dict):
            # Dictionary formatındaki yorumları detaylı göster
            review_text = f"YORUM {i+1}: "
            if 'comment' in chunk:
                review_text += chunk['comment']
            if 'rate' in chunk and chunk['rate'] > 0:
                review_text += f" (Puan: {chunk['rate']}/5)"
            if 'user' in chunk and chunk['user'] != 'Anonim':
                review_text += f" (Kullanıcı: {chunk['user']})"
            all_reviews.append(review_text)
        elif isinstance(chunk, str):
            all_reviews.append(f"YORUM {i+1}: {chunk}")
    
    # Tüm yorumları birleştir
    top_chunks = all_reviews
    
    # Ürün istatistiklerini çıkar
    product_stats = extract_product_stats(chunks)
    
    # Geliştirilmiş prompt kullan
    prompt = build_improved_prompt(args.question, top_chunks, product_stats)

    # Gemini ile yanıt al
    gemini = genai.GenerativeModel('gemini-1.5-pro')
    response = gemini.generate_content(prompt)
    
    # Cevabın sonuna yorum sayısını ekle
    final_response = add_review_count_to_response(response.text.strip(), len(chunks), len(top_chunks))
    print(final_response)

if __name__ == "__main__":
    main()
