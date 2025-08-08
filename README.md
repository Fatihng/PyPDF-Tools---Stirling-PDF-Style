# PyPDF Tools - Stirling-PDF Style

Stirling-PDF'den ilham alınarak geliştirilmiş kapsamlı Python PDF işleme uygulaması.

## 🚀 Özellikler

### 📄 Temel İşlemler
- **PDF Birleştirme**: Birden fazla PDF dosyasını tek bir dosyada birleştirin
- **PDF Bölme**: PDF'leri sayfalara veya belirtilen aralıklara bölün  
- **Sayfa Döndürme**: PDF sayfalarını döndürün
- **Sayfa Yeniden Düzenleme**: Sayfaları istediğiniz sırada düzenleyin

### 🔄 Dönüştürme İşlemleri
- **PDF'e Dönüştürme**: Çeşitli formatları PDF'e dönüştürün
- **PDF'den Dönüştürme**: PDF'i diğer formatlara dönüştürün
- **Görüntü Çıkarma**: PDF'lerden görüntüleri çıkarın
- **Metin Çıkarma**: PDF'lerden metinleri çıkarın

### 🗜️ Optimizasyon
- **PDF Sıkıştırma**: Dosya boyutunu küçültün
- **PDF Optimizasyonu**: Performansı artırın
- **Temizleme**: Gereksiz verileri kaldırın
- **Onarma**: Bozuk PDF'leri onarın

### 🔒 Güvenlik
- **Şifreleme**: PDF'lere şifre koyun
- **Şifre Kaldırma**: Mevcut şifreleri kaldırın
- **Dijital İmzalama**: PDF'leri dijital olarak imzalayın
- **İmza Doğrulama**: İmzaları doğrulayın

### 📝 Düzenleme
- **Filigran Ekleme**: Metin veya resim filigranı ekleyin
- **Metin Ekleme**: PDF'lere metin ekleyin
- **Görüntü Ekleme**: PDF'lere resim ekleyin
- **Sayfa Numarası**: Otomatik sayfa numarası ekleyin

### 🔍 OCR ve Arama
- **OCR İşlemi**: Taranmış PDF'leri aranabilir hale getirin
- **Metin Arama**: PDF içinde metin arayın
- **Dil Desteği**: Çoklu dil desteği (Türkçe, İngilizce, vb.)

### 📊 Analiz ve Raporlama
- **PDF Bilgileri**: Detaylı PDF analizi
- **Metadata Düzenleme**: PDF metadata bilgilerini düzenleyin
- **Karşılaştırma**: İki PDF'i karşılaştırın
- **Doğrulama**: PDF formatını doğrulayın

## 📋 Gereksinimler

### Python Sürümü
- Python 3.7 veya üzeri

### Temel Gereksinimler
```bash
pip install PyPDF2>=3.0.0
pip install Pillow>=9.0.0
pip install reportlab>=3.6.0
```

### OCR Desteği İçin
```bash
pip install pytesseract>=0.3.8
pip install pdf2image>=1.16.0
```

### Tesseract OCR Kurulumu

#### Windows
1. [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) indirin
2. Varsayılan klasöre kurun: `C:\Program Files\Tesseract-OCR`
3. Türkçe dil paketini indirin

#### macOS
```bash
brew install tesseract
brew install tesseract-lang  # Dil paketleri için
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-tur  # Türkçe için
```

## 🛠️ Kurulum

### Hızlı Kurulum
```bash
# Repository'i klonlayın
git clone <repository-url>
cd pypdf-tools

# Gerekli paketleri kurun
pip install -r requirements.txt

# Uygulamayı başlatın
python main.py
```

### Detaylı Kurulum

1. **Python Kontrolü**
   ```bash
   python --version  # 3.7+ olmalı
   ```

2. **Sanal Ortam Oluşturma (Önerilen)**
   ```bash
   python -m venv pypdf_env
   
   # Windows
   pypdf_env\Scripts\activate
   
   # macOS/Linux
   source pypdf_env/bin/activate
   ```

3. **Bağımlılıkları Kurma**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **OCR Desteği (İsteğe Bağlı)**
   - Tesseract OCR'ı sistem genelinde kurun
   - Gerekli dil paketlerini kurun

## 🎯 Kullanım

### Temel Kullanım

1. **Uygulamayı Başlatın**
   ```bash
   python main.py
   ```

2. **Dosya Seçin**
   - "Dosya Seç" butonuna tıklayın
   - PDF dosyalarınızı seçin

3. **İşlem Seçin**
   - Sol menüden istediğiniz işlemi seçin
   - İşlem ayarlarını yapılandırın

4. **İşlemi Başlatın**
   - "İşlemi Başlat" butonuna tıklayın
   - Sonuçları çıktı klasöründe görün

### Toplu İşlemler

