from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    AllergenCreate,
    AllergenDB,
    BookingCreate,
    BookingDB,
    BookingStatusEnum,
    BookingUpdate,
    EmailStr,
    FaqCreate,
    FaqDB,
    HttpUrl,
    MenuCategoryCreate,
    MenuCategoryDB,
    MenuItemCreate,
    MenuItemDB,
    OrderCreate,
    OrderDB,
    OrderItemCreate,
    OrderItemDB,
    OrderStatusEnum,
    OrderUpdate,
    RestaurantInfoCreate,
    RestaurantInfoDB,
    SpecialOfferCreate,
    SpecialOfferDB,
)


def get_restaurant_info(db: Session, info_id: int) -> RestaurantInfoDB | None:
    return db.query(RestaurantInfoDB).filter(RestaurantInfoDB.id == info_id).first()


def get_all_restaurant_info(db: Session, skip: int = 0, limit: int = 100) -> list[RestaurantInfoDB]:
    return db.query(RestaurantInfoDB).offset(skip).limit(limit).all()


def get_first_restaurant_info(db: Session) -> RestaurantInfoDB | None:
    return db.query(RestaurantInfoDB).first()


def create_restaurant_info(db: Session, info: RestaurantInfoCreate) -> RestaurantInfoDB:
    info_data = info.model_dump()
    if isinstance(info_data.get('website'), HttpUrl):
        info_data['website'] = str(info_data['website'])
    if isinstance(info_data.get('email'), EmailStr):
        info_data['email'] = str(info_data['email'])

    db_info = RestaurantInfoDB(**info_data)
    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    return db_info


def update_restaurant_info(
    db: Session, info_id: int, info_update: RestaurantInfoCreate
) -> RestaurantInfoDB | None:
    db_info = get_restaurant_info(db, info_id)
    if db_info:
        update_data = info_update.model_dump(exclude_unset=True)
        if 'website' in update_data and isinstance(update_data['website'], HttpUrl):
            update_data['website'] = str(update_data['website'])
        if 'email' in update_data and isinstance(update_data['email'], EmailStr):
            update_data['email'] = str(update_data['email'])

        for key, value in update_data.items():
            setattr(db_info, key, value)
        db.commit()
        db.refresh(db_info)
    return db_info


def delete_restaurant_info(db: Session, info_id: int) -> RestaurantInfoDB | None:
    db_info = get_restaurant_info(db, info_id)
    if db_info:
        db.delete(db_info)
        db.commit()
    return db_info


def get_allergen(db: Session, allergen_id: int) -> AllergenDB | None:
    return db.query(AllergenDB).filter(AllergenDB.id == allergen_id).first()


def get_allergen_by_name(db: Session, name: str) -> AllergenDB | None:
    return db.query(AllergenDB).filter(AllergenDB.name == name).first()


def get_allergens(db: Session, skip: int = 0, limit: int = 100) -> list[AllergenDB]:
    return db.query(AllergenDB).offset(skip).limit(limit).all()


def create_allergen(db: Session, allergen: AllergenCreate) -> AllergenDB:
    db_allergen = AllergenDB(name=allergen.name)
    db.add(db_allergen)
    db.commit()
    db.refresh(db_allergen)
    return db_allergen


def get_menu_category(db: Session, category_id: int) -> MenuCategoryDB | None:
    return db.query(MenuCategoryDB).filter(MenuCategoryDB.id == category_id).first()


def get_menu_category_by_name(db: Session, name: str) -> MenuCategoryDB | None:
    return db.query(MenuCategoryDB).filter(MenuCategoryDB.name == name).first()


def get_menu_categories(db: Session, skip: int = 0, limit: int = 100) -> list[MenuCategoryDB]:
    return db.query(MenuCategoryDB).offset(skip).limit(limit).all()


