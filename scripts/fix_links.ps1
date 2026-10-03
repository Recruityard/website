param()

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot ".."))
Write-Host "Repo root: $repoRoot"

$htmlFiles = Get-ChildItem -Path $repoRoot -Recurse -Include *.html | Where-Object { -not $_.FullName.Contains('node_modules') }

foreach ($file in $htmlFiles) {
    $path = $file.FullName
    $text = Get-Content $path -Raw
    $orig = $text

    # Replace /about-us -> /about-us.html (but ignore links that already have an extension or are anchors)
    $text = [regex]::Replace($text, 'href="/(about-us)(#?[^"]*)"', 'href="/about-us.html$2"', 'IgnoreCase')

    # Convert /contact-us, /find-jobs, /hire-talent, /privacy-policy, /terms-and-conditions, /cookie-policy
    $pages = @('contact-us','find-jobs','hire-talent','privacy-policy','terms-and-conditions','cookie-policy','404')
    foreach ($p in $pages) {
        $text = [regex]::Replace($text, "href=\"/($p)(#?[^"]*)\"", "href=\"/$p.html$2\"", 'IgnoreCase')
    }

    # Convert /blog-articles/<slug> to /articles/<slug>.html
    $text = [regex]::Replace($text, 'href="/blog-articles/([^"]+)"', 'href="/articles/$1.html"', 'IgnoreCase')

    # Convert top-level /blog-articles to /blog-articles.html
    $text = [regex]::Replace($text, 'href="/blog-articles"', 'href="/blog-articles.html"', 'IgnoreCase')

    # Convert links like /about-us#fragment that became /about-us.html#fragment
    # (already handled by regexes above)

    if ($text -ne $orig) {
        Write-Host "Patching links in $path"
        Set-Content -Path $path -Value $text -Encoding UTF8
    }
}

Write-Host "Link fixes applied." 
