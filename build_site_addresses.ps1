# Rebuild hieroglyph print set from current GenAI letter masters.
# Uses py -3 (Pillow). For a full icon reprocess, run build_hieroglyph_addresses.py first.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== Glyphs, addresses, tiles, decipher card ===" -ForegroundColor Cyan
py -3 HieroGlyphs\rebuild_print_set.py
if ($LASTEXITCODE -ne 0) { throw "Python rebuild_print_set failed" }

New-Item -ItemType Directory -Force -Path Output | Out-Null

Write-Host "=== Compiling site_addresses_player.tex ===" -ForegroundColor Cyan
pdflatex -interaction=nonstopmode -output-directory=Output site_addresses_player.tex | Out-Null
if ($LASTEXITCODE -ne 0) { throw "pdflatex player failed" }

Write-Host "=== Compiling site_addresses_gm.tex (pass 1) ===" -ForegroundColor Cyan
pdflatex -interaction=nonstopmode -output-directory=Output site_addresses_gm.tex | Out-Null
Write-Host "=== Compiling site_addresses_gm.tex (pass 2) ===" -ForegroundColor Cyan
pdflatex -interaction=nonstopmode -output-directory=Output site_addresses_gm.tex | Out-Null
if ($LASTEXITCODE -ne 0) { throw "pdflatex GM failed" }

Write-Host "=== Compiling hieroglyph_decipher_keys.tex ===" -ForegroundColor Cyan
pdflatex -interaction=nonstopmode -output-directory=Output hieroglyph_decipher_keys.tex | Out-Null
if ($LASTEXITCODE -ne 0) { throw "pdflatex decipher keys failed" }

Write-Host ""
Write-Host "Done:" -ForegroundColor Green
Write-Host "  Output\site_addresses_player.pdf"
Write-Host "  Output\site_addresses_gm.pdf"
Write-Host "  Output\hieroglyph_decipher_keys.pdf"
