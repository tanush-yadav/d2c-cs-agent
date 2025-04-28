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
Tools for the customer service agent.

This module exports all tool functions for the customer service agent,
organized by category:
- General tools: discount approval, communication tools
- Cart management: cart access and modification
- Product tools: recommendations and availability checking
- Service tools: scheduling and service information
- Order tools: order tracking and management
"""

from .tools import (
    access_cart_information,
    approve_discount,
    check_product_availability,
    generate_qr_code,
    get_available_planting_times,
    get_product_recommendations,
    modify_cart,
    schedule_planting_service,
    send_call_companion_link,
    send_care_instructions,
    sync_ask_for_approval,
    update_salesforce_crm,
)

from .order import (
    get_order,
    track_package,
    get_recent_orders,
    handle_delivery_request,
)

__all__ = [
    # General tools
    "send_call_companion_link",
    "approve_discount",
    "sync_ask_for_approval",
    "update_salesforce_crm",

    # Cart management tools
    "access_cart_information",
    "modify_cart",

    # Product tools
    "get_product_recommendations",
    "check_product_availability",

    # Service tools
    "schedule_planting_service",
    "get_available_planting_times",
    "send_care_instructions",
    "generate_qr_code",

    # Order tools
    "get_order",
    "track_package",
    "get_recent_orders",
    "handle_delivery_request",
]
