from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import (
    create_allergen,
    create_booking,
    create_faq,
    create_menu_category,
    create_menu_item,
    create_order,
    create_restaurant_info,
    create_special_offer,
    delete_booking,
    delete_faq,
    delete_menu_item,
    delete_order,
    delete_restaurant_info,
    delete_special_offer,
    get_allergen_by_name,
    get_allergens,
    get_booking,
    get_bookings,
    get_bookings_by_date,
    get_faq,
    get_faqs,
    get_first_restaurant_info,
    get_menu_categories,
    get_menu_category,
    get_menu_category_by_name,
    get_menu_item,
    get_menu_items,
    get_menu_items_by_category,
    get_order,
    get_orders,
    get_restaurant_info,
    get_special_offer,
    get_special_offers,
    update_booking,
    update_booking_status,
    update_faq,
    update_menu_item,
    update_order,
    update_order_status,
    update_restaurant_info,
    update_special_offer,
)
from app.database import get_db
from app.models import (
    Allergen,
    AllergenCreate,
    Booking,
    BookingCreate,
    BookingStatusEnum,
    BookingUpdate,
    Faq,
    FaqCreate,
    MenuCategory,
    MenuCategoryCreate,
    MenuItem,
    MenuItemCreate,
    Order,
    OrderCreate,
    OrderStatusEnum,
    OrderUpdate,
    RestaurantInfo,
    RestaurantInfoCreate,
    SpecialOffer,
    SpecialOfferCreate,
)

router = APIRouter()


@router.post(
    '/restaurant-info/', response_model=RestaurantInfo, status_code=status.HTTP_201_CREATED
)
def create_restaurant_info_endpoint(info: RestaurantInfoCreate, db: Session = Depends(get_db)):
    existing_info = get_first_restaurant_info(db)
    if existing_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Restaurant info already exists. Use PUT to update.',
        )
    return create_restaurant_info(db=db, info=info)


@router.get('/restaurant-info/', response_model=RestaurantInfo | None)
def read_restaurant_info_endpoint(db: Session = Depends(get_db)):
    db_info = get_first_restaurant_info(db)
    return db_info


@router.get('/restaurant-info/{info_id}', response_model=RestaurantInfo)
def read_single_restaurant_info_endpoint(info_id: int, db: Session = Depends(get_db)):
    db_info = get_restaurant_info(db, info_id=info_id)
    if db_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Restaurant info not found'
        )
    return db_info


@router.put('/restaurant-info/{info_id}', response_model=RestaurantInfo)
def update_restaurant_info_endpoint(
    info_id: int, info: RestaurantInfoCreate, db: Session = Depends(get_db)
):
    db_info = update_restaurant_info(db, info_id=info_id, info_update=info)
    if db_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Restaurant info not found for updating'
        )
    return db_info


@router.delete('/restaurant-info/{info_id}', response_model=RestaurantInfo)
def delete_restaurant_info_endpoint(info_id: int, db: Session = Depends(get_db)):
    db_info = delete_restaurant_info(db, info_id=info_id)
    if db_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Restaurant info not found for deletion'
        )
    return db_info


@router.post('/menu-categories/', response_model=MenuCategory, status_code=status.HTTP_201_CREATED)
def create_menu_category_endpoint(category: MenuCategoryCreate, db: Session = Depends(get_db)):
    db_category = get_menu_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Menu category '{category.name}' already exists.",
        )
    return create_menu_category(db=db, category=category)


@router.get('/menu-categories/', response_model=list[MenuCategory])
def read_menu_categories_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = get_menu_categories(db, skip=skip, limit=limit)
    return categories


@router.get('/menu-categories/{category_id}', response_model=MenuCategory)
def read_single_menu_category_endpoint(category_id: int, db: Session = Depends(get_db)):
    db_category = get_menu_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Menu category not found')
    return db_category


