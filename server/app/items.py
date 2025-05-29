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


class ReservationInput(BaseModel):
    """Model for providing reservation details to the agent tool."""

    customer_name: str = Field(description='Name for the reservation')
    booking_date: str = Field(description='Date of reservation (YYYY-MM-DD)')
    booking_time: str = Field(description='Time of reservation (HH:MM)')
    party_size: int = Field(description='Number of guests', ge=1)
    customer_phone: str = Field(description='Contact phone number')
    customer_email: str | None = Field(None, description='Contact email address (optional)')
    special_requests: str | None = Field(None, description='Any special requests (optional)')
