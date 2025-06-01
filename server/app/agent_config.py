"""
Specialized agents for specific gastronomy tasks.
These agents handle specific aspects of the restaurant experience.
"""

from agents import Agent
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions

from app.agent_tools import (
    convert_natural_date_to_iso,
    find_menu_item_by_name,
    get_order_status,
    make_reservation,
    place_order,
    query_restaurant_database,
)
from app.settings import (
    AGENT_NAME,
    INFORMATION_AGENT_INSTRUCTIONS,
    ORDER_AGENT_INSTRUCTIONS,
    RESERVATION_AGENT_INSTRUCTIONS,
    TRIAGE_AGENT_INSTRUCTIONS,
)

information_agent = Agent(
    name='Restaurant Information Specialist',
    handoff_description=(
        'Specialist for answering questions about the restaurant, menu, and services.'
    ),
    instructions=prompt_with_handoff_instructions(INFORMATION_AGENT_INSTRUCTIONS),
    model='gpt-4o-mini',
    tools=[query_restaurant_database],
    handoffs=[],
)


order_agent = Agent(
    name='Order Taker',
    handoff_description='Specialist for taking food and drink orders',
    instructions=prompt_with_handoff_instructions(ORDER_AGENT_INSTRUCTIONS),
    model='gpt-4o-mini',
    tools=[place_order, get_order_status, find_menu_item_by_name],
    handoffs=[],
)


reservation_agent = Agent(
    name='Reservation Manager',
    handoff_description='Specialist for handling table reservations',
    instructions=prompt_with_handoff_instructions(RESERVATION_AGENT_INSTRUCTIONS),
    model='gpt-4o-mini',
    tools=[
        make_reservation,
        convert_natural_date_to_iso,
    ],
    handoffs=[],
)


triage_agent = Agent(
    name=AGENT_NAME,
    instructions=prompt_with_handoff_instructions(TRIAGE_AGENT_INSTRUCTIONS),
    handoffs=[],
)

information_agent.handoffs = [triage_agent]
order_agent.handoffs = [triage_agent]
reservation_agent.handoffs = [triage_agent]
triage_agent.handoffs = [order_agent, reservation_agent, information_agent]


starting_agent = triage_agent
