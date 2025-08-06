// Akilli Yorum Asistani - Chrome Extension Frontend
// Bu dosya Chrome extension'ının popup arayüzünü ve API iletişimini yönetir
// Backend API ile iletişim kurarak yorum analizi yapar

// DOM elementlerini seç
const questionInput = document.getElementById('question-input');
const askBtn = document.getElementById('ask-btn');
const statusDiv = document.getElementById('status');
const resultsContainer = document.getElementById('results-container');
const resultsContent = document.getElementById('results-content');

// Buton durumunu yönet - Loading ve normal durumlar arasında geçiş
function setButtonDisabled(disabled) {
  askBtn.disabled = disabled;
  if (disabled) {
    // Loading durumu - buton devre dışı ve gri renk
    askBtn.innerHTML = '<span class="icon"></span>Analiz Ediliyor...';
    askBtn.style.background = 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)';
  } else {
    // Normal durum - buton aktif ve mavi renk
    askBtn.innerHTML = '<span class="icon"></span>Sor ve Analiz Et';
    askBtn.style.background = 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)';
  }
}

// Durum mesajlarını göster - Kullanıcıya işlem durumu hakkında bilgi verir
function showStatus(message, type = 'info') {
  statusDiv.textContent = message;
  statusDiv.className = `status ${type}`;
  
  // Smooth fade in animasyonu
  statusDiv.style.opacity = '0';
  statusDiv.style.transform = 'translateY(10px)';
  
  setTimeout(() => {
    statusDiv.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    statusDiv.style.opacity = '1';
    statusDiv.style.transform = 'translateY(0)';
  }, 10);
}

