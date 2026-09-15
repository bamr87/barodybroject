# Jekyll site data

Data files for the Jekyll sidecar in `src/pages/`, which publishes generated parody-news content. Jekyll loads everything in this directory into `site.data`, keyed by filename, so a template reads `ui-text.yml` as `site.data.ui-text` and `navigation/main.yml` as `site.data.navigation.main`. The site renders with the [`bamr87/zer0-mistakes`](https://github.com/bamr87/zer0-mistakes) remote theme, which is what expects these particular files.

## Contents

| Path | What it holds |
|---|---|
| [`navigation/`](navigation/) | Menu structure: `main.yml` (header), `about.yml` and `posts.yml` (section menus). See [navigation/README.md](navigation/README.md). |
| `ui-text.yml` | Interface strings for the theme, grouped by locale (`en` is the default). Pagination labels, breadcrumbs, skip links and similar chrome. |

## Changing site text

Wording that belongs to the theme's chrome rather than to a page lives in `ui-text.yml` under its locale key:

```yaml
en: &DEFAULT_EN
  pagination_previous        : "Previous"
  breadcrumb_home_label      : "Home"
```

Templates read it as `{{ site.data.ui-text[site.locale].pagination_previous }}`, so a missing key renders as an empty string rather than failing the build. Add a new locale by copying the `en` block and overriding the strings that differ.

## Changing the menus

Edit the relevant file in [`navigation/`](navigation/). Entries are a list of `title`/`url` pairs, optionally with `sublinks`:

```yaml
- title: News
  url: /posts
  sublinks:
    - title: Pages
      url: /pages
```

URLs are site-relative and are not validated at build time, so a typo produces a dead menu item rather than a build error.

## Related

- [Jekyll data files documentation](https://jekyllrb.com/docs/datafiles/)
- [Site configuration](../_config.yml)
- [Project documentation index](../../../docs/README.md)
