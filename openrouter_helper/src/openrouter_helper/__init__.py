"""OpenRouter Helper - A Python library for querying OpenRouter models."""

from .client import OpenRouterClient
from .models import Model, ModelPricing, ModelArchitecture, TopProvider
from .query import ModelQuery
from .nl_interface import NaturalLanguageQuery, QueryPlan

__version__ = "0.1.0"

__all__ = [
    "OpenRouterClient",
    "Model",
    "ModelPricing",
    "ModelArchitecture",
    "TopProvider",
    "ModelQuery",
    "NaturalLanguageQuery",
    "QueryPlan",
]