// Analiz sonuçlarını göster - AI yanıtını kullanıcıya sunar
function showResults(content) {
  resultsContent.textContent = content;
  resultsContainer.style.display = 'block';
  
  // Smooth slide up animasyonu
  resultsContainer.style.opacity = '0';
  resultsContainer.style.transform = 'translateY(20px)';
  
  setTimeout(() => {
    resultsContainer.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
    resultsContainer.style.opacity = '1';
    resultsContainer.style.transform = 'translateY(0)';
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, 50);
}

// Sonuçları gizle - Yeni analiz başlatmadan önce önceki sonuçları temizler
function hideResults() {
  resultsContainer.style.display = 'none';
}

// Professional loading animasyonu - Kullanıcı deneyimini iyileştirir
function showLoadingAnimation() {
  const loadingStates = [
    'Yorumlar çekiliyor',
    'Veriler analiz ediliyor',
    'AI modeli çalışıyor',
    'Sonuçlar hazırlanıyor'
  ];
  
  let stateIndex = 0;
  let dotCount = 0;
  
  // Her 800ms'de bir loading mesajını değiştir
  const interval = setInterval(() => {
    if (!askBtn.disabled) {
      clearInterval(interval);
      return;
    }
    
    const dots = '.'.repeat(dotCount + 1);
    const loadingText = `${loadingStates[stateIndex]}${dots}`;
    showStatus(loadingText, 'loading');
    
    dotCount++;
    if (dotCount > 3) {
      dotCount = 0;
      stateIndex = (stateIndex + 1) % loadingStates.length;
    }
  }, 800);
  
  return interval;
}

// Backend API ile iletişim kur - HTTP istekleri gönderir
async function makeApiCall(endpoint, data) {
    try {
    const response = await fetch(`http://localhost:3000/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        // Timeout ayarı - 10 dakika (uzun süren işlemler için)
        signal: AbortSignal.timeout(600000)
      });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    // Timeout hatalarını özel olarak yakala
    if (error.name === 'TimeoutError') {
      throw new Error('İşlem çok uzun sürdü. Lütfen tekrar deneyin.');
    }
    throw new Error(`API hatası: ${error.message}`);
  }
}

// Aktif sekmenin URL'sini al - Chrome API kullanarak mevcut sayfa URL'sini alır
async function getCurrentTabUrl() {
  try {
    const tabs = await chrome.tabs.query({active: true, currentWindow: true});
    return tabs[0]?.url || '';
  } catch (error) {
    throw new Error('Sekme URL\'si alınamadı');
  }
}

// Ana fonksiyon: Yorumları çek ve analiz et - Kullanıcı sorularını AI ile yanıtlar
async function askAndAnalyze() {
  try {
    // Kullanıcı soru girişini kontrol et
    const question = questionInput.value.trim();
    if (!question) {
      showStatus('❌ Lütfen bir soru girin.', 'error');
      return;
    }
    
    // UI'yi loading durumuna geçir
    setButtonDisabled(true);
    hideResults();
    const loadingInterval = showLoadingAnimation();
    
    // Mevcut sayfa URL'sini al ve kontrol et
    const productUrl = await getCurrentTabUrl();
    if (!productUrl.includes('trendyol.com') && !productUrl.includes('hepsiburada.com')) {
      throw new Error('Bu sayfa Trendyol veya Hepsiburada ürün sayfası değil. Lütfen bir e-ticaret ürün sayfasında olun.');
    }
    
    // Backend API'ye istek gönder - Yorumları çek ve analiz et
    const data = await makeApiCall('fetch-and-analyze', { 
      question, 
      product_url: productUrl 
    });
    
    // Loading animasyonunu durdur ve başarı mesajı göster
    clearInterval(loadingInterval);
    showStatus('✅ Analiz başarıyla tamamlandı!', 'success');
    
    // AI yanıtını formatla - Sadece "Genel Değerlendirme" ve "Test Bilgisi" kısımlarını çıkar
    let generalEvaluation = '';
    let testInfo = '';
    if (data.answer) {
      const lines = data.answer.split('\n');
      let inGeneralSection = false;
      let inTestSection = false;
      
      // AI yanıtını satır satır işle
      for (const line of lines) {
        const cleanLine = line.replace(/\*\*/g, '').trim(); // Markdown formatını temizle
        
        // Bölüm başlıklarını tespit et
        if (cleanLine.includes('Genel Değerlendirme') || cleanLine.includes('GENEL DEĞERLENDİRME')) {
          inGeneralSection = true;
          inTestSection = false;
          continue;
        } else if (cleanLine.includes('Test Bilgisi') || cleanLine.includes('TEST BİLGİSİ')) {
          inGeneralSection = false;
          inTestSection = true;
          continue;
        } else if (cleanLine.includes('Sonuç:') || cleanLine.includes('SONUÇ:')) {
          // Sonuç kısmını atla
          break;
        } else if (inGeneralSection && cleanLine === '') {
          // Boş satırla genel değerlendirme biter
          inGeneralSection = false;
        } else if (inGeneralSection) {
          generalEvaluation += cleanLine + '\n';
        } else if (inTestSection) {
          testInfo += cleanLine + '\n';
        }
      }
    }
    
    // Fallback: Eğer "Genel Değerlendirme" bulunamazsa, tüm cevabı göster
    if (!generalEvaluation.trim()) {
      generalEvaluation = data.answer.replace(/\*\*/g, ''); // Markdown formatını temizle
    }
    
    // Son formatı oluştur: Genel Değerlendirme + Test Bilgisi
    let formattedResponse = generalEvaluation.trim();
    if (testInfo.trim()) {
      formattedResponse += '\n\n' + testInfo.trim();
    }
    
    // Sonuçları kullanıcıya göster
    showResults(formattedResponse);
    
  } catch (error) {
    // Hata durumunda kullanıcıya bilgi ver
    showStatus('❌ Hata: ' + error.message, 'error');
  } finally {
    // Her durumda butonu tekrar aktif hale getir
    setButtonDisabled(false);
  }
}

// Event listeners - Kullanıcı etkileşimlerini yakala
askBtn.addEventListener('click', askAndAnalyze);

// Enter tuşu ile soru sor - Kullanıcı deneyimini iyileştirir
questionInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    askAndAnalyze();
  }
});

// Gelişmiş focus yönetimi - Professional animasyonlar ile kullanıcı deneyimini iyileştirir
questionInput.addEventListener('focus', () => {
  questionInput.style.borderColor = '#3b82f6';
  questionInput.style.transform = 'translateY(-1px)';
  questionInput.style.boxShadow = '0 0 0 4px rgba(59, 130, 246, 0.1), 0 4px 6px -1px rgba(0, 0, 0, 0.1)';
});

questionInput.addEventListener('blur', () => {
  questionInput.style.borderColor = '#e2e8f0';
  questionInput.style.transform = 'translateY(0)';
  questionInput.style.boxShadow = 'none';
});

// Professional buton hover efektleri - Kullanıcı etkileşimini iyileştirir
askBtn.addEventListener('mouseenter', () => {
  if (!askBtn.disabled) {
    askBtn.style.transform = 'translateY(-2px)';
  }
});

askBtn.addEventListener('mouseleave', () => {
  if (!askBtn.disabled) {
    askBtn.style.transform = 'translateY(0)';
  }
});

// Sayfa yüklendiğinde durumu kontrol et - Kullanıcıya mevcut sayfa hakkında bilgi ver
document.addEventListener('DOMContentLoaded', async () => {
  try {
    const url = await getCurrentTabUrl();
    if (url.includes('trendyol.com')) {
      showStatus('✅ Trendyol sayfasında bulunuyorsunuz. Soru sorun, yorumları otomatik çekip analiz edelim.', 'success');
    } else if (url.includes('hepsiburada.com')) {
      showStatus('✅ Hepsiburada sayfasında bulunuyorsunuz. Soru sorun, yorumları otomatik çekip analiz edelim.', 'success');
    } else {
      showStatus('⚠️ Trendyol veya Hepsiburada ürün sayfasında değilsiniz.', 'error');
    }
  } catch (error) {
    showStatus('❌ Sayfa durumu kontrol edilemedi.', 'error');
  }
});
