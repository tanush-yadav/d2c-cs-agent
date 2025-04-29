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

"""Callback functions for Customer Service Agent.

This module provides callback functions for rate limiting, tool pre-processing,
and agent initialization.
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.models import LlmRequest
from google.adk.tools import BaseTool

from customer_service.entities.customer import Customer

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Rate limiting constants
RATE_LIMIT_SECS = 60
RPM_QUOTA = 10

# Get customer ID from environment or use default
DEFAULT_CUSTOMER_ID = "7730071404758"  # Fallback default
CUSTOMER_ID = os.environ.get("CUSTOMER_ID", DEFAULT_CUSTOMER_ID)


def rate_limit_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    """
    Implement a query rate limit for LLM requests.

    Ensures that no more than RPM_QUOTA requests are made within RATE_LIMIT_SECS.
    If quota is exceeded, this function will sleep to enforce the rate limit.

    Args:
        callback_context: The active callback context containing state
        llm_request: The active LLM request to be rate limited
    """
    # Fix empty text parts
    for content in llm_request.contents:
        for part in content.parts:
            if part.text == "":
                part.text = " "

    now = time.time()

    # Initialize rate limiting state if first call
    if "timer_start" not in callback_context.state:
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
        logger.debug(
            "rate_limit_callback [timestamp: %i, req_count: 1, elapsed_secs: 0]",
            now,
        )
        return

    # Update request count and calculate elapsed time
    request_count = callback_context.state["request_count"] + 1
    elapsed_secs = now - callback_context.state["timer_start"]
    logger.debug(
        "rate_limit_callback [timestamp: %i, request_count: %i, elapsed_secs: %i]",
        now,
        request_count,
        elapsed_secs,
    )

    # Apply rate limiting if quota exceeded
    if request_count > RPM_QUOTA:
        delay = RATE_LIMIT_SECS - elapsed_secs + 1
        if delay > 0:
            logger.debug("Sleeping for %i seconds", delay)
            time.sleep(delay)
        # Reset timer and counter after delay
        callback_context.state["timer_start"] = time.time()
        callback_context.state["request_count"] = 1
    else:
        callback_context.state["request_count"] = request_count


def lowercase_value(value: Any) -> Any:
    """
    Recursively convert string values to lowercase in various data structures.

    Args:
        value: The value to process (can be a dict, list, set, tuple, string, or other type)

    Returns:
        The processed value with all strings converted to lowercase
    """
    if isinstance(value, dict):
        return {k: lowercase_value(v) for k, v in value.items()}
    elif isinstance(value, str):
        return value.lower()
    elif isinstance(value, (list, set, tuple)):
        tp = type(value)
        return tp(lowercase_value(i) for i in value)
    else:
        return value


def before_tool(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: CallbackContext
) -> Optional[Dict[str, str]]:
    """
    Process tool arguments before tool execution.

    This callback runs before each tool execution to:
    1. Convert all string values to lowercase
    2. Apply business logic for specific tools
    3. Potentially short-circuit tool execution with predefined responses

    Args:
        tool: The tool being called
        args: The arguments being passed to the tool
        tool_context: The callback context for the tool

    Returns:
        Optional dictionary with results if short-circuiting the tool call,
        or None to continue with normal tool execution
    """
    # Normalize input values to lowercase
    args = lowercase_value(args)

    # Apply tool-specific business logic
    if tool.name == "sync_ask_for_approval":
        amount = args.get("value", None)
        if amount is not None and amount <= 10:  # Business rule
            return {
                "result": "You can approve this discount; no manager needed."
            }

    elif tool.name == "modify_cart":
        if (
            args.get("items_added") is True
            and args.get("items_removed") is True
        ):
            return {"result": "I have added and removed the requested items."}

    # Continue with normal tool execution
    return None


def before_agent(callback_context: InvocationContext) -> None:
    """
    Initialize the agent context with required state.

    This callback runs before agent processing to ensure that all necessary
    state, such as customer profiles, is loaded and available.

    Args:
        callback_context: The invocation context for the agent
    """
    # Load customer profile if not already present
    if "customer_profile" not in callback_context.state:
        callback_context.state["customer_profile"] = Customer.get_customer(
            CUSTOMER_ID
        ).to_json()

        logger.debug(f"Loaded customer profile for customer ID: {CUSTOMER_ID}")