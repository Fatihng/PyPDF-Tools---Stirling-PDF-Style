"""
Header bileşeni - Dosya yükleme, navigasyon ve durum bilgileri
"""

import tkinter as tk
from tkinter import ttk, filedialog
import os
from datetime import datetime

class Header(ttk.Frame):
    def __init__(self, parent, on_file_select=None, on_clear_files=None):
        super().__init__(parent)

        self.on_file_select = on_file_select
        self.on_clear_files = on_clear_files
        self.file_count = 0

        self.setup_styles()
        self.create_header()

    def setup_styles(self):
        """Header için özel stiller"""
        style = ttk.Style()

        # Header frame style
        style.configure('Header.TFrame',
                       background='#3498db',
                       relief='raised',
                       borderwidth=1)

        # Title label style
        style.configure('Title.TLabel',
                       background='#3498db',
                       foreground='white',
                       font=('Arial', 16, 'bold'))

        # Info label style
        style.configure('Info.TLabel',
                       background='#3498db',
                       foreground='#ecf0f1',
                       font=('Arial', 10))

        # Header button style
        style.configure('Header.TButton',
                       background='#2980b9',
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       borderwidth=1,
                       relief='raised')

        style.map('Header.TButton',
                 background=[('active', '#1f5582'),
                           ('pressed', '#174a6b')])

    def create_header(self):
        """Header içeriğini oluştur"""
        self.configure(style='Header.TFrame')

        # Ana container
        main_container = ttk.Frame(self, style='Header.TFrame')
        main_container.pack(fill='both', expand=True, padx=10, pady=5)

        # Sol taraf - Logo ve başlık
        left_frame = ttk.Frame(main_container, style='Header.TFrame')
        left_frame.pack(side='left', fill='y')

        # Logo (eğer varsa)
        self.add_logo(left_frame)

        # Başlık
        title_label = ttk.Label(left_frame,
                               text="PyPDF Tools",
                               style='Title.TLabel')
        title_label.pack(side='left', padx=(10, 20))

        # Alt başlık
        subtitle_label = ttk.Label(left_frame,
                                  text="Stirling-PDF Style PDF İşleme Araçları",
                                  style='Info.TLabel')
        subtitle_label.pack(side='left', padx=(0, 20))

        # Orta kısım - Dosya bilgileri ve butonlar
        center_frame = ttk.Frame(main_container, style='Header.TFrame')
        center_frame.pack(side='left', fill='both', expand=True, padx=20)

        self.create_file_section(center_frame)

        # Sağ taraf - Durum bilgileri ve yardımcı butonlar
        right_frame = ttk.Frame(main_container, style='Header.TFrame')
        right_frame.pack(side='right', fill='y')

        self.create_status_section(right_frame)

    def add_logo(self, parent):
        """Logo ekle (eğer varsa)"""
        try:
            logo_path = os.path.join('icons', 'logo.png')
            if os.path.exists(logo_path):
                from PIL import Image, ImageTk

                image = Image.open(logo_path)
                image = image.resize((32, 32), Image.Resampling.LANCZOS)
                logo_image = ImageTk.PhotoImage(image)

                logo_label = ttk.Label(parent, image=logo_image,
                                     style='Header.TFrame')
                logo_label.image = logo_image  # Keep a reference
                logo_label.pack(side='left', padx=(0, 10))

        except ImportError:
            # PIL yoksa sadece text logo
            logo_label = ttk.Label(parent, text="📄",
                                 font=('Arial', 20),
                                 style='Title.TLabel')
            logo_label.pack(side='left', padx=(0, 10))
        except:
            pass

    def create_file_section(self, parent):
        """Dosya seçimi ve bilgi bölümü"""
        # Dosya butonları frame'i
        file_buttons_frame = ttk.Frame(parent, style='Header.TFrame')
        file_buttons_frame.pack(anchor='w', pady=(5, 0))

        # Dosya seç butonu
        select_button = ttk.Button(file_buttons_frame,
                                 text="📁 Dosya Seç",
                                 style='Header.TButton',
                                 command=self.select_files)
        select_button.pack(side='left', padx=(0, 10))

        # Toplu dosya seç butonu
        batch_button = ttk.Button(file_buttons_frame,
                                text="📂 Klasör Seç",
                                style='Header.TButton',
                                command=self.select_folder)
        batch_button.pack(side='left', padx=(0, 10))

        # Dosyaları temizle butonu
        clear_button = ttk.Button(file_buttons_frame,
                                text="🗑️ Temizle",
                                style='Header.TButton',
                                command=self.clear_files)
        clear_button.pack(side='left', padx=(0, 10))

        # Dosya bilgileri
        self.file_info_frame = ttk.Frame(parent, style='Header.TFrame')
        self.file_info_frame.pack(anchor='w', pady=(5, 0))

        self.file_count_label = ttk.Label(self.file_info_frame,
                                        text="Seçili dosya: 0",
                                        style='Info.TLabel')
        self.file_count_label.pack(side='left')

        # Son işlem bilgisi
        self.last_operation_label = ttk.Label(self.file_info_frame,
                                            text="",
                                            style='Info.TLabel')
        self.last_operation_label.pack(side='left', padx=(20, 0))

    def create_status_section(self, parent):
        """Durum bilgileri bölümü"""
        # Saat
        self.time_label = ttk.Label(parent,
                                  text="",
                                  style='Info.TLabel')
        self.time_label.pack(anchor='e', pady=(0, 5))

        # Sistem durumu
        self.status_label = ttk.Label(parent,
                                    text="Hazır",
                                    style='Info.TLabel')
        self.status_label.pack(anchor='e', pady=(0, 5))

        # Ayarlar butonu
        settings_button = ttk.Button(parent,
                                   text="⚙️",
                                   style='Header.TButton',
                                   width=3,
                                   command=self.open_settings)
        settings_button.pack(anchor='e', pady=(0, 5))

        # Yardım butonu
        help_button = ttk.Button(parent,
                               text="❓",
                               style='Header.TButton',
                               width=3,
                               command=self.open_help)
        help_button.pack(anchor='e')

        # Zamanı güncelle
        self.update_time()

    def select_files(self):
        """Dosya seçme dialogunu aç"""
        files = filedialog.askopenfilenames(
            title="PDF Dosyalarını Seçin",
            filetypes=[
                ("PDF dosyaları", "*.pdf"),
                ("Tüm dosyalar", "*.*")
            ],
            multiple=True
        )

        if files and self.on_file_select:
            self.on_file_select()

    def select_folder(self):
        """Klasör seçme dialogunu aç"""
        folder = filedialog.askdirectory(
            title="PDF Dosyaları İçeren Klasörü Seçin"
        )

        if folder:
            # Klasördeki PDF dosyalarını bul
            pdf_files = []
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))

            if pdf_files and self.on_file_select:
                # Dosyaları seçili hale getir (bu kısım main app'te handle edilmeli)
                self.on_file_select()

    def clear_files(self):
        """Seçili dosyaları temizle"""
        if self.on_clear_files:
            self.on_clear_files()

        self.update_last_operation("Dosyalar temizlendi")

    def update_file_count(self, count):
        """Dosya sayısını güncelle"""
        self.file_count = count
        self.file_count_label.config(text=f"Seçili dosya: {count}")

        if count > 0:
            self.status_label.config(text=f"Hazır - {count} dosya seçili")
        else:
            self.status_label.config(text="Hazır")

    def update_last_operation(self, operation):
        """Son işlem bilgisini güncelle"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.last_operation_label.config(text=f"Son işlem: {operation} ({timestamp})")

    def update_time(self):
        """Saati güncelle"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)

        # Her saniye güncelle
        self.after(1000, self.update_time)

    def set_status(self, status):
        """Durum mesajını ayarla"""
        self.status_label.config(text=status)

    def open_settings(self):
        """Ayarlar penceresini aç"""
        # Bu kısım ayrı bir settings window açabilir
        self.update_last_operation("Ayarlar açıldı")

    def open_help(self):
        """Yardım penceresini aç"""
        # Bu kısım yardım dökümanını açabilir
        self.update_last_operation("Yardım açıldı")

    def show_progress(self, progress=0):
        """İlerleme çubuğunu göster"""
        if not hasattr(self, 'progress_bar'):
            self.progress_bar = ttk.Progressbar(
                self.file_info_frame,
                mode='determinate',
                length=200
            )
            self.progress_bar.pack(side='left', padx=(20, 0))

        self.progress_bar['value'] = progress

    def hide_progress(self):
        """İlerleme çubuğunu gizle"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.destroy()
            delattr(self, 'progress_bar')
