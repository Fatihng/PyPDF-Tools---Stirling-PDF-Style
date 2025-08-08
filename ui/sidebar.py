"""
Sidebar bileşeni - PDF araçlarının kategorize edilmiş listesi
"""

import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk

class Sidebar(ttk.Frame):
    def __init__(self, parent, on_tool_select=None):
        super().__init__(parent)
        self.on_tool_select = on_tool_select

        self.configure(style='Sidebar.TFrame')
        self.setup_styles()
        self.create_sidebar()

    def setup_styles(self):
        """Özel stiller tanımla"""
        style = ttk.Style()

        # Sidebar frame style
        style.configure('Sidebar.TFrame',
                       background='#2c3e50',
                       relief='flat')

        # Category label style
        style.configure('Category.TLabel',
                       background='#2c3e50',
                       foreground='#ecf0f1',
                       font=('Arial', 12, 'bold'))

        # Tool button style
        style.configure('Tool.TButton',
                       background='#34495e',
                       foreground='#ecf0f1',
                       font=('Arial', 10),
                       borderwidth=1,
                       relief='flat')

        style.map('Tool.TButton',
                 background=[('active', '#3498db'),
                           ('pressed', '#2980b9')])

    def create_sidebar(self):
        """Sidebar içeriğini oluştur"""
        # Başlık
        title_label = ttk.Label(self, text="PDF Araçları", style='Category.TLabel')
        title_label.pack(fill='x', padx=10, pady=(10, 20))

        # Ana container için scrollable frame
        self.create_scrollable_frame()

        # Kategorileri ve araçları ekle
        self.add_categories_and_tools()

    def create_scrollable_frame(self):
        """Kaydırılabilir frame oluştur"""
        # Canvas ve scrollbar
        self.canvas = tk.Canvas(self, bg='#2c3e50', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)

        # Scrollable frame
        self.scrollable_frame = ttk.Frame(self.canvas, style='Sidebar.TFrame')

        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas ve scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel binding
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        """Mouse wheel ile kaydırma"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def add_categories_and_tools(self):
        """Kategoriler ve araçları ekle"""

        # Kategori ve araç tanımları
        categories = {
            "📄 Temel İşlemler": [
                ("Birleştir", "merge", "Birden fazla PDF'i birleştir"),
                ("Böl", "split", "PDF'i sayfalara böl"),
                ("Döndür", "rotate", "Sayfaları döndür"),
                ("Yeniden Düzenle", "reorganize", "Sayfaları yeniden düzenle")
            ],

            "🔄 Dönüştürme": [
                ("PDF'e Dönüştür", "convert_to_pdf", "Dosyaları PDF'e dönüştür"),
                ("PDF'den Dönüştür", "convert_from_pdf", "PDF'i diğer formatlara dönüştür"),
                ("Görüntü Çıkar", "extract_images", "PDF'den görüntüleri çıkar"),
                ("Metin Çıkar", "extract_text", "PDF'den metni çıkar")
            ],

            "🗜️ Optimizasyon": [
                ("Sıkıştır", "compress", "PDF boyutunu küçült"),
                ("Optimize Et", "optimize", "PDF'i optimize et"),
                ("Temizle", "clean", "Gereksiz verileri temizle"),
                ("Onar", "repair", "Bozuk PDF'leri onar")
            ],

            "🔒 Güvenlik": [
                ("Şifrele", "encrypt", "PDF'e şifre koy"),
                ("Şifre Kaldır", "decrypt", "Şifreyi kaldır"),
                ("İmzala", "sign", "Dijital imza ekle"),
                ("Doğrula", "verify", "İmzayı doğrula")
            ],

            "📝 Düzenleme": [
                ("Filigran Ekle", "add_watermark", "Filigran ekle"),
                ("Filigran Kaldır", "remove_watermark", "Filigranı kaldır"),
                ("Metin Ekle", "add_text", "Metin ekle"),
                ("Görüntü Ekle", "add_image", "Görüntü ekle")
            ],

            "🔍 OCR & Arama": [
                ("OCR Uygula", "ocr", "Tarama yaparak metin çıkar"),
                ("Aranabilir Yap", "make_searchable", "PDF'i aranabilir hale getir"),
                ("Metin Ara", "search_text", "PDF içinde metin ara"),
                ("Değiştir", "replace_text", "Metni değiştir")
            ],

            "📊 Analiz": [
                ("PDF Bilgisi", "pdf_info", "PDF bilgilerini görüntüle"),
                ("Metadata", "metadata", "Metadata bilgilerini düzenle"),
                ("Karşılaştır", "compare", "İki PDF'i karşılaştır"),
                ("Doğrula", "validate", "PDF formatını doğrula")
            ],

            "🎨 Özelleştirme": [
                ("Sayfa Numarası", "add_page_numbers", "Sayfa numarası ekle"),
                ("Header/Footer", "header_footer", "Başlık/altbilgi ekle"),
                ("Kenarlık", "add_border", "Kenarlık ekle"),
                ("Arka Plan", "background", "Arka plan rengi/resmi")
            ],

            "📋 Formlar": [
                ("Form Doldur", "fill_form", "PDF formunu doldur"),
                ("Form Oluştur", "create_form", "Yeni form oluştur"),
                ("Alan Çıkar", "extract_fields", "Form alanlarını çıkar"),
                ("Düzleştir", "flatten_form", "Formu düzleştir")
            ],

            "🔧 Gelişmiş": [
                ("Toplu İşlem", "batch_process", "Toplu işlem yap"),
                ("Otomasyon", "automation", "İşlem otomasyonu"),
                ("API Test", "api_test", "API test aracı"),
                ("Ayarlar", "settings", "Uygulama ayarları")
            ]
        }

        # Her kategori için bölüm oluştur
        for category, tools in categories.items():
            self.add_category_section(category, tools)

    def add_category_section(self, category_name, tools):
        """Kategori bölümü ekle"""
        # Kategori başlığı
        category_frame = ttk.Frame(self.scrollable_frame, style='Sidebar.TFrame')
        category_frame.pack(fill='x', padx=5, pady=(10, 5))

        category_label = ttk.Label(category_frame, text=category_name,
                                 style='Category.TLabel')
        category_label.pack(anchor='w', padx=5, pady=2)

        # Araçlar için frame
        tools_frame = ttk.Frame(self.scrollable_frame, style='Sidebar.TFrame')
        tools_frame.pack(fill='x', padx=15, pady=(0, 5))

        # Her araç için buton oluştur
        for tool_name, tool_id, description in tools:
            self.add_tool_button(tools_frame, tool_name, tool_id, description)

    def add_tool_button(self, parent, tool_name, tool_id, description):
        """Araç butonu ekle"""
        button_frame = ttk.Frame(parent, style='Sidebar.TFrame')
        button_frame.pack(fill='x', pady=1)

        # Icon yüklemeye çalış
        icon = self.load_icon(tool_id)

        button = ttk.Button(
            button_frame,
            text=f"  {tool_name}",
            style='Tool.TButton',
            command=lambda: self.tool_selected(tool_id),
            image=icon if icon else None,
            compound='left' if icon else 'none'
        )
        button.pack(fill='x', padx=2, pady=1)

        # Tooltip ekle
        self.create_tooltip(button, description)

    def load_icon(self, tool_id):
        """Araç ikonu yükle"""
        try:
            icon_path = os.path.join('icons', f'{tool_id}.png')
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
                image = image.resize((16, 16), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
        except:
            pass
        return None

    def create_tooltip(self, widget, text):
        """Tooltip oluştur"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.configure(bg='black')

            label = tk.Label(tooltip, text=text, bg='black', fg='white',
                           font=('Arial', 9), wraplength=200)
            label.pack()

            # Position tooltip
            x, y = event.widget.winfo_rootx(), event.widget.winfo_rooty()
            tooltip.wm_geometry(f"+{x+20}+{y+20}")

            # Store tooltip reference
            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(event.widget, 'tooltip'):
                event.widget.tooltip.destroy()
                del event.widget.tooltip

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def tool_selected(self, tool_id):
        """Araç seçildiğinde çağrılır"""
        if self.on_tool_select:
            self.on_tool_select(tool_id)

    def highlight_tool(self, tool_id):
        """Seçili aracı vurgula"""
        # Implementation for highlighting selected tool
        pass
