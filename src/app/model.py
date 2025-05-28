from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    """Model for an order item."""

    item_name: str = Field(description='Name of the food or drink item')
    quantity: int = Field(description='Quantity of the item', ge=1)
    special_requests: str | None = Field(None, description='Any special requests for this item')


class TableOrder(BaseModel):
    """Model for storing orders by table."""

    table_number: int
    items: list[OrderItem] = []
    status: str = 'pending'  # pending, in-progress, served, paid


class Reservation(BaseModel):
    """Model for a table reservation."""

    name: str = Field(description='Name for the reservation')
    date: str = Field(description='Date of reservation (YYYY-MM-DD)')
    time: str = Field(description='Time of reservation (HH:MM)')
    guests: int = Field(description='Number of guests', ge=1)
    contact: str = Field(description='Contact phone number')
    special_requests: str | None = Field(None, description='Any special requests')
