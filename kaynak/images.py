"""Orijinal görselleri kırpar, optimize eder ve site/img altına AVIF + WebP olarak yazar.

Kullanım:  python kaynak/images.py
Orijinaller kaynak/orijinal/ altında durur (Wix'ten indirildi). Çıktı listesi
site/img/manifest.json dosyasına yazılır; build.py bu listeyi <picture> etiketleri için okur.
"""
import json
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

try:  # iPhone fotoğrafları (HEIC) için
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "kaynak" / "orijinal"
OUT = ROOT / "kaynak" / "img-cache"  # tüm boyutlar burada; build.py sayfalarda geçenleri site/img/e kopyalar

def left_lift(im, span=0.32, strength=1.4):
    """Soldan karartması gömülü fotoğraflarda sol kenardaki kişileri açar: gölgeleri yükseltir, sağa doğru söner."""
    w, h = im.size
    out = im.copy()
    n = int(w * span)
    for x in range(n):
        g = 1 / (1 + strength * (1 - x / n) ** 1.2)
        lut = [round(255 * ((i / 255) ** g)) for i in range(256)] * 3
        out.paste(im.crop((x, 0, x + 1, h)).point(lut), (x, 0))
    return out


def ekip_sol_aydinlat():
    """Orijinaller yerelde yok; ekip fotoğrafının önbellekteki boyutlarına sol aydınlatmayı bir kez uygular.
    (Orijinalden yeniden üretirsen önce main() sonrası left_lift'i 'ekip' için çağır.) Tekrar çalıştırmayı manifest'teki işaret engeller."""
    mf = OUT / "manifest.json"
    manifest = json.loads(mf.read_text(encoding="utf-8"))
    if manifest["ekip"].get("left_lift"):
        print("ekip zaten aydınlatılmış, atlandı")
        return
    for x in manifest["ekip"]["widths"]:
        im = left_lift(Image.open(OUT / f"ekip-{x}.webp").convert("RGB"))
        im.save(OUT / f"ekip-{x}.webp", quality=80, method=6)
        try:
            im.save(OUT / f"ekip-{x}.avif", quality=58)
        except Exception as e:  # AVIF yazıcısı yoksa site yalnızca WebP kullandığı için sorun değil
            print("avif yazılamadı:", e)
    manifest["ekip"]["left_lift"] = True
    mf.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print("ekip sol kenarı aydınlatıldı")


# ad: (kaynak dosya, kırpma (sol, üst, sağ, alt) oran olarak, parlaklık, genişlikler)
# Eski Wix ana sayfa görsellerinde soldan karartma gömülü; o yüzden sağ taraf kırpılıp hafifçe açılıyor.
SPECS = {
    "ekip":   ("f32975_393b0948fa8e435e8403f376adfe308d_mv2.jpg", (0.13, 0, 1, 1), 1.50, [800, 1400]),
    "fest26": ("f32975_e55fb11157cb479a933edcf2b2ad7955_mv2.png", (0.48, 0, 1, 1), 1.00, [600, 1000]),
    # Lawment Insights 1. sayı kapağı (1358×1929, dernekten)
    "insights-kapak": ("insights-kapak.webp", None, 1.00, [400, 700, 1000]),
}
# Etkinlik fotoğrafları Drive seçimlerinden gelir (kaynak/drive2, kaynak/fotolar.py): drive_specs()


