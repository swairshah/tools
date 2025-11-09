# OpenRouter Helper - Complete Usage Guide

## Installation Options

### Option 1: Install from GitHub with uv (Recommended)

```bash
# Install the package directly from GitHub
uv pip install "git+https://github.com/swairshah/tools#subdirectory=openrouter_helper"

# Or install in editable mode for development
git clone https://github.com/swairshah/tools
cd tools/openrouter_helper
uv pip install -e .
```

### Option 2: Install from GitHub with pip

```bash
# Install directly
pip install "git+https://github.com/swairshah/tools#subdirectory=openrouter_helper"

# Or clone and install
git clone https://github.com/swairshah/tools
cd tools/openrouter_helper
pip install -e .
```

### Option 3: One-off script execution with uv

You can run scripts without installing the package:

```bash
# Run a script with dependencies installed on-the-fly
uv run --with "git+https://github.com/swairshah/tools#subdirectory=openrouter_helper" your_script.py
```

## Setup

Set your OpenRouter API key:

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

## Usage Examples

### 1. Basic Query Interface

```python
import openrouter_helper as orh

# Initialize client
client = orh.OpenRouterClient()

# List all models
all_models = client.get_models()
print(f"Total models: {len(all_models)}")

# Get specific model
gpt4 = client.get_model("openai/gpt-4")
print(f"GPT-4 context: {gpt4.context_length}")
```

### 2. Programmatic Filtering

```python
import openrouter_helper as orh

query = orh.ModelQuery()

# Example: Find cheap models
cheap_models = (
    query
    .where_input_price_less_than(0.5)   # < $0.50 per million input tokens
    .where_output_price_less_than(1.0)  # < $1.00 per million output tokens
    .list_models()
)

# Example: Find large context models
large_context = (
    orh.ModelQuery()
    .where_context_length_greater_than(100_000)
    .list_models()
)

# Example: Complex filter
good_value = (
    orh.ModelQuery()
    .where_input_price_less_than(2.0)
    .where_output_price_less_than(5.0)
    .where_context_length_greater_than(32_000)
    .where_name_contains("Claude")
    .list_models()
)

# Print results
for model in good_value:
    print(f"{model.name}")
    print(f"  Price: ${model.input_price_per_million:.2f}/${model.output_price_per_million:.2f} per M")
    print(f"  Context: {model.context_length:,} tokens")
```

### 3. Natural Language Queries (DSPy)

```python
import openrouter_helper as orh

# Initialize NL interface
nl = orh.NaturalLanguageQuery(lm_model="openai/gpt-4o-mini")

# Query with natural language
models = nl.query("list models where input price < 0.5, output price < 1")
models = nl.query("find models with context length over 100000")
models = nl.query("show me cheap Claude models")
models = nl.query("GPT models under $5 per million output tokens")

# See how your query was interpreted
plan = nl.get_query_plan("find models under $2 with 128k context")
print(f"Input price max: {plan.input_price_max}")
print(f"Context min: {plan.context_length_min}")
```

### 4. Chaining and Custom Filters

```python
import openrouter_helper as orh

query = orh.ModelQuery()

# Chain multiple filters
models = (
    query
    .where_input_price_less_than(1.0)
    .where_context_length_greater_than(50_000)
    .where_name_contains("gpt")
    .list_models()
)

# Custom filter function
models = (
    orh.ModelQuery()
    .where(lambda m: m.context_length > 100_000 and m.input_price_per_million < 5.0)
    .list_models()
)

# Get count instead of list
count = query.where_input_price_less_than(0.1).count()
print(f"Found {count} ultra-cheap models")

# Get just the first match
first_model = query.where_name_contains("claude").first()
```

## Common Query Patterns

### Find the cheapest models

```python
import openrouter_helper as orh

models = orh.ModelQuery().list_models()
cheapest = sorted(models, key=lambda m: m.input_price_per_million)[:10]

for model in cheapest:
    print(f"{model.id}: ${model.input_price_per_million:.4f} per M")
```

### Find best value for large context

```python
import openrouter_helper as orh

models = (
    orh.ModelQuery()
    .where_context_length_greater_than(100_000)
    .list_models()
)

# Sort by price per token per context
best_value = sorted(
    models,
    key=lambda m: m.input_price_per_million / m.context_length
)[:10]
```

### Compare specific models

```python
import openrouter_helper as orh

client = orh.OpenRouterClient()

model_ids = [
    "openai/gpt-4-turbo",
    "anthropic/claude-3-opus",
    "google/gemini-pro-1.5"
]

for model_id in model_ids:
    model = client.get_model(model_id)
    if model:
        print(f"{model.name}:")
        print(f"  Price: ${model.input_price_per_million:.2f}/${model.output_price_per_million:.2f}")
        print(f"  Context: {model.context_length:,}")
```

## Publishing to PyPI

To publish this package to PyPI:

```bash
# 1. Install build tools
uv pip install build twine

# 2. Build the package
python -m build

# 3. Upload to PyPI
twine upload dist/*

# Or use uv directly
uv build
uv publish
```

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests (requires pytest)
pytest

# Format code
black src/ examples/
ruff check src/ examples/
```

## Troubleshooting

### API Key Issues

If you get authentication errors, make sure your API key is set:

```bash
echo $OPENROUTER_API_KEY  # Should print your key
```

### Import Errors

If you get import errors, make sure dependencies are installed:

```bash
uv pip install pydantic requests dspy
```

### Rate Limiting

OpenRouter has rate limits. If you hit them, the client will raise an exception. Consider adding retry logic or reducing request frequency.
