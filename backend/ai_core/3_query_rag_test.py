import argparse
import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def load_index_and_chunks():
    # Script'in bulunduğu dizini al
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    index_path = os.path.join(script_dir, 'index.faiss')
    chunks_path = os.path.join(script_dir, 'chunks.json')
    
    index = faiss.read_index(index_path)
    with open(chunks_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    return index, chunks

def get_top_chunks(question, model, index, chunks, top_k=5):
    q_vec = model.encode([question], convert_to_numpy=True)
    D, I = index.search(q_vec, top_k)
    top_chunks = [chunks[i] for i in I[0]]
    return top_chunks

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--question', required=True, help='Kullanıcı sorusu')
    args = parser.parse_args()

    # Model ve indexleri yükle
    model = SentenceTransformer('all-MiniLM-L6-v2')
    index, chunks = load_index_and_chunks()

    # En alakalı 5 chunk'ı bul
    top_chunks = get_top_chunks(args.question, model, index, chunks, top_k=5)
    
    # Test yanıtı oluştur
    response = f"TEST MODU - Soru: {args.question}\n\nEn alakalı yorumlar:\n"
    for i, chunk in enumerate(top_chunks, 1):
        response += f"{i}. {chunk}\n"
    
    response += "\n[Bu bir test yanıtıdır. Gemini API quota limiti nedeniyle gerçek AI yanıtı verilemiyor.]"
    
    print(response.strip())

if __name__ == "__main__":
    main() 