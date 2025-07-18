import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import queue
import os
import sys
from datetime import datetime
import json
from PIL import Image, ImageTk

# Ana modülü import et
try:
    from spotifylisteindir import SpotifyPlaylistDownloader
except ImportError:
    messagebox.showerror("Hata", "spotifylisteindir.py dosyası bulunamadı!")
    sys.exit(1)

class ModernSpotifyGUI:
    def __init__(self):
        # CustomTkinter ayarları
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        # Ana pencere
        self.root = ctk.CTk()
        self.root.title("🎵 Spotify Playlist İndirici")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Renk paleti
        self.colors = {
            'primary': '#1DB954',      # Spotify yeşili
            'secondary': '#191414',    # Spotify siyahı
            'accent': '#1ED760',       # Açık yeşil
            'background': '#121212',   # Koyu arka plan
            'surface': '#282828',      # Yüzey rengi
            'text': '#FFFFFF',         # Beyaz metin
            'text_secondary': '#B3B3B3', # Gri metin
            'success': '#1DB954',      # Başarı yeşili
            'warning': '#FFD700',      # Uyarı sarısı
            'error': '#E74C3C'         # Hata kırmızısı
        }
        
        # Downloader instance
        self.downloader = None
        self.is_downloading = False
        self.is_paused = False  # Duraklatma durumu
        self.selected_folder = None
        
        # Log ayarları
        self.detailed_log = False  # Detaylı log modu
        
        # GUI bileşenleri
        self.setup_gui()
        self.load_config()
        
    def setup_gui(self):
        """Modern GUI bileşenlerini oluştur"""
        # Ana container
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Başlık bölümü
        self.create_header()
        
        # Ana içerik bölümü
        self.create_main_content()
        
        # Alt bölüm
        self.create_footer()
        
    def create_header(self):
        """Başlık bölümünü oluştur"""
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Logo ve başlık
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left")
        
        # Spotify logosu (emoji ile)
        logo_label = ctk.CTkLabel(title_frame, text="🎵", font=ctk.CTkFont(size=32))
        logo_label.pack(side="left", padx=(0, 10))
        
        # Başlık
        title_label = ctk.CTkLabel(title_frame, text="Spotify Playlist İndirici", 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(side="left")
        
        # Sağ taraf - Ayarlar butonu
        settings_btn = ctk.CTkButton(header_frame, text="⚙️ Ayarlar", 
                                   command=self.open_settings, width=100)
        settings_btn.pack(side="right")
        
    def create_main_content(self):
        """Ana içerik bölümünü oluştur"""
        # Sol panel - Giriş ve kontroller
        left_panel = ctk.CTkFrame(self.main_container, fg_color=self.colors['surface'])
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # URL girişi
        url_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        url_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(url_frame, text="Spotify Playlist URL", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        
        self.url_entry = ctk.CTkEntry(url_frame, placeholder_text="https://open.spotify.com/playlist/...", 
                                    height=40, font=ctk.CTkFont(size=14))
        self.url_entry.pack(fill="x", pady=(10, 0))
        
        # İndirme konumu seçimi
        folder_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        folder_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(folder_frame, text="İndirme Konumu", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        
        folder_select_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        folder_select_frame.pack(fill="x", pady=(10, 0))
        
        self.folder_label = ctk.CTkLabel(folder_select_frame, text="Klasör seçilmedi", 
                                       text_color=self.colors['text_secondary'])
        self.folder_label.pack(side="left", fill="x", expand=True)
        
        folder_btn = ctk.CTkButton(folder_select_frame, text="📁 Seç", 
                                 command=self.select_folder, width=80)
        folder_btn.pack(side="right", padx=(10, 0))
        
        # İndirme butonu
        button_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        self.download_btn = ctk.CTkButton(button_frame, text="📥 İndirmeyi Başlat", 
                                        command=self.start_download, 
                                        height=50, font=ctk.CTkFont(size=16, weight="bold"))
        self.download_btn.pack(fill="x")
        
        # İlerleme çubuğu
        progress_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)
        
        # Durum etiketi
        self.status_label = ctk.CTkLabel(progress_frame, text="Hazır", 
                                       font=ctk.CTkFont(size=12))
        self.status_label.pack()
        
        # Sağ panel - Log alanı
        right_panel = ctk.CTkFrame(self.main_container, fg_color=self.colors['surface'])
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Log başlığı
        log_header = ctk.CTkFrame(right_panel, fg_color="transparent")
        log_header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(log_header, text="İndirme Logları", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # Log kontrolleri
        log_controls = ctk.CTkFrame(log_header, fg_color="transparent")
        log_controls.pack(side="right")
        
        # Detaylı log toggle
        self.detail_toggle = ctk.CTkSwitch(log_controls, text="Detaylı", 
                                         command=self.toggle_log_detail,
                                         onvalue=True, offvalue=False)
        self.detail_toggle.pack(side="left", padx=(0, 10))
        
        clear_btn = ctk.CTkButton(log_controls, text="🧹 Temizle", 
                                command=self.clear_log, width=80)
        clear_btn.pack(side="left")
        
        # Log alanı
        self.log_text = ctk.CTkTextbox(right_panel, font=ctk.CTkFont(size=12))
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
    def create_footer(self):
        """Alt bölümü oluştur"""
        footer_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        footer_frame.pack(fill="x", pady=(20, 0))
        
        # Sol taraf - İstatistikler
        stats_frame = ctk.CTkFrame(footer_frame, fg_color=self.colors['surface'])
        stats_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.stats_label = ctk.CTkLabel(stats_frame, text="Başarılı: 0 | Başarısız: 0 | Toplam: 0", 
                                      font=ctk.CTkFont(size=12))
        self.stats_label.pack(pady=10)
        
        # Sağ taraf - Hızlı butonlar
        quick_buttons_frame = ctk.CTkFrame(footer_frame, fg_color=self.colors['surface'])
        quick_buttons_frame.pack(side="right")
        
        # Durdur butonu (başlangıçta gizli)
        self.stop_btn = ctk.CTkButton(quick_buttons_frame, text="⏹️ Durdur", 
                                    command=self.stop_download, width=80,
                                    fg_color=self.colors['error'])
        self.stop_btn.pack(side="left", padx=5, pady=10)
        self.stop_btn.pack_forget()  # Başlangıçta gizli
        
        open_folder_btn = ctk.CTkButton(quick_buttons_frame, text="📁 Klasör Aç", 
                                      command=self.open_download_folder, width=100)
        open_folder_btn.pack(side="left", padx=5, pady=10)
        
        test_btn = ctk.CTkButton(quick_buttons_frame, text="🧪 Test", 
                               command=self.test_connection, width=80)
        test_btn.pack(side="left", padx=5, pady=10)
        
    def load_config(self):
        """Config dosyasını yükle"""
        try:
            # Önce gömülü config'i dene
            try:
                import embedded_config
                config = embedded_config.get_config()
                self.downloader = SpotifyPlaylistDownloader(
                    client_id=config["spotify"]["client_id"],
                    client_secret=config["spotify"]["client_secret"]
                )
                self.log("✅ Gömülü config dosyası yüklendi", "success", force_detail=True)
            except ImportError:
                # Gömülü config yoksa varsayılan yöntemi kullan
                self.downloader = SpotifyPlaylistDownloader()
                self.log("✅ Config dosyası yüklendi", "success", force_detail=True)
            
            if self.downloader.client_id and self.downloader.client_secret:
                self.log("✅ Spotify API bilgileri bulundu", "success", force_detail=True)
            else:
                self.log("⚠️ Spotify API bilgileri bulunamadı", "warning", force_detail=True)
                
            # Varsayılan klasörü ayarla
            self.selected_folder = self.downloader.download_folder
            self.folder_label.configure(text=f"📁 {self.selected_folder}")
                
        except Exception as e:
            self.log(f"❌ Config yükleme hatası: {e}", "error", force_detail=True)
            messagebox.showerror("Hata", f"Config dosyası yüklenemedi:\n{e}")
    
    def log(self, message, level="info", force_detail=False):
        """Log mesajı ekle"""
        # Detaylı log kapalıysa ve force_detail False ise mesajı gösterme
        if not self.detailed_log and not force_detail:
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Renk kodları
        colors = {
            "info": self.colors['text'],
            "success": self.colors['success'],
            "warning": self.colors['warning'],
            "error": self.colors['error']
        }
        
        # Tag oluştur
        tag_name = f"tag_{timestamp.replace(':', '_')}"
        
        # Mesajı ekle
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        
        # Renk uygula
        start = f"end-{len(message) + len(timestamp) + 3}l"
        end = "end-1l"
        self.log_text.tag_add(tag_name, start, end)
        self.log_text.tag_config(tag_name, foreground=colors.get(level, self.colors['text']))
        
        # Otomatik kaydır
        self.log_text.see("end")
        self.root.update_idletasks()
    
    def toggle_log_detail(self):
        """Detaylı log modunu aç/kapat"""
        self.detailed_log = self.detail_toggle.get()
        if self.detailed_log:
            self.log("📝 Detaylı log modu açıldı", "info", force_detail=True)
        else:
            self.log("📝 Kompakt log modu açıldı", "info", force_detail=True)
    
    def select_folder(self):
        """İndirme klasörü seç"""
        folder = filedialog.askdirectory(
            title="İndirme Klasörü Seç",
            initialdir=self.selected_folder or os.path.expanduser("~")
        )
        
        if folder:
            self.selected_folder = folder
            self.folder_label.configure(text=f"📁 {folder}")
            self.log(f"✅ İndirme klasörü seçildi", "success", force_detail=True)
    
    def start_download(self):
        """İndirme işlemini başlat/duraklat/durdur"""
        # Eğer indirme devam ediyorsa, duraklat/durdur
        if self.is_downloading:
            if self.is_paused:
                # Duraklatılmış durumda - devam et
                self.is_paused = False
                self.download_btn.configure(text="⏸️ Duraklat", fg_color=self.colors['warning'])
                self.status_label.configure(text="İndirme devam ediyor...")
                self.log("▶️ İndirme devam ediyor", "info", force_detail=True)
            else:
                # Çalışıyor durumda - duraklat
                self.is_paused = True
                self.download_btn.configure(text="▶️ Devam Et", fg_color=self.colors['success'])
                self.status_label.configure(text="İndirme duraklatıldı")
                self.log("⏸️ İndirme duraklatıldı", "warning", force_detail=True)
            return
        
        # Yeni indirme başlat
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Hata", "Lütfen bir Spotify playlist URL'si girin!")
            return
        
        if not url.startswith("https://open.spotify.com/playlist/"):
            messagebox.showerror("Hata", "Geçersiz Spotify playlist URL'si!")
            return
        
        if not self.selected_folder:
            messagebox.showerror("Hata", "Lütfen bir indirme klasörü seçin!")
            return
        
        # İndirme thread'ini başlat
        self.is_downloading = True
        self.is_paused = False
        self.download_btn.configure(text="⏸️ Duraklat", fg_color=self.colors['warning'])
        self.progress_bar.set(0)
        self.status_label.configure(text="İndirme başlatılıyor...")
        
        # İstatistikleri sıfırla
        self.stats = {"successful": 0, "failed": 0, "total": 0}
        self.update_stats()
        
        download_thread = threading.Thread(target=self.download_playlist, args=(url,))
        download_thread.daemon = True
        download_thread.start()
        
        # Durdur butonunu göster
        self.stop_btn.pack(side="left", padx=5, pady=10)
    
    def stop_download(self):
        """İndirme işlemini tamamen durdur"""
        if self.is_downloading:
            self.is_downloading = False
            self.is_paused = False
            self.download_btn.configure(text="📥 İndirmeyi Başlat", fg_color=self.colors['primary'])
            self.status_label.configure(text="İndirme durduruldu")
            self.log("⏹️ İndirme durduruldu", "warning", force_detail=True)
            
            # Durdur butonunu gizle
            self.stop_btn.pack_forget()
    
    def download_playlist(self, url):
        """Playlist indirme işlemi"""
        try:
            self.log(f"🎵 Playlist indirme başlatılıyor", "info", force_detail=True)
            
            # İndirme klasörünü güncelle
            self.downloader.download_folder = self.selected_folder
            
            # Playlist bilgilerini al
            playlist_info = self.downloader.get_playlist_info(url)
            if not playlist_info:
                self.log("❌ Playlist bilgileri alınamadı", "error", force_detail=True)
                self.download_complete(False)
                return
            
            self.log(f"📋 {playlist_info['name']} ({playlist_info['tracks_count']} şarkı)", "success", force_detail=True)
            
            # Şarkıları al
            tracks = self.downloader.get_playlist_tracks(url)
            if not tracks:
                self.log("❌ Hiç şarkı bulunamadı", "error", force_detail=True)
                self.download_complete(False)
                return
            
            self.log(f"📥 İndirme başlıyor...", "success", force_detail=True)
            
            # İndirme işlemi
            total_tracks = len(tracks)
            self.stats["total"] = total_tracks
            
            for i, track in enumerate(tracks):
                if not self.is_downloading:  # İptal kontrolü
                    break
                
                # Duraklatma kontrolü
                while self.is_paused and self.is_downloading:
                    self.status_label.configure(text="⏸️ İndirme duraklatıldı - Devam etmek için butona basın")
                    self.root.update_idletasks()
                    import time
                    time.sleep(0.1)  # CPU kullanımını azaltmak için kısa bekleme
                
                # Eğer indirme durdurulduysa döngüden çık
                if not self.is_downloading:
                    break
                
                track_name = track['name']
                artists = ', '.join(track['artists'])
                
                self.status_label.configure(text=f"İndiriliyor: {track_name} - {artists}")
                
                # Detaylı log modunda şarkı detaylarını göster
                if self.detailed_log:
                    self.log(f"⬇️ İndiriliyor: {track_name} - {artists}", "info")
                
                # İndirme işlemi
                success = self.downloader.download_track(track, playlist_info['name'])
                
                if success:
                    self.stats["successful"] += 1
                    if self.detailed_log:
                        self.log(f"✅ Tamamlandı: {track_name} - {artists}", "success")
                else:
                    self.stats["failed"] += 1
                    if self.detailed_log:
                        self.log(f"❌ Başarısız: {track_name} - {artists}", "error")
                
                # İlerleme güncelle
                progress = ((i + 1) / total_tracks)
                self.progress_bar.set(progress)
                self.update_stats()
                
                # GUI güncelle
                self.root.update_idletasks()
            
            # Özet - her zaman göster
            self.log("=" * 30, "info", force_detail=True)
            self.log("🎉 İndirme Tamamlandı!", "success", force_detail=True)
            self.log(f"✅ Başarılı: {self.stats['successful']} | ❌ Başarısız: {self.stats['failed']}", "success", force_detail=True)
            
            self.download_complete(True)
            
        except Exception as e:
            self.log(f"❌ İndirme hatası: {e}", "error", force_detail=True)
            self.download_complete(False)
    
    def download_complete(self, success):
        """İndirme tamamlandığında çağrılır"""
        self.is_downloading = False
        self.is_paused = False
        self.download_btn.configure(text="📥 İndirmeyi Başlat", fg_color=self.colors['primary'])
        
        # Durdur butonunu gizle
        self.stop_btn.pack_forget()
        
        if success:
            self.status_label.configure(text="İndirme tamamlandı!")
            self.progress_bar.set(1.0)
            messagebox.showinfo("Başarılı", "Playlist indirme tamamlandı!")
        else:
            self.status_label.configure(text="İndirme başarısız!")
            messagebox.showerror("Hata", "İndirme işlemi başarısız oldu!")
    
    def update_stats(self):
        """İstatistikleri güncelle"""
        stats_text = f"Başarılı: {self.stats.get('successful', 0)} | Başarısız: {self.stats.get('failed', 0)} | Toplam: {self.stats.get('total', 0)}"
        self.stats_label.configure(text=stats_text)
    
    def open_settings(self):
        """Ayarlar penceresini aç"""
        SettingsWindow(self.root, self.downloader, self.log)
    
    def open_download_folder(self):
        """İndirme klasörünü aç"""
        if self.selected_folder and os.path.exists(self.selected_folder):
            os.startfile(self.selected_folder)  # Windows
        else:
            messagebox.showwarning("Uyarı", "İndirme klasörü bulunamadı!")
    
    def clear_log(self):
        """Log alanını temizle"""
        self.log_text.delete("1.0", "end")
        self.log("🧹 Log temizlendi", "info", force_detail=True)
    
    def test_connection(self):
        """Bağlantı testi"""
        self.log("🧪 Bağlantı testi başlatılıyor...", "info", force_detail=True)
        
        if not self.downloader.client_id or not self.downloader.client_secret:
            self.log("❌ Spotify API bilgileri eksik", "error", force_detail=True)
            return
        
        try:
            # Test playlist'i
            test_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
            playlist_info = self.downloader.get_playlist_info(test_url)
            
            if playlist_info:
                self.log("✅ Spotify API bağlantısı başarılı", "success", force_detail=True)
                self.log(f"📋 Test playlist: {playlist_info['name']}", "info", force_detail=True)
            else:
                self.log("❌ Spotify API bağlantısı başarısız", "error", force_detail=True)
                
        except Exception as e:
            self.log(f"❌ Test hatası: {e}", "error", force_detail=True)
    
    def run(self):
        """GUI'yi çalıştır"""
        self.root.mainloop()

class SettingsWindow:
    def __init__(self, parent, downloader, log_callback):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("⚙️ Ayarlar")
        self.window.geometry("450x400")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.downloader = downloader
        self.log_callback = log_callback
        
        self.setup_gui()
        
    def setup_gui(self):
        """Ayarlar GUI'sini oluştur"""
        # Ana container
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = ctk.CTkLabel(main_frame, text="⚙️ Ayarlar", 
                                  font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # Paralel İndirme Ayarları
        download_frame = ctk.CTkFrame(main_frame)
        download_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(download_frame, text="📥 Paralel İndirme Ayarları", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Açıklama
        desc_label = ctk.CTkLabel(download_frame, 
                                 text="Aynı anda kaç şarkı indirileceğini belirler.\n"
                                      "Daha yüksek değerler daha hızlı indirme sağlar,\n"
                                      "ancak sistem kaynaklarını daha fazla kullanır.",
                                 font=ctk.CTkFont(size=12),
                                 text_color="#B3B3B3",
                                 justify="center")
        desc_label.pack(pady=(0, 15))
        
        # Paralel İndirme Slider
        ctk.CTkLabel(download_frame, text="Paralel İndirme Sayısı:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20)
        
        self.workers_var = ctk.IntVar(value=self.downloader.max_workers)
        workers_frame = ctk.CTkFrame(download_frame, fg_color="transparent")
        workers_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkSlider(workers_frame, from_=1, to=10, number_of_steps=9, 
                     variable=self.workers_var).pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(workers_frame, textvariable=self.workers_var, 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(side="right", padx=(10, 0))
        
        # Mevcut değer gösterimi
        current_value_label = ctk.CTkLabel(download_frame, 
                                         text=f"Mevcut değer: {self.downloader.max_workers}",
                                         font=ctk.CTkFont(size=12),
                                         text_color="#1DB954")
        current_value_label.pack(pady=(0, 15))
        
        # Butonlar
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(button_frame, text="💾 Kaydet", 
                     command=self.save_settings, width=100).pack(side="left", padx=(0, 10))
        ctk.CTkButton(button_frame, text="❌ İptal", 
                     command=self.window.destroy).pack(side="right")
    
    def save_settings(self):
        """Paralel indirme ayarını kaydet"""
        try:
            # Paralel indirme sayısını güncelle
            new_workers = self.workers_var.get()
            self.downloader.max_workers = new_workers
            
            # Config'i kaydet
            self.downloader.config['settings']['max_workers'] = new_workers
            self.downloader.save_config(self.downloader.config)
            
            self.log_callback(f"✅ Paralel indirme sayısı {new_workers} olarak güncellendi", "success", force_detail=True)
            messagebox.showinfo("Başarılı", f"Paralel indirme sayısı {new_workers} olarak kaydedildi!")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Ayar kaydedilemedi:\n{e}")
    
    def open_config_file(self):
        """Config dosyasını varsayılan editörde aç"""
        try:
            config_path = "config.json"
            if os.path.exists(config_path):
                os.startfile(config_path)  # Windows
                self.log_callback("📁 Config dosyası açıldı", "info", force_detail=True)
            else:
                messagebox.showerror("Hata", "Config dosyası bulunamadı!")
        except Exception as e:
            messagebox.showerror("Hata", f"Config dosyası açılamadı:\n{e}")

def main(config=None):
    """Ana fonksiyon"""
    app = ModernSpotifyGUI()
    app.run()

if __name__ == "__main__":
    main() 