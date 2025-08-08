"""
PDF işleme utilities modülü
PyPDF2, ReportLab ve diğer kütüphaneler kullanarak PDF işlemleri
"""

import os
import io
from pathlib import Path
from typing import List, Dict, Optional, Union
import tempfile

try:
    import PyPDF2
    from PyPDF2 import PdfReader, PdfWriter, PdfMerger
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    print("Uyarı: PyPDF2 bulunamadı. 'pip install PyPDF2' ile yükleyin.")

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Uyarı: ReportLab bulunamadı. 'pip install reportlab' ile yükleyin.")

try:
    from PIL import Image, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Uyarı: Pillow bulunamadı. 'pip install Pillow' ile yükleyin.")

class PDFProcessor:
    """PDF işleme ana sınıfı"""

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="pypdf_")

    def __del__(self):
        """Geçici dosyaları temizle"""
        try:
            import shutil
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass

    def get_page_count(self, pdf_path: str) -> int:
        """PDF dosyasındaki sayfa sayısını döndür"""
        if not PYPDF2_AVAILABLE:
            return 0

        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                return len(reader.pages)
        except Exception as e:
            print(f"Sayfa sayısı alınamadı {pdf_path}: {e}")
            return 0

    def get_pdf_info(self, pdf_path: str) -> Dict:
        """PDF bilgilerini al"""
        if not PYPDF2_AVAILABLE:
            return {}

        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                metadata = reader.metadata

                info = {
                    'title': metadata.get('/Title', 'N/A') if metadata else 'N/A',
                    'author': metadata.get('/Author', 'N/A') if metadata else 'N/A',
                    'subject': metadata.get('/Subject', 'N/A') if metadata else 'N/A',
                    'creator': metadata.get('/Creator', 'N/A') if metadata else 'N/A',
                    'producer': metadata.get('/Producer', 'N/A') if metadata else 'N/A',
                    'creation_date': metadata.get('/CreationDate', 'N/A') if metadata else 'N/A',
                    'modification_date': metadata.get('/ModDate', 'N/A') if metadata else 'N/A',
                    'page_count': len(reader.pages),
                    'file_size': os.path.getsize(pdf_path),
                    'encrypted': reader.is_encrypted
                }

                return info

        except Exception as e:
            print(f"PDF bilgisi alınamadı {pdf_path}: {e}")
            return {}

    def merge_pdfs(self, pdf_files: List[str], output_path: str,
                   add_bookmarks: bool = True, sort_by: str = "name") -> bool:
        """Birden fazla PDF'i birleştir"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 gerekli")

        try:
            merger = PdfMerger()

            # Dosyaları sırala
            if sort_by == "name":
                pdf_files = sorted(pdf_files, key=lambda x: os.path.basename(x))
            elif sort_by == "date":
                pdf_files = sorted(pdf_files, key=lambda x: os.path.getmtime(x))
            elif sort_by == "size":
                pdf_files = sorted(pdf_files, key=lambda x: os.path.getsize(x))

            # Dosyaları birleştir
            for pdf_file in pdf_files:
                if add_bookmarks:
                    bookmark_title = os.path.splitext(os.path.basename(pdf_file))[0]
                    merger.append(pdf_file, bookmark=bookmark_title)
                else:
                    merger.append(pdf_file)

            # Çıktı dosyasını yaz
            merger.write(output_path)
            merger.close()

            return True

        except Exception as e:
            print(f"PDF birleştirme hatası: {e}")
            return False

    def split_pdf_by_pages(self, pdf_path: str, output_dir: str, pages: str) -> bool:
        """PDF'i belirtilen sayfalara böl"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 gerekli")

        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)

                # Sayfa numaralarını parse et
                page_numbers = self._parse_page_numbers(pages, len(reader.pages))

                for page_num in page_numbers:
                    writer = PdfWriter()
                    writer.add_page(reader.pages[page_num - 1])  # 0-indexli

                    output_filename = f"page_{page_num}.pdf"
                    output_path = os.path.join(output_dir, output_filename)

                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)

            return True

        except Exception as e:
            print(f"PDF bölme hatası: {e}")
            return False

    def split_pdf_each_page(self, pdf_path: str, output_dir: str) -> bool:
        """PDF'i her sayfa için ayrı dosyaya böl"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 gerekli")

        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)

                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)

                    output_filename = f"page_{i+1}.pdf"
                    output_path = os.path.join(output_dir, output_filename)

                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)

            return True

        except Exception as e:
            print(f"PDF bölme hatası: {e}")
            return False

    def split_pdf_by_ranges(self, pdf_path: str, output_dir: str, ranges: str) -> bool:
        """PDF'i belirtilen aralıklara böl"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 gerekli")

        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)

                # Aralıkları parse et (örn: "1-3,5-7,9")
                range_groups = self._parse_page_ranges(ranges, len(reader.pages))

                for i, (start, end) in enumerate(range_groups):
                    writer = PdfWriter()

                    for page_num in range(start, end + 1):
                        writer.add_page(reader.pages[page_num - 1])  # 0-indexli

                    output_filename = f"pages_{start}-{end}.pdf"
                    output_path = os.path.join(output_dir, output_filename)

                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)

            return True

        except Exception as e:
            print(f"PDF aralık bölme hatası: {e}")
            return False

    def rotate_pdf(self, pdf_path: str, output_path: str,
                   rotation: int, pages: Optional[str] = None) -> bool:
        """PDF sayfalarını döndür"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 gerekli")

        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                writer = PdfWriter()

                if pages:
                    page_numbers = self._parse_page_numbers(pages, len(reader.pages))
                    pages_to_rotate = set(page_numbers)
                else:
                    pages_to_rotate = set(range(1, len(reader.pages) + 1))

                for i, page in enumerate(reader.pages):
                    if (i + 1) in pages_to_rotate:
                        rotated_page = page.rotate(rotation)
                        writer.add_page(rotated_page)
                    else:
                        writer.add_page(page)

                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

            return True

        except Exception as e:
            print(f"PDF döndürme hatası: {e}")
            return False

    def compress_pdf(self, pdf_path: str, output_path: str,
                     quality: str = "medium", dpi: int = 150) -> bool:
        """PDF'i sıkıştır"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 gerekli")

        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                writer = PdfWriter()

                # Kalite ayarlarını belirle
                quality_settings = {
                    "high": 0.9,
                    "medium": 0.7,
                    "low": 0.5,
                    "minimum": 0.3
                }

                compression_level = quality_settings.get(quality, 0.7)

                for page in reader.pages:
                    # Sayfa içeriğini sıkıştır
                    page.compress_content_streams()
                    writer.add_page(page)

                # Writer ayarlarını optimize et
                writer.add_metadata(reader.metadata)

                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

            return True

        except Exception as e:
            print(f"PDF sıkıştırma hatası: {e}")
            return False

    def encrypt_pdf(self, pdf_path: str, output_path: str,
                    password: str, permissions: Dict = None) -> bool:
        """PDF'i şifrele"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 gerekli")

        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                writer = PdfWriter()

                # Sayfaları kopyala
                for page in reader.pages:
                    writer.add_page(page)

                # Metadata kopyala
                if reader.metadata:
                    writer.add_metadata(reader.metadata)

                # Şifreleme ayarları
                allow_printing = permissions.get('print', True) if permissions else True
                allow_copying = permissions.get('copy', True) if permissions else True
                allow_modifying = permissions.get('modify', False) if permissions else False

                # Şifrele
                writer.encrypt(
                    user_pwd=password,
                    owner_pwd=password + "_owner",
                    use_128bit=True,
                    permissions_flag=(
                        (4 if allow_printing else 0) |
                        (16 if allow_copying else 0) |
                        (32 if allow_modifying else 0)
                    )
                )

                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

            return True

        except Exception as e:
            print(f"PDF şifreleme hatası: {e}")
            return False

    def decrypt_pdf(self, pdf_path: str, output_path: str, password: str) -> bool:
        """PDF şifresini kaldır"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 gerekli")

        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)

                if reader.is_encrypted:
                    reader.decrypt(password)

                writer = PdfWriter()

                for page in reader.pages:
                    writer.add_page(page)

                if reader.metadata:
                    writer.add_metadata(reader.metadata)

                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

            return True

        except Exception as e:
            print(f"PDF şifre kaldırma hatası: {e}")
            return False

    def extract_text(self, pdf_path: str) -> str:
        """PDF'den metin çıkar"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 gerekli")

        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)

                for page in reader.pages:
                    text += page.extract_text() + "\n"

            return text

        except Exception as e:
            print(f"Metin çıkarma hatası: {e}")
            return ""

    def extract_images(self, pdf_path: str, output_dir: str) -> List[str]:
        """PDF'den görselleri çıkar"""
        if not PYPDF2_AVAILABLE or not PIL_AVAILABLE:
            raise ImportError("PyPDF2 ve Pillow gerekli")

        extracted_images = []

        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)

                for page_num, page in enumerate(reader.pages):
                    if '/XObject' in page['/Resources']:
                        xObject = page['/Resources']['/XObject'].get_object()

                        for obj in xObject:
                            if xObject[obj]['/Subtype'] == '/Image':
                                size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                                data = xObject[obj].get_data()

                                if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                                    mode = "RGB"
                                else:
                                    mode = "P"

                                try:
                                    img = Image.frombytes(mode, size, data)

                                    img_filename = f"page_{page_num+1}_img_{obj[1:]}.png"
                                    img_path = os.path.join(output_dir, img_filename)

                                    img.save(img_path)
                                    extracted_images.append(img_path)

                                except Exception as e:
                                    print(f"Görsel kaydedilemedi: {e}")

            return extracted_images

        except Exception as e:
            print(f"Görsel çıkarma hatası: {e}")
            return []

    def add_watermark(self, pdf_path: str, output_path: str,
                      watermark_text: str, opacity: float = 0.3) -> bool:
        """PDF'e filigran ekle"""
        if not PYPDF2_AVAILABLE or not REPORTLAB_AVAILABLE:
            raise ImportError("PyPDF2 ve ReportLab gerekli")

        try:
            # Filigran PDF'i oluştur
            watermark_pdf = os.path.join(self.temp_dir, "watermark.pdf")
            self._create_watermark_pdf(watermark_pdf, watermark_text, opacity)

            with open(pdf_path, 'rb') as input_file:
                reader = PdfReader(input_file)

                with open(watermark_pdf, 'rb') as watermark_file:
                    watermark_reader = PdfReader(watermark_file)
                    watermark_page = watermark_reader.pages[0]

                    writer = PdfWriter()

                    for page in reader.pages:
                        # Filigranı sayfaya ekle
                        page.merge_page(watermark_page)
                        writer.add_page(page)

                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)

            return True

        except Exception as e:
            print(f"Filigran ekleme hatası: {e}")
            return False

    def _create_watermark_pdf(self, output_path: str, text: str, opacity: float):
        """Filigran PDF'i oluştur"""
        if not REPORTLAB_AVAILABLE:
            return

        from reportlab.pdfgen import canvas
        from reportlab.lib.colors import Color

        c = canvas.Canvas(output_path, pagesize=A4)

        # Sayfanın ortasına metin yerleştir
        width, height = A4

        # Şeffaflık ayarla
        color = Color(0.5, 0.5, 0.5, alpha=opacity)
        c.setFillColor(color)

        # Font ve boyut ayarla
        c.setFont("Helvetica-Bold", 50)

        # Metni döndürüp ortala
        c.rotate(45)
        text_width = c.stringWidth(text, "Helvetica-Bold", 50)
        c.drawCentredText(width/2, height/2, text)

        c.save()

    def _parse_page_numbers(self, pages_str: str, total_pages: int) -> List[int]:
        """Sayfa numaralarını parse et (örn: "1,3,5-7")"""
        page_numbers = []

        for part in pages_str.split(','):
            part = part.strip()

            if '-' in part:
                # Aralık (5-7)
                start, end = map(int, part.split('-'))
                page_numbers.extend(range(start, min(end + 1, total_pages + 1)))
            else:
                # Tek sayfa (1,3)
                page_num = int(part)
                if 1 <= page_num <= total_pages:
                    page_numbers.append(page_num)

        return sorted(list(set(page_numbers)))

    def _parse_page_ranges(self, ranges_str: str, total_pages: int) -> List[tuple]:
        """Sayfa aralıklarını parse et"""
        ranges = []

        for part in ranges_str.split(','):
            part = part.strip()

            if '-' in part:
                start, end = map(int, part.split('-'))
                start = max(1, start)
                end = min(total_pages, end)
                if start <= end:
                    ranges.append((start, end))
            else:
                # Tek sayfa aralığı olarak değerlendir
                page_num = int(part)
                if 1 <= page_num <= total_pages:
                    ranges.append((page_num, page_num))

        return ranges

    def add_page_numbers(self, pdf_path: str, output_path: str,
                        position: str = "bottom-right",
                        start_number: int = 1) -> bool:
        """PDF'e sayfa numarası ekle"""
        if not PYPDF2_AVAILABLE or not REPORTLAB_AVAILABLE:
            raise ImportError("PyPDF2 ve ReportLab gerekli")

        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                writer = PdfWriter()

                for i, page in enumerate(reader.pages):
                    # Sayfa numarası PDF'i oluştur
                    page_num_pdf = os.path.join(self.temp_dir, f"page_num_{i}.pdf")
                    self._create_page_number_pdf(page_num_pdf, start_number + i, position)

                    # Sayfa numarasını sayfaya ekle
                    with open(page_num_pdf, 'rb') as num_file:
                        num_reader = PdfReader(num_file)
                        page.merge_page(num_reader.pages[0])

                    writer.add_page(page)

                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

            return True

        except Exception as e:
            print(f"Sayfa numarası ekleme hatası: {e}")
            return False

    def _create_page_number_pdf(self, output_path: str, page_number: int, position: str):
        """Sayfa numarası PDF'i oluştur"""
        if not REPORTLAB_AVAILABLE:
            return

        from reportlab.pdfgen import canvas

        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        # Pozisyona göre koordinatları belirle
        positions = {
            "top-left": (50, height - 50),
            "top-center": (width/2, height - 50),
            "top-right": (width - 50, height - 50),
            "bottom-left": (50, 50),
            "bottom-center": (width/2, 50),
            "bottom-right": (width - 50, 50)
        }

        x, y = positions.get(position, positions["bottom-right"])

        c.setFont("Helvetica", 10)

        if "center" in position:
            c.drawCentredText(x, y, str(page_number))
        elif "right" in position:
            c.drawRightString(x, y, str(page_number))
        else:
            c.drawString(x, y, str(page_number))

        c.save()

    def create_form_field(self, pdf_path: str, output_path: str,
                         fields: List[Dict]) -> bool:
        """PDF'e form alanları ekle"""
        # Bu özellik daha gelişmiş PDF kütüphaneleri gerektirir
        # Şu an için basit bir implementasyon
        try:
            # Form alanları ekleme mantığı buraya gelecek
            return True
        except Exception as e:
            print(f"Form alanı ekleme hatası: {e}")
            return False

    def flatten_form(self, pdf_path: str, output_path: str) -> bool:
        """PDF formunu düzleştir (form alanlarını sabit metne çevir)"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 gerekli")

        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                writer = PdfWriter()

                for page in reader.pages:
                    writer.add_page(page)

                # Form alanlarını düzleştir
                writer.update_page_form_field_values(
                    writer.pages[0], {"field_name": "value"}
                )

                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

            return True

        except Exception as e:
            print(f"Form düzleştirme hatası: {e}")
            return False

    def compare_pdfs(self, pdf1_path: str, pdf2_path: str) -> Dict:
        """İki PDF'i karşılaştır"""
        comparison_result = {
            "identical": False,
            "page_count_match": False,
            "content_differences": [],
            "metadata_differences": {}
        }

        try:
            # Temel karşılaştırma
            info1 = self.get_pdf_info(pdf1_path)
            info2 = self.get_pdf_info(pdf2_path)

            comparison_result["page_count_match"] = info1.get("page_count") == info2.get("page_count")

            # Metadata farklarını bul
            for key in info1:
                if key in info2 and info1[key] != info2[key]:
                    comparison_result["metadata_differences"][key] = {
                        "pdf1": info1[key],
                        "pdf2": info2[key]
                    }

            # İçerik karşılaştırması (basit)
            text1 = self.extract_text(pdf1_path)
            text2 = self.extract_text(pdf2_path)

            comparison_result["identical"] = text1 == text2

            if text1 != text2:
                comparison_result["content_differences"].append("Metin içeriği farklı")

            return comparison_result

        except Exception as e:
            print(f"PDF karşılaştırma hatası: {e}")
            return comparison_result

    def repair_pdf(self, pdf_path: str, output_path: str) -> bool:
        """Bozuk PDF'i onarmeye çalış"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 gerekli")

        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file, strict=False)
                writer = PdfWriter()

                # Her sayfayı kopyala (hatalı sayfalar atlanır)
                for i, page in enumerate(reader.pages):
                    try:
                        writer.add_page(page)
                    except Exception as e:
                        print(f"Sayfa {i+1} atlandı: {e}")
                        continue

                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

            return True

        except Exception as e:
            print(f"PDF onarma hatası: {e}")
            return False

    def validate_pdf(self, pdf_path: str) -> Dict:
        """PDF formatını doğrula"""
        validation_result = {
            "is_valid": False,
            "errors": [],
            "warnings": [],
            "info": {}
        }

        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)

                # Temel doğrulama
                validation_result["is_valid"] = True
                validation_result["info"] = self.get_pdf_info(pdf_path)

                # Şifreleme kontrolü
                if reader.is_encrypted:
                    validation_result["warnings"].append("PDF şifrelenmiş")

                # Sayfa kontrolü
                if len(reader.pages) == 0:
                    validation_result["errors"].append("PDF'de sayfa bulunamadı")
                    validation_result["is_valid"] = False

                # Her sayfa için kontrol
                for i, page in enumerate(reader.pages):
                    try:
                        # Sayfa içeriğini okumaya çalış
                        content = page.extract_text()
                    except Exception as e:
                        validation_result["warnings"].append(f"Sayfa {i+1} okuma uyarısı: {e}")

        except Exception as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"PDF açma hatası: {e}")

        return validation_result

    def batch_process(self, file_list: List[str], operation: str,
                     output_dir: str, **kwargs) -> Dict:
        """Toplu işlem"""
        results = {
            "successful": [],
            "failed": [],
            "total": len(file_list),
            "success_count": 0,
            "error_count": 0
        }

        for pdf_path in file_list:
            try:
                filename = os.path.basename(pdf_path)
                name_without_ext = os.path.splitext(filename)[0]

                if operation == "compress":
                    output_path = os.path.join(output_dir, f"compressed_{filename}")
                    success = self.compress_pdf(pdf_path, output_path, **kwargs)
                elif operation == "encrypt":
                    output_path = os.path.join(output_dir, f"encrypted_{filename}")
                    success = self.encrypt_pdf(pdf_path, output_path, **kwargs)
                elif operation == "rotate":
                    output_path = os.path.join(output_dir, f"rotated_{filename}")
                    success = self.rotate_pdf(pdf_path, output_path, **kwargs)
                elif operation == "watermark":
                    output_path = os.path.join(output_dir, f"watermarked_{filename}")
                    success = self.add_watermark(pdf_path, output_path, **kwargs)
                else:
                    success = False

                if success:
                    results["successful"].append({
                        "input": pdf_path,
                        "output": output_path,
                        "operation": operation
                    })
                    results["success_count"] += 1
                else:
                    results["failed"].append({
                        "input": pdf_path,
                        "operation": operation,
                        "error": "İşlem başarısız"
                    })
                    results["error_count"] += 1

            except Exception as e:
                results["failed"].append({
                    "input": pdf_path,
                    "operation": operation,
                    "error": str(e)
                })
                results["error_count"] += 1

        return results

    def get_available_operations(self) -> List[str]:
        """Kullanılabilir operasyonları döndür"""
        operations = []

        if PYPDF2_AVAILABLE:
            operations.extend([
                "merge", "split", "rotate", "encrypt", "decrypt",
                "compress", "extract_text", "extract_images",
                "add_watermark", "add_page_numbers", "repair", "validate"
            ])

        if REPORTLAB_AVAILABLE:
            operations.extend([
                "create_form", "flatten_form"
            ])

        return sorted(list(set(operations)))

    def get_operation_requirements(self) -> Dict:
        """Operasyon gereksinimlerini döndür"""
        return {
            "PyPDF2": PYPDF2_AVAILABLE,
            "ReportLab": REPORTLAB_AVAILABLE,
            "Pillow": PIL_AVAILABLE,
            "missing_packages": [
                pkg for pkg, available in [
                    ("PyPDF2", PYPDF2_AVAILABLE),
                    ("reportlab", REPORTLAB_AVAILABLE),
                    ("Pillow", PIL_AVAILABLE)
                ] if not available
            ]
        }
