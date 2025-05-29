"""
Custom function tools for the gastronomy voice assistant.
These tools allow the assistant to perform restaurant-specific actions.
"""

import traceback

from agents import function_tool

from app.crud import create_booking as crud_create_booking
from app.database import SessionLocal
from app.items import OrderItem, ReservationInput, TableOrder
from app.knowledge_base import get_knowledge_base
from app.models import BookingCreate
from app.utils import log_debug, log_error

_orders: dict[int, TableOrder] = {}


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
def make_reservation(reservation_input: ReservationInput) -> str:
    """Make a table reservation using the restaurant's booking system."""
    log_debug(f'Tool: make_reservation called with input: {reservation_input}')

    db = SessionLocal()
    try:
        booking_data = BookingCreate(
            customer_name=reservation_input.customer_name,
            customer_phone=reservation_input.customer_phone,
            customer_email=reservation_input.customer_email,
            booking_date=reservation_input.booking_date,
            booking_time=reservation_input.booking_time,
            party_size=reservation_input.party_size,
            special_requests=reservation_input.special_requests,
        )

        created_booking = crud_create_booking(db=db, booking=booking_data)

        return (
            f'Reservation confirmed for {created_booking.customer_name} '
            f'on {created_booking.booking_date} at {created_booking.booking_time} '
            f'for {created_booking.party_size} guests. Booking ID: {created_booking.id}. '
            f'Status: {created_booking.status.value}. We will contact you at '
            f'{created_booking.customer_phone} if needed.'
        )
    except Exception as e:
        log_error(f'Error in make_reservation tool: {e}\n{traceback.format_exc()}')
        return (
            'Sorry, I encountered an error while trying to make your reservation. '
            'Please try again later.'
        )
    finally:
        db.close()


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
