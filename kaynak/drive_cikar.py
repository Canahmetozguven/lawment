"""Drive bağlantısının diske kaydettiği indirme çıktılarını (JSON, base64 içerik) gerçek görsel dosyalarına çevirir.

Kullanım: python kaynak/drive_cikar.py <hedef klasör> <etiket> <çıktı.txt> [<çıktı.txt> ...]
Her dosya <hedef>/<etiket>__<Drive dosya adı> olarak yazılır; ayrıca seçim için küçük bir önizleme üretilir.
"""
import base64
import json
import sys
from pathlib import Path
from PIL import Image, ImageOps

try:  # HEIC (iPhone) dosyaları için
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass


def main():
    out, tag, srcs = Path(sys.argv[1]), sys.argv[2], sys.argv[3:]
    (out / "onizleme").mkdir(parents=True, exist_ok=True)
    for s in srcs:
        d = json.loads(Path(s).read_text(encoding="utf-8"))
        name = f"{tag}__{d['title']}"
        p = out / name
        p.write_bytes(base64.b64decode(d["content"]))
        im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
        print(name, im.size)
        im.thumbnail((640, 640))
        im.save(out / "onizleme" / (p.stem + ".jpg"), quality=78)
        Path(s).unlink()  # büyük ara dosyayı temizle


if __name__ == "__main__":
    main()
