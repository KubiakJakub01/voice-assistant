import json
import re

from sqlalchemy.orm import Session

from app.crud import (
    create_allergen,
    create_faq,
    create_menu_category,
    create_menu_item,
    create_restaurant_info,
    create_special_offer,
    get_allergen_by_name,
    get_menu_category_by_name,
)
from app.database import SessionLocal
from app.models import (
    AllergenCreate,
    AllergenDB,
    FaqCreate,
    MenuCategoryCreate,
    MenuItemCreate,
    RestaurantInfoCreate,
    SpecialOfferCreate,
)
from app.utils import log_error, log_info, log_warning


def get_or_create_allergen_for_loader(db_session: Session, name: str) -> AllergenDB:
    """
    Get or create an allergen specifically for data loading.
    Uses existing CRUD functions but manages session within this scope for clarity during loading.
    """
    name = name.strip()

    allergen = get_allergen_by_name(db_session, name=name)
    if not allergen:
        allergen_schema = AllergenCreate(name=name)
        allergen = create_allergen(db_session, allergen=allergen_schema)
    return allergen


def parse_price(price_str):
    """
    Parse price from string. Handles simple numbers and strings like 'X PLN' or 'od X PLN'.
    Returns None if parsing fails.
    """
    if isinstance(price_str, int | float):
        return float(price_str)
    if isinstance(price_str, str):
        match = re.search(r'(\d+(?:\.\d+)?)', price_str)
        if match:
            return float(match.group(1))
    return None


def _load_restaurant_info(db: Session, info_data: dict):
    """Loads restaurant information into the database using CRUD operations."""
    if not info_data:
        log_warning('No restaurant_info found in JSON data.')
        return

    website_url = info_data.get('website')
    if website_url and not website_url.startswith(('http://', 'https://')):
        website_url = 'http://' + website_url
        log_info(f'Prepended http:// to website URL: {website_url}')

    try:
        restaurant_info_create = RestaurantInfoCreate(
            name=info_data.get('name'),
            address=info_data.get('address'),
            opening_hours_weekday=info_data.get('opening_hours', {}).get('weekday'),
            opening_hours_weekend=info_data.get('opening_hours', {}).get('weekend'),
            phone=info_data.get('phone'),
            email=info_data.get('email'),
            website=website_url,
            cuisine_type=info_data.get('cuisine_type'),
            payment_methods=info_data.get('payment_methods'),
            parking_available=info_data.get('parking_available', False),
            summer_garden_available=info_data.get('summer_garden_available', False),
            reservations_info=info_data.get('reservations_info'),
        )

        created_info = create_restaurant_info(db=db, info=restaurant_info_create)
        log_info(f'Processed restaurant info: {created_info.name}')

    except Exception as e:
        log_error(f'Error processing restaurant info: {e}')


def _load_menu_item(db: Session, item_data: dict, category_id: int, category_name: str):
    """Loads a single menu item (not a drink) into the database using CRUD."""
    name = item_data.get('name')
    price_val = item_data.get('price')
    description = item_data.get('description')
    options = item_data.get('options')
    allergens_list = item_data.get('allergens', [])

    if not name or price_val is None:
        log_warning(f'Skipping item in {category_name} due to missing name or price: {name}')
        return

    try:
        menu_item_create_schema = MenuItemCreate(
            name=name,
            description=description,
            price=float(price_val),
            category_id=category_id,
            options=options,
            allergen_names=[
                al_name.strip()
                for al_name in allergens_list
                if al_name and al_name.strip() and al_name.strip() != '-'
            ],
        )
        created_item = create_menu_item(
            db=db, item=menu_item_create_schema, category_id=category_id
        )
        log_info(f'  Added item: {created_item.name} to {category_name}')
    except Exception as e:
        log_error(f'Error processing menu item "{name}" in category "{category_name}": {e}')


def _load_drink_item(db: Session, item_data: dict, category_id: int, sub_category_name: str):
    """Loads a single drink item into the database using CRUD."""
    name_full = item_data.get('name')
    price_info_str = item_data.get('price_info')

    if not name_full:
        log_warning(f'Skipping drink in {sub_category_name} due to missing name.')
        return

    parsed_drink_price = parse_price(price_info_str)

    try:
        menu_item_create_schema = MenuItemCreate(
            name=f'{name_full} ({sub_category_name})' if sub_category_name else name_full,
            description=name_full,
            price=parsed_drink_price if parsed_drink_price is not None else 0.0,
            category_id=category_id,
            options=price_info_str if parsed_drink_price is None else None,
            allergen_names=[],
        )
        created_item = create_menu_item(
            db=db, item=menu_item_create_schema, category_id=category_id
        )
        log_info(f'  Added drink: {created_item.name} to category ID {category_id}')
    except Exception as e:
        log_error(
            f'Error processing drink item "{name_full}" in sub-category "{sub_category_name}": {e}'
        )


