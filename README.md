# linkedge

Generate LinkedIn profile banner images (1584×396px) with QR codes and monotone color fills.

## Installation

```bash
uv sync
```

## Usage

### Generate a banner

```bash
# Minimal
linkedge generate --name "Alan Bekov" --title "ML Engineer" --url "https://linkedin.com/in/alan" --color "#1a1a2e"

# Full options
linkedge generate \
  --name "Alan Bekov" \
  --title "ML Engineer @ Wildberries" \
  --tagline "MLOps · LLMs · Embeddings" \
  --url "https://linkedin.com/in/alan" \
  --color midnight \
  --qr-position right \
  --pattern grid \
  --output banner.png \
  --format png \
  --preview
```

### Options

| Option | Description | Default |
|---|---|---|
| `--name` | Display name (required) | — |
| `--title` | Professional title (required) | — |
| `--url` | LinkedIn URL for QR code (required) | — |
| `--color` | Hex code or palette name (required) | — |
| `--tagline` | Optional tagline | — |
| `--qr-position` | `right` / `left` / `corner-br` / `corner-bl` | `right` |
| `--pattern` | `none` / `grid` / `dots` / `lines` | `none` |
| `--output` / `-o` | Output file path | `banner.png` |
| `--format` / `-f` | `png` / `jpg` | `png` |
| `--preview` | Open image after generation | `false` |

### List palettes

```bash
linkedge palettes
```

Available palettes: midnight, ocean, forest, slate, burgundy, charcoal, navy, plum, steel, espresso, olive, graphite, teal, rust, indigo, sage.

## Development

```bash
make dev        # Install with dev deps
make lint       # Ruff check
make fmt        # Ruff format
make typecheck  # Mypy strict
make test       # Pytest
```
