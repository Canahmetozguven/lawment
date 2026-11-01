# lawment

Lawment Derneği'nin (İzmir) web sitesi. Kütüphanesiz, statik HTML/CSS/JS; Wix'e statik site olarak yüklenir.

## Derleme

```
python build.py                                   # src/ -> site/
python -m http.server 8080 --directory site      # http://127.0.0.1:8080
node kaynak/kontrol.mjs                           # taşma, bağlantı, konsol, tema ve reduced-motion kontrolleri
```

`kontrol.mjs` için önce `kaynak/` içinde `npm install` çalıştırılır.

## Önizleme (GitHub Pages)

```
python kaynak/onizleme.py                         # derler ve gh-pages dalına gönderir
```

Adres: https://canahmetozguven.github.io/lawment/ (yaklaşık bir dakikada güncellenir). Her sayfada `noindex` ve kökte `robots.txt` vardır; arama motorlarından gizlidir ama adresi bilen herkes açabilir. `gh-pages` dalı her seferinde sıfırdan yazılır, `main` değişmez. Depo ayarlarında Pages kaynağı "gh-pages dalı, / (kök)" olmalıdır. Gerçek yayın bu değil, Wix'e yükleme ([TESLIM.md](TESLIM.md)).

## Klasörler

| Klasör | İçerik |
|---|---|
| `src/pages/` | Sayfa metinleri |
| `src/assets/` | `style.css`, `main.js`, fontlar |
| `build.py` | Header, footer, menü, ekip ve kurum listeleri, dergi |
| `kaynak/` | Görsel, logo ve font hazırlama betikleri; işlenmiş görseller `kaynak/img-cache/` |
| `site/` | Derleme çıktısı (depoda yok, `build.py` üretir) |

Ham Drive fotoğrafları depoda yok (`.gitignore`); işlenmiş hâlleri `kaynak/img-cache/` içinde, bu yüzden site depodan derlenebilir.

Yer tutucular, teyit edilecek bilgiler ve Wix'e yükleme adımları: [TESLIM.md](TESLIM.md).
