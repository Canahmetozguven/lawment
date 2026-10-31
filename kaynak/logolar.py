"""Kurum logolarını şeritte tek renk maske olarak kullanılacak hâle getirir.

Girdi: şeffaf zeminli PNG'ler (kaynak/kurum-logolari/ altındaki SVG/PNG'ler tarayıcıda PNG'ye çevrilmiş hâli).
Maske yalnızca alfa kanalını kullanır; logonun içindeki beyaz alanlar (Arkas dalgası, GE monogramı,
Maersk yıldızı) dolu görünmesin diye beyaza yakın pikseller şeffaflaştırılır.
Kale logosunda yazının kendisi beyaz olduğu için bu işlem atlanır.

Kullanım: python kaynak/logolar.py <png klasörü>
Kaynaklar: Arkas, Baker McKenzie, EDAC, Kale, QNB, SOCAR kendi sitelerinden; GE HealthCare, Maersk,
MSC Wikimedia Commons'taki resmi logo dosyalarından (siteleri logoyu script ile yüklüyor).
"""
import sys
from pathlib import Path
from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "site" / "img" / "kurumlar"
KEEP_WHITE = {"kale-group", "actecon"}  # yazısı beyaz olan logolar


def main(src):
    OUT.mkdir(parents=True, exist_ok=True)
    for f in sorted(Path(src).glob("*.png")):
        im = Image.open(f).convert("RGBA")
        if f.stem not in KEEP_WHITE:
            px = im.load()
            for y in range(im.height):
                for x in range(im.width):
                    r, g, b, a = px[x, y]
                    whiteness = min(r, g, b) / 255
                    if whiteness > .78:
                        px[x, y] = (r, g, b, int(a * max(0, (1 - whiteness) / .22)))
        bbox = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        if bbox:
            im = im.crop(bbox)
        im.thumbnail((480, 120), Image.LANCZOS)
        # maske yalnızca alfa kanalını kullanır: renk bilgisi atılır, dosya birkaç KB'a iner
        alpha = im.getchannel("A")
        mask = Image.merge("LA", (Image.new("L", im.size, 0), alpha))
        mask.save(OUT / f"{f.stem}.png", optimize=True)
        print(f.stem, im.size)


if __name__ == "__main__":
    main(sys.argv[1])