@router.post('/allergens/', response_model=Allergen, status_code=status.HTTP_201_CREATED)
def create_allergen_endpoint(allergen: AllergenCreate, db: Session = Depends(get_db)):
    db_allergen = get_allergen_by_name(db, name=allergen.name)
    if db_allergen:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Allergen '{allergen.name}' already exists.",
        )
    return create_allergen(db=db, allergen=allergen)


@router.get('/allergens/', response_model=list[Allergen])
def read_allergens_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    allergens = get_allergens(db, skip=skip, limit=limit)
    return allergens


@router.post('/menu-items/', response_model=MenuItem, status_code=status.HTTP_201_CREATED)
def create_menu_item_endpoint(item: MenuItemCreate, db: Session = Depends(get_db)):
    category = get_menu_category(db, category_id=item.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Menu category with id {item.category_id} not found.',
        )
    return create_menu_item(db=db, item=item, category_id=item.category_id)


@router.get('/menu-items/', response_model=list[MenuItem])
def read_menu_items_endpoint(
    skip: int = 0, limit: int = 100, category_id: int | None = None, db: Session = Depends(get_db)
):
    if category_id is not None:
        category = get_menu_category(db, category_id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Menu category with id {category_id} not found.',
            )
        items = get_menu_items_by_category(db, category_id=category_id, skip=skip, limit=limit)
    else:
        items = get_menu_items(db, skip=skip, limit=limit)
    return items


@router.get('/menu-items/{item_id}', response_model=MenuItem)
def read_single_menu_item_endpoint(item_id: int, db: Session = Depends(get_db)):
    db_item = get_menu_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Menu item not found')
    return db_item


@router.put('/menu-items/{item_id}', response_model=MenuItem)
def update_menu_item_endpoint(item_id: int, item: MenuItemCreate, db: Session = Depends(get_db)):
    if item.category_id:
        category = get_menu_category(db, category_id=item.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Menu category with id {item.category_id} not found for update.',
            )

    updated_item = update_menu_item(db, item_id=item_id, item_update=item)
    if updated_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Menu item not found for updating'
        )
    return updated_item


@router.delete('/menu-items/{item_id}', response_model=MenuItem)
def delete_menu_item_endpoint(item_id: int, db: Session = Depends(get_db)):
    deleted_item = delete_menu_item(db, item_id=item_id)
    if deleted_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Menu item not found for deletion'
        )
    return deleted_item


@router.post('/bookings/', response_model=Booking, status_code=status.HTTP_201_CREATED)
def create_booking_endpoint(booking: BookingCreate, db: Session = Depends(get_db)):
    return create_booking(db=db, booking=booking)


@router.get('/bookings/', response_model=list[Booking])
def read_bookings_endpoint(
    skip: int = 0, limit: int = 100, date: str | None = None, db: Session = Depends(get_db)
):
    if date:
        bookings = get_bookings_by_date(db, date=date, skip=skip, limit=limit)
    else:
        bookings = get_bookings(db, skip=skip, limit=limit)
    return bookings


@router.get('/bookings/{booking_id}', response_model=Booking)
def read_single_booking_endpoint(booking_id: int, db: Session = Depends(get_db)):
    db_booking = get_booking(db, booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Booking not found')
    return db_booking


@router.put('/bookings/{booking_id}', response_model=Booking)
def update_booking_endpoint(
    booking_id: int, booking_update: BookingUpdate, db: Session = Depends(get_db)
):
    updated_booking = update_booking(db, booking_id=booking_id, booking_update=booking_update)
    if updated_booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Booking not found for updating'
        )
    return updated_booking


@router.patch('/bookings/{booking_id}/status', response_model=Booking)
def update_booking_status_endpoint(
    booking_id: int, status_update: BookingStatusEnum, db: Session = Depends(get_db)
):
    updated_booking = update_booking_status(db, booking_id=booking_id, status=status_update)
    if updated_booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Booking not found for status update'
        )
    return updated_booking


@router.delete('/bookings/{booking_id}', response_model=Booking)
def delete_booking_endpoint(booking_id: int, db: Session = Depends(get_db)):
    deleted_booking = delete_booking(db, booking_id=booking_id)
    if deleted_booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Booking not found for deletion'
        )
    return deleted_booking


