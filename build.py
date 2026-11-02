"""Lawment sitesi derleyicisi.

src/pages/*.html dosyalarını ortak <head>, header ve footer ile birleştirip site/ klasörüne yazar,
src/assets/ klasörünü site/assets/ altına kopyalar.

Kullanım:  python build.py

Sayfa dosyalarının başında kısa bir başlık bloğu bulunur:
    ---
    title: Biz Kimiz
    description: ...
    nav: biz-kimiz
    ---
Sayfa gövdesinde kullanılabilen kısayollar:
    <x-img name="hero-fest" alt="..." sizes="..." class="..." eager>   -> <picture> (AVIF + WebP, srcset)
    <h1 data-split>...</h1>                                            -> kelime kelime yükselen başlık
    <x-marquee class="...">A|B|C</x-marquee>                           -> kayan şerit
    ' →</a>'                                                            -> kayan ok
"""
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "site"
SITE_URL = "https://www.lawment.org/"

NAV = [
    ("home", "index.html", "Ana Sayfa"),
    ("biz-kimiz", "biz-kimiz.html", "Biz Kimiz"),
    ("projeler", "projeler.html", "Projeler"),
    ("arsiv", "arsiv.html", "Arşiv"),
    ("kurumlar", "sponsorluk.html", "Kurumlar İçin"),
    ("iletisim", "iletisim.html", "Destek &amp; İletişim"),
]

CACHE = ROOT / "kaynak" / "img-cache"  # kaynak/images.py çıktısı (tüm boyutlar)
MANIFEST = json.loads((CACHE / "manifest.json").read_text(encoding="utf-8"))

# Fontlar siteye gömülü (kaynak/fonts.py). Tek aile (Archivo) önceden yüklenir: büyük başlık sayfanın LCP'si
# ve geç gelirse yeniden dizilip kaymaya yol açıyor. Latin-ext alt kümesi önceden yüklenmez; Türkçe karakter olunca iner.
FONT_PRELOADS = "\n".join(
    f'<link rel="preload" href="fonts/{f.name}" as="font" type="font/woff2" crossorigin>'
    for f in sorted((OUT / "fonts").glob("*.woff2"))
    if f.name.startswith("archivo-normal-")
)


