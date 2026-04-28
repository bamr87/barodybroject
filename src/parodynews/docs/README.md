# Parodynews Sphinx Docs

Sphinx documentation sources for the `parodynews` Django app.

## Build

```bash
cd src/parodynews/docs
make html
```

The development compose file also includes an optional `docs` service for live documentation work.

## Key Files

| Path | Purpose |
|---|---|
| [index.rst](index.rst) | Root Sphinx index. |
| [source/](source/) | RST sources and Sphinx configuration. |
| [requirements.txt](requirements.txt) | Documentation-only Python dependencies. |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deployment notes for the docs service. |