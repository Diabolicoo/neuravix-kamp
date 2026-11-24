# GeoJSON Görev Noktası ve Rota Mesafe Hesaplayıcı

Bu proje, GeoJSON formatındaki görev noktalarını okuyarak `GorevNoktasi` nesnelerine dönüştürür; Haversine formülü ile ardışık noktalar arası mesafeleri ve toplam rota uzunluğunu metre cinsinden hesaplar.

## Proje Yapısı

- `main.py`: `GorevNoktasi` sınıfı, `haversine` mesafe hesaplama fonksiyonu, GeoJSON okuma ve rota çıktısı üretme kodlarını içerir.
- `README.md`: Projenin kurulum, hazırlık ve çalıştırma adımlarını açıklar.

## Gereksinimler

- **Python 3.10+** (Yalnızca Python standart kütüphaneleri olan `json`, `math`, `sys` ve `pathlib` kullanılır; harici bir paket kurulumu gerekmez).

## Kurulum ve Veri Hazırlığı

1. Bu depoyu bilgisayarınıza indirin veya klonlayın:
   ```bash
   git clone <REPO_LINKI>
   ```
2. `1.GÜN Kombinasyonları.zip` arşivini ayıklayın.
3. Ortaya çıkan `1.GÜN Kombinasyonları` klasörünü (içinde `kombinasyon_001.geojson` – `kombinasyon_224.geojson` dosyaları bulunur) `main.py` ile aynı proje dizinine yerleştirin.

## Çalıştırma

### 1. Varsayılan Dosya ile Çalıştırma
PyCharm üzerinden **Run** butonuna basarak veya terminalde aşağıdaki komutu çalıştırarak varsayılan `kombinasyon_001.geojson` dosyasını işleyebilirsiniz:

```bash
python main.py
```

### 2. Belirli Bir GeoJSON Dosyası ile Çalıştırma
Farklı bir kombinasyon dosyasını analiz etmek için dosya yolunu argüman olarak verin:

```bash
python main.py "1.GÜN Kombinasyonları/kombinasyon_005.geojson"
```

### 3. Tüm Klasörü Toplu Analiz Etme
Klasördeki 224 `.geojson` dosyasının tamamını tarayıp en kısa rota, en uzun rota ve ortalama uzunluk istatistiklerini görmek için klasör yolunu verin:

```bash
python main.py "1.GÜN Kombinasyonları"
```

### 4. `datum` Noktasını Hesaba Dahil Etme
Varsayılan olarak `datum` (Referans Noktası) mesafe hesabının dışında tutulur ve rota `start` noktasından `park_giris` noktasına kadar hesaplanır. `datum` noktasını da ardışık mesafe hesabına dahil etmek için `--datum-dahil` parametresini kullanın:

```bash
python main.py "1.GÜN Kombinasyonları/kombinasyon_001.geojson" --datum-dahil
```

## Hata Yönetimi

- Belirtilen dosya yolu bulunamadığında (`FileNotFoundError`) veya dosya geçerli bir JSON/GeoJSON yapısında olmadığında (`JSONDecodeError`) program çökmeden kullanıcıya anlaşılır bir hata mesajı gösterir.