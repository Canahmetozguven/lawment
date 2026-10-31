# Lighthouse ölçümü (mobil, varsayılan kısıtlamalarla). Yerel sunucu http://127.0.0.1:8080 açık olmalı.
# Kullanım: powershell -File kaynak\lighthouse.ps1 [port]
# Bu bilgisayardaki Kaspersky her sayfaya ~210 KB script ekliyor; gerçek ziyaretçiyi ölçmek için engellenir.
# Sıkıştırmalı ölçüm için siteyi 8081'de `serve` ile açıp port olarak 8081 verin.
param([int]$Port = 8080)
$env:CHROME_PATH = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$out = Join-Path $PSScriptRoot "lighthouse"
New-Item -ItemType Directory -Force $out | Out-Null
$lh = Join-Path $PSScriptRoot "node_modules\lighthouse\cli\index.js"
foreach ($p in "index","biz-kimiz","projeler","arsiv","katil","sponsorluk","iletisim","kvkk") {
  $json = Join-Path $out "$p.json"
  node $lh "http://127.0.0.1:$Port/$p.html" --quiet --output=json --output-path="$json" --chrome-flags="--headless=new" --blocked-url-patterns="*kaspersky-labs.com*" --only-categories=performance,accessibility,best-practices,seo | Out-Null
  $r = Get-Content $json -Raw -Encoding utf8 | ConvertFrom-Json
  "{0,-12} perf {1,3}  a11y {2,3}  best {3,3}  seo {4,3}" -f $p, [math]::Round($r.categories.performance.score*100), [math]::Round($r.categories.accessibility.score*100), [math]::Round($r.categories.'best-practices'.score*100), [math]::Round($r.categories.seo.score*100)
}
