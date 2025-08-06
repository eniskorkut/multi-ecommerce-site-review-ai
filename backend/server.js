// Akilli Yorum Asistani - Hackathon Projesi
// Bu dosya Express.js server'ını içerir ve AI destekli yorum analizi API'sini sağlar
// Backend: Node.js + Express.js
// AI Core: Python + RAG (Retrieval-Augmented Generation)

const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');

// Express uygulamasını başlat
const app = express();
const PORT = 3000; // Server portu

// Middleware ayarları
app.use(cors()); // CORS desteği
app.use(express.json()); // JSON body parser

// Yorumları çekme endpoint'i - Trendyol ürün sayfalarından yorumları çeker
app.post('/fetch-reviews', (req, res) => {
  const { product_url } = req.body;
  
  // URL kontrolü
  if (!product_url) {
    return res.status(400).json({ error: 'product_url zorunludur.' });
  }

  console.log(`Yorumlar çekiliyor: ${product_url}`);

  // Python scraper scriptini çalıştır
  // Selenium ile web scraping yaparak yorumları toplar
  const py = spawn('python', [
    '1_fetch_reviews.py',
    '--url', product_url,
    '--max-pages', '5', // Maksimum sayfa sayısı
    '--max-reviews', '50' // Maksimum yorum sayısı
  ], {
    cwd: path.join(__dirname, 'ai_core') // AI core klasöründe çalıştır
  });

  let output = '';
  let errorOutput = '';

  // Python script çıktısını yakala
  py.stdout.on('data', (data) => {
    output += data.toString();
    console.log('Python output:', data.toString());
  });

  // Python script hatalarını yakala
  py.stderr.on('data', (data) => {
    errorOutput += data.toString();
    console.error('Python error:', data.toString());
  });

  // Python script tamamlandığında
  py.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).json({ 
        error: 'Yorumlar çekilemedi', 
        details: errorOutput,
        output: output 
      });
    }
    
    // Yorumlar çekildikten sonra RAG index'ini güncelle
    updateRagIndex(res, output);
  });
});

// RAG index'ini güncelle - Yorumları vektörleştirip arama indexi oluşturur
function updateRagIndex(res, fetchOutput) {
  console.log('RAG index güncelleniyor...');
  
  // RAG index oluşturma scriptini çalıştır
  const py = spawn('python', ['2_create_rag_index.py'], {
    cwd: path.join(__dirname, 'ai_core')
  });

  let output = '';
  let errorOutput = '';

  // RAG script çıktısını yakala
  py.stdout.on('data', (data) => {
    output += data.toString();
    console.log('RAG output:', data.toString());
  });

  // RAG script hatalarını yakala
  py.stderr.on('data', (data) => {
    errorOutput += data.toString();
    console.error('RAG error:', data.toString());
  });

  // RAG script tamamlandığında
  py.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).json({ 
        error: 'RAG index güncellenemedi', 
        details: errorOutput,
        fetchOutput: fetchOutput 
      });
    }
    
    // Başarılı yanıt döndür
    res.json({ 
      success: true, 
      message: 'Yorumlar çekildi ve RAG index güncellendi',
      fetchOutput: fetchOutput,
      ragOutput: output 
    });
  });
}

// Analiz endpoint'i - Mevcut yorumlardan soru yanıtlar
app.post('/analyze', (req, res) => {
  const { question } = req.body;
  
  // Soru kontrolü
  if (!question) {
    return res.status(400).json({ error: 'question zorunludur.' });
  }

  console.log(`Soru analiz ediliyor: ${question}`);

  // Python RAG sorgulama scriptini çalıştır
  // Gemini AI ile yorumları analiz eder ve soruya yanıt verir
  const py = spawn('python', [
    '3_query_rag.py',
    '--question', question
  ], {
    cwd: path.join(__dirname, 'ai_core')
  });

  let output = '';
  let errorOutput = '';

  // Python script çıktısını yakala
  py.stdout.on('data', (data) => {
    output += data.toString();
  });

  // Python script hatalarını yakala
  py.stderr.on('data', (data) => {
    errorOutput += data.toString();
  });

  // Python script tamamlandığında
  py.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).json({ error: 'Python script hatası', details: errorOutput });
    }
    res.json({ answer: output.trim() });
  });
});

