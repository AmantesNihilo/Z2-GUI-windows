$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

Write-Host "Building Zapret2GUI portable package..." -ForegroundColor Cyan

python -m PyInstaller --clean --noconfirm .\Zapret2GUI.spec

$outDir = Join-Path $PSScriptRoot "dist\Zapret2GUI"
if (-not (Test-Path $outDir)) {
    throw "Build output not found: $outDir"
}

$rootFiles = @(
    "README.md",
    "README.ru.md",
    "NOTICE.md"
)

foreach ($file in $rootFiles) {
    $source = Join-Path $PSScriptRoot $file
    if (Test-Path -LiteralPath $source) {
        Copy-Item -LiteralPath $source -Destination (Join-Path $outDir $file) -Force
    }
}

Write-Host ""
Write-Host "Build complete:" -ForegroundColor Green
Write-Host "  $outDir"
Write-Host ""
Write-Host "Run:" -ForegroundColor Yellow
Write-Host "  $outDir\Zapret2GUI.exe"
