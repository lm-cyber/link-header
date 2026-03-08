# linkheader

![banner](banner.png)

Generate LinkedIn profile banner images (1584×396px) with multiple QR codes and favicon overlays.

## Installation

```bash
uv sync
```

## Usage

### Generate a banner

```bash
# Single QR code
linkheader generate --url "https://github.com/user" --color midnight

# Multiple QR codes with favicons
linkheader generate \
  --url "https://github.com/lm-cyber" \
  --url "https://www.kaggle.com/asdasdsadasdsasdasd" \
  --url "https://t.me/overfeat_and_data_leak" \
  --color midnight \
  --pattern dots \
  --preview

# 4 QR codes
linkheader generate \
  --url "https://github.com/user" \
  --url "https://kaggle.com/user" \
  --url "https://t.me/user" \
  --url "https://linkedin.com/in/user" \
  --color ocean \
  --pattern grid \
  --preview
```

### Options

| Option | Description | Default |
|---|---|---|
| `--url` | URL for QR code (repeat for multiple, max 4) | — |
| `--color` | Hex code or palette name (required) | — |
| `--pattern` | `none` / `grid` / `dots` / `lines` | `none` |
| `--output` / `-o` | Output file path | `banner.png` |
| `--format` / `-f` | `png` / `jpg` | `png` |
| `--preview` | Open image after generation | `false` |

### List palettes

```bash
linkheader palettes
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
