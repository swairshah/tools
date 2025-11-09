"""Query interface for filtering OpenRouter models."""

from typing import List, Optional, Callable
from .models import Model
from .client import OpenRouterClient


class ModelQuery:
    """Query builder for filtering OpenRouter models."""

    def __init__(self, client: Optional[OpenRouterClient] = None):
        """
        Initialize model query.

        Args:
            client: OpenRouter client. If not provided, creates a new one.
        """
        self.client = client or OpenRouterClient()
        self._filters: List[Callable[[Model], bool]] = []

    def where_input_price_less_than(self, price: float) -> "ModelQuery":
        """
        Filter models by input price per million tokens.

        Args:
            price: Maximum input price per million tokens in USD

        Returns:
            Self for chaining
        """
        self._filters.append(lambda m: m.input_price_per_million < price)
        return self

    def where_output_price_less_than(self, price: float) -> "ModelQuery":
        """
        Filter models by output price per million tokens.

        Args:
            price: Maximum output price per million tokens in USD

        Returns:
            Self for chaining
        """
        self._filters.append(lambda m: m.output_price_per_million < price)
        return self

    def where_input_price_greater_than(self, price: float) -> "ModelQuery":
        """
        Filter models by minimum input price per million tokens.

        Args:
            price: Minimum input price per million tokens in USD

        Returns:
            Self for chaining
        """
        self._filters.append(lambda m: m.input_price_per_million > price)
        return self

    def where_output_price_greater_than(self, price: float) -> "ModelQuery":
        """
        Filter models by minimum output price per million tokens.

        Args:
            price: Minimum output price per million tokens in USD

        Returns:
            Self for chaining
        """
        self._filters.append(lambda m: m.output_price_per_million > price)
        return self

    def where_context_length_greater_than(self, length: int) -> "ModelQuery":
        """
        Filter models by minimum context length.

        Args:
            length: Minimum context length in tokens

        Returns:
            Self for chaining
        """
        self._filters.append(lambda m: m.context_length > length)
        return self

    def where_name_contains(self, text: str) -> "ModelQuery":
        """
        Filter models by name containing text (case-insensitive).

        Args:
            text: Text to search for in model name

        Returns:
            Self for chaining
        """
        self._filters.append(lambda m: text.lower() in m.name.lower())
        return self

    def where_id_contains(self, text: str) -> "ModelQuery":
        """
        Filter models by ID containing text (case-insensitive).

        Args:
            text: Text to search for in model ID

        Returns:
            Self for chaining
        """
        self._filters.append(lambda m: text.lower() in m.id.lower())
        return self

    def where(self, filter_fn: Callable[[Model], bool]) -> "ModelQuery":
        """
        Add a custom filter function.

        Args:
            filter_fn: Function that takes a Model and returns True to include it

        Returns:
            Self for chaining
        """
        self._filters.append(filter_fn)
        return self

    def list_models(self) -> List[Model]:
        """
        Execute the query and return filtered models.

        Returns:
            List of models matching all filters
        """
        models = self.client.get_models()

        for filter_fn in self._filters:
            models = [m for m in models if filter_fn(m)]

        return models

    def count(self) -> int:
        """
        Count models matching the filters.

        Returns:
            Number of matching models
        """
        return len(self.list_models())

    def first(self) -> Optional[Model]:
        """
        Get the first model matching the filters.

        Returns:
            First matching model or None
        """
        models = self.list_models()
        return models[0] if models else None
