"""
Main gastronomy agent definition for the voice assistant.
This agent handles all gastronomy-related queries and interactions.
"""

from agents import Agent  # type: ignore

from ..config import settings
from ..tools import get_order_status, make_reservation, place_order, query_restaurant_knowledge_base

restaurant_tools = [
    query_restaurant_knowledge_base,
    place_order,
    get_order_status,
    make_reservation,
]

gastronomy_agent = Agent(
    name=settings.AGENT_NAME,
    instructions=settings.AGENT_INSTRUCTIONS,
    tools=restaurant_tools,
)
