# Parody CLI

The parody CLI tool converts web articles into rat-themed parodies for Rat News Network (RNN).

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python src/parody.py --url <article-url> [--output <output-file>]
```

### Arguments

- `--url`: URL of the article to parody (required)
- `--output`: Output file path for the parody (optional, defaults to stdout)

### Example

```bash
python src/parody.py --url https://example.com/article --output parody.md
```

## Testing

```bash
python -m pytest tests/test_parody.py
```

## Architecture

The tool follows these steps:

1. Fetches and converts article HTML to markdown using `docling`
2. Extracts clean article data (title, body, author) using OpenAI
3. (Future) Converts the article into a rat-themed parody

## Error Handling

- Invalid URLs will raise a ValueError
- Failed HTML conversion will raise a DocumentConversionError
- Failed article cleaning will raise an ArticleExtractionError