def head(meta, filename):
    title = meta["title"]
    full = "Lawment Derneği" if title == "Lawment Derneği" else f"{title} · Lawment Derneği"
    desc = html.escape(meta["description"], quote=True)
    url = SITE_URL + ("" if filename == "index.html" else filename)
    robots = '\n<meta name="robots" content="noindex">' if meta.get("noindex") else ""
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{full}</title>
<meta name="description" content="{desc}">{robots}
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="tr_TR">
<meta property="og:site_name" content="Lawment Derneği">
<meta property="og:title" content="{full}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}img/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F6F5F3">
<link rel="icon" type="image/png" href="img/favicon.png">
<link rel="apple-touch-icon" href="img/apple-touch-icon.png">
{FONT_PRELOADS}
<link rel="stylesheet" href="assets/style.css">
<script>
/* Kaydırma animasyonları yalnızca JS gerçekten çalışırsa devreye girer; main.js 2,5 sn içinde gelmezse içerik düz gösterilir. */
(function (d) {{
  /* ziyaretçinin seçtiği tema (açık/koyu) ilk boyamadan önce uygulanır */
  try {{ var t = localStorage.getItem('lm-theme'); if (t) d.setAttribute('data-theme', t); }} catch (e) {{}}
  if (matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;
  d.classList.add('anim');
  setTimeout(function () {{ if (!window.LM_READY) d.classList.remove('anim'); }}, 2500);
}})(document.documentElement);
</script>
<script src="assets/main.js" defer></script>
</head>
<body>
"""


BRAND = '<span class="logo" role="img" aria-label="Lawment"></span><span class="brand-sub">Derneği</span>'


def header(active):
    links = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if key == active else ""}>{label}</a>'
        for key, href, label in NAV
    )
    katil = ' aria-current="page"' if active == "katil" else ""
    return f"""<a class="skip" href="#icerik">İçeriğe geç</a>
<div class="read-progress" aria-hidden="true"></div>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="Lawment Derneği ana sayfa">{BRAND}</a>
    <button class="theme-toggle" type="button" aria-label="Koyu temaya geç" data-theme-toggle><span aria-hidden="true"></span></button>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav"><span class="nav-toggle-bars" aria-hidden="true"></span><span class="nav-toggle-text">Menü</span></button>
    <nav class="nav" id="site-nav" aria-label="Ana menü">
      {links}
      <a class="btn btn--primary btn--sm" href="katil.html"{katil}>Katıl</a>
    </nav>
  </div>
</header>
<main id="icerik">
"""


FOOTER = f"""</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-about">
        <a class="brand" href="index.html" aria-label="Lawment Derneği ana sayfa">{BRAND}</a>
        <p class="muted measure">Öğrencileri, genç hukukçuları ve sektörün öncü isimlerini aynı masada buluşturan bağımsız hukuk derneği. İzmir'den Türkiye'ye.</p>
        <p class="kunye">Dernek kütük no 35-085-124<br>Koşukavak Mah. 4169/2 Sk. No:5, Atatürk Kültür Merkezi, 35080 Bornova/İzmir<br>Yönetim Kurulu Başkanı: Av. Kerimcan Demir</p>
      </div>
      <div>
        <p class="label">Site</p>
        <a href="biz-kimiz.html">Biz Kimiz</a>
        <a href="projeler.html">Projeler</a>
        <a href="arsiv.html">Arşiv</a>
        <a href="katil.html">Katıl</a>
        <a href="sponsorluk.html">Kurumlar İçin</a>
        <a href="iletisim.html">Destek &amp; İletişim</a>
      </div>
      <div>
        <p class="label">Bize ulaş</p>
        <a href="mailto:info@lawment.org">info@lawment.org</a>
        <a href="https://instagram.com/lawment.der/" target="_blank" rel="noopener">Instagram · @lawment.der</a>
        <a href="https://tr.linkedin.com/company/lawment" target="_blank" rel="noopener">LinkedIn · Lawment</a>
        <a href="iletisim.html#destek">Bağış yap</a>
      </div>
    </div>
    <div class="foot-bottom">
      <span>© <span data-year>2026</span> Lawment Derneği</span>
      <a href="kvkk.html">KVKK Aydınlatma Metni ve Gizlilik</a>
    </div>
  </div>
</footer>
</body>
</html>
"""


# ---------- gövde kısayolları ----------

def attrs(s):
    out = {}
    for m in re.finditer(r'([\w-]+)(?:="([^"]*)")?', s):
        out[m.group(1)] = m.group(2) if m.group(2) is not None else True
    return out


def picture(m):
    a = attrs(m.group(1))
    info = MANIFEST[a["name"]]
    name = a["name"]
    sizes = a.get("sizes", "100vw")
    widths = info["widths"]
    srcset = lambda ext: ", ".join(f"img/{name}-{w}.{ext} {w}w" for w in widths)
    fallback = f"img/{name}-{widths[-1]}.webp"
    eager = a.get("eager")
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    cls = f' class="{a["class"]}"' if "class" in a else ""
    # yalnızca WebP: Wix'in sunucusu AVIF'i application/octet-stream olarak gönderiyor, Safari bunu göstermeyebilir
    return (
        f'<picture{cls}><source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
        f'<img src="{fallback}" alt="{a["alt"]}" width="{info["w"]}" height="{info["h"]}" {load}></picture>'
    )


def split_heading(m):
    rest, inner = (m.group(1) + m.group(2)).strip(), m.group(3)
    tokens = re.findall(r'<span class="hl">.*?</span>|\S+', inner)
    words = " ".join(f'<span class="w" style="--i:{i}"><span>{t}</span></span>' for i, t in enumerate(tokens))
    # ekran okuyucular başlığı tek parça okusun diye düz metin aria-label olarak eklenir
    plain = re.sub(r"<[^>]+>", "", inner).strip()
    return f'<h1 class="split-h" style="--n:{len(tokens)}" aria-label="{plain}"{(" " + rest) if rest else ""}><span aria-hidden="true">{words}</span></h1>'


def marquee(m):
    return marquee_html(m.group(1), [i.strip() for i in m.group(2).split("|") if i.strip()])


def marquee_html(attr_str, items):
    a = attrs(attr_str)
    track = "".join(f'<li>{i}</li><li class="mq-star" aria-hidden="true">✦</li>' for i in items)
    cls = "marquee " + a.get("class", "")
    label = a.get("label", "")
    lab = f' aria-label="{label}"' if label else ""
    return (
        f'<div class="{cls.strip()}"{lab}><div class="mq-track">'
        f'<ul class="mq-list">{track}</ul><ul class="mq-list" aria-hidden="true">{track}</ul>'
        f'<ul class="mq-list" aria-hidden="true">{track}</ul></div></div>'
    )


# Etkinliklerimizde yer alan kurumlar. site/img/kurumlar/<kısa-ad>.svg (ya da .png/.webp, şeffaf zeminli)
# eklendiğinde şeritte yazı yerine logo gösterilir; logo tek renge boyanır, böylece iki temada da okunur.
ORGS = [
    ("actecon", "ACTECON"), ("arkas", "Arkas"), ("baker-mckenzie", "Baker McKenzie"), ("congar-law", "Congar Law"), ("edac", "EDAC"),
    ("ge-healthcare", "GE Healthcare"), ("kale-group", "Kale Group"), ("maersk", "Maersk"), ("msc", "MSC"),
    ("qnb-finansbank", "QNB Finansbank"), ("socar", "SOCAR"),
]


def org_logo(slug):
    for ext in ("svg", "webp", "png"):
        if (OUT / "img" / "kurumlar" / f"{slug}.{ext}").exists():
            return f"img/kurumlar/{slug}.{ext}"
    return None


def orgs_marquee(_m):
    items = []
    for slug, name in ORGS:
        logo = org_logo(slug)
        if logo:
            # mask doğrudan satır içi yazılır: CSS değişkeni içindeki url() stil dosyasına göre çözülür ve kırılır
            items.append(f'<span class="org-logo" style="-webkit-mask-image:url({logo});mask-image:url({logo})" role="img" aria-label="{name}"></span>')
        else:
            items.append(name)
    return marquee_html('class="marquee--orgs" label="Etkinliklerimizde yer alan kurumlar"', items)


# ---------- ekip (Lawment Üyeler.xlsx + yönetimden gelen düzeltmeler) ----------
# rol: "ykb" (Yönetim Kurulu Başkanı) | "yk" | "yrb" (Yürütme Kurulu Başkanı) | "yr" | "uye".
# Bir kişi birden çok departmanda olabilir: dept=("kurumsal", "yasal-finans"); ilki avatar rengini belirler.
# Fotoğraf eklemek için kişinin satırına foto="img/ekip/dosya.webp" yazılır.
DEPTS = [
    ("kurumsal", "Kurumsal İlişkiler"),
    ("uye-gelisim", "Üye Gelişim"),
    ("proje", "Proje ve İnovasyon"),
    ("dijital", "Dijital İletişim"),
    ("yasal-finans", "Yasal ve Finans"),
]
TEAM = [
    # Yönetim Kurulu
    dict(ad="Av. Kerimcan Demir", rol="ykb", dept=("dijital",)),
    dict(ad="Av. İrem Türkoğlu", rol="yk", dept=("kurumsal",)),
    dict(ad="Av. Ömer Faruk Kılıç", rol="yk", dept=("kurumsal",)),
    dict(ad="Av. Zeynep Sude Akıllı", rol="yk", dept=("proje",)),
    dict(ad="Av. Ezgi Çamca", rol="yk", dept=("yasal-finans",)),
    dict(ad="Dilan Beğtaş", rol="yk", dept=("uye-gelisim",)),
    # Yürütme Kurulu
    dict(ad="Özlem Sultan Hatip", rol="yrb", dept=("kurumsal", "yasal-finans")),
    dict(ad="Eylem Türk", rol="yr", dept=("uye-gelisim",)),
    dict(ad="Eslem Yağmur Atmaca", rol="yr", dept=("kurumsal",)),
    dict(ad="Betül Nas Üner", rol="yr", dept=("kurumsal",)),
    dict(ad="Tayfun Koçoğlu", rol="yr", dept=("dijital",)),
    dict(ad="Efe Kutay Alaçiçek", rol="yr", dept=("proje",)),
    dict(ad="Abdullah Emin Şimşek", rol="yr", dept=("proje",)),
] + [dict(ad=n, rol="uye", dept=("uye-gelisim",)) for n in (
    "Sıla Uluç", "Hüsna Çökmez", "Ayşenur Güler", "İrem Büşra Güner", "Asel Nehir Pakşı", "Bengisu Bedir")
] + [dict(ad=n, rol="uye", dept=("kurumsal",)) for n in (
    "Firdevs Nur Sürer", "Cansu Bağ", "Cemre Örer", "Selim Zunluoğlu", "Berfin Nur Tunç", "Nur Karakoç",
    "Yağmur Karakuş", "Gizem Öztürk", "Hande Öztürk")
] + [dict(ad=n, rol="uye", dept=("dijital",)) for n in (
    "Beyza Selen Çiçek", "Tuğçenur Çiçek", "Zeynep Düzmen", "Özgecan Esen", "Nilay Çabuk", "Can Ahmet Özgüven")
] + [dict(ad=n, rol="uye", dept=("proje",)) for n in (
    "Hatice Zehre Kışla", "Mehmet Kılıç", "Ayşe Naz Özen", "Betül Doğan", "İrem Gündoğdu", "Reşat Karamanlıoğlu",
    "Kübra Yıldırım", "Derya Nur Kılıç")
]
ROLE_LABEL = {
    "ykb": "Yönetim Kurulu Başkanı", "yk": "Yönetim Kurulu Üyesi",
    "yrb": "Yürütme Kurulu Başkanı", "yr": "Yürütme Kurulu Üyesi", "uye": "Departman Üyesi",
}
ROLE_GROUP = {"ykb": "yonetim", "yk": "yonetim", "yrb": "yurutme", "yr": "yurutme", "uye": "uye"}


def initials(name):
    parts = [p for p in name.split() if not p.endswith(".")]  # "Av." unvanını atla
    return parts[0][0] + parts[-1][0]


def team_count(dept=None, role=None):
    return sum(1 for m in TEAM
               if (dept is None or dept in m["dept"]) and (role is None or ROLE_GROUP[m["rol"]] == role))


def avatar(m):
    inner = f'<img src="{m["foto"]}" alt="" loading="lazy">' if m.get("foto") else initials(m["ad"])
    return f'<span class="avatar avatar--{m["dept"][0]}" aria-hidden="true">{inner}</span>'


def board_html(m):
    role = re.match(r"<x-board role=\"(\w+)\"></x-board>", m.group(0)).group(1)
    dept_name = dict(DEPTS)
    cards = []
    for p in TEAM:
        if ROLE_GROUP[p["rol"]] != role:
            continue
        lead = " leader--chair" if p["rol"] in ("ykb", "yrb") else ""
        depts = " · ".join(dept_name[d] for d in p["dept"])
        cards.append(
            f'<li class="leader{lead}">{avatar(p)}'
            f'<span class="leader-role">{ROLE_LABEL[p["rol"]]}</span>'
            f'<span class="leader-name">{p["ad"]}</span>'
            f'<span class="leader-dept">{depts}</span></li>'
        )
    return f'<ul class="leaders leaders--{role}">{"".join(cards)}</ul>'


def team_html(_m):
    """Departman üyeleri: departmana göre filtrelenen sade kartlar (kurullar ayrıca board_html ile gösterilir)."""
    dept_name = dict(DEPTS)
    members = [p for p in TEAM if p["rol"] == "uye"]
    chips = [("hepsi", "Hepsi")] + DEPTS
    filt = "".join(
        f'<button type="button" class="chip" data-filter="{k}" aria-pressed="{"true" if k == "hepsi" else "false"}">{label}</button>'
        for k, label in chips
    )
    cards = [
        f'<li class="member" data-dept="{" ".join(p["dept"])}">{avatar(p)}'
        f'<span class="member-name">{p["ad"]}</span>'
        f'<span class="member-dept">{" · ".join(dept_name[d] for d in p["dept"])}</span></li>'
        for p in members
    ]
    # departman üyesi olmayan departmanlar için kimin yürüttüğünü gösteren not kartı
    for key, name in DEPTS:
        if not any(key in p["dept"] for p in members):
            leads = ", ".join(p["ad"] for p in TEAM if key in p["dept"])
            cards.append(
                f'<li class="member member--note" data-dept="{key}" hidden>'
                f'<span class="member-name">{name}</span>'
                f'<span class="member-dept">Bu departmanı kurul üyelerimiz yürütüyor: {leads}.</span></li>'
            )
    return (
        f'<div class="team-filters" role="group" aria-label="Departman üyelerini filtrele">{filt}</div>'
        f'<p class="sr-only" data-team-status aria-live="polite"></p>'
        f'<ul class="team-grid" data-team>{"".join(cards)}</ul>'
    )


# ---------- etkinlik fotoğrafları (kaynak/drive2, seçim listesi kaynak/fotolar.py) ----------
import sys
sys.path.insert(0, str(ROOT / "kaynak"))
from fotolar import picks as _drive_picks  # noqa: E402

PHOTOS = _drive_picks()


def photos_html(m):
    """<x-photos set="fest25" start="1" count="5" class="t-photos" sizes="..."> → fotoğraf listesi.
    Fotoğraflar puan sırasıyla gelir; start/count ile aynı etkinliğin farklı kareleri farklı yerlerde kullanılır."""
    a = attrs(m.group(1))
    items = PHOTOS.get(a["set"], [])
    start = int(a.get("start", 1)) - 1
    items = items[start:start + int(a.get("count", len(items)))]
    if "kind" in a:
        items = [it for it in PHOTOS.get(a["set"], []) if it["kind"] == a["kind"]][: int(a.get("count", 99))]
    sizes = a.get("sizes", "(max-width: 760px) 80vw, 30vw")
    lis = "".join(
        f'<li class="zoom"><div class="media" data-reveal="clip"><x-img name="{it["name"]}" alt="{html.escape(it["alt"], quote=True)}" sizes="{sizes}"></div></li>'
        for it in items
    )
    return f'<ul class="{a.get("class", "t-photos")}">{lis}</ul>'


# ---------- Lawment Insights: sayfa çevirmeli dergi ----------
# Sayfalar kaynak/dergi/ klasöründen (ada göre sıralı) gelir; images.py onları dergi-00, dergi-01... yapar.
DERGI_ALT = [
    "Kapak: Lawment Insights, Sayı 1, 10.02.2026; sepya tonlu adalet heykeli",
    "İçindekiler: Hakkımızda 2, Comparena 3, Lawment Fest 6, Back in Lawment 11",
    "Sayfa 2: Hakkımızda; Lawment Derneği'nin tanıtımı ve dergi ekibi",
    "Sayfa 3: Comparena, rekabet hukukunda teori ile pratiğin kesişim noktası",
    "Sayfa 4: Comparena'yı katılımcıların ve jürinin gözünden anlatan söyleşi",
    "Sayfa 5: Jüri üyelerine sorduk; Comparena'nın bir Lawment geleneğine dönüşmesi",
    "Sayfa 6: Lawment Fest, genç hukukçular için bir kariyer festivali; paneller",
    "Sayfa 7: Lawment Fest'25 panelleri devam ediyor",
    "Sayfa 8: Dava avukatlığı paneli ve sosyal aktiviteler",
    "Sayfa 9: Sponsorlarımıza ve konuşmacılarımıza sorduk",
    "Sayfa 10: Lawment Fest'i diğer etkinliklerden ayıran şey",
    "Sayfa 11: Back in Lawment, yeni döneme merhaba",
]


def flipbook_html(_m):
    pages = sorted(k for k in MANIFEST if k.startswith("dergi-")) or ["insights-kapak"]
    alt = lambda i: DERGI_ALT[i] if i < len(DERGI_ALT) else f"Sayfa {i}"
    sizes = "(max-width: 760px) 46vw, 380px"
    leaves = []
    for i in range(0, len(pages), 2):
        front = f'<div class="fb-face fb-front"><x-img name="{pages[i]}" alt="" sizes="{sizes}"></div>'
        back = (f'<div class="fb-face fb-back"><x-img name="{pages[i + 1]}" alt="" sizes="{sizes}"></div>'
                if i + 1 < len(pages) else '<div class="fb-face fb-back fb-blank"></div>')
        leaves.append(f'<div class="fb-leaf" data-leaf>{front}{back}</div>')
    items = "".join(
        f'<li><div class="media"><x-img name="{p}" alt="{html.escape(alt(i), quote=True)}" sizes="(max-width: 760px) 70vw, 260px"></div></li>'
        for i, p in enumerate(pages)
    )
    return (
        f'<div class="fb-book" aria-hidden="true"><div class="fb-cover-back"><b>Lawment Insights</b><span>Sayı 1 · Şubat 2026</span></div>{"".join(leaves)}</div>'
        f'<div class="fb-controls"><button type="button" class="btn btn--sm" data-fb-prev aria-label="Önceki sayfa">←</button>'
        f'<span class="fb-count" data-fb-count aria-live="polite">Kapak</span>'
        f'<button type="button" class="btn btn--sm" data-fb-next aria-label="Sonraki sayfa">→</button></div>'
        f'<ol class="fb-list" aria-label="Lawment Insights sayfaları">{items}</ol>'
    )


def lit_html(m):
    """<p class="lit" data-lit>metin</p> → her kelime ayrı span: kaydırdıkça sırayla aydınlanır (main.js)."""
    words = m.group(2).split()
    return f'<p{m.group(1)}>' + " ".join(f'<span class="lw">{w}</span>' for w in words) + "</p>"


def render_body(body):
    body = re.sub(r'<p( class="lit" data-lit)>(.*?)</p>', lit_html, body, flags=re.S)
    if not any(k.startswith("dergi-") for k in MANIFEST):
        # dergi sayfaları henüz yok (kaynak/dergi boş): çevirmeli bölümü ve ona giden bağlantıları gizle
        body = re.sub(r'\n*<section class="fb" id="dergi-oku".*?</section>', "", body, flags=re.S)
        body = body.replace('\n    <a href="#dergi-oku">Dergiyi çevir</a>', "")
        body = body.replace('<a class="btn btn--primary" href="#dergi-oku">Dergiyi çevir ↓</a><a class="btn" href="https://lnkd.in/p/dt2QCk_9" target="_blank" rel="noopener">LinkedIn\'de oku →</a>',
                            '<a class="btn btn--primary" href="https://lnkd.in/p/dt2QCk_9" target="_blank" rel="noopener">İlk sayıyı oku →</a>')
    body = body.replace("<x-flipbook></x-flipbook>", flipbook_html(None))
    body = re.sub(r"<x-photos\s+([^>]*)>", photos_html, body)
    body = body.replace("<x-orgs></x-orgs>", orgs_marquee(None))
    body = body.replace("<x-team></x-team>", team_html(None))
    body = re.sub(r"<x-board role=\"\w+\"></x-board>", board_html, body)
    body = re.sub(r"<x-count dept=\"([\w-]*)\"></x-count>", lambda m: str(team_count(dept=m.group(1) or None)), body)
    body = re.sub(r"<x-count role=\"(\w+)\"></x-count>", lambda m: str(team_count(role=m.group(1))), body)
    body = re.sub(r"<x-img\s+([^>]*)>", picture, body)
    body = re.sub(r"<h1([^>]*?)\sdata-split([^>]*)>(.*?)</h1>", split_heading, body, flags=re.S)
    body = re.sub(r"<x-marquee\s*([^>]*)>(.*?)</x-marquee>", marquee, body, flags=re.S)
    body = body.replace(" →</a>", ' <span class="arr" aria-hidden="true">→</span></a>')
    return body


EN_NAMES = ("Lawment Insights", "Lawment Inspired", "Back in Lawment", "Insights", "Inspired", "Equilibrium")


def mark_english(html_text):
    """İngilizce adlar lang="en" alır: sayfa dili Türkçe olduğundan büyük harfe çevrilince
    "Insights" → "INSİGHTS" olmasın. Yalnızca metin düğümlerine dokunur, etiket ve özniteliklere değil."""
    pat = re.compile("|".join(re.escape(n) for n in EN_NAMES))
    parts = re.split(r"(<[^>]+>)", html_text)
    return "".join(p if p.startswith("<") else pat.sub(lambda m: f'<span lang="en">{m.group(0)}</span>', p) for p in parts)


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines() if ": " in line)
    return meta, text[m.end():]


def main():
    if (OUT / "assets").exists():
        shutil.rmtree(OUT / "assets")
    shutil.copytree(SRC / "assets", OUT / "assets", ignore=shutil.ignore_patterns("fonts.css"))
    # @font-face tanımları ayrı bir istek olmasın diye style.css'in başına eklenir
    css = (SRC / "assets" / "fonts.css").read_text(encoding="utf-8") + (SRC / "assets" / "style.css").read_text(encoding="utf-8")
    (OUT / "assets" / "style.css").write_text(css, encoding="utf-8", newline="\n")
    for page in sorted((SRC / "pages").glob("*.html")):
        meta, body = parse(page)
        out = head(meta, page.name) + mark_english(header(meta.get("nav", "")) + render_body(body) + FOOTER)
        (OUT / page.name).write_text(out, encoding="utf-8", newline="\n")
        print("yazıldı:", page.name)
    sync_images()


def sync_images():
    """Önbellekteki görsellerden (kaynak/img-cache) yalnızca sayfalarda ve CSS'te geçenleri site/img/e kopyalar,
    geçmeyenleri site/img/den siler. Böylece Wix'e yalnızca kullanılan dosyalar gider (site boyutu sınırı)."""
    refs = "".join(p.read_text(encoding="utf-8") for p in OUT.glob("*.html"))
    refs += (OUT / "assets" / "style.css").read_text(encoding="utf-8")
    dst = OUT / "img"
    dst.mkdir(exist_ok=True)
    copied = removed = 0
    for f in CACHE.glob("*.*"):
        if f.name == "manifest.json" or f"img/{f.name}" not in refs:
            continue
        t = dst / f.name
        if not t.exists() or t.stat().st_mtime < f.stat().st_mtime:
            shutil.copy2(f, t)
            copied += 1
    for f in dst.glob("*.*"):
        if f"img/{f.name}" not in refs:
            f.unlink()
            removed += 1
    print(f"görseller: {copied} kopyalandı, {removed} silindi")


if __name__ == "__main__":
    main()
