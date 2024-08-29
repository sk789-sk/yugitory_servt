from .repository_interface import ReadWriteRepositoryInterface
from utils.constants import ALLOWED_ATTRIBUTES
from models import CardinDeck
from flask_sqlalchemy import SQLAlchemy
from config import db
from sqlalchemy.exc import SQLAlchemyError

class CardinDeckRepository(ReadWriteRepositoryInterface):
    card_filters = {
        'card_id' : lambda value: CardinDeck.card_id==value,
        'location' : lambda value: CardinDeck.location==value,
        'deck_id' : lambda value: CardinDeck.deck_id==value,
    }
    
    def __init__(self):
        super().__init__(CardinDeck)
    
    def create(self, card_id, deck_id, location, quantity):
        new_CardinDeck = CardinDeck(
            quantity = quantity,
            location = location,
            deck_id = deck_id,
            card_id = card_id
        )
        db.session.commit(new_CardinDeck)
        return new_CardinDeck

    def create_and_commit(self, card_id, deck_id, location, quantity):
        new_cardinDeck = self.create(card_id,deck_id,location,quantity)
        db.session.commit()
        return new_cardinDeck