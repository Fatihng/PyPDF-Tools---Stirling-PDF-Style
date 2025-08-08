"""
OCR (Optical Character Recognition) modülü
Tesseract OCR ve PDF işleme için gerekli fonksiyonlar
"""

import os
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import io

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Uyarı: pytesseract veya Pillow bulunamadı. 'pip install pytesseract Pillow' ile yükleyin.")

try:
    import pdf2image
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    print("Uyarı: pdf2image bulunamadı. 'pip install pdf2image' ile yükleyin.")

try:
    from PyPDF2 import PdfReader, PdfWriter
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    try:
        from PyPDF2 import PdfReader, PdfWriter
        PYPDF2_AVAILABLE = True
    except ImportError:
        PYPDF2_AVAILABLE = False
        print("Uyarı: PyPDF2 veya PyMuPDF bulunamadı.")

class OCRProcessor:
    """OCR işlemleri için ana sınıf"""

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="ocr_")
        self.supported_languages = {
            'tur': 'Türkçe',
            'eng': 'English',
            'deu': 'Deutsch',
            'fra': 'Français',
            'spa': 'Español',
            'ita': 'Italiano',
            'por': 'Português',
            'rus': 'Русский',
            'ara': 'العربية',
            'chi_sim': '中文 (简体)',
            'chi_tra': '中文 (繁體)',
            'jpn': '日本語'
        }

        # Tesseract yolu kontrolü
        self.tesseract_path = self._find_tesseract()

    def __del__(self):
        """Geçici dosyaları temizle"""
        try:
            import shutil
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass

    def _find_tesseract(self) -> Optional[str]:
        """Tesseract executable'ını bul"""
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract',
            '/opt/homebrew/bin/tesseract'  # macOS Homebrew
        ]

        # PATH'taki tesseract'ı kontrol et
        try:
            result = subprocess.run(['tesseract', '--version'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return 'tesseract'
        except:
            pass

        # Önceden tanımlanmış yolları kontrol et
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    pytesseract.pytesseract.tesseract_cmd = path
                    return path
                except:
                    continue

        return None

    def is_available(self) -> bool:
        """OCR fonksiyonlarının kullanılabilir olup olmadığını kontrol et"""
        return TESSERACT_AVAILABLE and self.tesseract_path is not None

    def get_available_languages(self) -> Dict[str, str]:
        """Kullanılabilir dilleri döndür"""
        if not self.is_available():
            return {}

        try:
            # Tesseract'ta yüklü dilleri kontrol et
            langs = pytesseract.get_languages(config='')
            available_langs = {}

            for lang_code, lang_name in self.supported_languages.items():
                if lang_code in langs:
                    available_langs[lang_code] = lang_name

            return available_langs

        except Exception as e:
            print(f"Dil listesi alınamadı: {e}")
            return self.supported_languages

    def preprocess_image(self, image: Image.Image,
                        enhance_contrast: bool = True,
                        denoise: bool = True,
                        resize_factor: float = 2.0) -> Image.Image:
        """Görüntüyü OCR için ön işleme tabi tut"""
        try:
            # Gri tonlamaya çevir
            if image.mode != 'L':
                image = image.convert('L')

            # Boyutlandır
            if resize_factor != 1.0:
                width, height = image.size
                new_size = (int(width * resize_factor), int(height * resize_factor))
                image = image.resize(new_size, Image.Resampling.LANCZOS)

            # Kontrast artır
            if enhance_contrast:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.5)

            # Gürültü azalt
            if denoise:
                image = image.filter(ImageFilter.MedianFilter(size=3))

            # Keskinlik artır
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)

            return image

        except Exception as e:
            print(f"Görüntü ön işleme hatası: {e}")
            return image

    def extract_text_from_image(self, image_path: str,
                               language: str = 'tur',
                               psm: int = 6,
                               oem: int = 3) -> Dict:
        """Görüntüden metin çıkar"""
        if not self.is_available():
            raise RuntimeError("OCR kullanılabilir değil")

        try:
            # Görüntüyü aç
            image = Image.open(image_path)

            # Ön işleme
            processed_image = self.preprocess_image(image)

            # OCR konfigürasyonu
            config = f'--oem {oem} --psm {psm}'

            # Metin çıkar
            text = pytesseract.image_to_string(
                processed_image,
                lang=language,
                config=config
            )

            # Güven skorları al
            data = pytesseract.image_to_data(
                processed_image,
                lang=language,
                config=config,
                output_type=pytesseract.Output.DICT
            )

            # Ortalama güven skorunu hesapla
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            result = {
                'text': text.strip(),
                'confidence': avg_confidence,
                'language': language,
                'word_count': len(text.split()),
                'character_count': len(text),
                'processing_info': {
                    'psm': psm,
                    'oem': oem,
                    'preprocessed': True
                }
            }

            return result

        except Exception as e:
            print(f"OCR hatası: {e}")
            return {
                'text': '',
                'confidence': 0,
                'language': language,
                'error': str(e)
            }

    def pdf_to_images(self, pdf_path: str, dpi: int = 300,
                     format: str = 'PNG') -> List[str]:
        """PDF'i sayfa görüntülerine dönüştür"""
        if not PDF2IMAGE_AVAILABLE:
            # Alternatif yöntem: PyMuPDF kullan
            return self._pdf_to_images_pymupdf(pdf_path, dpi)

        try:
            images = pdf2image.convert_from_path(
                pdf_path,
                dpi=dpi,
                format=format,
                thread_count=4
            )

            image_paths = []
            for i, image in enumerate(images):
                image_path = os.path.join(self.temp_dir, f"page_{i+1}.{format.lower()}")
                image.save(image_path, format)
                image_paths.append(image_path)

            return image_paths

        except Exception as e:
            print(f"PDF görüntü dönüştürme hatası: {e}")
            return []

    def _pdf_to_images_pymupdf(self, pdf_path: str, dpi: int = 300) -> List[str]:
        """PyMuPDF ile PDF'i görüntülere dönüştür"""
        if not PYMUPDF_AVAILABLE:
            return []

        try:
            doc = fitz.open(pdf_path)
            image_paths = []

            # DPI'ya göre zoom faktörünü hesapla
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=mat)

                image_path = os.path.join(self.temp_dir, f"page_{page_num+1}.png")
                pix.save(image_path)
                image_paths.append(image_path)

            doc.close()
            return image_paths

        except Exception as e:
            print(f"PyMuPDF PDF dönüştürme hatası: {e}")
            return []

    def process_pdf(self, pdf_path: str, output_path: str,
                   language: str = 'tur', dpi: int = 300,
                   create_searchable: bool = True) -> Dict:
        """PDF'i OCR ile işle"""
        if not self.is_available():
            raise RuntimeError("OCR kullanılabilir değil")

        try:
            results = {
                'success': False,
                'total_pages': 0,
                'processed_pages': 0,
                'total_text': '',
                'pages': [],
                'processing_time': 0,
                'average_confidence': 0
            }

            import time
            start_time = time.time()

            # PDF'i görüntülere dönüştür
            print("PDF görüntülere dönüştürülüyor...")
            image_paths = self.pdf_to_images(pdf_path, dpi)

            if not image_paths:
                results['error'] = "PDF görüntülere dönüştürülemedi"
                return results

            results['total_pages'] = len(image_paths)

            # Her sayfa için OCR işlemi
            all_confidences = []
            page_texts = []

            for i, image_path in enumerate(image_paths):
                print(f"Sayfa {i+1}/{len(image_paths)} işleniyor...")

                ocr_result = self.extract_text_from_image(image_path, language)

                page_info = {
                    'page_number': i + 1,
                    'text': ocr_result.get('text', ''),
                    'confidence': ocr_result.get('confidence', 0),
                    'word_count': ocr_result.get('word_count', 0),
                    'character_count': ocr_result.get('character_count', 0)
                }

                results['pages'].append(page_info)
                page_texts.append(ocr_result.get('text', ''))
                all_confidences.append(ocr_result.get('confidence', 0))
                results['processed_pages'] += 1

            # Toplam metin ve ortalama güven
            results['total_text'] = '\n\n'.join(page_texts)
            results['average_confidence'] = sum(all_confidences) / len(all_confidences) if all_confidences else 0

            # Aranabilir PDF oluştur
            if create_searchable:
                success = self.create_searchable_pdf(pdf_path, output_path, results['pages'])
                results['searchable_created'] = success
            else:
                # Sadece metin dosyası oluştur
                text_output_path = output_path.replace('.pdf', '_ocr.txt')
                with open(text_output_path, 'w', encoding='utf-8') as f:
                    f.write(results['total_text'])

            results['processing_time'] = time.time() - start_time
            results['success'] = True

            return results

        except Exception as e:
            print(f"PDF OCR işleme hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_pages': 0,
                'processed_pages': 0
            }

    def create_searchable_pdf(self, original_pdf_path: str,
                            output_path: str, page_results: List[Dict]) -> bool:
        """Orijinal PDF'e OCR metni ekleyerek aranabilir PDF oluştur"""
        try:
            if PYMUPDF_AVAILABLE:
                return self._create_searchable_pdf_pymupdf(
                    original_pdf_path, output_path, page_results
                )
            else:
                return self._create_searchable_pdf_pypdf2(
                    original_pdf_path, output_path, page_results
                )

        except Exception as e:
            print(f"Aranabilir PDF oluşturma hatası: {e}")
            return False

    def _create_searchable_pdf_pymupdf(self, original_pdf_path: str,
                                     output_path: str, page_results: List[Dict]) -> bool:
        """PyMuPDF ile aranabilir PDF oluştur"""
        if not PYMUPDF_AVAILABLE:
            return False

        try:
            doc = fitz.open(original_pdf_path)

            for page_result in page_results:
                page_num = page_result['page_number'] - 1
                text = page_result['text']

                if text.strip():
                    page = doc.load_page(page_num)

                    # Metni görünmez katman olarak ekle
                    text_dict = {
                        "spans": [{
                            "text": text,
                            "bbox": page.rect,
                            "font": "helv",
                            "size": 1,  # Çok küçük boyut (görünmez)
                            "color": 0xFFFFFF  # Beyaz (görünmez)
                        }]
                    }

                    page.insert_textbox(page.rect, text,
                                      fontsize=1, color=(1, 1, 1), overlay=False)

            doc.save(output_path)
            doc.close()

            return True

        except Exception as e:
            print(f"PyMuPDF aranabilir PDF hatası: {e}")
            return False

    def _create_searchable_pdf_pypdf2(self, original_pdf_path: str,
                                    output_path: str, page_results: List[Dict]) -> bool:
        """PyPDF2 ile basit metin katmanı ekleme"""
        try:
            # Bu implementasyon daha sınırlıdır
            # Orijinal PDF'i kopyala ve metin dosyası oluştur
            import shutil
            shutil.copy2(original_pdf_path, output_path)

            # Metin dosyası oluştur
            text_file = output_path.replace('.pdf', '_searchable_text.txt')
            with open(text_file, 'w', encoding='utf-8') as f:
                for page_result in page_results:
                    f.write(f"=== Sayfa {page_result['page_number']} ===\n")
                    f.write(page_result['text'])
                    f.write('\n\n')

            return True

        except Exception as e:
            print(f"PyPDF2 aranabilir PDF hatası: {e}")
            return False

    def extract_tables(self, image_path: str, language: str = 'tur') -> List[List[str]]:
        """Görüntüden tablo verilerini çıkar"""
        if not self.is_available():
            raise RuntimeError("OCR kullanılabilir değil")

        try:
            # OCR ile detaylı veri al
            image = Image.open(image_path)
            processed_image = self.preprocess_image(image)

            # Tablo yapısını tespit etmek için özel PSM kullan
            data = pytesseract.image_to_data(
                processed_image,
                lang=language,
                config='--psm 6',
                output_type=pytesseract.Output.DICT
            )

            # Koordinatlara göre metni grupla
            words_by_line = {}

            for i, word in enumerate(data['text']):
                if word.strip():
                    top = data['top'][i]
                    left = data['left'][i]

                    # Satır grupları oluştur (y koordinatına göre)
                    line_key = top // 20  # 20 piksel tolerans

                    if line_key not in words_by_line:
                        words_by_line[line_key] = []

                    words_by_line[line_key].append({
                        'text': word,
                        'left': left,
                        'top': top,
                        'confidence': data['conf'][i]
                    })

            # Her satırdaki kelimeleri x koordinatına göre sırala
            table_rows = []
            for line_key in sorted(words_by_line.keys()):
                words = sorted(words_by_line[line_key], key=lambda x: x['left'])
                row_text = [word['text'] for word in words]
                table_rows.append(row_text)

            return table_rows

        except Exception as e:
            print(f"Tablo çıkarma hatası: {e}")
            return []

    def batch_ocr_images(self, image_paths: List[str],
                        language: str = 'tur',
                        output_format: str = 'txt') -> Dict:
        """Birden fazla görüntü için toplu OCR işlemi"""
        if not self.is_available():
            raise RuntimeError("OCR kullanılabilir değil")

        results = {
            'total_files': len(image_paths),
            'processed_files': 0,
            'failed_files': 0,
            'results': [],
            'combined_text': '',
            'average_confidence': 0
        }

        all_confidences = []
        all_texts = []

        for i, image_path in enumerate(image_paths):
            try:
                print(f"İşleniyor {i+1}/{len(image_paths)}: {os.path.basename(image_path)}")

                ocr_result = self.extract_text_from_image(image_path, language)

                file_result = {
                    'file_path': image_path,
                    'filename': os.path.basename(image_path),
                    'text': ocr_result.get('text', ''),
                    'confidence': ocr_result.get('confidence', 0),
                    'success': True
                }

                results['results'].append(file_result)
                results['processed_files'] += 1

                all_texts.append(ocr_result.get('text', ''))
                all_confidences.append(ocr_result.get('confidence', 0))

            except Exception as e:
                file_result = {
                    'file_path': image_path,
                    'filename': os.path.basename(image_path),
                    'error': str(e),
                    'success': False
                }

                results['results'].append(file_result)
                results['failed_files'] += 1

        # Toplam sonuçları hesapla
        results['combined_text'] = '\n\n'.join(all_texts)
        results['average_confidence'] = sum(all_confidences) / len(all_confidences) if all_confidences else 0

        return results

    def detect_text_orientation(self, image_path: str) -> Dict:
        """Metinin yönelimini tespit et"""
        if not self.is_available():
            raise RuntimeError("OCR kullanılabilir değil")

        try:
            image = Image.open(image_path)

            # OSD (Orientation and Script Detection) kullan
            osd_data = pytesseract.image_to_osd(image)

            orientation_info = {}
            for line in osd_data.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    orientation_info[key.strip()] = value.strip()

            return {
                'orientation': orientation_info.get('Orientation in degrees', '0'),
                'script': orientation_info.get('Script', 'Latin'),
                'confidence': orientation_info.get('Orientation confidence', '0'),
                'script_confidence': orientation_info.get('Script confidence', '0')
            }

        except Exception as e:
            print(f"Yönelim tespit hatası: {e}")
            return {
                'orientation': '0',
                'script': 'Latin',
                'confidence': '0',
                'error': str(e)
            }

    def correct_text_orientation(self, image_path: str, output_path: str) -> bool:
        """Metin yönelimini düzelt"""
        try:
            # Yönelimi tespit et
            orientation_info = self.detect_text_orientation(image_path)
            orientation = int(float(orientation_info.get('orientation', 0)))

            if orientation != 0:
                image = Image.open(image_path)
                # Ters yönde döndür
                corrected_image = image.rotate(-orientation, expand=True)
                corrected_image.save(output_path)
                return True
            else:
                # Yönelim doğru, kopyala
                import shutil
                shutil.copy2(image_path, output_path)
                return True

        except Exception as e:
            print(f"Yönelim düzeltme hatası: {e}")
            return False

    def enhance_image_for_ocr(self, image_path: str, output_path: str,
                             enhancement_level: str = 'medium') -> bool:
        """Görüntüyü OCR için gelişmiş şekilde iyileştir"""
        try:
            image = Image.open(image_path)

            # İyileştirme seviyesine göre parametreler
            enhancement_params = {
                'light': {
                    'resize_factor': 1.5,
                    'contrast': 1.2,
                    'sharpness': 1.1,
                    'denoise': True
                },
                'medium': {
                    'resize_factor': 2.0,
                    'contrast': 1.5,
                    'sharpness': 1.3,
                    'denoise': True
                },
                'heavy': {
                    'resize_factor': 3.0,
                    'contrast': 1.8,
                    'sharpness': 1.5,
                    'denoise': True
                }
            }

            params = enhancement_params.get(enhancement_level, enhancement_params['medium'])

            # Gri tonlamaya çevir
            if image.mode != 'L':
                image = image.convert('L')

            # Boyutlandır
            if params['resize_factor'] != 1.0:
                width, height = image.size
                new_size = (int(width * params['resize_factor']),
                           int(height * params['resize_factor']))
                image = image.resize(new_size, Image.Resampling.LANCZOS)

            # Kontrast artır
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(params['contrast'])

            # Keskinlik artır
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(params['sharpness'])

            # Gürültü azalt
            if params['denoise']:
                image = image.filter(ImageFilter.MedianFilter(size=3))

            # Histogram eşitleme (basit)
            import numpy as np
            img_array = np.array(image)

            # Basit histogram genişletme
            min_val, max_val = img_array.min(), img_array.max()
            if max_val > min_val:
                img_array = ((img_array - min_val) * 255 / (max_val - min_val)).astype(np.uint8)
                image = Image.fromarray(img_array)

            # Kaydet
            image.save(output_path, 'PNG', optimize=True)
            return True

        except Exception as e:
            print(f"Görüntü iyileştirme hatası: {e}")
            return False

    def extract_text_with_coordinates(self, image_path: str,
                                    language: str = 'tur') -> Dict:
        """Koordinatlarla birlikte metin çıkar"""
        if not self.is_available():
            raise RuntimeError("OCR kullanılabilir değil")

        try:
            image = Image.open(image_path)
            processed_image = self.preprocess_image(image)

            # Detaylı veri al
            data = pytesseract.image_to_data(
                processed_image,
                lang=language,
                config='--psm 6',
                output_type=pytesseract.Output.DICT
            )

            words_with_coords = []

            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if text:
                    word_info = {
                        'text': text,
                        'confidence': int(data['conf'][i]),
                        'bbox': {
                            'x': int(data['left'][i]),
                            'y': int(data['top'][i]),
                            'width': int(data['width'][i]),
                            'height': int(data['height'][i])
                        },
                        'page_num': int(data['page_num'][i]),
                        'block_num': int(data['block_num'][i]),
                        'par_num': int(data['par_num'][i]),
                        'line_num': int(data['line_num'][i]),
                        'word_num': int(data['word_num'][i])
                    }
                    words_with_coords.append(word_info)

            # Tam metin oluştur
            full_text = ' '.join([word['text'] for word in words_with_coords])

            result = {
                'full_text': full_text,
                'words': words_with_coords,
                'word_count': len(words_with_coords),
                'language': language
            }

            return result

        except Exception as e:
            print(f"Koordinatlı metin çıkarma hatası: {e}")
            return {
                'full_text': '',
                'words': [],
                'word_count': 0,
                'error': str(e)
            }

    def search_text_in_pdf(self, pdf_path: str, search_term: str,
                          language: str = 'tur', case_sensitive: bool = False) -> Dict:
        """PDF içinde metin arama (OCR ile)"""
        try:
            # PDF'i işle
            ocr_result = self.process_pdf(pdf_path, pdf_path + '_temp_ocr.pdf',
                                        language, create_searchable=False)

            if not ocr_result['success']:
                return {
                    'found': False,
                    'total_matches': 0,
                    'pages_with_matches': [],
                    'error': 'OCR işlemi başarısız'
                }

            search_results = {
                'found': False,
                'total_matches': 0,
                'pages_with_matches': [],
                'search_term': search_term,
                'case_sensitive': case_sensitive
            }

            # Her sayfada ara
            for page_info in ocr_result['pages']:
                page_text = page_info['text']

                if not case_sensitive:
                    page_text_search = page_text.lower()
                    search_term_search = search_term.lower()
                else:
                    page_text_search = page_text
                    search_term_search = search_term

                # Eşleşmeleri bul
                matches = []
                start_pos = 0

                while True:
                    pos = page_text_search.find(search_term_search, start_pos)
                    if pos == -1:
                        break

                    # Bağlam metni al (50 karakter öncesi ve sonrası)
                    context_start = max(0, pos - 50)
                    context_end = min(len(page_text), pos + len(search_term) + 50)
                    context = page_text[context_start:context_end]

                    matches.append({
                        'position': pos,
                        'context': context,
                        'line_number': page_text[:pos].count('\n') + 1
                    })

                    start_pos = pos + 1

                if matches:
                    search_results['pages_with_matches'].append({
                        'page_number': page_info['page_number'],
                        'matches_count': len(matches),
                        'matches': matches,
                        'page_confidence': page_info['confidence']
                    })

                    search_results['total_matches'] += len(matches)
                    search_results['found'] = True

            return search_results

        except Exception as e:
            print(f"PDF metin arama hatası: {e}")
            return {
                'found': False,
                'total_matches': 0,
                'pages_with_matches': [],
                'error': str(e)
            }

    def get_ocr_statistics(self, results: Dict) -> Dict:
        """OCR sonuçları için istatistikler"""
        stats = {
            'total_pages': results.get('total_pages', 0),
            'processed_pages': results.get('processed_pages', 0),
            'success_rate': 0,
            'average_confidence': results.get('average_confidence', 0),
            'total_words': 0,
            'total_characters': 0,
            'pages_by_confidence': {
                'high': 0,    # >90%
                'medium': 0,  # 70-90%
                'low': 0      # <70%
            }
        }

        if results.get('pages'):
            total_words = sum(page.get('word_count', 0) for page in results['pages'])
            total_chars = sum(page.get('character_count', 0) for page in results['pages'])

            stats['total_words'] = total_words
            stats['total_characters'] = total_chars

            # Güven seviyelerine göre sayfa sayıları
            for page in results['pages']:
                confidence = page.get('confidence', 0)
                if confidence > 90:
                    stats['pages_by_confidence']['high'] += 1
                elif confidence > 70:
                    stats['pages_by_confidence']['medium'] += 1
                else:
                    stats['pages_by_confidence']['low'] += 1

        if stats['total_pages'] > 0:
            stats['success_rate'] = (stats['processed_pages'] / stats['total_pages']) * 100

        return stats

    def export_ocr_results(self, results: Dict, output_path: str,
                          format: str = 'txt') -> bool:
        """OCR sonuçlarını farklı formatlarda dışa aktar"""
        try:
            if format.lower() == 'txt':
                return self._export_to_txt(results, output_path)
            elif format.lower() == 'json':
                return self._export_to_json(results, output_path)
            elif format.lower() == 'csv':
                return self._export_to_csv(results, output_path)
            elif format.lower() == 'html':
                return self._export_to_html(results, output_path)
            else:
                print(f"Desteklenmeyen format: {format}")
                return False

        except Exception as e:
            print(f"Dışa aktarma hatası: {e}")
            return False

    def _export_to_txt(self, results: Dict, output_path: str) -> bool:
        """TXT formatında dışa aktar"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"OCR Sonuçları\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"Toplam Sayfa: {results.get('total_pages', 0)}\n")
            f.write(f"İşlenen Sayfa: {results.get('processed_pages', 0)}\n")
            f.write(f"Ortalama Güven: {results.get('average_confidence', 0):.2f}%\n\n")

            if results.get('pages'):
                for page in results['pages']:
                    f.write(f"--- Sayfa {page.get('page_number', 0)} ---\n")
                    f.write(f"Güven: {page.get('confidence', 0):.2f}%\n")
                    f.write(f"Kelime Sayısı: {page.get('word_count', 0)}\n\n")
                    f.write(page.get('text', ''))
                    f.write("\n\n")

        return True

    def _export_to_json(self, results: Dict, output_path: str) -> bool:
        """JSON formatında dışa aktar"""
        import json

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        return True

    def _export_to_csv(self, results: Dict, output_path: str) -> bool:
        """CSV formatında dışa aktar"""
        import csv

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Sayfa', 'Güven', 'Kelime Sayısı', 'Karakter Sayısı', 'Metin'])

            if results.get('pages'):
                for page in results['pages']:
                    writer.writerow([
                        page.get('page_number', 0),
                        f"{page.get('confidence', 0):.2f}%",
                        page.get('word_count', 0),
                        page.get('character_count', 0),
                        page.get('text', '').replace('\n', ' ')[:200] + '...'  # İlk 200 karakter
                    ])

        return True

    def _export_to_html(self, results: Dict, output_path: str) -> bool:
        """HTML formatında dışa aktar"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OCR Sonuçları</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 10px; }}
                .page {{ border: 1px solid #ccc; margin: 10px 0; padding: 10px; }}
                .page-header {{ background-color: #e0e0e0; padding: 5px; font-weight: bold; }}
                .confidence {{ color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>OCR Sonuçları</h1>
                <p>Toplam Sayfa: {results.get('total_pages', 0)}</p>
                <p>İşlenen Sayfa: {results.get('processed_pages', 0)}</p>
                <p>Ortalama Güven: {results.get('average_confidence', 0):.2f}%</p>
            </div>
        """

        if results.get('pages'):
            for page in results['pages']:
                confidence_color = "green" if page.get('confidence', 0) > 80 else "orange" if page.get('confidence', 0) > 60 else "red"
                html_content += f"""
                <div class="page">
                    <div class="page-header">
                        Sayfa {page.get('page_number', 0)}
                        <span class="confidence" style="color: {confidence_color}">
                            (Güven: {page.get('confidence', 0):.2f}%)
                        </span>
                    </div>
                    <p><strong>Kelime Sayısı:</strong> {page.get('word_count', 0)}</p>
                    <div>
                        {page.get('text', '').replace('\n', '<br>')}
                    </div>
                </div>
                """

        html_content += """
        </body>
        </html>
        """

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return True
