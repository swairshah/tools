"""Data models for OpenRouter API responses."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ModelPricing(BaseModel):
    """Pricing information for a model."""

    prompt: float = Field(description="Cost per token for input (prompt), in USD")
    completion: float = Field(description="Cost per token for output (completion), in USD")
    request: Optional[float] = Field(default=None, description="Cost per request, in USD")
    image: Optional[float] = Field(default=None, description="Cost per image, in USD")


class ModelArchitecture(BaseModel):
    """Architecture information for a model."""

    modality: str = Field(description="Model modality (e.g., 'text', 'multimodal')")
    tokenizer: str = Field(description="Tokenizer used by the model")
    instruct_type: Optional[str] = Field(default=None, description="Instruction format type")


class TopProvider(BaseModel):
    """Information about the top provider for a model."""

    context_length: Optional[int] = Field(default=None, description="Maximum context length")
    max_completion_tokens: Optional[int] = Field(default=None, description="Maximum completion tokens")
    is_moderated: bool = Field(default=False, description="Whether the provider moderates content")


class Model(BaseModel):
    """OpenRouter model information."""

    id: str = Field(description="Unique model identifier")
    name: str = Field(description="Human-readable model name")
    created: Optional[int] = Field(default=None, description="Creation timestamp")
    description: Optional[str] = Field(default=None, description="Model description")
    context_length: int = Field(description="Maximum context length in tokens")
    pricing: ModelPricing = Field(description="Pricing information")
    architecture: Optional[ModelArchitecture] = Field(default=None, description="Architecture details")
    top_provider: Optional[TopProvider] = Field(default=None, description="Top provider information")
    per_request_limits: Optional[Dict[str, Any]] = Field(default=None, description="Request limits")

    @property
    def input_price_per_million(self) -> float:
        """Get input price per million tokens."""
        return self.pricing.prompt * 1_000_000

    @property
    def output_price_per_million(self) -> float:
        """Get output price per million tokens."""
        return self.pricing.completion * 1_000_000
