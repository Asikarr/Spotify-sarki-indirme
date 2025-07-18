#!/usr/bin/env python3
"""
Spotify Playlist İndirici GUI Başlatıcı
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Gerekli dosyaları kontrol et"""
    required_files = ['spotifylisteindir.py', 'spotify_modern_gui.py']
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Gerekli dosya bulunamadı: {file}")
            return False
    
    return True

def load_config():
    """Config dosyasını yükle"""
    try:
        # Config dosyasından oku
        import json
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Varsayılan config
        return {
            "spotify": {
                "client_id": "",
                "client_secret": ""
            },
            "settings": {
                "download_folder": "spotify_downloads",
                "max_workers": 4,
                "auto_update_ytdlp": True
            }
        }

def main():
    """Ana fonksiyon"""
    print("🎵 Spotify Playlist İndirici GUI")
    print("=" * 40)
    
    # Dosya kontrolü
    if not check_dependencies():
        print("\n💡 Lütfen tüm dosyaların aynı klasörde olduğundan emin olun.")
        root = tk.Tk(); root.withdraw()
        messagebox.showerror("Eksik Dosya", "Gerekli dosya bulunamadı!\nLütfen tüm dosyaların aynı klasörde olduğundan emin olun.")
        return
    
    try:
        # Config'i yükle
        config = load_config()
        print("✅ Config dosyası yüklendi")
        
        # Modern GUI'yi başlat
        from spotify_modern_gui import main as gui_main
        gui_main(config)
        
    except ImportError as e:
        print(f"❌ Import hatası: {e}")
        print("\n💡 Gerekli kütüphaneler eksik.")
        root = tk.Tk(); root.withdraw()
        messagebox.showerror("Import Hatası", f"Gerekli kütüphaneler eksik!\n{e}")
        return
        
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        root = tk.Tk(); root.withdraw()
        messagebox.showerror("Beklenmeyen Hata", f"Beklenmeyen bir hata oluştu!\n{e}")

if __name__ == "__main__":
    main() 