def _load_menu_categories(db: Session, menu_data: list):
    """Loads menu categories and their items into the database using CRUD."""
    if not menu_data:
        log_warning('No menu data found in JSON.')
        return

    for category_data in menu_data:
        cat_name = category_data.get('category_name')
        if not cat_name:
            log_warning('Skipping menu category with no name.')
            continue

        db_category_orm = get_menu_category_by_name(db, name=cat_name)
        if not db_category_orm:
            category_create_schema = MenuCategoryCreate(name=cat_name)
            db_category_orm = create_menu_category(db, category=category_create_schema)
            log_info(f'Added category: {db_category_orm.name} (ID: {db_category_orm.id})')

        if not db_category_orm:
            log_error(
                f'Failed to get or create category: {cat_name}. Skipping items for this category.'
            )
            continue

        category_id = db_category_orm.id

        if 'items' in category_data:
            for item_data in category_data.get('items', []):
                _load_menu_item(db, item_data, category_id, cat_name)
        elif 'sub_categories' in category_data:
            for sub_cat_data in category_data.get('sub_categories', []):
                sub_cat_name = sub_cat_data.get('sub_category_name')
                for item_data in sub_cat_data.get('items', []):
                    _load_drink_item(db, item_data, category_id, sub_cat_name)


def _load_special_offers(db: Session, offers_data: list):
    """Loads special offers into the database using CRUD."""
    if not offers_data:
        log_warning('No special offers data found in JSON.')
        return

    for offer_data in offers_data:
        title = offer_data.get('title')
        if not title:
            log_warning('Skipping special offer with no title.')
            continue
        try:
            offer_create_schema = SpecialOfferCreate(
                title=title,
                description=offer_data.get('description'),
                price_info=offer_data.get('price_info'),
                details=offer_data.get('details'),
                validity=offer_data.get('validity'),
            )
            created_offer = create_special_offer(db, offer=offer_create_schema)
            log_info(f'Added special offer: {created_offer.title}')
        except Exception as e:
            log_error(f'Error processing offer "{title}": {e}')


def _load_faq(db: Session, faq_data: list):
    """Loads FAQ entries into the database using CRUD."""
    if not faq_data:
        log_warning('No FAQ data found in JSON.')
        return

    for faq_item in faq_data:
        question = faq_item.get('question')
        answer = faq_item.get('answer')
        if not question or not answer:
            log_warning('Skipping FAQ entry with missing question or answer.')
            continue
        try:
            faq_create_schema = FaqCreate(question=question, answer=answer)
            created_faq = create_faq(db, faq=faq_create_schema)
            log_info(f'Added FAQ: {created_faq.question[:50]}...')
        except Exception as e:
            log_error(f'Error processing FAQ "{question[:50]}...": {e}')


def load_data_from_json(json_file_path: str):
    """
    Load data from JSON file into the database.
    Uses CRUD operations and Pydantic schemas for validation.
    """
    try:
        with open(json_file_path, encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        log_error(f'JSON data file not found at: {json_file_path}')
        return
    except json.JSONDecodeError as e:
        log_error(f'Error decoding JSON from file {json_file_path}: {e}')
        return
    except Exception as e:
        log_error(f'An unexpected error occurred while reading {json_file_path}: {e}')
        return

    db: Session = SessionLocal()
    try:
        log_info('Starting data loading process...')

        log_info('Processing Restaurant Info...')
        _load_restaurant_info(db, data.get('restaurant_info'))

        log_info('Processing Menu...')
        _load_menu_categories(db, data.get('menu', []))

        log_info('Processing Special Offers...')
        _load_special_offers(db, data.get('special_offers', []))

        log_info('Processing FAQ...')
        _load_faq(db, data.get('faq', []))

        log_info('Data loading process completed.')

    except Exception as e:
        log_error(f'A critical error occurred during the data loading orchestration: {e}.')
        db.rollback()
    finally:
        db.close()
        log_info('Database session closed after data loading process.')
