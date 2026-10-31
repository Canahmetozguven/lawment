# Lawment sitesi: teslim notu

Yayına hazır site `site/` klasöründe. 8 sayfa: Ana Sayfa, Biz Kimiz, Projeler, Arşiv, Katıl, Kurumlar İçin, Destek & İletişim, KVKK (taslak).
Canlı siteye ve Wix'teki mevcut siteye dokunulmadı.

## Siteyi yerelde açmak ve güncellemek

```
python build.py                                   # src/ -> site/ (header, footer, <head> tek yerden)
python -m http.server 8080 --directory site      # http://127.0.0.1:8080
node kaynak/kontrol.mjs                           # 1366/390 px, açık/koyu ekran görüntüsü + taşma, bağlantı, konsol, reduced-motion, JS kapalı
powershell -File kaynak/lighthouse.ps1            # Lighthouse
```

| Ne değişecek | Nerede |
|---|---|
| Sayfa metinleri | `src/pages/*.html` |
| Header, footer, menü, SEO etiketleri | `build.py` (`head`, `header`, `FOOTER`, `NAV`) |
| Ekip listesi (Excel'den) | `build.py` → `TEAM`. Fotoğraf eklemek için kişinin satırına `foto="img/ekip/ad.webp"` |
| Kurum listesi ve logolar | `build.py` → `ORGS`; logo dosyası: `site/img/kurumlar/<kısa-ad>.png` (`kaynak/logolar.py` ile) |
| Renkler, yazı, hareket | `src/assets/style.css` |
| Davranışlar ve formlar | `src/assets/main.js` |
| Fotoğraflar (kırpma, parlaklık) | `kaynak/images.py` (orijinaller `kaynak/orijinal/`) |
| Fontlar (siteye gömülü) | `kaynak/fonts.py` |

Kök klasördeki eski taslak HTML'ler ve `assets/` klasörü yedek olarak duruyor, yeni site bunları kullanmıyor.

## Yer tutucular (sitede sarı, kesik çizgili kutu)

| Sayfa | Eksik bilgi |
|---|---|
| Ana Sayfa | Lawment Fest'26 katılımcı sayısı (katılım çubuğu) |
| Projeler | Fest'26 katılımcı sayısı · Lawment Fest 27 tarih ve yer · Comparena 27 tarihi · Comparena başvuru tarihleri ve takım kuralları · Back in Lawment tarih ve yer |
| Arşiv | 2026 programına eklenecek diğer başlıklar · 2026 katılımcı sayısı · 2026'da yer alan kurumlar · 2027 tarih ve yerler |
| Destek & İletişim | Banka adı · IBAN |
| KVKK | Çerez/ölçüm araçları · hukuki sebep eşleştirmesi · barındırma ve e-posta sağlayıcıları, yurt dışı aktarım dayanağı · saklama süreleri · KEP adresi · çerez politikası · güncelleme tarihi |

KVKK sayfası **taslak**: en üstte "hukuki kontrol gerekli" uyarısı var ve arama motorlarına kapalı (`noindex`). Bir hukukçu onaylayınca `src/pages/kvkk.html` başındaki `noindex: true` satırı ve uyarı kutusu kaldırılmalı.

## Teyit edilmesi gerekenler

- **Kurum logoları:** Kurumların kendi sitelerinden (GE HealthCare, Maersk, MSC: Wikimedia Commons'taki resmi dosyalar) alındı. Yayından önce kurumlardan logo kullanım izni teyit edilmeli.
- **Congar Law:** İnternette bulunamadı; şeritte yazıyla duruyor. Logo ya da web sitesi gelirse eklenir.
- **EDAC:** Enerji Uyuşmazlıkları Tahkim Merkezi (arbitrationcenter.org) olarak kabul edildi. Farklı bir EDAC ise logo değişmeli.
- **Görsel yorumları:** Yeni yıl süslü, LAWMENT balonlu toplu fotoğraf "Back in Lawment" görseli olarak kullanıldı; rekabet hukuku sunumu yapan takım fotoğrafı Comparena için kullanıldı. Fotoğraflar başka etkinliklere aitse söyleyin.
- **Eski Wix görselleri:** Ana sayfa ve ekip fotoğraflarında Wix'in gömülü karartması vardı; kırpılıp parlaklığı açıldı.

## Ölçümler

Playwright: 8 sayfa × 1366/390 px × açık/koyu temada yatay taşma, kırık bağlantı ve konsol hatası yok. Reduced-motion açıkken animasyon çalışmıyor; JS kapalıyken bütün metinler görünür.

Lighthouse (mobil, sıkıştırmalı yerel sunucu, bu bilgisayardaki Kaspersky'nin eklediği script engellenerek):

| Sayfa | Performans | Erişilebilirlik | En iyi uygulamalar | SEO |
|---|---|---|---|---|
| Ana Sayfa | 79 | 100 | 82* | 100 |
| Biz Kimiz | 85 | 100 | 82* | 100 |
| Projeler | 84 | 100 | 82* | 100 |
| Arşiv | 86 | 100 | 82* | 100 |
| Katıl | 87 | 100 | 82* | 100 |
| Kurumlar İçin | 85 | 100 | 82* | 100 |
| Destek & İletişim | 87 | 100 | 82* | 100 |
| KVKK | 89 | 100 | 82* | 63** |

\* Tek eksik HTTPS; yerel sunucu HTTP. Wix'te HTTPS ile 100 olması beklenir.
\*\* Taslak olduğu için bilerek `noindex`.

Performansın 90'ın altında kalma nedeni: Lighthouse yavaş 4G simüle ediyor ve sayfalar büyük fotoğraf, fotoğraf kolajı ve dört font ailesi taşıyor. Ana sayfa en görsel ağır sayfa (hero + ikinci fotoğraf + festival kolajı + 9 logo). Yapılan iyileştirmeler: fontlar siteye gömüldü ve küçültüldü, başlık fontu önceden yükleniyor (yerleşim kayması 0.118 → 0.004), logolar 260 KB → 87 KB, görseller AVIF/WebP ve ekran boyutuna göre.

## Geçici Wix sitesi

Önizleme, Lawment Wix hesabında ayrı bir site olarak yayında (mevcut site ve lawment.org'dan bağımsız):
- Site: https://instant-bwduvuqlgslw-kerimcandemir-140d.wix-site-host.com/
- Panel: https://manage.wix.com/dashboard/2d9b239e-4569-4c49-9590-9fb714f5fb73

Güncellemek için: `python build.py`, ardından `site/` klasörünün tamamı Wix'in drop uç noktasına yüklenir
(Wix CLI girişi gerekir; giriş bilgisi `%USERPROFILE%\.wix\auth\account.json`, 4 saat geçerli).

Etkinlik fotoğrafları Drive'daki etkinlik klasörlerinden seçildi (`kaynak/drive/secim.json`). 2023 Yeni Yüzyılın Hukuku için Drive'da fotoğraf bulunamadı.

## Wix'e yükleme (yalnızca "yükle" dendiğinde)

1. `site/` klasörünün tamamı statik site olarak yüklenir (Wix MCP'de statik/headless site akışı; bu oturumda Wix MCP bağlı değildi).
2. Önce test adresinde yayınlanıp kontrol edilir.
3. lawment.org alan adı ancak onaydan sonra taşınır. Mevcut Wix sitesi (2dc9980c-cf67-458e-b285-c25c7c40d38d) silinmez, yedek kalır.
4. Formlar şimdilik ziyaretçinin e-posta uygulamasında info@lawment.org'a hazır bir taslak açıyor. Wix Forms'a bağlamak için `main.js` içindeki `Forms.send` fonksiyonu değiştirilir; form verisi `Forms.collect` ile hazır (alan adı → değer).

### Eski adreslerden yönlendirmeler (301)

| Eski adres | Yeni adres |
|---|---|
| `/hakkımızda` (`/hakk%C4%B1m%C4%B1zda`) | `/biz-kimiz.html` |
| `/destek` | `/iletisim.html#destek` |
| `/iletişim` (`/ileti%C5%9Fim`) | `/iletisim.html` |
| `/copy-of-terms-conditions` (eski KVKK) | `/kvkk.html` |
| `/terms-and-conditions` | `/kvkk.html` (şartlar sayfası yazılana kadar) |

Wix'teki diğer eski sayfa adresleri yükleme öncesi Wix panelinden listelenip bu tabloya eklenmeli.
