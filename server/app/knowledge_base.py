from typing import Any

from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import Base, Faq, MenuCategory, RestaurantInfo, SpecialOffer
from app.utils import log_error, log_info, log_warning


class KnowledgeBase:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.restaurant_info: dict[str, Any] | None = None
        self.menu: dict[str, list[dict[str, Any]]] = {}
        self.special_offers: list[dict[str, Any]] = []
        self.faq: list[dict[str, str]] = []
        self._load_data()

    def _load_data(self):
        log_info('Loading data from database into KnowledgeBase...')
        self._load_restaurant_info()
        self._load_menu()
        self._load_special_offers()
        self._load_faq()
        log_info('Data loaded successfully into KnowledgeBase from database.')

    def _load_restaurant_info(self):
        info = self.db.query(RestaurantInfo).first()
        if info:
            self.restaurant_info = {
                'Nazwa Restauracji': info.name,
                'Adres': info.address,
                'Godziny Otwarcia': {
                    'Poniedziałek - Piątek': info.opening_hours_weekday,
                    'Sobota - Niedziela': info.opening_hours_weekend,
                },
                'Telefon': info.phone,
                'Email': info.email,
                'Strona WWW': info.website,
                'Rodzaj kuchni': info.cuisine_type,
                'Akceptowane formy płatności': info.payment_methods,
                'Dostępność parkingu': 'Tak' if info.parking_available else 'Nie',
                'Ogródek letni': 'Tak' if info.summer_garden_available else 'Nie',
                'Rezerwacje': info.reservations_info,
            }
        else:
            log_warning('Restaurant info not found in the database for KnowledgeBase.')

    def _load_menu(self):
        categories = self.db.query(MenuCategory).all()
        if not categories:
            log_warning('No menu categories found in the database for KnowledgeBase.')
        for category in categories:
            items_data = []
            for item in category.items:
                allergens = [allergen.name for allergen in item.allergens]
                item_dict = {
                    'nazwa': item.name,
                    'opis': item.description,
                    'alergeny': ', '.join(allergens) if allergens else '-',
                }

                if item.price is not None and item.price > 0:
                    item_dict['cena'] = f'{item.price:.2f} PLN'
                    if item.options:
                        item_dict['opcje'] = item.options
                elif item.options:
                    item_dict['cena'] = item.options
                else:
                    item_dict['cena'] = 'Zapytaj obsługę'

                items_data.append(item_dict)
            self.menu[category.name] = items_data

    def _load_special_offers(self):
        offers = self.db.query(SpecialOffer).all()
        if not offers:
            log_info('No special offers found in the database. This might be normal.')
        for offer in offers:
            offer_dict = {
                'nazwa': offer.title,
                'opis': offer.description,
            }
            if offer.price_info:
                offer_dict['cena'] = offer.price_info
            if offer.details:
                offer_dict['szczegóły'] = offer.details
            if offer.validity:
                offer_dict['ważność'] = offer.validity
            self.special_offers.append(offer_dict)

    def _load_faq(self):
        faqs = self.db.query(Faq).all()
        if not faqs:
            log_warning('No FAQs found in the database.')
        for faq_item in faqs:
            self.faq.append(
                {
                    'pytanie': faq_item.question,
                    'odpowiedź': faq_item.answer,
                }
            )

    def get_structured_data(self) -> dict[str, Any]:
        return {
            'restaurant_info': self.restaurant_info or {},
            'menu': self.menu or {},
            'special_offers': self.special_offers or [],
            'faq': self.faq or [],
        }

    def get_full_context_as_text(self) -> str:
        # pylint: disable=too-many-branches
        context_parts = []

        if self.restaurant_info:
            context_parts.append('## Informacje o Restauracji')
            for key, value in self.restaurant_info.items():
                if isinstance(value, dict):
                    context_parts.append(f'*   **{key}**:')
                    for sub_key, sub_value in value.items():
                        context_parts.append(f'    *   {sub_key}: {sub_value}')
                else:
                    context_parts.append(f'*   **{key}**: {value}')
            context_parts.append('\n')

        if self.menu:
            context_parts.append('## Menu')
            for category, items in self.menu.items():
                context_parts.append(f'### {category}')
                for item in items:
                    context_parts.append(f'*   **{item.get("nazwa")}**')
                    if item.get('opis'):
                        context_parts.append(f'    *   Opis: {item.get("opis")}')
                    context_parts.append(f'    *   Cena: {item.get("cena")}')
                    if item.get('alergeny') and item.get('alergeny') != '-':
                        context_parts.append(f'    *   Alergeny: {item.get("alergeny")}')
                    if item.get('opcje'):
                        context_parts.append(f'    *   Opcje: {item.get("opcje")}')
                context_parts.append('\n')

        if self.special_offers:
            context_parts.append('## Oferty Specjalne')
            for offer in self.special_offers:
                context_parts.append(f'*   **{offer.get("nazwa")}**')
                context_parts.append(f'    *   Opis: {offer.get("opis")}')
                if offer.get('cena'):
                    context_parts.append(f'    *   Cena: {offer.get("cena")}')
                if offer.get('szczegóły'):
                    context_parts.append(f'    *   Szczegóły: {offer.get("szczegóły")}')
                if offer.get('ważność'):
                    context_parts.append(f'    *   Ważność: {offer.get("ważność")}')
            context_parts.append('\n')

        if self.faq:
            context_parts.append('## FAQ - Często Zadawane Pytania')
            for item in self.faq:
                context_parts.append(f'*   **Pytanie**: {item.get("pytanie")}')
                context_parts.append(f'    *   **Odpowiedź**: {item.get("odpowiedź")}')
            context_parts.append('\n')

        return '\n'.join(context_parts)


# Global singleton instance for KnowledgeBase
_knowledge_base_instance: KnowledgeBase | None = None


def get_knowledge_base() -> KnowledgeBase:
    # pylint: disable=global-statement
    global _knowledge_base_instance
    if _knowledge_base_instance is None:
        log_info('Initializing KnowledgeBase singleton...')
        db_session = SessionLocal()
        try:
            Base.metadata.create_all(bind=engine)

            if not db_session.query(RestaurantInfo).first():
                log_warning('Database appears to be empty (no RestaurantInfo found).')

            _knowledge_base_instance = KnowledgeBase(db_session=db_session)
            log_info('KnowledgeBase singleton initialized.')
        except Exception as e:
            log_error(f'Error initializing KnowledgeBase: {e}')
            if db_session:
                db_session.close()
            raise
    return _knowledge_base_instance