```python
from resources.pdf_utils import PDFProcessor

processor = PDFProcessor()

# Toplu sıkıştırma
results = processor.batch_process(
    file_list=['doc1.pdf', 'doc2.pdf'],
    operation='compress',
    output_dir='compressed_files/',
    quality='medium'
)
```

### OCR Kullanımı

```python
from ocr_module import OCRProcessor

ocr = OCRProcessor()

# PDF'i aranabilir hale getir
result = ocr.process_pdf(
    pdf_path='scanned_document.pdf',
    output_path='searchable_document.pdf',
    language='tur',
    dpi=300
)
```

## 📁 Proje Yapısı

```
proje_klasoru/
│
├── main.py                 # Ana uygulama dosyası
├── requirements.txt        # Gerekli paketler
├── README.md              # Bu dosya
│
├── ui/                    # Kullanıcı arayüzü
│   ├── __init__.py
│   ├── sidebar.py         # Sol menü
│   ├── header.py          # Üst panel
│   └── content.py         # Ana çalışma alanı
│
├── resources/             # PDF işleme modülleri
│   ├── __init__.py
│   └── pdf_utils.py       # PDF işleme fonksiyonları
│
├── utils.py               # Yardımcı fonksiyonlar
├── ocr_module.py          # OCR işlemleri
│
└── icons/                 # Uygulama ikonları
    ├── merge.png
    ├── compress.png
    ├── convert.png
    └── sign.png
```

## ⚙️ Konfigürasyon

### Ayar Dosyası Konumu
- **Windows**: `%APPDATA%\PyPDF Tools\config.ini`
- **macOS**: `~/Library/Application Support/PyPDF Tools/config.ini`
- **Linux**: `~/.config/PyPDF Tools/config.ini`

### Temel Ayarlar
```ini
[PDF]
default_output_dir = ~/Desktop
default_quality = medium
default_dpi = 150

[OCR]
default_language = tur
default_dpi = 300
preprocessing = true

[UI]
window_width = 1200
window_height = 800
```

## 🐛 Sorun Giderme

### Yaygın Sorunlar

**1. ModuleNotFoundError: No module named 'PyPDF2'**
```bash
pip install PyPDF2
```

**2. Tesseract bulunamadı hatası**
- Tesseract OCR'ın doğru kurulduğundan emin olun
- PATH değişkenini kontrol edin

**3. Dosya izinleri sorunu**
- Dosyaların yazma iznine sahip olduğundan emin olun
- Yönetici olarak çalıştırmayı deneyin

**4. Bellek yetersizliği (büyük dosyalar)**
- Dosyaları parça parça işleyin
- Geçici dosyaları düzenli temizleyin

### Log Dosyaları
Hata ayıklama için log dosyalarını kontrol edin:
- Konum: `[Konfigürasyon Klasörü]/pypdf_tools.log`

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/YeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/YeniOzellik`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🙏 Teşekkürler

- [Stirling-PDF](https://github.com/Stirling-Tools/Stirling-PDF) - İlham kaynağı
- [PyPDF2](https://github.com/py-pdf/PyPDF2) - PDF işleme kütüphanesi
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR motoru
- [ReportLab](https://www.reportlab.com/) - PDF oluşturma araçları

## 🔗 Faydalı Bağlantılar

- [PyPDF2 Dokümantasyonu](https://pypdf2.readthedocs.io/)
- [Tesseract OCR Wiki](https://github.com/tesseract-ocr/tesseract/wiki)
- [ReportLab Kılavuzu](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [Python Tkinter Rehberi](https://docs.python.org/3/library/tkinter.html)

## 📞 Destek

Herhangi bir sorun yaşarsanız:
1. İlk olarak bu README dosyasını okuyun
2. Issues bölümünde benzer sorunları arayın
3. Yeni bir issue açın ve detaylı bilgi verin

## 🔄 Güncellemeler

### v1.0.0
- İlk stabil sürüm
- Temel PDF işlemleri
- OCR desteği
- Kullanıcı dostu arayüz

### Gelecek Özellikler
- [ ] Batch işlem iyileştirmeleri
- [ ] Daha fazla dil desteği
- [ ] PDF form işlemleri
- [ ] Cloud storage entegrasyonu
- [ ] API desteği

## 🌟 Öne Çıkan Özellikler

### Hızlı Başlangıç Butonları
- Sık kullanılan işlemler için hızlı erişim
- Tek tıkla dosya seçimi ve işlem başlatma

### Gelişmiş OCR
- Çoklu dil desteği
- Otomatik görüntü ön işleme
- Güven skorları ve istatistikler

### Akıllı Dosya Yönetimi
- Otomatik yedekleme
- Son kullanılan dosyalar
- Proje dosyası desteği

### Kullanıcı Dostu Arayüz
- Modern ve sezgisel tasarım
- İlerleme göstergeleri
- Detaylı hata mesajları

---

**PyPDF Tools** ile PDF işlemlerinizi kolaylaştırın! 🎉