// Yorumları çek ve analiz et endpoint'i - Tek seferde hem yorum çeker hem analiz eder
app.post('/fetch-and-analyze', async (req, res) => {
  const { question, product_url } = req.body;
  
  // Gerekli parametreleri kontrol et
  if (!question || !product_url) {
    return res.status(400).json({ error: 'question ve product_url zorunludur.' });
  }

  console.log(`Yorumlar çekiliyor ve analiz ediliyor: ${product_url}`);

  // İlk adım: Yorumları çek
  // Selenium ile web scraping yaparak ürün yorumlarını toplar
  const fetchPy = spawn('python', [
    '1_fetch_reviews.py',
    '--url', product_url,
    '--max-pages', '2', // Maksimum 2 sayfa
    '--max-reviews', '100' // Maksimum 100 yorum
  ], {
    cwd: path.join(__dirname, 'ai_core'),
    timeout: 300000 // 5 dakika timeout
  });

  let fetchOutput = '';
  let fetchError = '';

  // Yorum çekme script çıktısını yakala
  fetchPy.stdout.on('data', (data) => {
    fetchOutput += data.toString();
  });

  // Yorum çekme script hatalarını yakala
  fetchPy.stderr.on('data', (data) => {
    fetchError += data.toString();
  });

  // Yorum çekme script tamamlandığında
  fetchPy.on('close', (fetchCode) => {
    if (fetchCode !== 0) {
      return res.status(500).json({ 
        error: 'Yorumlar çekilemedi', 
        details: fetchError 
      });
    }

    // İkinci adım: RAG index'ini güncelle
    // Yorumları vektörleştirip arama indexi oluşturur
    const ragPy = spawn('python', ['2_create_rag_index.py'], {
      cwd: path.join(__dirname, 'ai_core'),
      timeout: 120000 // 2 dakika timeout
    });

    let ragOutput = '';
    let ragError = '';

    // RAG script çıktısını yakala
    ragPy.stdout.on('data', (data) => {
      ragOutput += data.toString();
    });

    // RAG script hatalarını yakala
    ragPy.stderr.on('data', (data) => {
      ragError += data.toString();
    });

    // RAG script tamamlandığında
    ragPy.on('close', (ragCode) => {
      if (ragCode !== 0) {
        return res.status(500).json({ 
          error: 'RAG index güncellenemedi', 
          details: ragError 
        });
      }

      // Üçüncü adım: Soruyu analiz et
      // Gemini AI ile yorumları analiz eder ve soruya yanıt verir
      const queryPy = spawn('python', [
        '3_query_rag.py',
        '--question', question
      ], {
        cwd: path.join(__dirname, 'ai_core'),
        timeout: 120000 // 2 dakika timeout
      });

      let queryOutput = '';
      let queryError = '';

      // Sorgulama script çıktısını yakala
      queryPy.stdout.on('data', (data) => {
        queryOutput += data.toString();
      });

      // Sorgulama script hatalarını yakala
      queryPy.stderr.on('data', (data) => {
        queryError += data.toString();
      });

      // Sorgulama script tamamlandığında
      queryPy.on('close', (queryCode) => {
        if (queryCode !== 0) {
          return res.status(500).json({ 
            error: 'Soru analiz edilemedi', 
            details: queryError 
          });
        }

        // Başarılı yanıt döndür
        res.json({ 
          answer: queryOutput.trim(),
          fetchOutput: fetchOutput,
          ragOutput: ragOutput
        });
      });
    });
  });

  // Hata yönetimi - Timeout ve diğer hatalar
  fetchPy.on('error', (error) => {
    if (error.code === 'ETIMEDOUT') {
      return res.status(408).json({ 
        error: 'Yorum çekme işlemi zaman aşımına uğradı', 
        details: 'İşlem 2 dakikadan uzun sürdü'
      });
    }
    return res.status(500).json({ 
      error: 'Yorum çekme hatası', 
      details: error.message 
    });
  });
});

// Server'ı başlat
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
