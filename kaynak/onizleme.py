"""Önizleme yayını: siteyi derleyip GitHub Pages'e (gh-pages dalı) gönderir.

Önizleme arama motorlarına kapalıdır (her sayfada noindex, kökte robots.txt). Gerçek yayın için kullanılmaz.
Adres: https://<kullanıcı>.github.io/<depo>/
gh-pages dalı her seferinde sıfırdan yazılır (zorla gönderilir); main'e ve çalışma dalına dokunulmaz.
İlk kez: depo ayarlarında Pages kaynağı "gh-pages dalı, / (kök)" olmalı (README'ye bakın).

Kullanım:  python kaynak/onizleme.py
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOINDEX = '<meta name="robots" content="noindex, nofollow">'


def run(*cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        sys.exit(f"HATA: {' '.join(cmd)}\n{r.stdout}{r.stderr}")
    return r.stdout.strip()


def main():
    run(sys.executable, "build.py")
    remote = run("git", "remote", "get-url", "origin")
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", remote)
    if not m:
        sys.exit(f"origin GitHub adresi gibi görünmüyor: {remote}")
    user, repo = m.groups()
    name = run("git", "config", "user.name") or "Lawment önizleme"
    email = run("git", "config", "user.email") or "onizleme@lawment.org"

    tmp = Path(tempfile.mkdtemp(prefix="lawment-onizleme-"))
    try:
        out = tmp / "site"
        shutil.copytree(ROOT / "site", out)
        for page in out.glob("*.html"):
            t = page.read_text(encoding="utf-8")
            if 'name="robots"' in t:
                t = re.sub(r'<meta name="robots"[^>]*>', NOINDEX, t, count=1)
            else:
                t = t.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + NOINDEX, 1)
            assert NOINDEX in t, page.name
            page.write_text(t, encoding="utf-8", newline="\n")
        (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8", newline="\n")
        (out / ".nojekyll").write_text("", encoding="utf-8")  # Jekyll'i kapatır; dosyalar olduğu gibi sunulur

        msg = f"Önizleme güncellendi ({datetime.now():%Y-%m-%d %H:%M})"
        if os.environ.get("ONIZLEME_TRAILER"):
            msg += "\n\n" + os.environ["ONIZLEME_TRAILER"]
        run("git", "init", "-q", "-b", "gh-pages", cwd=out)
        run("git", "config", "core.autocrlf", "false", cwd=out)
        run("git", "add", "-A", cwd=out)
        run("git", "-c", f"user.name={name}", "-c", f"user.email={email}", "commit", "-q", "-m", msg, cwd=out)
        run("git", "remote", "add", "origin", remote, cwd=out)
        run("git", "push", "--force", "-q", "origin", "gh-pages", cwd=out)
        n = sum(1 for p in out.rglob("*") if p.is_file() and ".git" not in p.parts)
        print(f"gönderildi: {n} dosya -> gh-pages")
        print(f"adres: https://{user.lower()}.github.io/{repo}/")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
