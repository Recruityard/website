# Downloads Framer-hosted assets (fonts, images, searchIndex JSON) into the repo
# and rewrites HTML files to reference the local copies.
# Usage: PowerShell -ExecutionPolicy Bypass -File .\scripts\download_framer_assets.ps1

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Resolve-Path "$root\.."
$assetsFonts = Join-Path $repoRoot "assets\fonts"
$assetsSearch = Join-Path $repoRoot "assets\searchIndex"
$imagesDir = Join-Path $repoRoot "images"

foreach ($d in @($assetsFonts, $assetsSearch, $imagesDir)) {
    if (-Not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
}

$htmlFiles = Get-ChildItem -Path $repoRoot -Recurse -Include *.html | Where-Object { -not $_.FullName.Contains('node_modules') }

$downloaded = @{}

function Download-File($url, $localPath) {
    if (-Not (Test-Path $localPath)) {
        Write-Host "Downloading $url -> $localPath"
        try {
            Invoke-WebRequest -Uri $url -OutFile $localPath -UseBasicParsing -ErrorAction Stop
        } catch {
            $msg = $_.Exception.Message
            Write-Warning ("Failed to download {0}: {1}" -f $url, $msg)
        }
    } else {
        Write-Host "Already exists: $localPath"
    }
}

foreach ($file in $htmlFiles) {
    $path = $file.FullName
    $text = Get-Content $path -Raw
    $modified = $false

    # 1) Download and replace fonts served from framerusercontent.com/assets/*.woff2
    $fontPattern = 'https://framerusercontent\.com/assets/[^"\)\s]+?\.woff2'
    $fontMatches = [regex]::Matches($text, $fontPattern)
    foreach ($m in $fontMatches) {
        $url = $m.Value
        if (-not $downloaded.ContainsKey($url)) {
            $base = [System.IO.Path]::GetFileName($url)
            $local = Join-Path $assetsFonts $base
            Download-File $url $local
            $downloaded[$url] = "/assets/fonts/" + $base
        }
        $text = $text -replace [regex]::Escape($url), $downloaded[$url]
        $modified = $true
    }

    # 2) Download and replace images from framerusercontent.com/images/...
    $imgPattern = 'https://framerusercontent\.com/images/[^"\)\s]+'
    $imgMatches = [regex]::Matches($text, $imgPattern)
    foreach ($m in $imgMatches) {
        $url = $m.Value
        # strip query string
        $urlNoQuery = $url.Split('?')[0]
        if (-not $downloaded.ContainsKey($url)) {
            $base = [System.IO.Path]::GetFileName($urlNoQuery)
            if (-not $base) { $base = [System.Guid]::NewGuid().ToString() }
            $local = Join-Path $imagesDir $base
            Download-File $url $local
            $downloaded[$url] = "/images/" + $base
        }
        $text = $text -replace [regex]::Escape($url), $downloaded[$url]
        $modified = $true
    }

    # 3) Download and replace framer search index JSON files
    $jsonPattern = 'https://framerusercontent\.com/sites/[^"\)\s]+?\.json'
    $jsonMatches = [regex]::Matches($text, $jsonPattern)
    foreach ($m in $jsonMatches) {
        $url = $m.Value
        if (-not $downloaded.ContainsKey($url)) {
            $base = [System.IO.Path]::GetFileName($url)
            if (-not $base) { $base = [System.Guid]::NewGuid().ToString() + '.json' }
            $local = Join-Path $assetsSearch $base
            Download-File $url $local
            $downloaded[$url] = "/assets/searchIndex/" + $base
        }
        $text = $text -replace [regex]::Escape($url), $downloaded[$url]
        $modified = $true
    }

    # 4) Remove "Made in Framer" comment and Framer generator meta
    $madePattern = '<!--\s*Made in Framer.*?-->\r?\n?'
    if ([regex]::IsMatch($text, $madePattern, 'IgnoreCase')) {
        $text = [regex]::Replace($text, $madePattern, '', 'IgnoreCase')
        $modified = $true
    }
    $metaPattern = '<meta\s+content="Framer[^"]*"\s+name="generator"\s*\/?>\r?\n?'
    if ([regex]::IsMatch($text, $metaPattern, 'IgnoreCase')) {
        $text = [regex]::Replace($text, $metaPattern, '', 'IgnoreCase')
        $modified = $true
    }

    if ($modified) {
        Write-Host "Patching $path"
        Set-Content -Path $path -Value $text -Encoding UTF8
    }
}

Write-Host "Done. Review changes in assets and images, then commit on branch cleanup-framer-work." 
