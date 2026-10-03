# Website

Serve from main (GitHub Pages)

To publish this static site from the `main` branch using GitHub Pages, enable Pages in your repository settings and use the included GitHub Actions workflow which deploys the repository root on each push to `main`.

Steps:

1. Ensure the repository's Pages source is set to "GitHub Actions" or leave default; the workflow will publish from the repository root.
2. Push to `main` (or merge a pull request) to trigger deployment.
3. Confirm Pages has a published site in the repository Settings → Pages panel.

Notes on asset paths:

- The site uses absolute root paths (for example `/images/` and `/fonts/`). For a user/org Pages site (e.g., `https://username.github.io/`), these paths work as-is.
- For a project Pages site (e.g., `https://username.github.io/repo/`), update asset references to include the repository path or use relative paths.

If you want, I can create a branch and apply a safe, incremental cleanup to remove any remaining external Framer-hosted assets and make all fonts/images local before publishing.

