from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.database import Base


class RestaurantInfo(Base):
    __tablename__ = 'restaurant_info'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    address = Column(String)
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    cuisine_type = Column(String)
    payment_methods = Column(String)  # Consider a separate table or JSON if more structured
    parking_available = Column(Boolean, default=False)
    summer_garden_available = Column(Boolean, default=False)
    reservations_info = Column(String)
    opening_hours_weekday = Column(String)
    opening_hours_weekend = Column(String)


class MenuCategory(Base):
    __tablename__ = 'menu_categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    items = relationship('MenuItem', back_populates='category')


# Association table for MenuItem and Allergen (many-to-many)
menu_item_allergen_association = Table(
    'menu_item_allergen_association',
    Base.metadata,
    Column('menu_item_id', Integer, ForeignKey('menu_items.id')),
    Column('allergen_id', Integer, ForeignKey('allergens.id')),
)


class MenuItem(Base):
    __tablename__ = 'menu_items'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float)
    category_id = Column(Integer, ForeignKey('menu_categories.id'))
    options = Column(String, nullable=True)  # e.g., "Wegetariańskie"

    category = relationship('MenuCategory', back_populates='items')
    allergens = relationship(
        'Allergen', secondary=menu_item_allergen_association, back_populates='menu_items'
    )


class Allergen(Base):
    __tablename__ = 'allergens'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    menu_items = relationship(
        'MenuItem', secondary=menu_item_allergen_association, back_populates='allergens'
    )


class SpecialOffer(Base):
    __tablename__ = 'special_offers'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    price_info = Column(String, nullable=True)
    validity = Column(String, nullable=True)
    details = Column(String, nullable=True)


class FAQ(Base):
    __tablename__ = 'faqs'

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, unique=True, index=True)
    answer = Column(String)
