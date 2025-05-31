"""
Custom function tools for the gastronomy voice assistant.
These tools allow the assistant to perform restaurant-specific actions.
"""

import traceback

from agents import function_tool

from app.knowledge_base import get_knowledge_base
from app.model import OrderItem, Reservation, TableOrder
from app.utils import log_debug, log_error

# In-memory store for orders
_orders: dict[int, TableOrder] = {}
# In-memory store for reservations
_reservations: list[Reservation] = []


@function_tool
def place_order(items: list[OrderItem], table_number: int) -> str:
    """Places a food or drink order for a given table."""
    if table_number in _orders:
        _orders[table_number].items.extend(items)
        _orders[table_number].status = 'pending'
    else:
        _orders[table_number] = TableOrder(table_number=table_number, items=items)

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
        f'for {reservation.guests} guests. We will contact you at {reservation.contact} if needed.'
    )


@function_tool
def query_restaurant_database(query: str) -> str:
    """
    Queries the Poligon Smaków WAT restaurant's live database for factual information.
    Use this for specific questions about the menu details (prices, descriptions, allergens),
    restaurant opening hours, address, phone, payment methods, parking, summer garden,
    reservation info, current special offers, and FAQs.
    This tool provides the most up-to-date information directly from the database.
    Example query:
        - "What are the allergens in Pierogi Ruskie?"
        - "What are the opening hours today?"

    Args:
        query: The user's specific question.

    Returns:
        A string containing the relevant information from the database,
        or a message indicating an issue.
    """
    log_debug(
        "Tool: query_restaurant_database attempting to answer query: '%s' by fetching full context",
        query,
    )
    try:
        kb = get_knowledge_base()
        full_context = kb.get_full_context_as_text()
        if not full_context.strip():
            return "The restaurant's information is currently unavailable in the database."

        return f'Full information from the restaurant database:\n{full_context}'
    except Exception as e:  # pylint: disable=broad-exception-caught
        log_error('Error in query_restaurant_database: %s\n%s', e, traceback.format_exc())
        return (
            "Sorry, I encountered an error while trying to access the restaurant's information "
            'from the database.'
        )