@router.post('/special-offers/', response_model=SpecialOffer, status_code=status.HTTP_201_CREATED)
def create_special_offer_endpoint(offer: SpecialOfferCreate, db: Session = Depends(get_db)):
    return create_special_offer(db=db, offer=offer)


@router.get('/special-offers/', response_model=list[SpecialOffer])
def read_special_offers_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    offers = get_special_offers(db, skip=skip, limit=limit)
    return offers


@router.get('/special-offers/{offer_id}', response_model=SpecialOffer)
def read_single_special_offer_endpoint(offer_id: int, db: Session = Depends(get_db)):
    db_offer = get_special_offer(db, offer_id=offer_id)
    if db_offer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Special offer not found')
    return db_offer


@router.put('/special-offers/{offer_id}', response_model=SpecialOffer)
def update_special_offer_endpoint(
    offer_id: int, offer: SpecialOfferCreate, db: Session = Depends(get_db)
):
    updated_offer = update_special_offer(db, offer_id=offer_id, offer_update=offer)
    if updated_offer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Special offer not found for updating'
        )
    return updated_offer


@router.delete('/special-offers/{offer_id}', response_model=SpecialOffer)
def delete_special_offer_endpoint(offer_id: int, db: Session = Depends(get_db)):
    deleted_offer = delete_special_offer(db, offer_id=offer_id)
    if deleted_offer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Special offer not found for deletion'
        )
    return deleted_offer


@router.post('/faqs/', response_model=Faq, status_code=status.HTTP_201_CREATED)
def create_faq_endpoint(faq: FaqCreate, db: Session = Depends(get_db)):
    return create_faq(db=db, faq=faq)


@router.get('/faqs/', response_model=list[Faq])
def read_faqs_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    faqs = get_faqs(db, skip=skip, limit=limit)
    return faqs


@router.get('/faqs/{faq_id}', response_model=Faq)
def read_single_faq_endpoint(faq_id: int, db: Session = Depends(get_db)):
    db_faq = get_faq(db, faq_id=faq_id)
    if db_faq is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='FAQ not found')
    return db_faq


@router.put('/faqs/{faq_id}', response_model=Faq)
def update_faq_endpoint(faq_id: int, faq: FaqCreate, db: Session = Depends(get_db)):
    updated_faq = update_faq(db, faq_id=faq_id, faq_update=faq)
    if updated_faq is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='FAQ not found for updating'
        )
    return updated_faq


@router.delete('/faqs/{faq_id}', response_model=Faq)
def delete_faq_endpoint(faq_id: int, db: Session = Depends(get_db)):
    deleted_faq = delete_faq(db, faq_id=faq_id)
    if deleted_faq is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='FAQ not found for deletion'
        )
    return deleted_faq


@router.post('/orders/', response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order_endpoint(order: OrderCreate, db: Session = Depends(get_db)):
    return create_order(db=db, order=order)


@router.get('/orders/', response_model=list[Order])
def read_orders_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = get_orders(db, skip=skip, limit=limit)
    return orders


@router.get('/orders/{order_id}', response_model=Order)
def read_single_order_endpoint(order_id: int, db: Session = Depends(get_db)):
    db_order = get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Order not found')
    return db_order


@router.put('/orders/{order_id}', response_model=Order)
def update_order_endpoint(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    db_order = update_order(db, order_id=order_id, order_update=order_update)
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Order not found for updating'
        )
    return db_order


@router.patch('/orders/{order_id}/status', response_model=Order)
def update_order_status_endpoint(
    order_id: int, status_update: OrderStatusEnum, db: Session = Depends(get_db)
):
    db_order = update_order_status(db, order_id=order_id, status=status_update)
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Order not found for status update'
        )
    return db_order


@router.delete('/orders/{order_id}', response_model=Order)
def delete_order_endpoint(order_id: int, db: Session = Depends(get_db)):
    db_order = delete_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Order not found for deletion'
        )
    return db_order
