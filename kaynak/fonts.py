"""Google Fonts'u siteye gömer (self-host): EB Garamond (başlıklar; dik ve italik, ağırlık 400–700) ve
DM Sans (metin; ağırlık 400–700).

Yalnızca latin ve latin-ext alt kümeleri alınır (Türkçe karakterler latin-ext'te).
Çıktı: site/fonts/*.woff2 ve src/assets/fonts.css. build.py fonts.css'i style.css'in başına ekler.
Fontların hepsi SIL Open Font License ile dağıtılıyor; siteye gömülmeleri serbest.
Çalıştırmadan önce site/fonts/ içindeki eski (artık kullanılmayan) .woff2 dosyalarını silin.

Kullanım: python kaynak/fonts.py
"""
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS_URL = ("https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400..700;1,400..700"
           "&family=DM+Sans:wght@400..700&display=swap")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()


def main():
    css = get(CSS_URL).decode("utf-8")
    out_dir = ROOT / "site" / "fonts"
    out_dir.mkdir(parents=True, exist_ok=True)
    blocks = re.findall(r"/\* ([\w-]+) \*/\s*(@font-face\s*\{.*?\})", css, re.S)
    kept, files = [], {}
    for subset, block in blocks:
        if subset not in ("latin", "latin-ext"):
            continue
        fam = re.search(r"font-family: '([^']+)'", block).group(1)
        style = re.search(r"font-style: (\w+)", block).group(1)
        url = re.search(r"url\((https://[^)]+\.woff2)\)", block).group(1)
        # değişken fontlarda aynı dosya birden çok ağırlık için tekrar eder; bir kez indirilir
        if url not in files:
            name = f"{fam.lower().replace(' ', '-')}-{style}-{subset}-{len(files)}.woff2"
            (out_dir / name).write_bytes(get(url))
            files[url] = name
        kept.append(f"/* {fam} {style} {subset} */\n" + block.replace(url, f"../fonts/{files[url]}"))
    (ROOT / "src" / "assets" / "fonts.css").write_text(
        "/* kaynak/fonts.py tarafından üretildi; elle düzenleme */\n" + "\n".join(kept) + "\n", encoding="utf-8")
    for n in sorted(set(files.values())):
        print(n, (out_dir / n).stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
