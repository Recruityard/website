# Remove Framer script_main modules and helper inline scripts/templates

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Resolve-Path "$root\.."

$htmlFiles = Get-ChildItem -Path $repoRoot -Recurse -Include *.html | Where-Object { -not $_.FullName.Contains('node_modules') }

foreach ($file in $htmlFiles) {
    $path = $file.FullName
    $text = Get-Content $path -Raw
    $orig = $text

    # Remove script_main module script tags
    $text = [regex]::Replace($text, '<script[^>]+src="https://framerusercontent\.com/sites/[^"\s]+?/script_main[^"\s]*\.(mjs|js)"[^>]*>\s*</script>', '', 'IgnoreCase')

    # Remove any script tags with id starting with __framer__hand or similar
    $text = [regex]::Replace($text, '<script[^>]+id="__framer__[^"]*"[^>]*>.*?</script>', '', 'IgnoreCase,Singleline')

    # Remove svg-templates container blocks
    $text = [regex]::Replace($text, '<div[^>]+id="svg-templates"[^>]*>.*?</div>', '', 'IgnoreCase,Singleline')

    # Remove attributes like data-framer-bundle references
    $text = [regex]::Replace($text, '\sdata-framer-bundle="[^"]+"', '', 'IgnoreCase')

    if ($text -ne $orig) {
        Write-Host "Stripping script_main and helpers from $path"
        Set-Content -Path $path -Value $text -Encoding UTF8
    }
}

Write-Host "Framer script_main and helper cleanup complete." 
