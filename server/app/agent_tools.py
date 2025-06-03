"""
Custom function tools for the gastronomy voice assistant.
These tools allow the assistant to perform restaurant-specific actions.
"""

import traceback
from datetime import datetime

import dateparser
from agents import function_tool

from app.crud import (
    create_booking as crud_create_booking,
)
from app.crud import (
    create_order as crud_create_order,
)
from app.crud import (
    get_menu_items_by_name_fuzzy as crud_get_menu_items_by_name_fuzzy,
)
from app.crud import (
    get_order as crud_get_order,
)
from app.database import SessionLocal
from app.items import ReservationInput
from app.knowledge_base import get_knowledge_base
from app.models import BookingCreate, OrderCreate, OrderItemCreate
from app.utils import log_debug, log_error


@function_tool
def place_order(items: list[OrderItemCreate], table_number: int, notes: str | None = None) -> str:
    """
    Places a food or drink order for a given table.
    Requires a list of order items, each specifying menu_item_id,
    quantity, and optional special requests.
    Optionally, general notes for the order can be provided.
    """
    log_debug(
        'Tool: place_order called with table_number: %s, items: %s, notes: %s',
        table_number,
        items,
        notes,
    )
    db = SessionLocal()
    try:
        order_payload = OrderCreate(table_number=table_number, items=items, notes=notes)

        created_order = crud_create_order(db=db, order=order_payload)

        item_count = sum(item.quantity for item in created_order.items)

        return (
            f'Order placed successfully for table {table_number}. '
            f'Order ID: {created_order.id}. Total items ordered: {item_count}. '
            f'Status: {created_order.status.value}.'
        )
    except ValueError as ve:
        log_error('Validation error in place_order tool: %s\n%s', ve, traceback.format_exc())
        return f"Sorry, I couldn't place the order. {str(ve)}"
    except Exception as e:
        log_error('Error in place_order tool: %s\n%s', e, traceback.format_exc())
        return (
            'Sorry, I encountered an error while trying to place your order. '
            'Please try again later.'
        )
    finally:
        db.close()


@function_tool
def get_order_status(order_id: int) -> str:
    """Check the status of an order using its unique order ID."""
    log_debug('Tool: get_order_status called with order_id: %s', order_id)
    db = SessionLocal()
    try:
        order = crud_get_order(db=db, order_id=order_id)
        if not order:
            return f'No order found with ID {order_id}.'

        items_summary = []
        if order.items:
            for item in order.items:
                items_summary.append(f'{item.quantity}x (Item ID: {item.menu_item_id})')

        items_desc = ', '.join(items_summary) if items_summary else 'No items in this order.'

        return (
            f'Order ID: {order.id} for table {order.table_number} is currently '
            f'{order.status.value}. Items: {items_desc}. Last updated: {order.updated_at}.'
        )
    except Exception as e:
        log_error('Error in get_order_status tool: %s\n%s', e, traceback.format_exc())
        return (
            'Sorry, I encountered an error while trying to check the order status. '
            'Please try again later.'
        )
    finally:
        db.close()


@function_tool
def make_reservation(reservation_input: ReservationInput) -> str:
    """Make a table reservation using the restaurant's booking system."""
    log_debug('Tool: make_reservation called with input: %s', reservation_input)

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
        log_error('Error in make_reservation tool: %s\n%s', e, traceback.format_exc())
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


@function_tool
def convert_natural_date_to_iso(raw_date: str) -> str | None:
    """
    Convert a natural language date to ISO 8601 format (YYYY-MM-DD).
    This tool is used to convert natural language dates to ISO 8601 format.
    Example:
        - "jutro" -> "2025-05-31"
        - "w przyszły poniedziałek" -> "2025-06-02"

    Args:
        raw_date: Raw text representation of the date (e.g., "jutro", "w przyszły poniedziałek")

    Returns:
        Converted date in ISO format, or None if parsing fails
    """
    if not raw_date:
        return None

    today = datetime.today()
    parsed_date = dateparser.parse(raw_date, settings={'RELATIVE_BASE': today})

    return parsed_date.strftime('%Y_%m_%d') if parsed_date else None


@function_tool
def find_menu_item_by_name(item_name: str) -> str:
    """
    Finds menu items by their name using a fuzzy search (case-insensitive, partial match).
    Returns a list of matching items with their ID,
    name, and price, or a message if no items are found.
    If multiple items are found, the agent should ask the user for clarification.
    Args:
        item_name: The name of the menu item to search for (e.g., "pierogi", "zupa pomidorowa").
    """
    log_debug("Tool: find_menu_item_by_name called with item_name: '%s'", item_name)
    db = SessionLocal()
    try:
        menu_items = crud_get_menu_items_by_name_fuzzy(db=db, name_query=item_name, limit=5)

        if not menu_items:
            return (
                f"No menu items found matching '{item_name}'. "
                'Please ask the user to try a different name or check the menu '
                '(e.g., using query_restaurant_database).'
            )

        if len(menu_items) == 1:
            item = menu_items[0]
            return (
                f'Found one item: ID: {item.id}, Name: {item.name}, Price: {item.price:.2f} PLN. '
                'You can use this ID to add the item to an order.'
            )

        response_parts = [
            'Found multiple items matching your query. '
            'Please ask the user to specify which one they mean:'
        ]
        for item in menu_items:
            response_parts.append(
                f'- ID: {item.id}, Name: {item.name}, Price: {item.price:.2f} PLN'
            )
        return '\n'.join(response_parts)

    except Exception as e:
        log_error('Error in find_menu_item_by_name tool: %s\n%s', e, traceback.format_exc())
        return (
            f'Sorry, I encountered an error while trying to find menu items matching '
            f"'{item_name}'. "
            'Please try again.'
        )
    finally:
        db.close()
