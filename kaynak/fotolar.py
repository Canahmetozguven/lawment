"""Drive'dan seçilen etkinlik fotoğraflarının ortak listesi.

kaynak/drive2/secim-*.json dosyalarını okur; her etkinlik etiketi (fest25, fest26, lawfest24, comparena, backin)
için fotoğrafları puana göre sıralar ve sitedeki adlarını verir: "<etiket>-01", "<etiket>-02"...
images.py bu adlarla görselleri üretir, build.py da <x-photos> etiketiyle sayfalara yerleştirir.
"""
import json
from pathlib import Path

DRIVE = Path(__file__).resolve().parent / "drive2"


def picks():
    """{etiket: [{name, file, alt, orientation, kind, desc, focus, year?}, ...]} — puanı yüksek olan önce."""
    out, hero = {}, []
    for f in sorted(DRIVE.glob("secim-*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        for tag, items in data.items():
            if tag == "hero":
                hero.extend(items)
                continue
            out.setdefault(tag, []).extend(items)
    for tag, items in out.items():
        items.sort(key=lambda x: (-float(x.get("score", 0)), x["file"]))
        for i, it in enumerate(items, 1):
            it["name"] = f"{tag}-{i:02d}"
            it["alt"] = it.get("alt_tr", "")
            it["hero"] = it["file"] in hero
    return out


def by_name():
    return {it["name"]: it for items in picks().values() for it in items}
