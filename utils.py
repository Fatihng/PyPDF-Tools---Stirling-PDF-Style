"""
Yardımcı fonksiyonlar ve utilities modülü
"""

import os
import sys
import json
import shutil
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import configparser

class AppUtils:
    """Uygulama yardımcı fonksiyonları"""

    def __init__(self):
        self.app_name = "PyPDF Tools"
        self.version = "1.0.0"
        self.config_dir = self._get_config_dir()
        self.temp_dir = tempfile.mkdtemp(prefix="pypdf_utils_")

        # Konfigürasyon dosyası
        self.config_file = os.path.join(self.config_dir, "config.ini")
        self.config = configparser.ConfigParser()

        # Log ayarları
        self.setup_logging()

        # Konfigürasyonu yükle
        self.load_config()

    def _get_config_dir(self) -> str:
        """Konfigürasyon klasörünü al"""
        if sys.platform == "win32":
            base_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
        elif sys.platform == "darwin":  # macOS
            base_dir = os.path.expanduser('~/Library/Application Support')
        else:  # Linux
            base_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))

        config_dir = os.path.join(base_dir, 'PyPDF Tools')
        os.makedirs(config_dir, exist_ok=True)

        return config_dir

    def setup_logging(self):
        """Logging ayarlarını yapılandır"""
        log_file = os.path.join(self.config_dir, 'pypdf_tools.log')

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger('PyPDF Tools')

    def log_info(self, message: str):
        """Bilgi mesajı logla"""
        self.logger.info(message)

    def log_error(self, message: str, exception: Exception = None):
        """Hata mesajı logla"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(message)

    def log_warning(self, message: str):
        """Uyarı mesajı logla"""
        self.logger.warning(message)

    def load_config(self):
        """Konfigürasyonu yükle"""
        if os.path.exists(self.config_file):
            try:
                self.config.read(self.config_file, encoding='utf-8')
                self.log_info("Konfigürasyon yüklendi")
            except Exception as e:
                self.log_error("Konfigürasyon yüklenirken hata", e)
                self._create_default_config()
        else:
            self._create_default_config()

    def _create_default_config(self):
        """Varsayılan konfigürasyon oluştur"""
        self.config['DEFAULT'] = {
            'language': 'tr',
            'theme': 'light',
            'auto_save': 'true',
            'max_recent_files': '10'
        }

        self.config['PDF'] = {
            'default_output_dir': os.path.expanduser('~/Desktop'),
            'default_quality': 'medium',
            'default_dpi': '150',
            'add_bookmarks': 'true',
            'preserve_metadata': 'true'
        }

        self.config['OCR'] = {
            'default_language': 'tur',
            'default_dpi': '300',
            'preprocessing': 'true',
            'create_searchable': 'true'
        }

        self.config['UI'] = {
            'window_width': '1200',
            'window_height': '800',
            'sidebar_width': '250',
            'remember_position': 'true'
        }

        self.save_config()

    def save_config(self):
        """Konfigürasyonu kaydet"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            self.log_info("Konfigürasyon kaydedildi")
        except Exception as e:
            self.log_error("Konfigürasyon kaydedilemedi", e)

    def get_config_value(self, section: str, key: str, fallback: str = '') -> str:
        """Konfigürasyon değeri al"""
        return self.config.get(section, key, fallback=fallback)

    def set_config_value(self, section: str, key: str, value: str):
        """Konfigürasyon değeri ayarla"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()

    def get_recent_files(self) -> List[str]:
        """Son kullanılan dosyaları al"""
        recent_files_path = os.path.join(self.config_dir, 'recent_files.json')

        if os.path.exists(recent_files_path):
            try:
                with open(recent_files_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.log_error("Son dosyalar yüklenirken hata", e)

        return []

    def add_recent_file(self, file_path: str):
        """Son kullanılan dosyalara ekle"""
        recent_files = self.get_recent_files()

        # Dosya zaten varsa önce kaldır
        if file_path in recent_files:
            recent_files.remove(file_path)

        # Başa ekle
        recent_files.insert(0, file_path)

        # Maksimum sayıyı aş
        max_files = int(self.get_config_value('DEFAULT', 'max_recent_files', '10'))
        recent_files = recent_files[:max_files]

        # Kaydet
        recent_files_path = os.path.join(self.config_dir, 'recent_files.json')
        try:
            with open(recent_files_path, 'w', encoding='utf-8') as f:
                json.dump(recent_files, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_error("Son dosyalar kaydedilemedi", e)

    def clear_recent_files(self):
        """Son kullanılan dosyaları temizle"""
        recent_files_path = os.path.join(self.config_dir, 'recent_files.json')
        try:
            if os.path.exists(recent_files_path):
                os.remove(recent_files_path)
            self.log_info("Son dosyalar temizlendi")
        except Exception as e:
            self.log_error("Son dosyalar temizlenirken hata", e)

    def validate_pdf_file(self, file_path: str) -> Dict[str, Any]:
        """PDF dosyasını doğrula"""
        validation = {
            'is_valid': False,
            'exists': False,
            'readable': False,
            'size': 0,
            'is_pdf': False,
            'errors': []
        }

        try:
            # Dosya varlığını kontrol et
            if not os.path.exists(file_path):
                validation['errors'].append('Dosya bulunamadı')
                return validation

            validation['exists'] = True
            validation['size'] = os.path.getsize(file_path)

            # Okuma yetkisi kontrolü
            if not os.access(file_path, os.R_OK):
                validation['errors'].append('Dosya okunamıyor')
                return validation

            validation['readable'] = True

            # PDF dosyası kontrolü (basit)
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    validation['errors'].append('Geçerli bir PDF dosyası değil')
                    return validation

            validation['is_pdf'] = True
            validation['is_valid'] = True

        except Exception as e:
            validation['errors'].append(f'Doğrulama hatası: {str(e)}')

        return validation

    def format_file_size(self, size_bytes: int) -> str:
        """Dosya boyutunu okunabilir formatta döndür"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)

        return f"{s} {size_names[i]}"

    def get_temp_file_path(self, prefix: str = "temp_", suffix: str = "") -> str:
        """Geçici dosya yolu oluştur"""
        import tempfile
        fd, temp_path = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=self.temp_dir)
        os.close(fd)  # Sadece yolu istiyoruz
        return temp_path

    def cleanup_temp_files(self):
        """Geçici dosyaları temizle"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.temp_dir = tempfile.mkdtemp(prefix="pypdf_utils_")
                self.log_info("Geçici dosyalar temizlendi")
        except Exception as e:
            self.log_error("Geçici dosyalar temizlenirken hata", e)

    def create_backup(self, file_path: str) -> Optional[str]:
        """Dosya yedeği oluştur"""
        try:
            backup_dir = os.path.join(self.config_dir, 'backups')
            os.makedirs(backup_dir, exist_ok=True)

            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{name}_backup_{timestamp}{ext}"
            backup_path = os.path.join(backup_dir, backup_filename)

            shutil.copy2(file_path, backup_path)
            self.log_info(f"Yedek oluşturuldu: {backup_path}")

            return backup_path

        except Exception as e:
            self.log_error("Yedek oluşturulurken hata", e)
            return None

    def clean_old_backups(self, days: int = 7):
        """Eski yedekleri temizle"""
        try:
            backup_dir = os.path.join(self.config_dir, 'backups')
            if not os.path.exists(backup_dir):
                return

            current_time = datetime.now()
            deleted_count = 0

            for file_name in os.listdir(backup_dir):
                file_path = os.path.join(backup_dir, file_name)

                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    age_days = (current_time - file_time).days

                    if age_days > days:
                        os.remove(file_path)
                        deleted_count += 1

            if deleted_count > 0:
                self.log_info(f"{deleted_count} eski yedek dosyası silindi")

        except Exception as e:
            self.log_error("Eski yedekler silinirken hata", e)

    def get_system_info(self) -> Dict[str, str]:
        """Sistem bilgilerini al"""
        import platform

        info = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0],
            'python_version': platform.python_version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }

        # Bellek bilgisi (varsa)
        try:
            import psutil
            memory = psutil.virtual_memory()
            info['total_memory'] = self.format_file_size(memory.total)
            info['available_memory'] = self.format_file_size(memory.available)
        except ImportError:
            info['memory_info'] = 'Bellek bilgisi alınamadı (psutil gerekli)'

        return info

    def check_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Gerekli kütüphaneleri kontrol et"""
        dependencies = {
            'PyPDF2': {'required': True, 'installed': False, 'version': None},
            'reportlab': {'required': False, 'installed': False, 'version': None},
            'Pillow': {'required': True, 'installed': False, 'version': None},
            'pytesseract': {'required': False, 'installed': False, 'version': None},
            'pdf2image': {'required': False, 'installed': False, 'version': None},
            'PyMuPDF': {'required': False, 'installed': False, 'version': None}
        }

        for package_name in dependencies:
            try:
                if package_name == 'PyPDF2':
                    import PyPDF2
                    dependencies[package_name]['installed'] = True
                    dependencies[package_name]['version'] = getattr(PyPDF2, '__version__', 'Unknown')
                elif package_name == 'reportlab':
                    import reportlab
                    dependencies[package_name]['installed'] = True
                    dependencies[package_name]['version'] = getattr(reportlab, '__version__', 'Unknown')
                elif package_name == 'Pillow':
                    from PIL import Image
                    dependencies[package_name]['installed'] = True
                    dependencies[package_name]['version'] = getattr(Image, '__version__', 'Unknown')
                elif package_name == 'pytesseract':
                    import pytesseract
                    dependencies[package_name]['installed'] = True
                    dependencies[package_name]['version'] = getattr(pytesseract, '__version__', 'Unknown')
                elif package_name == 'pdf2image':
                    import pdf2image
                    dependencies[package_name]['installed'] = True
                    dependencies[package_name]['version'] = getattr(pdf2image, '__version__', 'Unknown')
                elif package_name == 'PyMuPDF':
                    import fitz
                    dependencies[package_name]['installed'] = True
                    dependencies[package_name]['version'] = getattr(fitz, '__version__', 'Unknown')

            except ImportError:
                dependencies[package_name]['installed'] = False

        return dependencies

    def install_missing_dependencies(self) -> Dict[str, bool]:
        """Eksik bağımlılıkları yüklemeye çalış"""
        dependencies = self.check_dependencies()
        installation_results = {}

        for package_name, info in dependencies.items():
            if info['required'] and not info['installed']:
                try:
                    import subprocess
                    import sys

                    # pip install komutu
                    cmd = [sys.executable, '-m', 'pip', 'install', package_name]
                    result = subprocess.run(cmd, capture_output=True, text=True)

                    installation_results[package_name] = result.returncode == 0

                    if result.returncode == 0:
                        self.log_info(f"{package_name} başarıyla yüklendi")
                    else:
                        self.log_error(f"{package_name} yüklenirken hata: {result.stderr}")

                except Exception as e:
                    installation_results[package_name] = False
                    self.log_error(f"{package_name} yüklenirken hata", e)

        return installation_results

    def export_settings(self, export_path: str) -> bool:
        """Ayarları dışa aktar"""
        try:
            settings = {
                'config': dict(self.config._sections),
                'recent_files': self.get_recent_files(),
                'export_date': datetime.now().isoformat(),
                'app_version': self.version
            }

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            self.log_info(f"Ayarlar dışa aktarıldı: {export_path}")
            return True

        except Exception as e:
            self.log_error("Ayarlar dışa aktarılırken hata", e)
            return False

    def import_settings(self, import_path: str) -> bool:
        """Ayarları içe aktar"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Konfigürasyonu güncelle
            if 'config' in settings:
                for section_name, section_data in settings['config'].items():
                    if section_name not in self.config:
                        self.config[section_name] = {}
                    for key, value in section_data.items():
                        self.config[section_name][key] = value

            # Son dosyaları güncelle
            if 'recent_files' in settings:
                recent_files_path = os.path.join(self.config_dir, 'recent_files.json')
                with open(recent_files_path, 'w', encoding='utf-8') as f:
                    json.dump(settings['recent_files'], f, indent=2, ensure_ascii=False)

            self.save_config()
            self.log_info(f"Ayarlar içe aktarıldı: {import_path}")
            return True

        except Exception as e:
            self.log_error("Ayarlar içe aktarılırken hata", e)
            return False

    def reset_settings(self):
        """Ayarları sıfırla"""
        try:
            # Konfigürasyon dosyasını sil
            if os.path.exists(self.config_file):
                os.remove(self.config_file)

            # Son dosyaları temizle
            self.clear_recent_files()

            # Varsayılan ayarları yükle
            self._create_default_config()

            self.log_info("Ayarlar sıfırlandı")

        except Exception as e:
            self.log_error("Ayarlar sıfırlanırken hata", e)

    def create_desktop_shortcut(self) -> bool:
        """Masaüstü kısayolu oluştur"""
        try:
            desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')

            if sys.platform == "win32":
                # Windows için .lnk dosyası oluştur
                shortcut_path = os.path.join(desktop_path, f"{self.app_name}.lnk")

                # winshell kullanarak kısayol oluştur (eğer varsa)
                try:
                    import winshell
                    winshell.CreateShortcut(
                        Path=shortcut_path,
                        Target=sys.executable,
                        Arguments=os.path.abspath(__file__),
                        StartIn=os.path.dirname(os.path.abspath(__file__)),
                        Icon=(sys.executable, 0)
                    )
                    return True
                except ImportError:
                    self.log_warning("winshell bulunamadı, kısayol oluşturulamadı")
                    return False

            else:
                # Linux/macOS için .desktop dosyası
                shortcut_path = os.path.join(desktop_path, f"{self.app_name}.desktop")

                desktop_content = f"""[Desktop Entry]
