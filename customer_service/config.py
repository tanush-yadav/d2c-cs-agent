# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Configuration module for the customer service agent.

This module defines the configuration settings for the customer service agent,
using Pydantic for validation and environment variable loading.
"""

import logging
import os
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Configure basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AgentModel(BaseModel):
    """
    Agent model settings.

    Attributes:
        name: The name of the agent instance
        model: The AI model to use for the agent
    """

    name: str = Field(
        default="customer_service_agent",
        description="Name of the agent instance"
    )
    model: str = Field(
        default="gemini-2.0-flash-001",
        description="AI model to use for the agent"
    )


class Config(BaseSettings):
    """
    Configuration settings for the customer service agent.

    Loads settings from environment variables with the prefix GOOGLE_
    and falls back to default values when not specified.

    Attributes:
        agent_settings: Settings for the agent model
        app_name: Name of the application
        CLOUD_PROJECT: GCP project ID
        CLOUD_LOCATION: GCP region
        GENAI_USE_VERTEXAI: Flag to use VertexAI
        API_KEY: API key for authentication
    """

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../.env"
        ),
        env_prefix="GOOGLE_",
        case_sensitive=True,
    )

    agent_settings: AgentModel = Field(
        default_factory=AgentModel,
        description="Settings for the agent model"
    )
    app_name: str = Field(
        default="customer_service_app",
        description="Name of the application"
    )
    CLOUD_PROJECT: str = Field(
        default="my_project",
        description="GCP project ID"
    )
    CLOUD_LOCATION: str = Field(
        default="us-central1",
        description="GCP region"
    )
    GENAI_USE_VERTEXAI: str = Field(
        default="1",
        description="Flag to use VertexAI (1=enabled, 0=disabled)"
    )
    API_KEY: Optional[str] = Field(
        default="",
        description="API key for authentication"
    )
