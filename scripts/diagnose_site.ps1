param()

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot ".."))
Write-Host "Repo root: $repoRoot"

$htmlFiles = Get-ChildItem -Path $repoRoot -Recurse -Include *.html | Where-Object { -not $_.FullName.Contains('node_modules') }

$externalList = New-Object System.Collections.Generic.HashSet[string]
$missingFiles = @()

foreach ($file in $htmlFiles) {
    $text = Get-Content $file.FullName -Raw

    # Find all src and href attributes
    $pattern = '((?:src|href)\s*=\s*"([^"]+)")'
    $matches = [regex]::Matches($text, $pattern, 'IgnoreCase')
    foreach ($m in $matches) {
        $url = $m.Groups[2].Value
        if ($url -match '^https?://') {
            $externalList.Add($url) | Out-Null
        } else {
            # Strip query params and fragments
            $clean = $url -replace '\?.*$', '' -replace '#.*$', ''
            if ($clean -match '^/') {
                $target = Join-Path $repoRoot ($clean.TrimStart('/'))
            } else {
                $target = Join-Path $file.DirectoryName $clean
            }
            if (-not (Test-Path $target)) {
                $missingFiles += [PSCustomObject]@{ File = $file.FullName; Reference = $url; ExpectedPath = $target }
            }
        }
    }
}

Write-Host "\nExternal URLs found (unique):"
$externalList | Sort-Object | ForEach-Object { Write-Host " - $_" }

if ($missingFiles.Count -eq 0) {
    Write-Host "\nNo missing local assets detected."
} else {
    Write-Host "\nMissing local assets:"
    $missingFiles | ForEach-Object { Write-Host "- $($_.Reference) referenced in $($_.File) -> expected $($_.ExpectedPath)" }
}

# Quick grep for common breakage suspects
Write-Host "\nQuick checks:"
Get-ChildItem -Path $repoRoot -Recurse -Include *.html | ForEach-Object {
    $c = Get-Content $_.FullName -Raw
    if ($c -match 'data-framer-bundle|framerusercontent|events.framer.com|script_main|rolldown-runtime') {
        Write-Host " - Framer-related token found in $($_.FullName)"
    }
}

Write-Host "\nDiagnosis complete."
