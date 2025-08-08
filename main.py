"""
Stirling-PDF Style Python Application
Ana uygulama dosyası
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from pathlib import Path

# Local imports
from ui.sidebar import Sidebar
from ui.header import Header
from ui.content import ContentArea
from resources.pdf_utils import PDFProcessor
from utils import AppUtils
from ocr_module import OCRProcessor

class StirlingPDFApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PyPDF Tools - Stirling-PDF Style")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        # Ana pencere konfigürasyonu
        self.setup_window()

        # Bileşenleri başlat
        self.pdf_processor = PDFProcessor()
        self.ocr_processor = OCRProcessor()
        self.utils = AppUtils()

        # Seçili dosyalar listesi
        self.selected_files = []
        self.current_tool = None

        # UI bileşenlerini oluştur
        self.create_ui()

        # Event bindings
        self.setup_bindings()

    def setup_window(self):
        """Ana pencere ayarlarını yapılandır"""
        self.root.configure(bg='#f0f2f5')

        # Icon ayarla (eğer varsa)
        try:
            icon_path = os.path.join('icons', 'app_icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass

        # Grid yapılandırması
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def create_ui(self):
        """Ana UI bileşenlerini oluştur"""
        # Header
        self.header = Header(
            self.root,
            on_file_select=self.on_file_select,
            on_clear_files=self.clear_files
        )
        self.header.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        # Sidebar
        self.sidebar = Sidebar(
            self.root,
            on_tool_select=self.on_tool_select
        )
        self.sidebar.grid(row=1, column=0, sticky='nsew', padx=(5,0), pady=5)

        # Content Area
        self.content_area = ContentArea(
            self.root,
            pdf_processor=self.pdf_processor,
            ocr_processor=self.ocr_processor,
            utils=self.utils
        )
        self.content_area.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)

    def setup_bindings(self):
        """Event binding'lerini ayarla"""
        self.root.bind('<Control-o>', lambda e: self.on_file_select())
        self.root.bind('<F5>', lambda e: self.refresh_ui())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_file_select(self):
        """Dosya seçme işlemi"""
        files = filedialog.askopenfilenames(
            title="PDF Dosyalarını Seçin",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )

        if files:
            self.selected_files = list(files)
            self.header.update_file_count(len(self.selected_files))
            self.content_area.update_selected_files(self.selected_files)

    def clear_files(self):
        """Seçili dosyaları temizle"""
        self.selected_files = []
        self.header.update_file_count(0)
        self.content_area.update_selected_files([])

    def on_tool_select(self, tool_name):
        """Araç seçildiğinde çağrılır"""
        self.current_tool = tool_name
        self.content_area.show_tool(tool_name, self.selected_files)

    def refresh_ui(self):
        """UI'ı yenile"""
        self.content_area.refresh()

    def on_closing(self):
        """Uygulama kapatılırken çağrılır"""
        try:
            # Geçici dosyaları temizle
            self.utils.cleanup_temp_files()
        except:
            pass
        finally:
            self.root.destroy()

    def run(self):
        """Uygulamayı başlat"""
        try:
            # Gerekli klasörlerin varlığını kontrol et
            self.ensure_directories()

            # Ana loop'u başlat
            self.root.mainloop()

        except Exception as e:
            messagebox.showerror(
                "Hata",
                f"Uygulama başlatılırken hata oluştu:\n{str(e)}"
            )

    def ensure_directories(self):
        """Gerekli klasörlerin var olduğundan emin ol"""
        directories = ['temp', 'output', 'icons']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)


if __name__ == "__main__":
    try:
        app = StirlingPDFApp()
        app.run()
    except KeyboardInterrupt:
        print("\nUygulama kullanıcı tarafından sonlandırıldı.")
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")
        messagebox.showerror("Kritik Hata", f"Uygulama başlatılamadı:\n{str(e)}")
