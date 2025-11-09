"""Verify that the package can be imported and basic functionality works."""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import openrouter_helper as orh

def test_imports():
    """Test that all main classes can be imported."""
    print("Testing imports...")
    assert orh.OpenRouterClient is not None
    assert orh.Model is not None
    assert orh.ModelPricing is not None
    assert orh.ModelQuery is not None
    assert orh.NaturalLanguageQuery is not None
    print("✓ All imports successful")

def test_model_creation():
    """Test creating a model instance."""
    print("\nTesting model creation...")
    pricing = orh.ModelPricing(prompt=0.0000005, completion=0.0000015)
    model = orh.Model(
        id="test/model",
        name="Test Model",
        context_length=8192,
        pricing=pricing
    )
    assert model.id == "test/model"
    assert model.input_price_per_million == 0.5
    assert model.output_price_per_million == 1.5
    print("✓ Model creation works")

def test_query_creation():
    """Test creating a query."""
    print("\nTesting query creation...")
    query = orh.ModelQuery()
    assert query is not None
    print("✓ Query creation works")

if __name__ == "__main__":
    test_imports()
    test_model_creation()
    test_query_creation()
    print("\n✅ All basic verification tests passed!")