def create_menu_category(db: Session, category: MenuCategoryCreate) -> MenuCategoryDB:
    db_category = MenuCategoryDB(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_menu_item(db: Session, item_id: int) -> MenuItemDB | None:
    return db.query(MenuItemDB).filter(MenuItemDB.id == item_id).first()


def get_menu_items(db: Session, skip: int = 0, limit: int = 100) -> list[MenuItemDB]:
    return db.query(MenuItemDB).offset(skip).limit(limit).all()


def get_menu_items_by_category(
    db: Session, category_id: int, skip: int = 0, limit: int = 100
) -> list[MenuItemDB]:
    return (
        db.query(MenuItemDB)
        .filter(MenuItemDB.category_id == category_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_menu_items_by_name_fuzzy(
    db: Session, name_query: str, skip: int = 0, limit: int = 10
) -> list[MenuItemDB]:
    """Fetches menu items by a fuzzy (case-insensitive, partial) name match."""
    return (
        db.query(MenuItemDB)
        .filter(MenuItemDB.name.ilike(f'%{name_query}%'))
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_menu_item(db: Session, item: MenuItemCreate, category_id: int) -> MenuItemDB:
    db_item = MenuItemDB(
        name=item.name,
        description=item.description,
        price=item.price,
        options=item.options,
        category_id=category_id,
    )

    if item.allergen_names:
        for allergen_name in item.allergen_names:
            allergen_db = get_allergen_by_name(db, allergen_name)
            if not allergen_db:
                allergen_db = create_allergen(db, AllergenCreate(name=allergen_name))
            db_item.allergens.append(allergen_db)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_menu_item(db: Session, item_id: int, item_update: MenuItemCreate) -> MenuItemDB | None:
    db_item = get_menu_item(db, item_id)
    if db_item:
        update_data = item_update.model_dump(exclude_unset=True)

        if 'allergen_names' in update_data:
            allergen_names = update_data.pop('allergen_names')
            db_item.allergens.clear()
            if allergen_names:
                for allergen_name in allergen_names:
                    allergen_db = get_allergen_by_name(db, allergen_name)
                    if not allergen_db:
                        allergen_db = create_allergen(db, AllergenCreate(name=allergen_name))
                    db_item.allergens.append(allergen_db)

        for key, value in update_data.items():
            setattr(db_item, key, value)

        db.commit()
        db.refresh(db_item)
    return db_item


def delete_menu_item(db: Session, item_id: int) -> MenuItemDB | None:
    db_item = get_menu_item(db, item_id)
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item


def get_booking(db: Session, booking_id: int) -> BookingDB | None:
    return db.query(BookingDB).filter(BookingDB.id == booking_id).first()


def get_bookings(db: Session, skip: int = 0, limit: int = 100) -> list[BookingDB]:
    return db.query(BookingDB).offset(skip).limit(limit).all()


def get_bookings_by_date(
    db: Session, date: str, skip: int = 0, limit: int = 100
) -> list[BookingDB]:
    return (
        db.query(BookingDB).filter(BookingDB.booking_date == date).offset(skip).limit(limit).all()
    )


def create_booking(db: Session, booking: BookingCreate) -> BookingDB:
    db_booking = BookingDB(**booking.model_dump())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


def update_booking_status(
    db: Session, booking_id: int, status: BookingStatusEnum
) -> BookingDB | None:
    db_booking = get_booking(db, booking_id)
    if db_booking:
        db_booking.status = status
        db.commit()
        db.refresh(db_booking)
    return db_booking


def update_booking(db: Session, booking_id: int, booking_update: BookingUpdate) -> BookingDB | None:
    db_booking = get_booking(db, booking_id)
    if db_booking:
        update_data = booking_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_booking, key, value)
        db.commit()
        db.refresh(db_booking)
    return db_booking


def delete_booking(db: Session, booking_id: int) -> BookingDB | None:
    db_booking = get_booking(db, booking_id)
    if db_booking:
        db.delete(db_booking)
        db.commit()
    return db_booking


def get_special_offer(db: Session, offer_id: int) -> SpecialOfferDB | None:
    return db.query(SpecialOfferDB).filter(SpecialOfferDB.id == offer_id).first()


def get_special_offers(db: Session, skip: int = 0, limit: int = 100) -> list[SpecialOfferDB]:
    return db.query(SpecialOfferDB).offset(skip).limit(limit).all()


def create_special_offer(db: Session, offer: SpecialOfferCreate) -> SpecialOfferDB:
    db_offer = SpecialOfferDB(**offer.model_dump())
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    return db_offer


def update_special_offer(
    db: Session, offer_id: int, offer_update: SpecialOfferCreate
) -> SpecialOfferDB | None:
    db_offer = get_special_offer(db, offer_id)
    if db_offer:
        update_data = offer_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_offer, key, value)
        db.commit()
        db.refresh(db_offer)
    return db_offer


def delete_special_offer(db: Session, offer_id: int) -> SpecialOfferDB | None:
    db_offer = get_special_offer(db, offer_id)
    if db_offer:
        db.delete(db_offer)
        db.commit()
    return db_offer


def get_faq(db: Session, faq_id: int) -> FaqDB | None:
    return db.query(FaqDB).filter(FaqDB.id == faq_id).first()


def get_faqs(db: Session, skip: int = 0, limit: int = 100) -> list[FaqDB]:
    return db.query(FaqDB).offset(skip).limit(limit).all()


def create_faq(db: Session, faq: FaqCreate) -> FaqDB:
    db_faq = FaqDB(**faq.model_dump())
    db.add(db_faq)
    db.commit()
    db.refresh(db_faq)
    return db_faq


def update_faq(db: Session, faq_id: int, faq_update: FaqCreate) -> FaqDB | None:
    db_faq = get_faq(db, faq_id)
    if db_faq:
        update_data = faq_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_faq, key, value)
        db.commit()
        db.refresh(db_faq)
    return db_faq


def delete_faq(db: Session, faq_id: int) -> FaqDB | None:
    db_faq = get_faq(db, faq_id)
    if db_faq:
        db.delete(db_faq)
        db.commit()
    return db_faq


def get_order(db: Session, order_id: int) -> OrderDB | None:
    return db.query(OrderDB).filter(OrderDB.id == order_id).first()


def get_orders(db: Session, skip: int = 0, limit: int = 100) -> list[OrderDB]:
    return db.query(OrderDB).offset(skip).limit(limit).all()


def create_order(db: Session, order: OrderCreate) -> OrderDB:
    order_items_db = []
    for item_create in order.items:
        order_item_db = OrderItemDB(
            menu_item_id=item_create.menu_item_id,
            quantity=item_create.quantity,
            special_requests=item_create.special_requests,
        )
        order_items_db.append(order_item_db)

    db_order = OrderDB(
        table_number=order.table_number,
        status=OrderStatusEnum.PENDING,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        notes=order.notes,
        items=order_items_db,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def update_order_status(db: Session, order_id: int, status: OrderStatusEnum) -> OrderDB | None:
    db_order = get_order(db, order_id)
    if db_order:
        db_order.status = status
        db_order.updated_at = datetime.utcnow().isoformat()
        db.commit()
        db.refresh(db_order)
    return db_order


def update_order(db: Session, order_id: int, order_update: OrderUpdate) -> OrderDB | None:
    db_order = get_order(db, order_id)
    if db_order:
        update_data = order_update.model_dump(exclude_unset=True)

        if 'items' in update_data and update_data['items'] is not None:
            for item in db_order.items:
                db.delete(item)
            db.commit()

            new_items_db = []
            for item_create_data in update_data['items']:
                item_create = (
                    OrderItemCreate(**item_create_data)
                    if isinstance(item_create_data, dict)
                    else item_create_data
                )

                order_item_db = OrderItemDB(
                    order_id=db_order.id,
                    menu_item_id=item_create.menu_item_id,
                    quantity=item_create.quantity,
                    special_requests=item_create.special_requests,
                )
                new_items_db.append(order_item_db)
            db_order.items = new_items_db

        update_data.pop('items', None)

        for key, value in update_data.items():
            setattr(db_order, key, value)

        db_order.updated_at = datetime.utcnow().isoformat()
        db.commit()
        db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int) -> OrderDB | None:
    db_order = get_order(db, order_id)
    if db_order:
        db.delete(db_order)
        db.commit()
    return db_order
