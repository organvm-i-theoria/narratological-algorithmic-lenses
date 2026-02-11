# Narratological Algorithmic Lenses

A monorepo for formalized narrative analysis tools and source materials.

## Repository Layout

```text
narratological-algorithmic-lenses/
├── specs/                    # Narrative source material, templates, JSON exports
│   ├── 00-chat-transcripts/
│   ├── 01-primary-sources/
│   ├── 02-completed-studies/
│   ├── 03-structured-data/
│   ├── 04-templates/
│   ├── 05-secondary-sources/
│   ├── 06-open-view-drafts/
│   └── 07-skill-documentation/
├── packages/
│   ├── core/                 # Python library (models, algorithms, diagnostics)
│   ├── cli/                  # Typer CLI wrapper
│   ├── api/                  # FastAPI service
│   └── web/                  # React + Vite frontend
├── open-view-analysis/       # Research drafts and protocol worksheets
├── pyproject.toml            # Workspace + pytest/ruff/mypy configuration
└── package.json              # Web workspace scripts
```

## Getting Started

### Python workspace

```bash
uv sync
uv run pytest
uv run narratological --help
uv run uvicorn narratological_api.main:app --reload
```

### Web workspace

```bash
npm install
npm run web:dev
npm run web:build
npm run web:test
```

## Testing

- Root Python test gate: `uv run pytest`
- Core tests: `uv run pytest packages/core/tests`
- CLI tests: `uv run pytest packages/cli/tests`
- API tests: `uv run pytest packages/api/tests`
- Web tests: `npm run web:test`

## Data Loading

The core package includes a bundled compendium at:

- `packages/core/src/narratological/data/narratological-algorithms-unified.json`

The loader resolves packaged resources first and falls back to repository paths for local development.

## Notes

- Requires Python 3.11+.
- LLM-backed features require `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`.
- For deterministic local checks, run `uv run ruff check ...` and `uv run mypy ...` before opening a PR.
- Quality ratchet policy: changes must not introduce new `ruff` or `mypy` violations in modified files.
