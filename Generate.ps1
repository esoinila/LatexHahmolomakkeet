
# Generate.ps1

Write-Host "Starting Character Generation..."

# 1. Run the Generator Code
Set-Location System/Generator
dotnet run
if ($LASTEXITCODE -ne 0) { Write-Error "Generator failed"; exit 1 }
Set-Location ../..

# 2. Compile LaTeX
# Files are now in System/Temp
$tempDir = "System/Temp"
$outputDir = "Output"

if (-not (Test-Path $outputDir)) { mkdir $outputDir }

Get-ChildItem "$tempDir/character_*.tex" | ForEach-Object {
    $baseName = $_.BaseName
    Write-Host "Compiling $baseName..."
    
    # Run pdflatex. We need to run it inside the Temp directory or output-directory
    # Running inside temp is safer for relative image paths.
    Push-Location $tempDir
    
    # We run twice for resolving refs if needed, but once is usually enough for simple text.
    # We pipe output to null to keep console clean, or redirect.
    pdflatex -interaction=nonstopmode $_.Name | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Compilation failed for $_.Name. Check logs in System/Temp."
    } else {
        # Move PDF to Output
        if (Test-Path "$baseName.pdf") {
             Move-Item "$baseName.pdf" "../../$outputDir" -Force
             Write-Host "Generated: $outputDir/$baseName.pdf" -ForegroundColor Green
        }
    }
    Pop-Location
}

Get-ChildItem "$tempDir/namesign_*.tex" | ForEach-Object {
    $baseName = $_.BaseName
    Write-Host "Compiling $baseName..."
    Push-Location $tempDir
    pdflatex -interaction=nonstopmode $_.Name | Out-Null
     if ($LASTEXITCODE -eq 0) {
        if (Test-Path "$baseName.pdf") {
             Move-Item "$baseName.pdf" "../../$outputDir" -Force
             Write-Host "Generated: $outputDir/$baseName.pdf" -ForegroundColor Green
        }
    }
    Pop-Location
}

Write-Host "Done!"
