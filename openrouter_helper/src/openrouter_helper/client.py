"""OpenRouter API client."""

import os
from typing import List, Optional
import requests
from .models import Model


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key. If not provided, reads from OPENROUTER_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            # Allow initialization without key for public endpoints
            pass

    def _get_headers(self) -> dict:
        """Get headers for API requests."""
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def get_models(self, supported_parameters: Optional[List[str]] = None) -> List[Model]:
        """
        Fetch all available models from OpenRouter.

        Args:
            supported_parameters: Optional list of required parameters (e.g., ['temperature', 'top_p'])

        Returns:
            List of Model objects
        """
        url = f"{self.BASE_URL}/models"
        params = {}
        if supported_parameters:
            params["supported_parameters"] = ",".join(supported_parameters)

        response = requests.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()

        data = response.json()
        models = []

        for model_data in data.get("data", []):
            try:
                model = Model(**model_data)
                models.append(model)
            except Exception as e:
                # Skip models that don't parse correctly
                print(f"Warning: Failed to parse model {model_data.get('id', 'unknown')}: {e}")
                continue

        return models

    def get_model(self, model_id: str) -> Optional[Model]:
        """
        Get a specific model by ID.

        Args:
            model_id: The model identifier (e.g., 'openai/gpt-4')

        Returns:
            Model object or None if not found
        """
        models = self.get_models()
        for model in models:
            if model.id == model_id:
                return model
        return None
