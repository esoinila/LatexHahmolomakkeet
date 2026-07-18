# Build hieroglyph portal address tiles (player) + GM key PDFs
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== Generating glyphs, addresses, tiles ===" -ForegroundColor Cyan
python HieroGlyphs\build_hieroglyph_addresses.py
if ($LASTEXITCODE -ne 0) { throw "Python build failed" }

New-Item -ItemType Directory -Force -Path Output | Out-Null

Write-Host "=== Compiling site_addresses_player.tex ===" -ForegroundColor Cyan
pdflatex -interaction=nonstopmode -output-directory=Output site_addresses_player.tex | Out-Null
if ($LASTEXITCODE -ne 0) { throw "pdflatex player failed" }

Write-Host "=== Compiling site_addresses_gm.tex (pass 1) ===" -ForegroundColor Cyan
pdflatex -interaction=nonstopmode -output-directory=Output site_addresses_gm.tex | Out-Null
Write-Host "=== Compiling site_addresses_gm.tex (pass 2) ===" -ForegroundColor Cyan
pdflatex -interaction=nonstopmode -output-directory=Output site_addresses_gm.tex | Out-Null
if ($LASTEXITCODE -ne 0) { throw "pdflatex GM failed" }

Write-Host ""
Write-Host "Done:" -ForegroundColor Green
Write-Host "  Output\site_addresses_player.pdf"
Write-Host "  Output\site_addresses_gm.pdf"
