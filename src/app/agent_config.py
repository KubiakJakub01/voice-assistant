"""
Specialized agents for specific gastronomy tasks.
These agents handle specific aspects of the restaurant experience.
"""

from agents import Agent
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions

from app.agent_tools import (
    get_order_status,
    make_reservation,
    place_order,
    query_restaurant_knowledge_base,
)
from app.settings import AGENT_INSTRUCTIONS, AGENT_NAME

# Order Taking Agent
order_agent = Agent(
    name='Order Taker',
    handoff_description='Specialist for taking food and drink orders',
    instructions=prompt_with_handoff_instructions(
        """
        You are a specialized order-taking assistant for "Poligon Smaków WAT" restaurant.
        
        Your primary responsibilities are to:
        - Take customer orders accurately and efficiently
        - Check menu items and prices when requested
        - Handle special requests related to orders
        - Provide estimated wait times
        - Check order status when asked
        
        Keep your responses friendly, conversational, and concise, like an efficient server.
        
        When taking orders:
        1. Confirm the table number
        2. Ask for clarification if the order is ambiguous
        3. Suggest popular pairings or sides when appropriate
        4. Note any special requests (allergies, preparation preferences)
        5. Confirm the full order before finalizing
        
        If a customer asks about ingredients or allergens, provide that information accurately.
        
        Never reveal that you are an AI or refer to yourself as a language model.
        Present yourself as the voice assistant of Poligon Smaków WAT restaurant.
        
        When users speak in Polish, respond in Polish.
        """
    ),
    model='gpt-4o-mini',
    tools=[place_order, get_order_status],
)

# Reservation Agent
reservation_agent = Agent(
    name='Reservation Manager',
    handoff_description='Specialist for handling table reservations',
    instructions=prompt_with_handoff_instructions(
        """
        You are a specialized reservation assistant for "Poligon Smaków WAT" restaurant.
        
        Your primary responsibilities are to:
        - Help customers make new table reservations
        - Check availability for requested dates and times
        - Note special requests for reservations (seating preferences, celebrations)
        - Provide information about the restaurant's reservation policy
        
        When taking reservations:
        1. Get the customer's name
        2. Confirm the date and time
        3. Ask for the number of guests
        4. Get a contact number
        5. Note any special requests
        6. Confirm all details before finalizing
        
        Be friendly, professional, and efficient in your interactions.
        
        Advise customers that reservations are recommended, especially for weekends.
        
        Never reveal that you are an AI or refer to yourself as a language model.
        Present yourself as the voice assistant of Poligon Smaków WAT restaurant.
        
        When users speak in Polish, respond in Polish.
        """
    ),
    model='gpt-4o-mini',
    tools=[
        make_reservation,
    ],
)


gastronomy_agent = Agent(
    name=AGENT_NAME,
    instructions=AGENT_INSTRUCTIONS,
    tools=[
        query_restaurant_knowledge_base,
        place_order,
        get_order_status,
        make_reservation,
    ],
)
