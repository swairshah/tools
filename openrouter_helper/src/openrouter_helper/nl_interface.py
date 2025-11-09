"""Natural language interface for querying OpenRouter models using DSPy."""

import os
from typing import List, Optional
import dspy
from pydantic import BaseModel, Field

from .client import OpenRouterClient
from .models import Model
from .query import ModelQuery


class QueryPlan(BaseModel):
    """Structured query plan for filtering models."""

    input_price_max: Optional[float] = Field(
        default=None,
        description="Maximum input price per million tokens in USD"
    )
    output_price_max: Optional[float] = Field(
        default=None,
        description="Maximum output price per million tokens in USD"
    )
    input_price_min: Optional[float] = Field(
        default=None,
        description="Minimum input price per million tokens in USD"
    )
    output_price_min: Optional[float] = Field(
        default=None,
        description="Minimum output price per million tokens in USD"
    )
    context_length_min: Optional[int] = Field(
        default=None,
        description="Minimum context length in tokens"
    )
    name_contains: Optional[str] = Field(
        default=None,
        description="Text that should be in the model name"
    )
    id_contains: Optional[str] = Field(
        default=None,
        description="Text that should be in the model ID"
    )


class ModelQuerySignature(dspy.Signature):
    """Parse a natural language query about OpenRouter models into a structured query plan.

    Examples:
    - "list models where input price < 0.5, output price < 1"
    - "find models with context length > 100000"
    - "show me GPT models that cost less than $2 per million tokens"
    - "cheap models for text generation"
    - "find Claude models with low pricing"

    Note: Prices are per million tokens unless otherwise specified.
    """

    natural_query: str = dspy.InputField(desc="Natural language query about models")
    query_plan: QueryPlan = dspy.OutputField(desc="Structured query plan")


class NaturalLanguageQuery:
    """Natural language interface for querying OpenRouter models."""

    def __init__(
        self,
        client: Optional[OpenRouterClient] = None,
        lm_model: str = "openai/gpt-4o-mini",
        api_key: Optional[str] = None,
    ):
        """
        Initialize natural language query interface.

        Args:
            client: OpenRouter client. If not provided, creates a new one.
            lm_model: Language model to use for parsing queries (via OpenRouter)
            api_key: API key for the language model (defaults to OPENROUTER_API_KEY env var)
        """
        self.client = client or OpenRouterClient()

        # Configure DSPy to use OpenRouter
        if api_key is None:
            api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError(
                "API key required for natural language interface. "
                "Set OPENROUTER_API_KEY environment variable or pass api_key parameter."
            )

        # DSPy LM with OpenRouter
        lm = dspy.LM(
            model=lm_model,
            api_key=api_key,
            api_base="https://openrouter.ai/api/v1",
            temperature=0.0,  # Deterministic parsing
        )
        dspy.configure(lm=lm)

        # Create predictor
        self.predictor = dspy.Predict(ModelQuerySignature)

    def query(self, natural_query: str) -> List[Model]:
        """
        Execute a natural language query.

        Args:
            natural_query: Natural language query string
                Examples:
                - "list models where input price < 0.5, output price < 1"
                - "find models with context length > 100000"
                - "show me Claude models under $5 per million output tokens"

        Returns:
            List of models matching the query
        """
        # Parse natural language to structured query
        result = self.predictor(natural_query=natural_query)
        plan: QueryPlan = result.query_plan

        # Build query using structured plan
        query = ModelQuery(client=self.client)

        if plan.input_price_max is not None:
            query = query.where_input_price_less_than(plan.input_price_max)

        if plan.output_price_max is not None:
            query = query.where_output_price_less_than(plan.output_price_max)

        if plan.input_price_min is not None:
            query = query.where_input_price_greater_than(plan.input_price_min)

        if plan.output_price_min is not None:
            query = query.where_output_price_greater_than(plan.output_price_min)

        if plan.context_length_min is not None:
            query = query.where_context_length_greater_than(plan.context_length_min)

        if plan.name_contains:
            query = query.where_name_contains(plan.name_contains)

        if plan.id_contains:
            query = query.where_id_contains(plan.id_contains)

        return query.list_models()

    def get_query_plan(self, natural_query: str) -> QueryPlan:
        """
        Parse a natural language query and return the structured query plan.

        Useful for debugging or understanding how the query was interpreted.

        Args:
            natural_query: Natural language query string

        Returns:
            Structured query plan
        """
        result = self.predictor(natural_query=natural_query)
        return result.query_plan
