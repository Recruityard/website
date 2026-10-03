# Downloads specified Google WOFF2 font files to /fonts and updates HTML files to reference local paths.
# Usage: PowerShell -ExecutionPolicy Bypass -File .\scripts\download_google_fonts.ps1

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Resolve-Path "$root\.."
$fontsDir = Join-Path $repoRoot "fonts"

if (-Not (Test-Path $fontsDir)) {
    New-Item -ItemType Directory -Path $fontsDir | Out-Null
}

# Map of remote URL -> local filename
$fonts = @{
    "https://fonts.gstatic.com/s/manrope/v20/xn7_YHE41ni1AdIRqAuZuw1Bx9mbZk4jE9_P-bnBeA.woff2" = "manrope-600-cyrillic-ext.woff2"
    "https://fonts.gstatic.com/s/manrope/v20/xn7_YHE41ni1AdIRqAuZuw1Bx9mbZk4jE9_G-bnBeA.woff2" = "manrope-600-cyrillic.woff2"
    "https://fonts.gstatic.com/s/manrope/v20/xn7_YHE41ni1AdIRqAuZuw1Bx9mbZk4jE9_B-bnBeA.woff2" = "manrope-600-greek.woff2"
    "https://fonts.gstatic.com/s/manrope/v20/xn7_YHE41ni1AdIRqAuZuw1Bx9mbZk4jE9_N-bnBeA.woff2" = "manrope-600-vietnamese.woff2"
    "https://fonts.gstatic.com/s/manrope/v20/xn7_YHE41ni1AdIRqAuZuw1Bx9mbZk4jE9_M-bnBeA.woff2" = "manrope-600-latin-ext.woff2"
    "https://fonts.gstatic.com/s/manrope/v20/xn7_YHE41ni1AdIRqAuZuw1Bx9mbZk4jE9_C-bk.woff2" = "manrope-600-latin.woff2"

    "https://fonts.gstatic.com/s/montserrat/v31/JTUSjIg1_i6t8kCHKm459WRhyzbi.woff2" = "montserrat-400-cyrillic-ext.woff2"
    "https://fonts.gstatic.com/s/montserrat/v31/JTUSjIg1_i6t8kCHKm459W1hyzbi.woff2" = "montserrat-400-cyrillic.woff2"
    "https://fonts.gstatic.com/s/montserrat/v31/JTUSjIg1_i6t8kCHKm459WZhyzbi.woff2" = "montserrat-400-vietnamese.woff2"
    "https://fonts.gstatic.com/s/montserrat/v31/JTUSjIg1_i6t8kCHKm459Wdhyzbi.woff2" = "montserrat-400-latin-ext.woff2"
    "https://fonts.gstatic.com/s/montserrat/v31/JTUSjIg1_i6t8kCHKm459Wlhyw.woff2" = "montserrat-400-latin.woff2"
}

Write-Host "Downloading $($fonts.Count) fonts to $fontsDir"

foreach ($pair in $fonts.GetEnumerator()) {
    $url = $pair.Key
    $filename = $pair.Value
    $localPath = Join-Path $fontsDir $filename

    if (-Not (Test-Path $localPath)) {
        Write-Host "Downloading $url -> $filename"
        try {
            Invoke-WebRequest -Uri $url -OutFile $localPath -UseBasicParsing -ErrorAction Stop
        } catch {
            $errMsg = $_.Exception.Message
            Write-Warning ("Failed to download {0}: {1}" -f $url, $errMsg)
        }
    } else {
        Write-Host "Already exists: $filename"
    }
}

# Update all HTML files to replace fonts.gstatic.com references with /fonts/<localfile>
$htmlFiles = Get-ChildItem -Path $repoRoot -Recurse -Include *.html | Where-Object { -not $_.FullName.Contains('node_modules') }

foreach ($file in $htmlFiles) {
    $text = Get-Content $file.FullName -Raw
    $modified = $false

    foreach ($pair in $fonts.GetEnumerator()) {
        $remote = [regex]::Escape($pair.Key)
        $local = "/fonts/" + $pair.Value
        if ($text -match $remote) {
            $text = $text -replace $remote, $local
            $modified = $true
        }
    }

    if ($modified) {
        Write-Host "Updating fonts in $($file.FullName)"
        Set-Content -Path $file.FullName -Value $text -Encoding UTF8
    }
}

Write-Host "Done. Review changes and commit them on branch cleanup-framer-work."