def drive_specs():
    """Drive seçimlerini (kaynak/drive2) SPECS biçimine çevirir; hero adaylarına daha büyük boyutlar."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -P betik klasörünü eklemiyor
    from fotolar import picks
    specs = {}
    for items in picks().values():
        for it in items:
            widths = [800, 1400] if it["hero"] else [480, 960]  # galeriler en fazla ~600px gösteriliyor; 960 retina için yeter
            specs[it["name"]] = (f"../drive2/{it['file']}", None, 1.00, widths)
    return specs


def dergi_specs():
    """Lawment Insights sayfaları: kaynak/dergi/ içindeki görseller, ada göre sıralı → dergi-00, dergi-01, ..."""
    folder = ROOT / "kaynak" / "dergi"
    files = sorted(p for p in folder.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")) if folder.exists() else []
    return {f"dergi-{i:02d}": (f"../dergi/{p.name}", None, 1.00, [400, 760]) for i, p in enumerate(files)}


def load(name):
    im = ImageOps.exif_transpose(Image.open(SRC / name))
    return im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")


def main(only=None):
    """only: yalnızca bu adları üretir (ham fotoğrafların hepsi yerelde olmadığında: --only backin-07,backin-08)."""
    OUT.mkdir(parents=True, exist_ok=True)
    specs = {**SPECS, **drive_specs(), **dergi_specs()}
    old = json.loads((OUT / "manifest.json").read_text(encoding="utf-8")) if (OUT / "manifest.json").exists() else {}
    manifest = dict(old) if only else {}
    if only:
        specs = {k: v for k, v in specs.items() if k in only}
    for key, (fname, crop, lift, widths) in specs.items():
        # daha önce üretildiyse ve kaynak değişmediyse atla
        src = SRC / fname
        prev = old.get(key)
        if prev and all((OUT / f"{key}-{x}.{e}").exists() and (OUT / f"{key}-{x}.{e}").stat().st_mtime >= src.stat().st_mtime
                        for x in prev["widths"] for e in ("avif", "webp")) and prev.get("spec") == [str(crop), lift, widths]:
            manifest[key] = prev
            continue
        im = load(fname)
        if crop:
            w, h = im.size
            im = im.crop((round(crop[0] * w), round(crop[1] * h), round(crop[2] * w), round(crop[3] * h)))
        if lift != 1:
            im = ImageEnhance.Brightness(im).enhance(lift)
            im = ImageEnhance.Contrast(im).enhance(1.08)
            im = ImageEnhance.Color(im).enhance(1.12)
        alpha = im.mode == "RGBA"
        widths = sorted(set(min(x, im.width) for x in widths))
        for x in widths:
            r = im.resize((x, round(im.height * x / im.width)), Image.LANCZOS)
            r.save(OUT / f"{key}-{x}.avif", quality=58 if not alpha else 70)
            r.save(OUT / f"{key}-{x}.webp", quality=80, method=6)
        manifest[key] = {"w": im.width, "h": im.height, "widths": widths, "alpha": alpha, "spec": [str(crop), lift, specs[key][3]]}
        print(key, im.size, widths)

    if only:  # logo, paylaşım görseli ve favicon'a dokunma
        (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
        return

    # logo: beyaz yazı + şeffaf zemin. Sitede CSS mask olarak kullanılıyor, böylece her temada metin rengini alıyor.
    logo = load("f32975_6cdc64b2e3fb4f9dbd6774d2008e933d_mv2.png")
    logo.save(OUT / "logo.png", optimize=True)
    logo.save(OUT / "logo.webp", lossless=True)
    manifest["logo"] = {"w": logo.width, "h": logo.height}

    # paylaşım görseli ve favicon: bordo daire amblem
    mark = load("292279_290bccdf448144a099825018f9ce46f5_mv2.png")
    og = Image.new("RGB", (1200, 630), (241, 242, 238))
    m = mark.resize((440, 440), Image.LANCZOS)
    og.paste(m, (380, 95), m)
    og.save(OUT / "og.jpg", quality=86)
    mark.resize((180, 180), Image.LANCZOS).save(OUT / "apple-touch-icon.png", optimize=True)
    mark.resize((48, 48), Image.LANCZOS).save(OUT / "favicon.png", optimize=True)

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")


if __name__ == "__main__":
    import sys
    if "--ekip-sol" in sys.argv:
        ekip_sol_aydinlat()
    elif "--only" in sys.argv:
        main(only=set(sys.argv[sys.argv.index("--only") + 1].split(",")))
    else:
        main()