Name={self.app_name}
Comment=PDF Processing Tools
Exec=python "{os.path.abspath(__file__)}"
Icon=application-pdf
Terminal=false
Type=Application
Categories=Office;
"""

                with open(shortcut_path, 'w') as f:
                    f.write(desktop_content)

                # Çalıştırılabilir yap
                os.chmod(shortcut_path, 0o755)

                return True

        except Exception as e:
            self.log_error("Masaüstü kısayolu oluşturulurken hata", e)
            return False

    def get_app_info(self) -> Dict[str, str]:
        """Uygulama bilgilerini döndür"""
        return {
            'name': self.app_name,
            'version': self.version,
            'config_dir': self.config_dir,
            'temp_dir': self.temp_dir,
            'log_file': os.path.join(self.config_dir, 'pypdf_tools.log'),
            'config_file': self.config_file
        }

    def open_config_folder(self):
        """Konfigürasyon klasörünü aç"""
        try:
            if sys.platform == "win32":
                os.startfile(self.config_dir)
            elif sys.platform == "darwin":  # macOS
                os.system(f"open '{self.config_dir}'")
            else:  # Linux
                os.system(f"xdg-open '{self.config_dir}'")

        except Exception as e:
            self.log_error("Konfigürasyon klasörü açılırken hata", e)

    def create_project_file(self, project_name: str, files: List[str],
                          settings: Dict[str, Any]) -> Optional[str]:
        """Proje dosyası oluştur"""
        try:
            projects_dir = os.path.join(self.config_dir, 'projects')
            os.makedirs(projects_dir, exist_ok=True)

            project_file = os.path.join(projects_dir, f"{project_name}.pypdf")

            project_data = {
                'name': project_name,
                'created_date': datetime.now().isoformat(),
                'files': files,
                'settings': settings,
                'app_version': self.version
            }

            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)

            self.log_info(f"Proje dosyası oluşturuldu: {project_file}")
            return project_file

        except Exception as e:
            self.log_error("Proje dosyası oluşturulurken hata", e)
            return None

    def load_project_file(self, project_path: str) -> Optional[Dict[str, Any]]:
        """Proje dosyasını yükle"""
        try:
            with open(project_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)

            self.log_info(f"Proje dosyası yüklendi: {project_path}")
            return project_data

        except Exception as e:
            self.log_error("Proje dosyası yüklenirken hata", e)
            return None

    def get_available_projects(self) -> List[Dict[str, str]]:
        """Mevcut projeleri listele"""
        projects = []

        try:
            projects_dir = os.path.join(self.config_dir, 'projects')

            if os.path.exists(projects_dir):
                for file_name in os.listdir(projects_dir):
                    if file_name.endswith('.pypdf'):
                        project_path = os.path.join(projects_dir, file_name)

                        try:
                            project_data = self.load_project_file(project_path)
                            if project_data:
                                projects.append({
                                    'name': project_data.get('name', file_name),
                                    'path': project_path,
                                    'created_date': project_data.get('created_date', ''),
                                    'file_count': len(project_data.get('files', []))
                                })
                        except:
                            continue

        except Exception as e:
            self.log_error("Projeler listelenirken hata", e)

        return projects
