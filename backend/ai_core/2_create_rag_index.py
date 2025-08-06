# Akilli Yorum Asistani - RAG Index Oluşturma Modülü
# Bu dosya yorumları vektörleştirip arama indexi oluşturur
# Sentence Transformers ve FAISS kullanarak hızlı arama sağlar
# Hackathon Projesi - AI Destekli Yorum Analizi

import json
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

def chunk_text(text, max_length=200):
    """
    Yorumu anlamlı ve kısa parçalara böler. Noktalama ve uzunluk dikkate alınır.
    Bu fonksiyon uzun yorumları AI modelinin işleyebileceği boyutlara böler.
    """
    import re
    # Cümleleri noktalama işaretlerine göre ayır
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current = ''
    
    # Cümleleri birleştirerek uygun boyutta parçalar oluştur
    for sent in sentences:
        if len(current) + len(sent) <= max_length:
            current += (' ' if current else '') + sent
        else:
            if current:
                chunks.append(current.strip())
            current = sent
    
    # Son parçayı ekle
    if current:
        chunks.append(current.strip())
    
    # Boş parçaları filtrele
    return [c for c in chunks if c]

def main():
    # Script'in bulunduğu dizini al
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Yorumları oku - JSON dosyasından yorum verilerini yükle
    reviews_path = os.path.join(script_dir, 'reviews.json')
    with open(reviews_path, 'r', encoding='utf-8') as f:
        reviews = json.load(f)
    
    # 2. Chunk'lara ayır - Yorumları anlamlı parçalara böl
    all_chunks = []
    for review in reviews:
        text = review.get('comment', '')
        if text:
            chunks = chunk_text(text)
            all_chunks.extend(chunks)
    
    print(f"Toplam {len(all_chunks)} metin parçası oluşturuldu.")
    
    # 3. Embedding modeli yükle - Sentence Transformers ile vektörleştirme
    # all-MiniLM-L6-v2 modeli hızlı ve etkili embedding sağlar
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(all_chunks, show_progress_bar=True, convert_to_numpy=True)
    
    # 4. FAISS indeksi oluştur - Hızlı benzerlik araması için
    dim = embeddings.shape[1]  # Embedding boyutunu al
    index = faiss.IndexFlatL2(dim)  # L2 mesafesi kullanarak düz index
    index.add(embeddings)  # Embedding'leri index'e ekle
    
    # Index'i dosyaya kaydet
    index_path = os.path.join(script_dir, 'index.faiss')
    faiss.write_index(index, index_path)
    print(f"FAISS indeksi '{index_path}' olarak kaydedildi.")
    
    # 5. Chunks'ı kaydet - Metin parçalarını JSON formatında sakla
    chunks_path = os.path.join(script_dir, 'chunks.json')
    with open(chunks_path, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    print(f"Tüm metin parçaları '{chunks_path}' olarak kaydedildi.")

if __name__ == "__main__":
    main()
