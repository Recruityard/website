# Remove Framer runtime references and replace third-party Montserrat fonts with local files
# Usage: PowerShell -ExecutionPolicy Bypass -File .\scripts\remove_framer_refs.ps1

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Resolve-Path "$root\.."

$htmlFiles = Get-ChildItem -Path $repoRoot -Recurse -Include *.html | Where-Object { -not $_.FullName.Contains('node_modules') }

foreach ($file in $htmlFiles) {
    $path = $file.FullName
    $text = Get-Content $path -Raw
    $orig = $text

    # Replace Framer third-party Montserrat font URLs with local montserrat file
    $text = [regex]::Replace($text, 'https://framerusercontent\.com/third-party-assets/fontshare/[^"\s]+?\.woff2', '/fonts/montserrat-400-latin.woff2')

    # Remove events.framer.com script tags
    $text = [regex]::Replace($text, '<script[^>]+src="https://events\.framer\.com/[^"]+"[^>]*>\s*</script>', '', 'IgnoreCase')

    # Remove modulepreload links to rolldown-runtime.*.mjs
    $text = [regex]::Replace($text, '<link[^>]+href="https://framerusercontent\.com/sites/[^"]*?/rolldown-runtime[^"\s]*\.mjs"[^>]*>', '', 'IgnoreCase')

    # Remove inline style blocks that hide framer badges/editor UI
    if ($text -match '__framer-badge-container') {
        $text = [regex]::Replace($text, '<style[^>]*>[^<]*__framer-badge-container[^<]*</style>', '', 'IgnoreCase')
    }

    # Remove any remaining meta name="framer-search-index" or framer-search-index-fallback
    $text = [regex]::Replace($text, '<meta[^>]+name="framer-search-index[^"]*"[^>]*>', '', 'IgnoreCase')

    if ($text -ne $orig) {
        Write-Host "Updating $path"
        Set-Content -Path $path -Value $text -Encoding UTF8
    }
}

Write-Host "Framer reference cleanup complete."
