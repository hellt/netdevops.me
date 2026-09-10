# netdevops.me

The blog builds with **Zensical**, **uv**, and **Make**. Site configuration stays
in `mkdocs.yml`. Python dependencies use `pyproject.toml` and `uv.lock`;
no container image is required.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Make,
then run:

```sh
make serve-docs             # http://127.0.0.1:8002, including drafts, live rebuilds
make build-docs             # clean, strict production build in site/
make test-docs              # production build and migration regression checks
make htmltest               # build and check internal/external links (requires Go)
make check-docs             # regression tests and internal links (requires Go)
make deploy-docs            # test and push site/ to origin's gh-pages branch
```

`make serve-docs DEV_ADDR=0.0.0.0:8002` exposes the preview on other interfaces.
The first target invocation creates `.venv`, downloads the Python version from
`.python-version` if necessary, and installs dependencies from `uv.lock` using
`uv sync --locked`. Build and preview commands use `uv run --locked`, so a stale
lockfile fails instead of silently changing dependencies.
To update dependencies, edit `pyproject.toml`, run `make lock-docs`, then
`make check-docs`. Existing `make docs` and `make serve` aliases still work.

The OpenStack client post includes a remote code snippet, so builds need network
access to `raw.githubusercontent.com`. Fonts, comments, analytics, and some images
also use their existing external services in the browser.

## Compatibility

Zensical 0.0.60 supports the existing YAML configuration and several plugins
[natively](https://zensical.org/docs/compatibility/mkdocs/plugins/). It does **not**
implement Material's blog plugin, RSS, or Git revision dates yet. Simply changing
the build command would lose the blog index and change post URLs.

| Previous plugin | Replacement |
| --- | --- |
| `meta` | Native inherited `.meta.yml` metadata |
| `macros` | Native macros compatibility, retaining delimiters and `macros/data.yml` |
| `blog` | `scripts/docs.py`: title-based year/slug URLs, ten-post pagination, excerpts, authors, reading times, and draft filtering |
| `tags` | Native tags and the `material/tags` listing directive |
| `search` | Zensical search, with the existing separator |
| `minify` | Native HTML minification |
| `redirects` | Native redirect maps (currently empty) |
| `rss` | Two generated feeds with stable permalink GUIDs, dates, tags, and comment links |
| `glightbox` | Native lightbox integration |
| `typeset` | Zensical's heading/title rendering; no separate plugin |
| `git-revision-date-localized` | Git history metadata consumed by the theme's date partial when `CI=true` |

The compatibility script prepares `.build/docs` and an ignored
`.mkdocs-generated.yml` that inherits `mkdocs.yml`. It never rewrites post sources.
Use the Make targets rather than running `zensical build` directly, since the
preparation step supplies the blog features. Preview watches the sources,
configuration, and macro data, then lets Zensical rebuild and reload the browser.
Production builds remove old output so preview drafts cannot leak into deployment.

The site uses Zensical's modern theme with its default Inter and JetBrains Mono
fonts. Custom CSS, the sun/moon switcher, announcement, Giscus configuration,
analytics, and custom domain are retained. The post metadata layout is a small
local template.
Feeds retain the existing filenames and 20-item limit; their descriptions are
plain text abstracts of up to 5,000 characters. A sitemap override includes posts
and pagination pages that Zensical otherwise omits when they aren't in `nav`.

`tests/post-urls.json` records URLs produced by the previous Material blog plugin.
Regression checks cover these URLs, canonical links, draft exclusion, pagination,
RSS, tags, search data, macros, lightboxes, comments, and the sitemap.
When Node.js is available (including on the GitHub Actions runners), the tests
also execute the generated browser search worker and verify actual query results.

## Deployment

GitHub Actions installs uv and Go and calls Make targets. All build, check, and
deployment commands live in the Makefile. A full Git checkout supplies revision
dates. Deployment on `master` waits for the checks and retains branch-based Pages
publishing to `gh-pages`, including `CNAME` and `.nojekyll`.

CI gates on internal links and migration tests. The optional `make htmltest`
also audits external URLs; some historical Cisco and O'Reilly links currently
return HTTP 403, so external availability does not block publishing.

`make deploy-docs` **pushes** to the configured remote. For another destination,
set `DEPLOY_REMOTE` and `DEPLOY_BRANCH`; `DEPLOY_NAME` and `DEPLOY_EMAIL` control
the deployment commit identity. Python dependencies are pinned with hashes;
the native htmltest binary is installed from its pinned Go module version.
