"""Natural language query examples using DSPy."""

import openrouter_helper as orh


def main():
    # Create natural language query interface
    # Uses gpt-4o-mini via OpenRouter for parsing (very cheap)
    nl_query = orh.NaturalLanguageQuery(lm_model="openai/gpt-4o-mini")

    # Example 1: Basic price filter
    print("=== Example 1: Price filter ===")
    print("Query: 'list models where input price < 0.5, output price < 1'")
    models = nl_query.query("list models where input price < 0.5, output price < 1")
    print(f"Found {len(models)} models")
    for model in models[:5]:
        print(f"  - {model.id}: ${model.input_price_per_million:.3f}/${model.output_price_per_million:.3f} per M")
    print()

    # Example 2: Context length filter
    print("=== Example 2: Context length filter ===")
    print("Query: 'find models with context length over 100000'")
    models = nl_query.query("find models with context length over 100000")
    print(f"Found {len(models)} models")
    for model in models[:5]:
        print(f"  - {model.id}: {model.context_length:,} tokens")
    print()

    # Example 3: Name-based search
    print("=== Example 3: Name-based search ===")
    print("Query: 'show me Claude models that cost less than 5 dollars per million output tokens'")
    models = nl_query.query("show me Claude models that cost less than 5 dollars per million output tokens")
    print(f"Found {len(models)} models")
    for model in models[:5]:
        print(f"  - {model.name}")
        print(f"    Output price: ${model.output_price_per_million:.3f} per M tokens")
    print()

    # Example 4: Multiple criteria
    print("=== Example 4: Multiple criteria ===")
    print("Query: 'cheap GPT models with large context'")
    models = nl_query.query("cheap GPT models with large context")
    print(f"Found {len(models)} models")
    for model in models[:5]:
        print(f"  - {model.name}")
        print(f"    Price: ${model.input_price_per_million:.3f}/${model.output_price_per_million:.3f} per M")
        print(f"    Context: {model.context_length:,} tokens")
    print()

    # Example 5: Debug query plan
    print("=== Example 5: Debug query plan ===")
    query_text = "find models under $2 per million with 128k context"
    print(f"Query: '{query_text}'")
    plan = nl_query.get_query_plan(query_text)
    print("Parsed plan:")
    print(f"  Input price max: {plan.input_price_max}")
    print(f"  Output price max: {plan.output_price_max}")
    print(f"  Context length min: {plan.context_length_min}")
    print(f"  Name contains: {plan.name_contains}")
    print()


if __name__ == "__main__":
    main()
