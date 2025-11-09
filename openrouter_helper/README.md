# OpenRouter Helper

A Python library for querying OpenRouter models with both programmatic and natural language interfaces.

## Features

- **Simple API Client**: Fetch and query OpenRouter models
- **Fluent Query Interface**: Chain filters to find models matching your criteria
- **Natural Language Queries**: Use DSPy to query models with plain English
- **Type-Safe**: Built with Pydantic for robust data validation

## Installation

### From GitHub (recommended for testing)

```bash
# Using uv (fast)
uv pip install "git+https://github.com/yourusername/openrouter-helper"

# Using pip
pip install "git+https://github.com/yourusername/openrouter-helper"
```

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/openrouter-helper
cd openrouter-helper

# Install with uv
uv pip install -e .

# Or with pip
pip install -e .
```

## Quick Start

### Setup

Set your OpenRouter API key as an environment variable:

```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

### Basic Usage

```python
import openrouter_helper as orh

# Create a client
client = orh.OpenRouterClient()

# Get all models
models = client.get_models()

# Filter with programmatic query
query = orh.ModelQuery(client)
cheap_models = (
    query
    .where_input_price_less_than(0.5)   # < $0.50 per million tokens
    .where_output_price_less_than(1.0)  # < $1.00 per million tokens
    .list_models()
)

print(f"Found {len(cheap_models)} cheap models")
for model in cheap_models[:5]:
    print(f"{model.id}: ${model.input_price_per_million:.2f}/${model.output_price_per_million:.2f} per M")
```

### Natural Language Queries

```python
import openrouter_helper as orh

# Create natural language interface
nl = orh.NaturalLanguageQuery()

# Query with plain English
models = nl.query("list models where input price < 0.5, output price < 1")
models = nl.query("find Claude models with context length over 100000")
models = nl.query("show me cheap GPT models")

# Debug the query plan
plan = nl.get_query_plan("find models under $2 per million with 128k context")
print(plan)
```

## API Reference

### OpenRouterClient

```python
client = orh.OpenRouterClient(api_key="optional-key")

# Get all models
models = client.get_models()

# Get specific model
model = client.get_model("openai/gpt-4")
```

### ModelQuery

Fluent interface for filtering models:

```python
query = orh.ModelQuery(client)

query.where_input_price_less_than(price)      # Filter by max input price
query.where_output_price_less_than(price)     # Filter by max output price
query.where_input_price_greater_than(price)   # Filter by min input price
query.where_output_price_greater_than(price)  # Filter by min output price
query.where_context_length_greater_than(len)  # Filter by min context length
query.where_name_contains(text)               # Filter by name
query.where_id_contains(text)                 # Filter by ID
query.where(custom_filter_fn)                 # Custom filter function

# Execute query
models = query.list_models()
count = query.count()
first_model = query.first()
```

### NaturalLanguageQuery

Natural language interface powered by DSPy:

```python
nl = orh.NaturalLanguageQuery(
    client=None,              # Optional client
    lm_model="openai/gpt-4o-mini",  # Model for parsing
    api_key=None              # Optional API key
)

# Query with natural language
models = nl.query("your natural language query")

# Get query plan (for debugging)
plan = nl.get_query_plan("your query")
```

## Examples

See the `examples/` directory for complete examples:

- `basic_usage.py` - Programmatic query examples
- `nl_query_usage.py` - Natural language query examples

Run examples:

```bash
python examples/basic_usage.py
python examples/nl_query_usage.py
```

## Model Data Structure

```python
class Model:
    id: str                              # e.g., "openai/gpt-4"
    name: str                            # e.g., "GPT-4"
    context_length: int                  # Max context in tokens
    pricing: ModelPricing                # Pricing info
    architecture: ModelArchitecture      # Architecture details
    top_provider: TopProvider            # Provider info

    # Convenience properties
    input_price_per_million: float       # Input price per 1M tokens
    output_price_per_million: float      # Output price per 1M tokens
```

## Publishing

To publish this package to PyPI:

1. Update version in `pyproject.toml`
2. Build the package:
   ```bash
   uv build
   # or: python -m build
   ```
3. Upload to PyPI:
   ```bash
   uv publish
   # or: twine upload dist/*
   ```

## Development

### Setup

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ examples/
ruff check src/ examples/
```

## License

MIT
