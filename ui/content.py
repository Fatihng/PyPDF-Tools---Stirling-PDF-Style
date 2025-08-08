"""
Content Area bileşeni - Ana çalışma alanı ve araç arayüzleri
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from threading import Thread
import tempfile

class ContentArea(ttk.Frame):
    def __init__(self, parent, pdf_processor=None, ocr_processor=None, utils=None):
        super().__init__(parent)

        self.pdf_processor = pdf_processor
        self.ocr_processor = ocr_processor
        self.utils = utils

        self.selected_files = []
        self.current_tool = None
        self.output_path = ""

        self.setup_styles()
        self.create_content_area()

    def setup_styles(self):
        """Content area için stiller"""
        style = ttk.Style()

        # Main content style
        style.configure('Content.TFrame',
                       background='#ecf0f1',
                       relief='sunken',
                       borderwidth=1)

        # Tool title style
        style.configure('ToolTitle.TLabel',
                       background='#ecf0f1',
                       foreground='#2c3e50',
                       font=('Arial', 14, 'bold'))

        # Tool description style
        style.configure('ToolDesc.TLabel',
                       background='#ecf0f1',
                       foreground='#34495e',
                       font=('Arial', 10))

        # Process button style
        style.configure('Process.TButton',
                       background='#27ae60',
                       foreground='white',
                       font=('Arial', 11, 'bold'))

        style.map('Process.TButton',
                 background=[('active', '#219a52'),
                           ('pressed', '#1e8449')])

    def create_content_area(self):
        """Ana içerik alanını oluştur"""
        self.configure(style='Content.TFrame')

        # Hoş geldiniz ekranı
        self.create_welcome_screen()

    def create_welcome_screen(self):
        """Hoş geldiniz ekranı"""
        self.welcome_frame = ttk.Frame(self, style='Content.TFrame')
        self.welcome_frame.pack(fill='both', expand=True)

        # Merkezi içerik
        center_frame = ttk.Frame(self.welcome_frame, style='Content.TFrame')
        center_frame.pack(expand=True)

        # Büyük başlık
        welcome_label = ttk.Label(center_frame,
                                text="PDF İşleme Araçları",
                                font=('Arial', 24, 'bold'),
                                style='ToolTitle.TLabel')
        welcome_label.pack(pady=(50, 20))

        # Açıklama
        desc_label = ttk.Label(center_frame,
                             text="Soldaki menüden bir araç seçin ve PDF dosyalarınızı işlemeye başlayın",
                             style='ToolDesc.TLabel')
        desc_label.pack(pady=(0, 30))

        # Hızlı başlangıç butonları
        quick_start_frame = ttk.Frame(center_frame, style='Content.TFrame')
        quick_start_frame.pack(pady=20)

        quick_buttons = [
            ("📁 Dosya Seç", self.quick_select_files),
            ("🔗 PDF Birleştir", lambda: self.show_tool('merge', [])),
            ("✂️ PDF Böl", lambda: self.show_tool('split', [])),
            ("🗜️ Sıkıştır", lambda: self.show_tool('compress', []))
        ]

        for i, (text, command) in enumerate(quick_buttons):
            btn = ttk.Button(quick_start_frame,
                           text=text,
                           command=command,
                           width=15)
            btn.grid(row=i//2, column=i%2, padx=10, pady=5)

    def quick_select_files(self):
        """Hızlı dosya seçimi"""
        files = filedialog.askopenfilenames(
            title="PDF Dosyalarını Seçin",
            filetypes=[("PDF dosyaları", "*.pdf")]
        )
        if files:
            self.update_selected_files(list(files))

    def show_tool(self, tool_name, selected_files):
        """Seçili aracı göster"""
        self.current_tool = tool_name
        self.selected_files = selected_files

        # Mevcut içeriği temizle
        for widget in self.winfo_children():
            widget.destroy()

        # Araç arayüzünü oluştur
        self.create_tool_interface(tool_name)

    def create_tool_interface(self, tool_name):
        """Araç arayüzünü oluştur"""
        # Ana container
        self.tool_frame = ttk.Frame(self, style='Content.TFrame')
        self.tool_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Araç bilgileri
        self.create_tool_header(tool_name)

        # Dosya listesi
        self.create_file_list_section()

        # Araç-spesifik arayüz
        self.create_tool_specific_interface(tool_name)

        # İşlem butonları
        self.create_action_buttons()

    def create_tool_header(self, tool_name):
        """Araç başlığı ve açıklaması"""
        header_frame = ttk.Frame(self.tool_frame, style='Content.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))

        # Araç bilgilerini al
        tool_info = self.get_tool_info(tool_name)

        # Başlık
        title_label = ttk.Label(header_frame,
                              text=tool_info['title'],
                              style='ToolTitle.TLabel')
        title_label.pack(anchor='w')

        # Açıklama
        desc_label = ttk.Label(header_frame,
                             text=tool_info['description'],
                             style='ToolDesc.TLabel',
                             wraplength=600)
        desc_label.pack(anchor='w', pady=(5, 0))

    def create_file_list_section(self):
        """Dosya listesi bölümü"""
        files_frame = ttk.LabelFrame(self.tool_frame, text="Seçili Dosyalar", padding=10)
        files_frame.pack(fill='both', expand=True, pady=(0, 20))

        # Dosya listesi için treeview
        columns = ('Dosya', 'Boyut', 'Sayfa', 'Durum')
        self.file_tree = ttk.Treeview(files_frame, columns=columns, show='headings', height=8)

        # Sütun başlıkları
        for col in columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(files_frame, orient='vertical', command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        # Pack
        self.file_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Dosya butonları
        file_buttons_frame = ttk.Frame(files_frame)
        file_buttons_frame.pack(fill='x', pady=(10, 0))

        ttk.Button(file_buttons_frame, text="Dosya Ekle",
                  command=self.add_files).pack(side='left', padx=(0, 10))
        ttk.Button(file_buttons_frame, text="Dosya Kaldır",
                  command=self.remove_files).pack(side='left', padx=(0, 10))
        ttk.Button(file_buttons_frame, text="Tümünü Temizle",
                  command=self.clear_all_files).pack(side='left')

        # Dosya listesini güncelle
        self.update_file_list()

    def create_tool_specific_interface(self, tool_name):
        """Araç-spesifik arayüz öğeleri"""
        self.options_frame = ttk.LabelFrame(self.tool_frame, text="Seçenekler", padding=10)
        self.options_frame.pack(fill='x', pady=(0, 20))

        # Araç türüne göre farklı arayüzler
        if tool_name == 'merge':
            self.create_merge_options()
        elif tool_name == 'split':
            self.create_split_options()
        elif tool_name == 'compress':
            self.create_compress_options()
        elif tool_name == 'encrypt':
            self.create_encrypt_options()
        elif tool_name == 'ocr':
            self.create_ocr_options()
        else:
            self.create_generic_options(tool_name)

    def create_merge_options(self):
        """PDF birleştirme seçenekleri"""
        # Sıralama seçenekleri
        sort_frame = ttk.Frame(self.options_frame)
        sort_frame.pack(fill='x', pady=5)

        ttk.Label(sort_frame, text="Sıralama:").pack(side='left')
        self.sort_var = tk.StringVar(value="name")
        sort_options = [("Dosya Adına Göre", "name"), ("Tarih", "date"), ("Boyut", "size"), ("Manuel", "manual")]

        for text, value in sort_options:
            ttk.Radiobutton(sort_frame, text=text, variable=self.sort_var,
                          value=value).pack(side='left', padx=10)

        # Bookmark seçenekleri
        bookmark_frame = ttk.Frame(self.options_frame)
        bookmark_frame.pack(fill='x', pady=5)

        self.add_bookmarks = tk.BooleanVar(value=True)
        ttk.Checkbutton(bookmark_frame, text="Her dosya için bookmark ekle",
                       variable=self.add_bookmarks).pack(side='left')

    def create_split_options(self):
        """PDF bölme seçenekleri"""
        # Bölme türü
        split_type_frame = ttk.Frame(self.options_frame)
        split_type_frame.pack(fill='x', pady=5)

        ttk.Label(split_type_frame, text="Bölme Türü:").pack(side='left')
        self.split_type = tk.StringVar(value="pages")

        split_options = [("Sayfa Numaralarına Göre", "pages"), ("Her Sayfa", "each"), ("Sayfa Aralıkları", "ranges")]

        for text, value in split_options:
            ttk.Radiobutton(split_type_frame, text=text, variable=self.split_type,
                          value=value).pack(side='left', padx=10)

        # Sayfa numaraları
        pages_frame = ttk.Frame(self.options_frame)
        pages_frame.pack(fill='x', pady=5)

        ttk.Label(pages_frame, text="Sayfa Numaraları (örn: 1,3,5-7):").pack(side='left')
        self.split_pages = tk.StringVar()
        ttk.Entry(pages_frame, textvariable=self.split_pages, width=30).pack(side='left', padx=10)

    def create_compress_options(self):
        """PDF sıkıştırma seçenekleri"""
        # Kalite seviyesi
        quality_frame = ttk.Frame(self.options_frame)
        quality_frame.pack(fill='x', pady=5)

        ttk.Label(quality_frame, text="Kalite Seviyesi:").pack(side='left')
        self.quality_var = tk.StringVar(value="medium")

        quality_options = [("Yüksek", "high"), ("Orta", "medium"), ("Düşük", "low"), ("Minimum", "minimum")]

        for text, value in quality_options:
            ttk.Radiobutton(quality_frame, text=text, variable=self.quality_var,
                          value=value).pack(side='left', padx=10)

        # Görüntü kalitesi
        image_frame = ttk.Frame(self.options_frame)
        image_frame.pack(fill='x', pady=5)

        ttk.Label(image_frame, text="Görüntü DPI:").pack(side='left')
        self.dpi_var = tk.IntVar(value=150)
        ttk.Scale(image_frame, from_=72, to=300, variable=self.dpi_var,
                 orient='horizontal', length=200).pack(side='left', padx=10)

        self.dpi_label = ttk.Label(image_frame, text="150 DPI")
        self.dpi_label.pack(side='left', padx=5)

        # DPI değerini güncelle
        def update_dpi_label(*args):
            self.dpi_label.config(text=f"{self.dpi_var.get()} DPI")
        self.dpi_var.trace('w', update_dpi_label)

    def create_encrypt_options(self):
        """PDF şifreleme seçenekleri"""
        # Şifre girişi
        password_frame = ttk.Frame(self.options_frame)
        password_frame.pack(fill='x', pady=5)

        ttk.Label(password_frame, text="Şifre:").pack(side='left')
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=self.password_var,
                                 show="*", width=20)
        password_entry.pack(side='left', padx=10)

        # Şifre doğrulama
        ttk.Label(password_frame, text="Şifre Tekrar:").pack(side='left', padx=(20, 0))
        self.password_confirm_var = tk.StringVar()
        ttk.Entry(password_frame, textvariable=self.password_confirm_var,
                 show="*", width=20).pack(side='left', padx=10)

        # İzin seçenekleri
        permissions_frame = ttk.Frame(self.options_frame)
        permissions_frame.pack(fill='x', pady=10)

        ttk.Label(permissions_frame, text="İzinler:").pack(anchor='w')

        self.allow_print = tk.BooleanVar(value=True)
        self.allow_copy = tk.BooleanVar(value=True)
        self.allow_modify = tk.BooleanVar(value=False)

        ttk.Checkbutton(permissions_frame, text="Yazdırmaya izin ver",
                       variable=self.allow_print).pack(anchor='w')
        ttk.Checkbutton(permissions_frame, text="Kopyalamaya izin ver",
                       variable=self.allow_copy).pack(anchor='w')
        ttk.Checkbutton(permissions_frame, text="Değiştirmeye izin ver",
                       variable=self.allow_modify).pack(anchor='w')

    def create_ocr_options(self):
        """OCR seçenekleri"""
        # Dil seçimi
        lang_frame = ttk.Frame(self.options_frame)
        lang_frame.pack(fill='x', pady=5)

        ttk.Label(lang_frame, text="Dil:").pack(side='left')
        self.ocr_lang = tk.StringVar(value="tur")

        lang_combo = ttk.Combobox(lang_frame, textvariable=self.ocr_lang,
                                 values=["tur", "eng", "deu", "fra", "spa"],
                                 state="readonly", width=10)
        lang_combo.pack(side='left', padx=10)

        # DPI ayarı
        dpi_frame = ttk.Frame(self.options_frame)
        dpi_frame.pack(fill='x', pady=5)

        ttk.Label(dpi_frame, text="Tarama DPI:").pack(side='left')
        self.ocr_dpi = tk.IntVar(value=300)
        ttk.Spinbox(dpi_frame, from_=150, to=600, increment=50,
                   textvariable=self.ocr_dpi, width=10).pack(side='left', padx=10)

    def create_generic_options(self, tool_name):
        """Genel seçenekler"""
        # Çıktı klasörü
        output_frame = ttk.Frame(self.options_frame)
        output_frame.pack(fill='x', pady=5)

        ttk.Label(output_frame, text="Çıktı Klasörü:").pack(side='left')
        self.output_path_var = tk.StringVar(value=os.path.expanduser("~/Desktop"))
        ttk.Entry(output_frame, textvariable=self.output_path_var,
                 width=40).pack(side='left', padx=10)
        ttk.Button(output_frame, text="Gözat",
                  command=self.browse_output_folder).pack(side='left')

    def create_action_buttons(self):
        """İşlem butonları"""
        action_frame = ttk.Frame(self.tool_frame)
        action_frame.pack(fill='x', pady=20)

        # Sol taraf - Genel butonlar
        left_buttons = ttk.Frame(action_frame)
        left_buttons.pack(side='left')

        ttk.Button(left_buttons, text="Önizleme",
                  command=self.preview_operation).pack(side='left', padx=(0, 10))
        ttk.Button(left_buttons, text="Ayarları Sıfırla",
                  command=self.reset_options).pack(side='left')

        # Sağ taraf - Ana işlem butonu
        right_buttons = ttk.Frame(action_frame)
        right_buttons.pack(side='right')

        self.process_button = ttk.Button(right_buttons,
                                       text=f"🔄 İşlemi Başlat",
                                       style='Process.TButton',
                                       command=self.start_processing)
        self.process_button.pack(side='right')

        # İlerleme çubuğu (başlangıçta gizli)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(action_frame,
                                          variable=self.progress_var,
                                          maximum=100)

    def get_tool_info(self, tool_name):
        """Araç bilgilerini döndür"""
        tools_info = {
            'merge': {
                'title': '🔗 PDF Birleştirme',
                'description': 'Birden fazla PDF dosyasını tek bir dosyada birleştirin.'
            },
            'split': {
                'title': '✂️ PDF Bölme',
                'description': 'PDF dosyasını sayfalara veya belirtilen aralıklara bölün.'
            },
            'compress': {
                'title': '🗜️ PDF Sıkıştırma',
                'description': 'PDF dosyalarının boyutunu küçülterek depolama alanı tasarrufu yapın.'
            },
            'encrypt': {
                'title': '🔒 PDF Şifreleme',
                'description': 'PDF dosyalarınızı şifre ile koruma altına alın.'
            },
            'ocr': {
                'title': '🔍 OCR İşlemi',
                'description': 'Taranmış PDF dosyalarını aranabilir metin haline dönüştürün.'
            }
        }

        return tools_info.get(tool_name, {
            'title': f'{tool_name.title()} İşlemi',
            'description': f'{tool_name} işlemini gerçekleştirin.'
        })

    def update_selected_files(self, files):
        """Seçili dosyalar listesini güncelle"""
        self.selected_files = files
        self.update_file_list()

    def update_file_list(self):
        """Dosya listesini güncelle"""
        # Mevcut öğeleri temizle
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        # Yeni dosyaları ekle
        for file_path in self.selected_files:
            try:
                filename = os.path.basename(file_path)
                size = self.format_file_size(os.path.getsize(file_path))

                # PDF sayfa sayısını al (eğer mümkünse)
                try:
                    page_count = self.pdf_processor.get_page_count(file_path)
                except:
                    page_count = "N/A"

                status = "Hazır"

                self.file_tree.insert('', 'end', values=(filename, size, page_count, status))
            except Exception as e:
                print(f"Dosya bilgisi alınamadı {file_path}: {e}")

    def format_file_size(self, size_bytes):
        """Dosya boyutunu formatla"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.1f} GB"

    def add_files(self):
        """Yeni dosyalar ekle"""
        files = filedialog.askopenfilenames(
            title="PDF Dosyalarını Seçin",
            filetypes=[("PDF dosyaları", "*.pdf")]
        )

        if files:
            # Mevcut dosyalarla birleştir
            new_files = list(set(self.selected_files + list(files)))
            self.update_selected_files(new_files)

    def remove_files(self):
        """Seçili dosyaları kaldır"""
        selected_items = self.file_tree.selection()
        if not selected_items:
            messagebox.showwarning("Uyarı", "Kaldırılacak dosya seçiniz.")
            return

        for item in selected_items:
            filename = self.file_tree.item(item)['values'][0]
            # Dosyayı listeden kaldır
            self.selected_files = [f for f in self.selected_files
                                 if os.path.basename(f) != filename]

        self.update_file_list()

    def clear_all_files(self):
        """Tüm dosyaları temizle"""
        self.selected_files = []
        self.update_file_list()

    def browse_output_folder(self):
        """Çıktı klasörünü seç"""
        folder = filedialog.askdirectory(title="Çıktı Klasörünü Seçin")
        if folder:
            self.output_path_var.set(folder)

    def preview_operation(self):
        """İşlem önizlemesi"""
        if not self.selected_files:
            messagebox.showwarning("Uyarı", "Önce dosya seçiniz.")
            return

        # Önizleme penceresini aç
        self.show_preview_window()

    def show_preview_window(self):
        """Önizleme penceresi göster"""
        preview_window = tk.Toplevel(self)
        preview_window.title("İşlem Önizlemesi")
        preview_window.geometry("600x400")

        # Önizleme içeriği
        preview_text = tk.Text(preview_window, wrap='word')
        preview_text.pack(fill='both', expand=True, padx=10, pady=10)

        # İşlem bilgilerini ekle
        info = f"Araç: {self.current_tool}\n"
        info += f"Dosya Sayısı: {len(self.selected_files)}\n"
        info += f"Seçili Dosyalar:\n"

        for file_path in self.selected_files:
            info += f"- {os.path.basename(file_path)}\n"

        preview_text.insert('1.0', info)
        preview_text.config(state='disabled')

    def reset_options(self):
        """Seçenekleri sıfırla"""
        # Araça göre varsayılan değerleri ayarla
        if hasattr(self, 'sort_var'):
            self.sort_var.set("name")
        if hasattr(self, 'quality_var'):
            self.quality_var.set("medium")
        # Diğer varsayılan değerler...

    def start_processing(self):
        """İşlemi başlat"""
        if not self.selected_files:
            messagebox.showwarning("Uyarı", "Önce dosya seçiniz.")
            return

        # Doğrulama
        if not self.validate_options():
            return

        # İşlemi thread'de çalıştır
        self.disable_ui()
        self.show_progress()

        processing_thread = Thread(target=self.process_files, daemon=True)
        processing_thread.start()

    def validate_options(self):
        """Seçenekleri doğrula"""
        if self.current_tool == 'encrypt':
            if not self.password_var.get():
                messagebox.showerror("Hata", "Şifre giriniz.")
                return False
            if self.password_var.get() != self.password_confirm_var.get():
                messagebox.showerror("Hata", "Şifreler uyuşmuyor.")
                return False

        return True

    def process_files(self):
        """Dosyaları işle"""
        try:
            if self.current_tool == 'merge':
                self.process_merge()
            elif self.current_tool == 'split':
                self.process_split()
            elif self.current_tool == 'compress':
                self.process_compress()
            elif self.current_tool == 'encrypt':
                self.process_encrypt()
            elif self.current_tool == 'ocr':
                self.process_ocr()
            else:
                self.process_generic()

            # İşlem tamamlandı
            self.after(0, self.processing_completed)

        except Exception as e:
            self.after(0, lambda: self.processing_failed(str(e)))

    def process_merge(self):
        """PDF birleştirme işlemi"""
        output_path = os.path.join(self.output_path_var.get(), "merged_pdf.pdf")

        # İlerleme güncelleme
        total_files = len(self.selected_files)

        for i, file_path in enumerate(self.selected_files):
            progress = (i / total_files) * 100
            self.after(0, lambda p=progress: self.update_progress(p))

        # Birleştirme işlemi
        self.pdf_processor.merge_pdfs(
            self.selected_files,
            output_path,
            add_bookmarks=self.add_bookmarks.get(),
            sort_by=self.sort_var.get()
        )

        self.output_file = output_path

    def process_split(self):
        """PDF bölme işlemi"""
        if len(self.selected_files) != 1:
            raise ValueError("Bölme işlemi için tek bir dosya seçiniz.")

        file_path = self.selected_files[0]
        output_dir = os.path.join(self.output_path_var.get(), "split_pages")
        os.makedirs(output_dir, exist_ok=True)

        if self.split_type.get() == "pages":
            pages = self.split_pages.get()
            self.pdf_processor.split_pdf_by_pages(file_path, output_dir, pages)
        elif self.split_type.get() == "each":
            self.pdf_processor.split_pdf_each_page(file_path, output_dir)
        else:
            ranges = self.split_pages.get()
            self.pdf_processor.split_pdf_by_ranges(file_path, output_dir, ranges)

        self.output_file = output_dir

    def process_compress(self):
        """PDF sıkıştırma işlemi"""
        output_dir = os.path.join(self.output_path_var.get(), "compressed")
        os.makedirs(output_dir, exist_ok=True)

        total_files = len(self.selected_files)

        for i, file_path in enumerate(self.selected_files):
            progress = (i / total_files) * 100
            self.after(0, lambda p=progress: self.update_progress(p))

            filename = os.path.basename(file_path)
            output_path = os.path.join(output_dir, f"compressed_{filename}")

            self.pdf_processor.compress_pdf(
                file_path,
                output_path,
                quality=self.quality_var.get(),
                dpi=self.dpi_var.get()
            )

        self.output_file = output_dir

    def process_encrypt(self):
        """PDF şifreleme işlemi"""
        output_dir = os.path.join(self.output_path_var.get(), "encrypted")
        os.makedirs(output_dir, exist_ok=True)

        password = self.password_var.get()
        permissions = {
            'print': self.allow_print.get(),
            'copy': self.allow_copy.get(),
            'modify': self.allow_modify.get()
        }

        total_files = len(self.selected_files)

        for i, file_path in enumerate(self.selected_files):
            progress = (i / total_files) * 100
            self.after(0, lambda p=progress: self.update_progress(p))

            filename = os.path.basename(file_path)
            output_path = os.path.join(output_dir, f"encrypted_{filename}")

            self.pdf_processor.encrypt_pdf(
                file_path,
                output_path,
                password,
                permissions
            )

        self.output_file = output_dir

    def process_ocr(self):
        """OCR işlemi"""
        output_dir = os.path.join(self.output_path_var.get(), "ocr_processed")
        os.makedirs(output_dir, exist_ok=True)

        language = self.ocr_lang.get()
        dpi = self.ocr_dpi.get()

        total_files = len(self.selected_files)

        for i, file_path in enumerate(self.selected_files):
            progress = (i / total_files) * 100
            self.after(0, lambda p=progress: self.update_progress(p))

            filename = os.path.basename(file_path)
            output_path = os.path.join(output_dir, f"ocr_{filename}")

            self.ocr_processor.process_pdf(
                file_path,
                output_path,
                language=language,
                dpi=dpi
            )

        self.output_file = output_dir

    def process_generic(self):
        """Genel işlem"""
        # Diğer araçlar için genel işlem mantığı
        output_dir = os.path.join(self.output_path_var.get(), f"{self.current_tool}_output")
        os.makedirs(output_dir, exist_ok=True)

        total_files = len(self.selected_files)

        for i, file_path in enumerate(self.selected_files):
            progress = (i / total_files) * 100
            self.after(0, lambda p=progress: self.update_progress(p))

            # Araç-spesifik işlem mantığı burada implement edilir
            # Şu an için sadece dosyayı kopyalıyoruz
            import shutil
            filename = os.path.basename(file_path)
            output_path = os.path.join(output_dir, f"processed_{filename}")
            shutil.copy2(file_path, output_path)

        self.output_file = output_dir

    def update_progress(self, value):
        """İlerleme çubuğunu güncelle"""
        self.progress_var.set(value)

    def show_progress(self):
        """İlerleme çubuğunu göster"""
        self.progress_bar.pack(fill='x', pady=(10, 0))
        self.progress_var.set(0)

    def hide_progress(self):
        """İlerleme çubuğunu gizle"""
        self.progress_bar.pack_forget()

    def disable_ui(self):
        """UI'ı devre dışı bırak"""
        self.process_button.config(state='disabled', text="İşleniyor...")

    def enable_ui(self):
        """UI'ı etkinleştir"""
        self.process_button.config(state='normal', text="🔄 İşlemi Başlat")

    def processing_completed(self):
        """İşlem tamamlandığında çağrılır"""
        self.hide_progress()
        self.enable_ui()

        # Başarı mesajı
        success_msg = f"İşlem başarıyla tamamlandı!\n\nÇıktı konumu: {self.output_file}"

        result = messagebox.askyesno(
            "İşlem Tamamlandı",
            f"{success_msg}\n\nÇıktı klasörünü açmak istiyor musunuz?"
        )

        if result:
            self.open_output_folder()

        # Dosya listesindeki durumları güncelle
        self.update_file_status("Tamamlandı")

    def processing_failed(self, error_message):
        """İşlem başarısız olduğunda çağrılır"""
        self.hide_progress()
        self.enable_ui()

        messagebox.showerror(
            "İşlem Hatası",
            f"İşlem sırasında hata oluştu:\n\n{error_message}"
        )

        # Dosya listesindeki durumları güncelle
        self.update_file_status("Hata")

    def update_file_status(self, status):
        """Dosya durumlarını güncelle"""
        for item in self.file_tree.get_children():
            values = list(self.file_tree.item(item)['values'])
            values[3] = status  # Durum sütunu
            self.file_tree.item(item, values=values)

    def open_output_folder(self):
        """Çıktı klasörünü aç"""
        try:
            if hasattr(self, 'output_file'):
                if os.path.isfile(self.output_file):
                    # Dosya ise klasörünü aç
                    folder = os.path.dirname(self.output_file)
                else:
                    # Klasör ise direkt aç
                    folder = self.output_file

                # İşletim sistemine göre klasör aç
                import platform
                if platform.system() == "Windows":
                    os.startfile(folder)
                elif platform.system() == "Darwin":  # macOS
                    os.system(f"open '{folder}'")
                else:  # Linux
                    os.system(f"xdg-open '{folder}'")

        except Exception as e:
            messagebox.showerror("Hata", f"Klasör açılamadı: {str(e)}")

    def refresh(self):
        """İçerik alanını yenile"""
        if self.current_tool:
            self.update_file_list()
        else:
            self.create_welcome_screen()
