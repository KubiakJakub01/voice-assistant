import json
import re

from app.database import SessionLocal
from app.models import FAQ, Allergen, MenuCategory, MenuItem, RestaurantInfo, SpecialOffer
from app.utils import log_error, log_info, log_warning


def get_or_create_allergen(db_session, name):
    """
    Get or create an allergen.
    """
    name = name.strip()
    allergen = db_session.query(Allergen).filter_by(name=name).first()
    if not allergen:
        allergen = Allergen(name=name)
        db_session.add(allergen)
        db_session.commit()
    return allergen


def parse_price(price_str):
    """
    Parse price from string. Handles simple numbers and strings like 'X PLN' or 'od X PLN'.
    Returns None if parsing fails.
    """
    if isinstance(price_str, int | float):
        return float(price_str)
    if isinstance(price_str, str):
        match = re.search(r'(\\d+(?:\\.\\d+)?)', price_str)
        if match:
            return float(match.group(1))
    return None


def _load_restaurant_info(db, info_data):
    """Loads restaurant information into the database."""
    if not info_data:
        log_warning('No restaurant_info found in JSON data.')
        return
    try:
        restaurant = RestaurantInfo(
            name=info_data.get('name'),
            address=info_data.get('address'),
            phone=info_data.get('phone'),
            email=info_data.get('email'),
            website=info_data.get('website'),
            cuisine_type=info_data.get('cuisine_type'),
            payment_methods=info_data.get('payment_methods'),
            parking_available=info_data.get('parking_available', False),
            summer_garden_available=info_data.get('summer_garden_available', False),
            reservations_info=info_data.get('reservations_info'),
            opening_hours_weekday=info_data.get('opening_hours', {}).get('weekday'),
            opening_hours_weekend=info_data.get('opening_hours', {}).get('weekend'),
        )
        db.add(restaurant)
        log_info(f'Processed restaurant info: {info_data.get("name")}')
    except Exception as e:  # pylint: disable=broad-exception-caught
        log_error(f'Error processing restaurant info: {e}')
        db.rollback()  # Rollback for this specific section


def _load_menu_item(db, item_data, category_id, category_name):
    """Loads a single menu item (not a drink) into the database."""
    name = item_data.get('name')
    price_val = item_data.get('price')  # Expected to be a number in JSON for these items
    description = item_data.get('description')
    options = item_data.get('options')
    allergens_list = item_data.get('allergens', [])

    if not name or price_val is None:
        log_warning(f'Skipping item in {category_name} due to missing name or price: {name}')
        return

    menu_item = MenuItem(
        name=name,
        description=description,
        price=float(price_val),  # Ensure price is float
        category_id=category_id,
        options=options,
    )
    db.add(menu_item)
    db.flush()  # Flush to get menu_item id for allergens

    for al_name in allergens_list:
        if al_name and al_name.strip() and al_name.strip() != '-':
            allergen_obj = get_or_create_allergen(db, al_name.strip())
            menu_item.allergens.append(allergen_obj)
    log_info(f'  Added item: {name} to {category_name}')


def _load_drink_item(db, item_data, category_id, sub_category_name):
    """Loads a single drink item into the database."""
    name_full = item_data.get('name')
    price_info_str = item_data.get('price_info')

    if not name_full:
        log_warning(f'Skipping drink in {sub_category_name} due to missing name.')
        return

    parsed_drink_price = parse_price(price_info_str)

    menu_item = MenuItem(
        name=f'{name_full} ({sub_category_name})' if sub_category_name else name_full,
        description=name_full,
        price=parsed_drink_price if parsed_drink_price is not None else 0,
        category_id=category_id,
        options=price_info_str if parsed_drink_price is None else None,
    )
    db.add(menu_item)
    log_info(f'  Added drink: {name_full} ({sub_category_name})')


def _load_menu_categories(db, menu_data):
    """Loads menu categories and their items into the database."""
    if not menu_data:
        log_warning('No menu data found in JSON.')
        return

    for category_data in menu_data:
        cat_name = category_data.get('category_name')
        if not cat_name:
            log_warning('Skipping menu category with no name.')
            continue

        db_category = db.query(MenuCategory).filter_by(name=cat_name).first()
        if not db_category:
            db_category = MenuCategory(name=cat_name)
            db.add(db_category)
            db.flush()  # Flush to get category_id for menu items
            log_info(f'Added category: {cat_name}')

        category_id = db_category.id

        if 'items' in category_data:
            for item_data in category_data.get('items', []):
                _load_menu_item(db, item_data, category_id, cat_name)
        elif 'sub_categories' in category_data:  # Handling for 'Napoje' (Drinks)
            for sub_cat_data in category_data.get('sub_categories', []):
                sub_cat_name = sub_cat_data.get('sub_category_name')
                for item_data in sub_cat_data.get('items', []):
                    _load_drink_item(db, item_data, category_id, sub_cat_name)


def _load_special_offers(db, offers_data):
    """Loads special offers into the database."""
    if not offers_data:
        log_warning('No special offers data found in JSON.')
        return

    for offer_data in offers_data:
        title = offer_data.get('title')
        if not title:
            log_warning('Skipping special offer with no title.')
            continue
        try:
            offer = SpecialOffer(
                title=title,
                description=offer_data.get('description'),
                price_info=offer_data.get('price_info'),
                details=offer_data.get('details'),
                validity=offer_data.get('validity'),
            )
            db.add(offer)
            log_info(f'Added special offer: {title}')
        except Exception as e:  # pylint: disable=broad-exception-caught
            log_error(f'Error processing offer "{title}": {e}')
            # Continue to next offer, rollback for this item is implicit if commit fails later


def _load_faq(db, faq_data):
    """Loads FAQ entries into the database."""
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
            faq_entry = FAQ(question=question, answer=answer)
            db.add(faq_entry)
            log_info(f'Added FAQ: {question[:50]}...')
        except Exception as e:  # pylint: disable=broad-exception-caught
            log_error(f'Error processing FAQ "{question[:50]}...": {e}')
            # Continue to next FAQ item


def load_data_from_json(json_file_path):
    """
    Load data from JSON file into the database.
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
    except Exception as e:  # pylint: disable=broad-exception-caught
        log_error(f'An unexpected error occurred while reading {json_file_path}: {e}')
        return

    db = SessionLocal()
    try:
        log_info('Starting data loading process...')

        # Section 1: Restaurant Info
        log_info('Processing Restaurant Info...')
        _load_restaurant_info(db, data.get('restaurant_info'))

        # Section 2: Menu
        log_info('Processing Menu...')
        _load_menu_categories(db, data.get('menu', []))

        # Section 3: Special Offers
        log_info('Processing Special Offers...')
        _load_special_offers(db, data.get('special_offers', []))

        # Section 4: FAQ
        log_info('Processing FAQ...')
        _load_faq(db, data.get('faq', []))

        db.commit()
        log_info('Data loaded and committed successfully from JSON.')

    except Exception as e:  # pylint: disable=broad-exception-caught
        log_error(f'A critical error occurred during data loading: {e}. Rolling back all changes.')
        db.rollback()
    finally:
        db.close()
        log_info('Database session closed.')
