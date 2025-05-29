import enum

from pydantic import BaseModel, EmailStr, HttpUrl
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base


class BookingStatusEnum(str, enum.Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'


class RestaurantInfoDB(Base):
    __tablename__ = 'restaurant_info'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    opening_hours_weekday = Column(String)
    opening_hours_weekend = Column(String)
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    cuisine_type = Column(String)
    payment_methods = Column(String)
    parking_available = Column(Boolean)
    summer_garden_available = Column(Boolean)
    reservations_info = Column(Text)


class MenuCategoryDB(Base):
    __tablename__ = 'menu_categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    items = relationship('MenuItemDB', back_populates='category')


class AllergenDB(Base):
    __tablename__ = 'allergens'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    menu_items = relationship(
        'MenuItemDB', secondary='menu_item_allergen_association', back_populates='allergens'
    )


menu_item_allergen_association = Table(
    'menu_item_allergen_association',
    Base.metadata,
    Column('menu_item_id', Integer, ForeignKey('menu_items.id'), primary_key=True),
    Column('allergen_id', Integer, ForeignKey('allergens.id'), primary_key=True),
)


class MenuItemDB(Base):
    __tablename__ = 'menu_items'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float)
    category_id = Column(Integer, ForeignKey('menu_categories.id'))
    options = Column(String, nullable=True)

    category = relationship('MenuCategoryDB', back_populates='items')
    allergens = relationship(
        'AllergenDB', secondary=menu_item_allergen_association, back_populates='menu_items'
    )


class BookingDB(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    customer_email = Column(String, nullable=True)
    booking_date = Column(String, nullable=False)
    booking_time = Column(String, nullable=False)
    party_size = Column(Integer, nullable=False)
    special_requests = Column(Text, nullable=True)
    status = Column(SAEnum(BookingStatusEnum), default=BookingStatusEnum.PENDING, nullable=False)


class SpecialOfferDB(Base):
    __tablename__ = 'special_offers'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    price_info = Column(String, nullable=True)
    validity = Column(String, nullable=True)
    details = Column(Text, nullable=True)


class FaqDB(Base):
    __tablename__ = 'faqs'
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, unique=True, index=True, nullable=False)
    answer = Column(Text, nullable=False)


# --- Pydantic Schemas ---


class OrmBaseModel(BaseModel):
    class Config:
        from_attributes = True


class RestaurantInfoBase(OrmBaseModel):
    name: str
    address: str
    opening_hours_weekday: str
    opening_hours_weekend: str
    phone: str
    email: EmailStr
    website: HttpUrl | None = None
    cuisine_type: str
    payment_methods: str
    parking_available: bool
    summer_garden_available: bool
    reservations_info: str


class RestaurantInfoCreate(RestaurantInfoBase):
    pass


class RestaurantInfo(RestaurantInfoBase):
    id: int


class AllergenBase(OrmBaseModel):
    name: str


class AllergenCreate(AllergenBase):
    pass


class Allergen(AllergenBase):
    id: int


class MenuItemBase(OrmBaseModel):
    name: str
    description: str | None = None
    price: float
    category_id: int
    options: str | None = None


class MenuItemCreate(MenuItemBase):
    allergen_names: list[str] | None = []


class MenuItem(MenuItemBase):
    id: int
    allergens: list[Allergen] = []


class MenuCategoryBase(OrmBaseModel):
    name: str


class MenuCategoryCreate(MenuCategoryBase):
    pass


class MenuCategory(MenuCategoryBase):
    id: int
    items: list[MenuItem] = []


# Booking Schemas
class BookingBase(OrmBaseModel):
    customer_name: str
    customer_phone: str
    customer_email: EmailStr | None = None
    booking_date: str
    booking_time: str
    party_size: int
    special_requests: str | None = None


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BookingBase):
    status: BookingStatusEnum | None = None


class Booking(BookingBase):
    id: int
    status: BookingStatusEnum


class SpecialOfferBase(OrmBaseModel):
    title: str
    description: str
    price_info: str | None = None
    validity: str | None = None
    details: str | None = None


class SpecialOfferCreate(SpecialOfferBase):
    pass


class SpecialOffer(SpecialOfferBase):
    id: int


class FaqBase(OrmBaseModel):
    question: str
    answer: str


class FaqCreate(FaqBase):
    pass


class Faq(FaqBase):
    id: int
