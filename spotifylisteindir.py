import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import os
import re
import time
import subprocess
import sys
import json
from urllib.parse import quote
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class SpotifyPlaylistDownloader:
    def __init__(self, client_id=None, client_secret=None):
        """
        Spotify Playlist Downloader sınıfı
        
        Args:
            client_id (str): Spotify API Client ID
            client_secret (str): Spotify API Client Secret
        """
        # Config dosyasını yükle
        self.config = self.load_config()
        
        # Config'den bilgileri al veya parametreleri kullan
        self.client_id = client_id or self.config.get('spotify', {}).get('client_id', '')
        self.client_secret = client_secret or self.config.get('spotify', {}).get('client_secret', '')
        
        self.sp = None
        self.download_folder = self.config.get('settings', {}).get('download_folder', 'spotify_downloads')
        self.max_workers = self.config.get('settings', {}).get('max_workers', 3)
        self.lock = threading.Lock()
        
        # Klasör oluştur
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
        
        # Spotify API bağlantısı
        if self.client_id and self.client_secret:
            self.connect_spotify()
    
    def load_config(self):
        """Config dosyasını yükle"""
        config_file = "config.json"
        default_config = {
            "spotify": {
                "client_id": "",
                "client_secret": ""
            },
            "settings": {
                "download_folder": "spotify_downloads",
                "max_workers": 3
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Eksik ayarları varsayılan değerlerle doldur
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                        elif isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if sub_key not in config[key]:
                                    config[key][sub_key] = sub_value
                    return config
            else:
                # Config dosyası yoksa oluştur
                self.save_config(default_config)
                return default_config
        except Exception as e:
            print(f"⚠️ Config yükleme hatası: {e}")
            return default_config
    
    def save_config(self, config=None):
        """Config dosyasını kaydet"""
        if config is None:
            config = {
                "spotify": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                },
                "settings": {
                    "download_folder": self.download_folder,
                    "max_workers": self.max_workers
                }
            }
        
        try:
            with open("config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print("✅ Config dosyası kaydedildi!")
        except Exception as e:
            print(f"❌ Config kaydetme hatası: {e}")
    
    def update_spotify_credentials(self, client_id, client_secret):
        """Spotify kimlik bilgilerini güncelle"""
        self.client_id = client_id
        self.client_secret = client_secret
        
        # Config'i güncelle
        self.config['spotify']['client_id'] = client_id
        self.config['spotify']['client_secret'] = client_secret
        self.save_config(self.config)
        
        # Bağlantıyı yeniden kur
        if client_id and client_secret:
            self.connect_spotify()
    
    def update_ytdlp(self):
        """yt-dlp güncelleme özelliği kaldırıldı"""
        print("ℹ️ yt-dlp güncelleme özelliği kaldırıldı.")
    
    def connect_spotify(self):
        """Spotify API'ye bağlan"""
        try:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            print("✅ Spotify API'ye başarıyla bağlandı!")
        except Exception as e:
            print(f"❌ Spotify API bağlantı hatası: {e}")
            self.sp = None
    
    def extract_playlist_id(self, playlist_url):
        """Spotify playlist URL'sinden playlist ID'sini çıkar"""
        patterns = [
            r'spotify\.com/playlist/([a-zA-Z0-9]+)',
            r'spotify\.com/playlist/([a-zA-Z0-9]+)\?',
            r'playlist/([a-zA-Z0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, playlist_url)
            if match:
                return match.group(1)
        
        return None
    
    def get_playlist_info(self, playlist_url):
        """Playlist bilgilerini al"""
        if not self.sp:
            print("❌ Spotify API bağlantısı yok!")
            return None
        
        playlist_id = self.extract_playlist_id(playlist_url)
        if not playlist_id:
            print("❌ Geçersiz playlist URL'si!")
            return None
        
        try:
            playlist = self.sp.playlist(playlist_id)
            return {
                'id': playlist_id,
                'name': playlist['name'],
                'description': playlist.get('description', ''),
                'tracks_count': playlist['tracks']['total'],
                'owner': playlist['owner']['display_name']
            }
        except Exception as e:
            print(f"❌ Playlist bilgileri alınamadı: {e}")
            return None
    
    def get_playlist_tracks(self, playlist_url):
        """Playlist'teki tüm şarkıları al"""
        if not self.sp:
            print("❌ Spotify API bağlantısı yok!")
            return []
        
        playlist_id = self.extract_playlist_id(playlist_url)
        if not playlist_id:
            print("❌ Geçersiz playlist URL'si!")
            return []
        
        tracks = []
        offset = 0
        limit = 100
        
        try:
            while True:
                results = self.sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
                
                for item in results['items']:
                    track = item['track']
                    if track:  # None olmayan track'ler
                        track_info = {
                            'name': track['name'],
                            'artists': [artist['name'] for artist in track['artists']],
                            'album': track['album']['name'],
                            'duration_ms': track['duration_ms'],
                            'external_urls': track['external_urls'],
                            'id': track['id']
                        }
                        tracks.append(track_info)
                
                if len(results['items']) < limit:
                    break
                
                offset += limit
                
        except Exception as e:
            print(f"❌ Şarkılar alınamadı: {e}")
        
        return tracks
    
    def search_youtube(self, query):
        """YouTube'da şarkı ara (geliştirilmiş)"""
        try:
            # yt-dlp ile YouTube arama
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'default_search': 'ytsearch',
                'max_downloads': 3  # İlk 3 sonucu kontrol et
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                results = ydl.extract_info(f"ytsearch3:{query}", download=False)
                
                if results and 'entries' in results and results['entries']:
                    # En iyi sonucu seç (süre ve başlık uyumuna göre)
                    best_match = self._find_best_match(query, results['entries'])
                    if best_match:
                        return {
                            'id': best_match.get('id'),
                            'title': best_match.get('title'),
                            'duration': best_match.get('duration'),
                            'url': f"https://www.youtube.com/watch?v={best_match.get('id')}"
                        }
        
        except Exception as e:
            print(f"❌ YouTube arama hatası: {e}")
        
        return None
    
    def search_multiple_platforms(self, query):
        """Birden fazla platformda ara (geliştirilmiş)"""
        # Sadece YouTube'da ara (daha güvenilir)
        platforms = [
            ('YouTube', f"ytsearch5:{query}"),  # 5 sonuç kontrol et
        ]
        
        for platform_name, search_query in platforms:
            try:
                print(f"🔍 {platform_name}'da aranıyor...")
                result = self._search_platform(search_query, platform_name)
                if result:
                    return result
            except Exception as e:
                print(f"❌ {platform_name} arama hatası: {str(e)[:100]}")
                continue
        
        return None
    
    def _search_platform(self, search_query, platform_name):
        """Belirli bir platformda ara (geliştirilmiş)"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'max_downloads': 5,
            'ignoreerrors': True,
            'nooverwrites': False,
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'extractor_retries': 3
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                results = ydl.extract_info(search_query, download=False)
                
                if results and 'entries' in results and results['entries']:
                    # En iyi sonucu seç
                    best_match = self._find_best_match(search_query.split(':', 1)[1], results['entries'])
                    if best_match:
                        return {
                            'id': best_match.get('id'),
                            'title': best_match.get('title'),
                            'duration': best_match.get('duration'),
                            'url': f"https://www.youtube.com/watch?v={best_match.get('id')}",
                            'platform': platform_name
                        }
        except Exception as e:
            print(f"❌ Platform arama hatası: {str(e)[:100]}")
        
        return None
    
    def _find_best_match(self, query, entries):
        """En iyi eşleşmeyi bul"""
        query_lower = query.lower()
        
        for entry in entries:
            title = entry.get('title', '').lower()
            
            # Tam eşleşme kontrolü
            if all(word in title for word in query_lower.split()):
                return entry
            
            # Kısmi eşleşme kontrolü
            if any(word in title for word in query_lower.split()):
                return entry
        
        # Hiç eşleşme bulunamazsa ilk sonucu döndür
        return entries[0] if entries else None
    
    def download_audio(self, video_url, output_path):
        """YouTube'dan ses dosyası indir (geliştirilmiş hata yakalama)"""
        # Farklı format seçenekleri dene
        format_options = [
            'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio',
            'bestaudio/best',
            'worstaudio/worst',
            'best[height<=720]/best'
        ]
        
        for i, format_option in enumerate(format_options):
            try:
                print(f"🔄 Format {i+1} deneniyor: {format_option}")
                
                ydl_opts = {
                    'format': format_option,
                    'outtmpl': output_path + '.mp3',
                    'writethumbnail': False,
                    'embed_metadata': True,
                    'add_metadata': True,
                    'quiet': False,
                    'no_warnings': False,
                    'postprocessors': [],
                    'prefer_ffmpeg': False,
                    'keepvideo': False,
                    'ignoreerrors': True,
                    'nooverwrites': False,
                    'retries': 3,
                    'fragment_retries': 3,
                    'skip_unavailable_fragments': True,
                    'extractor_retries': 3
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                
                # Dosyanın indirilip indirilmediğini kontrol et
                if os.path.exists(output_path + '.mp3'):
                    print(f"✅ Başarıyla indirildi: {output_path}.mp3")
                    return True
                else:
                    print(f"⚠️ Dosya oluşturulamadı, sonraki format deneniyor...")
                    
            except Exception as e:
                print(f"❌ Format {i+1} hatası: {str(e)[:100]}")
                continue
        
        print(f"❌ Tüm formatlar başarısız oldu: {video_url}")
        
        # Son çare: Basit indirme yöntemi
        print("🔄 Son çare yöntemi deneniyor...")
        return self._simple_download(video_url, output_path)
    
    def _simple_download(self, video_url, output_path):
        """Basit indirme yöntemi (son çare)"""
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': output_path + '.%(ext)s',
                'quiet': False,
                'no_warnings': False,
                'ignoreerrors': True,
                'nooverwrites': False,
                'retries': 5,
                'fragment_retries': 5,
                'skip_unavailable_fragments': True,
                'extractor_retries': 5
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            # Dosya var mı kontrol et
            for ext in ['mp4', 'webm', 'm4a', 'mp3']:
                if os.path.exists(output_path + '.' + ext):
                    print(f"✅ Basit yöntemle indirildi: {output_path}.{ext}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Basit indirme de başarısız: {str(e)[:100]}")
            return False
    
    def sanitize_filename(self, filename):
        """Dosya adını güvenli hale getir"""
        # Geçersiz karakterleri kaldır
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Çok uzun dosya adlarını kısalt
        if len(filename) > 200:
            filename = filename[:200]
        return filename.strip()
    
    def download_track(self, track_info, playlist_name):
        """Tek bir şarkıyı indir"""
        track_name = track_info['name']
        artists = ', '.join(track_info['artists'])
        album = track_info['album']
        
        # Arama sorgusu oluştur
        search_query = f"{track_name} {artists} {album}"
        print(f"🔍 Aranıyor: {search_query}")
        
        # Birden fazla platformda ara
        print(f"🔍 Aranıyor: {search_query}")
        youtube_result = self.search_multiple_platforms(search_query)
        
        if not youtube_result:
            print(f"❌ Bulunamadı: {track_name} - {artists}")
            return False
        
        # Dosya adı oluştur
        safe_filename = self.sanitize_filename(f"{track_name} - {artists}")
        output_path = os.path.join(self.download_folder, playlist_name, f"{safe_filename}")
        
        # Klasör oluştur
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        platform = youtube_result.get('platform', 'YouTube')
        print(f"⬇️ İndiriliyor: {track_name} - {artists} ({platform})")
        
        # İndir
        success = self.download_audio(youtube_result['url'], output_path)
        
        if success:
            print(f"✅ Tamamlandı: {track_name} - {artists}")
        else:
            print(f"❌ Başarısız: {track_name} - {artists}")
        
        return success
    
    def download_playlist(self, playlist_url, max_workers=None):
        if max_workers is None:
            max_workers = self.max_workers
        """Tüm playlist'i indir"""
        print("🎵 Spotify Playlist İndirici Başlatılıyor...")
        print("=" * 50)
        
        # Playlist bilgilerini al
        playlist_info = self.get_playlist_info(playlist_url)
        if not playlist_info:
            return False
        
        print(f"📋 Playlist: {playlist_info['name']}")
        print(f"👤 Sahip: {playlist_info['owner']}")
        print(f"🎵 Şarkı Sayısı: {playlist_info['tracks_count']}")
        print(f"📝 Açıklama: {playlist_info['description']}")
        print("=" * 50)
        
        # Şarkıları al
        tracks = self.get_playlist_tracks(playlist_url)
        if not tracks:
            print("❌ Hiç şarkı bulunamadı!")
            return False
        
        print(f"📥 {len(tracks)} şarkı bulundu, indirme başlıyor...")
        print("=" * 50)
        
        # Playlist klasörü oluştur
        playlist_folder = self.sanitize_filename(playlist_info['name'])
        playlist_path = os.path.join(self.download_folder, playlist_folder)
        os.makedirs(playlist_path, exist_ok=True)
        
        # İndirme istatistikleri
        total_tracks = len(tracks)
        successful_downloads = 0
        failed_downloads = 0
        
        # Threading ile paralel indirme
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Future'ları oluştur
            future_to_track = {
                executor.submit(self.download_track, track, playlist_folder): track 
                for track in tracks
            }
            
            # Sonuçları topla
            for future in as_completed(future_to_track):
                track = future_to_track[future]
                try:
                    success = future.result()
                    if success:
                        successful_downloads += 1
                    else:
                        failed_downloads += 1
                except Exception as e:
                    print(f"❌ Hata: {track['name']} - {e}")
                    failed_downloads += 1
                
                # İlerleme göster
                completed = successful_downloads + failed_downloads
                progress = (completed / total_tracks) * 100
                print(f"📊 İlerleme: {completed}/{total_tracks} ({progress:.1f}%)")
        
        # Özet
        print("=" * 50)
        print("🎉 İndirme Tamamlandı!")
        print(f"✅ Başarılı: {successful_downloads}")
        print(f"❌ Başarısız: {failed_downloads}")
        print(f"📁 Klasör: {playlist_path}")
        
        return True

def main():
    """Ana fonksiyon"""
    print("🎵 Spotify Playlist İndirici")
    print("=" * 50)
    
    # Downloader oluştur
    downloader = SpotifyPlaylistDownloader()
    
    # Spotify API bilgileri kontrol et
    if not downloader.client_id or not downloader.client_secret:
        print("⚠️ Spotify API bilgileri bulunamadı!")
        print("💡 Spotify API bilgilerini girmek ister misiniz? (y/n): ", end="")
        choice = input().strip().lower()
        
        if choice == 'y':
            client_id = input("Spotify Client ID: ").strip()
            client_secret = input("Spotify Client Secret: ").strip()
            
            if client_id and client_secret:
                downloader.update_spotify_credentials(client_id, client_secret)
                print("✅ Spotify API bilgileri kaydedildi!")
            else:
                print("❌ Geçersiz bilgiler!")
        else:
            print("⚠️ Spotify API bilgileri olmadan çalışıyor...")
            print("💡 Daha iyi sonuçlar için Spotify API bilgilerini girin:")
            print("   https://developer.spotify.com/dashboard")
    else:
        print("✅ Spotify API bilgileri bulundu!")
    
    while True:
        print("\n" + "=" * 50)
        print("📋 Menü:")
        print("1. Playlist İndir")
        print("2. Ayarları Düzenle")
        print("3. Çıkış")
        
        choice = input("\nSeçiminiz (1-3): ").strip()
        
        if choice == '1':
            # Playlist indirme
            playlist_url = input("Spotify Playlist URL'sini girin: ").strip()
            
            if not playlist_url:
                print("❌ URL gerekli!")
                continue
            
            # İndirme başlat
            downloader.download_playlist(playlist_url)
            
        elif choice == '2':
            # Ayarları düzenle
            edit_settings(downloader)
            
        elif choice == '3':
            print("👋 Görüşürüz!")
            break
        
        else:
            print("❌ Geçersiz seçim!")

def edit_settings(downloader):
    """Ayarları düzenle"""
    print("\n⚙️ Ayarlar")
    print("=" * 30)
    
    while True:
        print("\n1. Spotify API Bilgilerini Değiştir")
        print("2. İndirme Klasörünü Değiştir")
        print("3. Paralel İndirme Sayısını Değiştir")
        print("4. Ana Menüye Dön")
        
        choice = input("\nSeçiminiz (1-4): ").strip()
        
        if choice == '1':
            # Spotify API bilgilerini değiştir
            client_id = input("Yeni Spotify Client ID: ").strip()
            client_secret = input("Yeni Spotify Client Secret: ").strip()
            
            if client_id and client_secret:
                downloader.update_spotify_credentials(client_id, client_secret)
                print("✅ Spotify API bilgileri güncellendi!")
            else:
                print("❌ Geçersiz bilgiler!")
                
        elif choice == '2':
            # İndirme klasörünü değiştir
            new_folder = input("Yeni indirme klasörü: ").strip()
            if new_folder:
                downloader.download_folder = new_folder
                downloader.config['settings']['download_folder'] = new_folder
                downloader.save_config(downloader.config)
                print(f"✅ İndirme klasörü güncellendi: {new_folder}")
            else:
                print("❌ Geçersiz klasör!")
                
        elif choice == '3':
            # Paralel indirme sayısını değiştir
            try:
                new_workers = int(input("Yeni paralel indirme sayısı (1-10): ").strip())
                if 1 <= new_workers <= 10:
                    downloader.max_workers = new_workers
                    downloader.config['settings']['max_workers'] = new_workers
                    downloader.save_config(downloader.config)
                    print(f"✅ Paralel indirme sayısı güncellendi: {new_workers}")
                else:
                    print("❌ 1-10 arası bir sayı girin!")
            except ValueError:
                print("❌ Geçerli bir sayı girin!")
                
        elif choice == '4':
            break
            
        else:
            print("❌ Geçersiz seçim!")

def test_youtube_download():
    """YouTube indirme testi"""
    print("🧪 YouTube İndirme Testi")
    print("=" * 50)
    
    downloader = SpotifyPlaylistDownloader()
    
    # Test URL'si
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    test_output = "test_download"
    
    print(f"Test URL: {test_url}")
    print(f"Test çıktı: {test_output}")
    
    success = downloader.download_audio(test_url, test_output)
    
    if success:
        print("✅ Test başarılı!")
    else:
        print("❌ Test başarısız!")
    
    # Test dosyasını temizle
    for ext in ['mp4', 'webm', 'm4a', 'mp3']:
        if os.path.exists(f"{test_output}.{ext}"):
            os.remove(f"{test_output}.{ext}")
            print(f"🧹 Test dosyası silindi: {test_output}.{ext}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_youtube_download()
    else:
        main()
