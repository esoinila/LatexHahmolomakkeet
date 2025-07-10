Remove-Item *.log -ErrorAction SilentlyContinue
Get-ChildItem character*.tex | ForEach-Object { 
    Write-Host "Processing $($_.Name)..."
    pdflatex $_.Name 
    Write-Host "Finished $($_.Name)"
} 