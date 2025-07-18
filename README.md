# 🎵 Spotify Playlist İndirici

Bu Python uygulaması, Spotify çalma listelerindeki şarkıları YouTube'dan indirmenizi sağlar.

## ✨ Özellikler

- 🎯 Spotify çalma listelerini otomatik olarak analiz eder
- 🎵 Şarkıları YouTube'dan yüksek kalitede indirir
- 📁 Her çalma listesi için ayrı klasör oluşturur
- 🔄 Paralel indirme ile hızlı performans
- 🎨 MP3 formatında metadata ile birlikte indirir
- 📊 İndirme ilerlemesini gösterir
- 🛡️ Güvenli dosya adları oluşturur
- 🖥️ **Modern GUI arayüzü**
- ⚙️ **Kolay ayarlar yönetimi**
- 📝 **Gerçek zamanlı log takibi**
- 🎨 **Spotify teması**

## 📋 Gereksinimler

### Sistem Gereksinimleri
- **FFmpeg**: Artık gerekli değil! Program yerleşik dönüştürme kullanıyor.

## 🚀 Başlangıç

**Spotify API bilgilerini alın** (opsiyonel ama önerilen):
- https://developer.spotify.com/dashboard adresine gidin
- Yeni bir uygulama oluşturun
- Client ID ve Client Secret'ı kopyalayın

## 🎯 Kullanım

### 🖥️ Modern GUI (Grafiksel Arayüz) - Önerilen
```bash
python run_gui.py
```
veya
```bash
python spotify_modern_gui.py
```

### 💻 Komut Satırı
```bash
python spotifylisteindir.py
```

### 🔧 Programatik Kullanım
```python
from spotifylisteindir import SpotifyPlaylistDownloader

# Downloader oluştur
downloader = SpotifyPlaylistDownloader(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Playlist indir
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
downloader.download_playlist(playlist_url)
```

## 📝 Kullanım Adımları

### 🖥️ Modern GUI Kullanımı (Önerilen)

1. **Modern GUI'yi başlatın:**
   ```bash
   python run_gui.py
   ```

2. **Spotify API bilgilerini ayarlayın:**
   - "⚙️ Ayarlar" butonuna tıklayın
   - Client ID ve Client Secret'ı girin
   - "💾 Kaydet" butonuna tıklayın

3. **İndirme konumunu seçin:**
   - "📁 Seç" butonuna tıklayın
   - İndirmek istediğiniz klasörü seçin

4. **Playlist URL'sini girin:**
   ```
   https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
   ```

5. **"📥 İndirmeyi Başlat" butonuna tıklayın:**
   - Program otomatik olarak şarkıları bulacak ve indirecek
   - Modern ilerleme çubuğu ile durumu takip edebilirsiniz
   - Renkli log alanında detaylı bilgileri görebilirsiniz
   - Alt kısımda başarı/başarısız istatistiklerini görebilirsiniz

### 💻 Komut Satırı Kullanımı

1. **Programı çalıştırın:**
   ```bash
   python spotifylisteindir.py
   ```

2. **Spotify API bilgilerini girin** (opsiyonel):
   - Client ID: Spotify Developer Dashboard'dan alın
   - Client Secret: Spotify Developer Dashboard'dan alın

3. **Playlist URL'sini girin:**
   ```
   https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
   ```

4. **İndirmeyi bekleyin:**
   - Program otomatik olarak şarkıları bulacak ve indirecek
   - İlerleme çubuğu ile durumu takip edebilirsiniz

## 🖥️ Modern GUI Özellikleri

### 🎨 Tasarım
- **Dark Mode**: Modern koyu tema
- **Spotify Teması**: Yeşil-siyah renk paleti
- **CustomTkinter**: Modern UI bileşenleri
- **Responsive**: Pencere boyutuna uyumlu tasarım

### 📋 Ana Ekran
- **URL Girişi**: Placeholder ile kolay giriş
- **İndirme Konumu**: İndirme başlamadan klasör seçimi
- **İndir Butonu**: Büyük, belirgin buton
- **İlerleme Çubuğu**: Modern progress bar
- **Log Alanı**: Renkli log mesajları
- **İstatistikler**: Gerçek zamanlı başarı/başarısız sayıları

### ⚙️ Ayarlar Penceresi
- **Spotify API**: Client ID ve Client Secret yönetimi
- **Paralel İndirme**: Slider ile kolay ayarlama (1-10)
- **Otomatik Güncelleme**: Checkbox ile kontrol
- **Modern Form**: Temiz ve düzenli arayüz

### 🚀 Gelişmiş Özellikler
- **Renkli Loglar**: Başarı, hata, uyarı renkleri
- **Bağlantı Testi**: Spotify API test butonu
- **Klasör Açma**: Tek tıkla indirme klasörünü aç
- **Threading**: Arka planda indirme, arayüz donmaz
- **Hata Yönetimi**: Kullanıcı dostu mesajlar

## 📁 Çıktı Yapısı

```
spotify_downloads/
├── Playlist Adı 1/
│   ├── Şarkı 1 - Sanatçı 1.mp3
│   ├── Şarkı 2 - Sanatçı 2.mp3
│   └── ...
└── Playlist Adı 2/
    ├── Şarkı 1 - Sanatçı 1.mp3
    └── ...
```

## ⚙️ Ayarlar

### Paralel İndirme Sayısı
```python
# Varsayılan: 3 thread
downloader.download_playlist(playlist_url, max_workers=5)
```

### İndirme Klasörü
```python
# Varsayılan: "spotify_downloads"
downloader.download_folder = "custom_folder"
```

## 🔧 Sorun Giderme

### "FFmpeg bulunamadı" Hatası
- Artık bu hata oluşmaz! Program FFmpeg gerektirmez
- Yerleşik dönüştürme kullanılıyor

### "Spotify API bağlantı hatası"
- Client ID ve Client Secret'ın doğru olduğundan emin olun
- İnternet bağlantınızı kontrol edin

### "YouTube arama hatası"
- YouTube'un erişilebilir olduğundan emin olun
- VPN kullanıyorsanız kapatmayı deneyin

### "İndirme hatası"
- İnternet bağlantınızı kontrol edin
- Disk alanınızın yeterli olduğundan emin olun
- Antivirüs programınızın engellemediğinden emin olun

## 📊 Performans

- **İndirme Hızı**: Bağlantı hızınıza bağlı (genellikle 1-3 MB/s)
- **Paralel İndirme**: 3 thread ile aynı anda 3 şarkı
- **Dosya Boyutu**: ~3-8 MB per şarkı (yüksek kalite ses)

## ⚠️ Yasal Uyarı

Bu uygulama sadece kişisel kullanım içindir. Telif hakkı korumalı içerikleri ticari amaçla kullanmayın. Yerel yasalarınıza uygun kullanım yapın.

## 🤝 Katkıda Bulunma

1. Bu repository'yi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🆘 Destek

Sorun yaşarsanız:
1. Bu README'deki sorun giderme bölümünü kontrol edin
2. GitHub Issues'da arama yapın
3. Yeni bir issue oluşturun

---

**Not**: Bu uygulama Spotify ve YouTube'un resmi API'lerini kullanır. Kullanım koşullarına uygun kullanım yapın. 