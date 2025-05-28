"""
Custom function tools for the gastronomy voice assistant.
These tools allow the assistant to perform restaurant-specific actions.
"""

import traceback
from logging import getLogger

from agents import function_tool
from langchain.schema import Document

from app.knowledge_base import get_restaurant_retriever
from app.model import OrderItem, Reservation, TableOrder

logger = getLogger(__name__)


# In-memory store for orders
_orders: dict[int, TableOrder] = {}
# In-memory store for reservations
_reservations = []


@function_tool
def place_order(items: list[OrderItem], table_number: int) -> str:
    """Places a food or drink order for a given table."""
    # Check if table already has an order
    if table_number in _orders:
        # Add to existing order
        _orders[table_number].items.extend(items)
        _orders[table_number].status = 'pending'
    else:
        # Create new order
        _orders[table_number] = TableOrder(table_number=table_number, items=items)

    # Format response
    ordered_items = ', '.join([f'{item.quantity}x {item.item_name}' for item in items])
    return f'Order placed successfully for table {table_number}. Ordered items: {ordered_items}'


@function_tool
def get_order_status(table_number: int) -> str:
    """Check the status of an order for a specific table."""
    if table_number not in _orders:
        return f'No active order found for table {table_number}.'

    order = _orders[table_number]
    items_list = ', '.join([f'{item.quantity}x {item.item_name}' for item in order.items])
    return f'Order for table {table_number} is {order.status}. Items: {items_list}'


@function_tool
def make_reservation(reservation: Reservation) -> str:
    """Make a table reservation."""
    _reservations.append(reservation)
    return (
        f'Reservation confirmed for {reservation.name} on {reservation.date} at {reservation.time} '
        f"for {reservation.guests} guests. We'll contact you at {reservation.contact} if needed."
    )


# ---- Knowledge Base Tool (Langchain based) ----
@function_tool
async def query_restaurant_knowledge_base(query: str) -> str:
    """
    Queries the Poligon Smaków WAT restaurant's knowledge base (data.md) to answer questions
    about the menu, opening hours, location, address, phone number, accepted payment methods,
    parking, summer garden, reservation policy, special offers, and FAQs.
    Use this tool ONLY when the user asks a specific question about
    the Poligon Smaków WAT restaurant that can likely be found in its documented information.
    This is the PREFERRED tool for all informational queries.
    Do not use it for general conversation or
    for actions like placing orders or making reservations.

    Args:
        query: The user's specific question about the restaurant.

    Returns:
        A string containing the relevant information found to answer the query,
        or a message indicating that no specific information was found for that query.
    """
    logger.debug("Tool: query_restaurant_knowledge_base attempting to answer query: '%s'", query)

    try:
        retriever = get_restaurant_retriever()
        documents: list[Document] = await retriever.ainvoke(query)

        if not documents:
            return (
                'No specific information was found in the knowledge base for your query '
                'about the restaurant.'
            )

        context = '\n\n'.join([doc.page_content for doc in documents])
        return f"Relevant information from the knowledge base for the query '{query}':\n{context}"
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.exception(
            'Error in query_restaurant_knowledge_base: %s\n%s', e, traceback.format_exc()
        )
        return (
            "Sorry, I encountered an error while trying to access the restaurant's information "
            'using the knowledge base.'
        )
