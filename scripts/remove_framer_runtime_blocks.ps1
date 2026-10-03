# Remove remaining Framer runtime inline style blocks and modulepreload links
# Usage: PowerShell -ExecutionPolicy Bypass -File .\scripts\remove_framer_runtime_blocks.ps1

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Resolve-Path "$root\.."

$htmlFiles = Get-ChildItem -Path $repoRoot -Recurse -Include *.html | Where-Object { -not $_.FullName.Contains('node_modules') }

foreach ($file in $htmlFiles) {
    $path = $file.FullName
    $text = Get-Content $path -Raw
    $orig = $text

    # Remove <style ... data-framer-components=...>...</style> blocks
    $text = [regex]::Replace($text, '<style[^>]*data-framer-components[^>]*?>.*?</style>', '', 'IgnoreCase,Singleline')

    # Remove modulepreload links that point to framer site runtime files (react.*, rolldown-runtime.*)
    $text = [regex]::Replace($text, '<link[^>]+rel="modulepreload"[^>]+href="https://framerusercontent\.com/sites/[^"\s]+?(react|rolldown-runtime)[^"\s]*\.(mjs|js)"[^>]*>', '', 'IgnoreCase')

    # Remove any remaining modulepreload links to framerusercontent.com
    $text = [regex]::Replace($text, '<link[^>]+href="https://framerusercontent\.com/sites/[^"\s]+"[^>]*>', '', 'IgnoreCase')

    # Remove any remaining inline scripts that reference events.framer.com
    $text = [regex]::Replace($text, '<script[^>]+src="https://events\.framer\.com/[^"]+"[^>]*>\s*</script>', '', 'IgnoreCase')

    if ($text -ne $orig) {
        Write-Host "Cleaning runtime blocks in $path"
        Set-Content -Path $path -Value $text -Encoding UTF8
    }
}

Write-Host "Runtime block cleanup complete." 
