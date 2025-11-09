"""Basic usage examples for openrouter_helper."""

import openrouter_helper as orh


def main():
    # Create a client (reads API key from OPENROUTER_API_KEY env var)
    client = orh.OpenRouterClient()

    # Example 1: List all models
    print("=== Example 1: List all models ===")
    models = client.get_models()
    print(f"Found {len(models)} models")
    print(f"First model: {models[0].id}")
    print()

    # Example 2: Filter models with ModelQuery
    print("=== Example 2: Filter with ModelQuery ===")
    query = orh.ModelQuery(client)
    cheap_models = (
        query
        .where_input_price_less_than(0.5)  # Input price < $0.5 per million tokens
        .where_output_price_less_than(1.0)  # Output price < $1 per million tokens
        .list_models()
    )
    print(f"Found {len(cheap_models)} cheap models")
    for model in cheap_models[:5]:  # Show first 5
        print(f"  - {model.id}: ${model.input_price_per_million:.3f}/${model.output_price_per_million:.3f} per M tokens")
    print()

    # Example 3: Find large context models
    print("=== Example 3: Large context models ===")
    large_context = (
        orh.ModelQuery(client)
        .where_context_length_greater_than(100_000)
        .list_models()
    )
    print(f"Found {len(large_context)} models with >100k context")
    for model in large_context[:5]:
        print(f"  - {model.id}: {model.context_length:,} tokens")
    print()

    # Example 4: Search by name
    print("=== Example 4: Search by name ===")
    gpt_models = (
        orh.ModelQuery(client)
        .where_name_contains("GPT")
        .list_models()
    )
    print(f"Found {len(gpt_models)} GPT models")
    for model in gpt_models[:5]:
        print(f"  - {model.name}")
    print()

    # Example 5: Complex query
    print("=== Example 5: Complex query ===")
    good_value = (
        orh.ModelQuery(client)
        .where_input_price_less_than(1.0)
        .where_context_length_greater_than(32_000)
        .where_name_contains("claude")
        .list_models()
    )
    print(f"Found {len(good_value)} Claude models with >32k context and <$1/M input")
    for model in good_value:
        print(f"  - {model.name}")
        print(f"    ID: {model.id}")
        print(f"    Price: ${model.input_price_per_million:.3f}/${model.output_price_per_million:.3f} per M tokens")
        print(f"    Context: {model.context_length:,} tokens")


if __name__ == "__main__":
    main()
