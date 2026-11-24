import json
import math
import sys
from pathlib import Path


class GorevNoktasi:
    """GeoJSON dosyasındaki bir görev noktasını temsil eder."""

    def __init__(self, ad: str, aciklama: str, enlem: float, boylam: float):
        self.ad = ad
        self.aciklama = aciklama
        self.enlem = enlem
        self.boylam = boylam

    def __str__(self) -> str:
        return f"{self.ad} ({self.aciklama}) -> Enlem: {self.enlem:.6f}, Boylam: {self.boylam:.6f}"


def haversine(n1: GorevNoktasi, n2: GorevNoktasi) -> float:
    """İki GorevNoktasi arasındaki mesafeyi metre cinsinden hesaplar."""
    R = 6_371_000  # Dünya yarıçapı (metre)

    phi1 = math.radians(n1.enlem)
    phi2 = math.radians(n2.enlem)
    delta_phi = math.radians(n2.enlem - n1.enlem)
    delta_lambda = math.radians(n2.boylam - n1.boylam)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    a = min(1.0, max(0.0, a))

    return 2 * R * math.asin(math.sqrt(a))


def gorev_noktalarini_oku(dosya_yolu: str | Path) -> list[GorevNoktasi]:
    """GeoJSON dosyasını okuyarak GorevNoktasi listesi döndürür."""
    with open(dosya_yolu, "r", encoding="utf-8") as dosya:
        veri = json.load(dosya)

    noktalar: list[GorevNoktasi] = []

    for ozellik in veri.get("features", []):
        geometri = ozellik.get("geometry", {})
        if geometri.get("type") != "Point":
            continue

        # GeoJSON formatında koordinat sırası [boylam, enlem] şeklindedir.
        boylam, enlem = geometri["coordinates"][:2]
        props = ozellik.get("properties", {})

        ad = props.get("name", "Bilinmeyen Nokta")
        aciklama = props.get("description", "")

        noktalar.append(GorevNoktasi(ad, aciklama, float(enlem), float(boylam)))

    return noktalar


def rota_mesafelerini_hesapla(
    noktalar: list[GorevNoktasi], datum_dahil: bool = False
) -> tuple[list[tuple[GorevNoktasi, GorevNoktasi, float]], float]:
    """Ardışık noktalar arası mesafeleri ve toplam rota uzunluğunu döndürür."""
    rota = noktalar if datum_dahil else [n for n in noktalar if n.ad.lower() != "datum"]

    adimlar: list[tuple[GorevNoktasi, GorevNoktasi, float]] = []
    toplam = 0.0

    for i in range(len(rota) - 1):
        mesafe = haversine(rota[i], rota[i + 1])
        adimlar.append((rota[i], rota[i + 1], mesafe))
        toplam += mesafe

    return adimlar, toplam


def tek_dosya_isle(dosya_yolu: Path, datum_dahil: bool = False) -> None:
    """Tek bir GeoJSON dosyasını okuyup detaylı rota çıktısı verir."""
    noktalar = gorev_noktalarini_oku(dosya_yolu)
    if not noktalar:
        print(f"Uyarı: '{dosya_yolu}' içinde geçerli görev noktası bulunamadı.")
        return

    print(f"=== Dosya: {dosya_yolu.name} ===")
    for i, nokta in enumerate(noktalar, start=1):
        print(f"{i}. {nokta}")

    adimlar, toplam = rota_mesafelerini_hesapla(noktalar, datum_dahil=datum_dahil)
    if not adimlar:
        print("\nMesafe hesaplamak için en az 2 rota noktası gereklidir.")
        return

    print("\n--- Ardışık Mesafeler ---")
    for n1, n2, mesafe in adimlar:
        print(f"{n1.ad} -> {n2.ad}: {mesafe:.2f} m")

    print(f"\nToplam Rota Uzunluğu: {toplam:.2f} m ({toplam / 1000:.3f} km)")


def klasor_isle(klasor_yolu: Path, datum_dahil: bool = False) -> None:
    """Klasördeki tüm .geojson dosyalarını tarar ve özet istatistikleri yazdırır."""
    dosyalar = sorted(klasor_yolu.glob("*.geojson"))
    if not dosyalar:
        print(f"Uyarı: '{klasor_yolu}' klasöründe hiç .geojson dosyası bulunamadı.")
        return

    sonuclar: list[tuple[str, float]] = []
    for dosya in dosyalar:
        try:
            noktalar = gorev_noktalarini_oku(dosya)
            _, toplam = rota_mesafelerini_hesapla(noktalar, datum_dahil=datum_dahil)
            sonuclar.append((dosya.name, toplam))
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as hata:
            print(f"Uyarı: '{dosya.name}' atlandı ({hata}).")

    if not sonuclar:
        print("Hiçbir dosya başarıyla işlenemedi.")
        return

    en_kisa = min(sonuclar, key=lambda x: x[1])
    en_uzun = max(sonuclar, key=lambda x: x[1])
    ortalama = sum(mesafe for _, mesafe in sonuclar) / len(sonuclar)

    print(f"=== Klasör Özeti: {klasor_yolu} ===")
    print(f"İşlenen dosya sayısı : {len(sonuclar)}")
    print(f"En kısa rota         : {en_kisa[0]} ({en_kisa[1]:.2f} m)")
    print(f"En uzun rota         : {en_uzun[0]} ({en_uzun[1]:.2f} m)")
    print(f"Ortalama uzunluk     : {ortalama:.2f} m")


def main() -> None:
    argumanlar = sys.argv[1:]
    datum_dahil = "--datum-dahil" in argumanlar
    yol_argumanlari = [arg for arg in argumanlar if arg != "--datum-dahil"]

    proje_dizini = Path(__file__).resolve().parent

    if yol_argumanlari:
        hedef = Path(yol_argumanlari[0])

    else:
        ilk_dosya = next(proje_dizini.rglob("kombinasyon_001.geojson"), None)
        hedef = ilk_dosya.parent if ilk_dosya else proje_dizini / "1.GÜN Kombinasyonları"

    try:
        if hedef.is_dir():
            klasor_isle(hedef, datum_dahil=datum_dahil)
        else:
            tek_dosya_isle(hedef, datum_dahil=datum_dahil)
    except FileNotFoundError:
        print(f"Hata: '{hedef}' dosyası bulunamadı. Dosya yolunu kontrol edip tekrar deneyin.")
    except json.JSONDecodeError as hata:
        print(f"Hata: '{hedef}' geçerli bir JSON/GeoJSON dosyası değil ({hata}).")
    except (KeyError, ValueError, TypeError) as hata:
        print(f"Hata: GeoJSON veri yapısı beklenenden farklı ({hata}).")
    except OSError as hata:
        print(f"Hata: Dosya okunurken bir sorun oluştu ({hata}).")

if __name__ == "__main__":
    main()
