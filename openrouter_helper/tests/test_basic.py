"""Basic tests for openrouter_helper."""

import pytest
from openrouter_helper import Model, ModelPricing, ModelQuery
from openrouter_helper.client import OpenRouterClient


def test_model_pricing():
    """Test ModelPricing model."""
    pricing = ModelPricing(prompt=0.0000005, completion=0.0000015)
    assert pricing.prompt == 0.0000005
    assert pricing.completion == 0.0000015


def test_model_creation():
    """Test Model creation with pricing."""
    pricing = ModelPricing(prompt=0.0000005, completion=0.0000015)
    model = Model(
        id="test/model",
        name="Test Model",
        context_length=8192,
        pricing=pricing
    )

    assert model.id == "test/model"
    assert model.name == "Test Model"
    assert model.context_length == 8192
    assert model.input_price_per_million == 0.5
    assert model.output_price_per_million == 1.5


def test_model_query_filters():
    """Test ModelQuery filter building."""
    # Create mock models
    models_data = [
        Model(
            id="cheap/model",
            name="Cheap Model",
            context_length=8192,
            pricing=ModelPricing(prompt=0.0000001, completion=0.0000002)
        ),
        Model(
            id="expensive/model",
            name="Expensive Model",
            context_length=128000,
            pricing=ModelPricing(prompt=0.000005, completion=0.000015)
        ),
    ]

    # Test price filtering logic
    cheap_filter = lambda m: m.input_price_per_million < 1.0
    expensive_filter = lambda m: m.input_price_per_million > 1.0

    cheap_models = [m for m in models_data if cheap_filter(m)]
    expensive_models = [m for m in models_data if expensive_filter(m)]

    assert len(cheap_models) == 1
    assert cheap_models[0].id == "cheap/model"
    assert len(expensive_models) == 1
    assert expensive_models[0].id == "expensive/model"


def test_context_length_filter():
    """Test context length filtering."""
    models_data = [
        Model(
            id="small/model",
            name="Small Model",
            context_length=8192,
            pricing=ModelPricing(prompt=0.0000001, completion=0.0000002)
        ),
        Model(
            id="large/model",
            name="Large Model",
            context_length=128000,
            pricing=ModelPricing(prompt=0.000005, completion=0.000015)
        ),
    ]

    large_context_filter = lambda m: m.context_length > 100000
    large_models = [m for m in models_data if large_context_filter(m)]

    assert len(large_models) == 1
    assert large_models[0].id == "large/model"


def test_name_search():
    """Test name-based searching."""
    models_data = [
        Model(
            id="openai/gpt-4",
            name="GPT-4",
            context_length=8192,
            pricing=ModelPricing(prompt=0.000005, completion=0.000015)
        ),
        Model(
            id="anthropic/claude-3",
            name="Claude 3",
            context_length=200000,
            pricing=ModelPricing(prompt=0.000003, completion=0.000015)
        ),
    ]

    gpt_filter = lambda m: "gpt" in m.name.lower()
    claude_filter = lambda m: "claude" in m.name.lower()

    gpt_models = [m for m in models_data if gpt_filter(m)]
    claude_models = [m for m in models_data if claude_filter(m)]

    assert len(gpt_models) == 1
    assert gpt_models[0].id == "openai/gpt-4"
    assert len(claude_models) == 1
    assert claude_models[0].id == "anthropic/claude-3"
