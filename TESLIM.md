# Lawment sitesi: teslim notu

Yayına hazır site `site/` klasöründe. 8 sayfa: Ana Sayfa, Biz Kimiz, Projeler, Arşiv, Katıl, Kurumlar İçin, Destek & İletişim, KVKK.
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

## Yer tutucular

Sitede yer tutucu (sarı, kesik çizgili kutu) kalmadı. Kontrol: `grep -r 'class="ph"' src/pages` sonuç vermemeli.

Banka adı ve IBAN sitede **yayımlanmıyor** (dernek istemedi). Destek & İletişim sayfasında bağış için e-posta adresi ve iletişim formundaki "Bağış" konusu gösteriliyor; hesap bilgisi eklenirse `iletisim.html` içindeki "Nasıl destek olabilirsin" kutusuna yazılır.

KVKK sayfası dernek kararına göre yazıldı: site ziyaretçilerden kişisel veri **toplamaz** (formlar yalnızca e-posta taslağı açar, analiz/reklam aracı yok); Wix'in teknik olarak işlediği veriler Wix'in kendi politikasındadır, dernek bunları kullanmaz. Bu varsayımlar değişirse (sunucuya gönderen form, Google Analytics, reklam pikseli vb. eklenirse) metin güncellenmeli. Sayfa hâlâ arama motorlarına kapalı (`noindex`); bir hukukçu metni okuyunca `src/pages/kvkk.html` başındaki `noindex: true` satırı kaldırılabilir.

## Teyit edilmesi gerekenler

- **İzinler:** Fotoğraf, ad, alıntı ve logolar için kimden neyin teyit edileceği `IZIN-KONTROL.md` dosyasında; kısa mesaj metinleri de orada. Şu an hiçbirinin izni dosyalanmış değil.
- **Kurum logoları:** Kurumların kendi sitelerinden (GE HealthCare, Maersk, MSC: Wikimedia Commons'taki resmi dosyalar) alındı. Yayından önce kurumlardan logo kullanım izni teyit edilmeli.
- **Congar Law:** İnternette bulunamadı; şeritte yazıyla duruyor. Logo ya da web sitesi gelirse eklenir.
- **EDAC:** Enerji Uyuşmazlıkları Tahkim Merkezi (arbitrationcenter.org) olarak kabul edildi. Farklı bir EDAC ise logo değişmeli.
- **Fotoğraflar:** Etkinlik fotoğrafları derneğin Drive klasörlerinden seçildi ve ekibin geri bildirimine göre değiştirildi; hangi fotoğrafın hangi etkinliğe ait olduğu Drive klasör adlarından alındı. Ana sayfa kapağında Fest'26 grup fotoğrafı ve Fest'25 panel fotoğrafı var.
- **Eski Wix görselleri:** Ana sayfa ve ekip fotoğraflarında Wix'in gömülü karartması vardı; kırpılıp parlaklığı açıldı.

## Ölçümler

Playwright: 8 sayfa × 1366/390 px × açık/koyu temada yatay taşma, kırık bağlantı ve konsol hatası yok. Reduced-motion açıkken animasyon çalışmıyor; JS kapalıyken bütün metinler görünür.

Lighthouse (mobil, 15 Kasım 2026; bu bilgisayardaki Kaspersky'nin eklediği script engellenerek):

| Ölçüm | Sayfalar | Performans | Erişilebilirlik | En iyi uygulamalar |
|---|---|---|---|---|
| HTTPS önizleme (GitHub Pages, sıkıştırmalı) | Ana Sayfa, Biz Kimiz, Projeler, Destek & İletişim | 98, 98, 99, 99 | 96* | 100 |
| Yerel sunucu | 8 sayfanın tamamı | | 100 | 100 |

Ana sayfa LCP 2,4 sn, Projeler 2,0 sn; yerleşim kayması ve toplam engelleme süresi 0. \* Ana sayfadaki 96, kaydırdıkça aydınlanan cümlenin soluk kelimelerindendi; renk koyulaştırıldı, düzeltmeden sonra yerel ölçümde 100. SEO puanı önizlemede 66: önizleme bilerek `noindex` olduğu için ("Sayfa dizine eklenmeye kapalı"); gerçek yayında 100 beklenir. PageSpeed Insights'ın herkese açık API'si bugün kota hatası verdi (429), bu yüzden ölçüm Lighthouse ile yapıldı. lawment.org'da yayından sonra https://pagespeed.web.dev adresinden bir kez daha ölçülmeli.

Performans için yapılanlar: fontlar siteye gömüldü ve küçültüldü, başlık fontu önceden yükleniyor, logolar küçültüldü, görseller AVIF/WebP ve ekran boyutuna göre.

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
| `/lawment-fest-2026` | `/projeler.html#lawment-fest` |
| `/ekibimiz` | `/biz-kimiz.html#ekibimiz` |
| `/etkinliklerimiz/lawmentfest` | `/projeler.html#lawment-fest` |
| `/etkinliklerimiz/comparena` | `/projeler.html#comparena` |
| `/etkinliklerimiz/backinlaw` | `/projeler.html#back-in-lawment` |
| `/etkinliklerimiz/lansman` | `/arsiv.html` |
| `/donation-thank-you-page` | `/iletisim.html#destek` |
| `/accessibility-statement` | `/` (erişilebilirlik beyanı sayfası yok) |
| `/search` | `/` |
| `/profile/*` (üç üye profili ve etkinlik sayfaları) | `/biz-kimiz.html` |

Bu liste www.lawment.org'un 15 Kasım 2026'daki site haritasından alındı (sayfalar, etkinlikler ve üye profilleri). Eski sitede başka bir bölüm varsa yükleme günü Wix panelinden bakılıp eklenmeli. Eski `/iletişim` adresi Wix'te `i̇letişim` (noktalı i, birleşik nokta) olarak kayıtlı; yönlendirmede iki yazım da tanımlanmalı.

### Arama motoru dosyaları

`python build.py` artık `site/sitemap.xml`, `site/robots.txt` ve `site/404.html` üretiyor. Site haritasında `noindex` sayfalar (KVKK) yok. Önizleme betiği (`kaynak/onizleme.py`) önizlemede robots.txt'yi `Disallow: /` ile değiştirir ve site haritasını siler; yani bu üç dosya yalnızca gerçek yayında geçerlidir. 404 sayfası köke bağlı çalışır: Wix özel 404 sayfasını ayrıca ister, oraya aynı metin elle konabilir.
