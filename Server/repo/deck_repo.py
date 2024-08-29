from .repository_interface import ReadWriteRepositoryInterface
from utils.constants import ALLOWED_ATTRIBUTES
from models import Deck , Card , CardinDeck
from flask_sqlalchemy import SQLAlchemy
from config import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, load_only

class DeckRepository(ReadWriteRepositoryInterface):
    
    search_filters = {
        'name' : lambda value: Deck.name.ilike(f'%{value}%'),
    }

    def __init__(self):
        super().__init__(Deck)

    def create(self, user_id, name , is_public=True):
        new_deck = Deck(
            name = name,
            user_id = user_id,
            isPublic = is_public
        )
        db.session.add(new_deck)
        return new_deck 
    
    def create_and_commit(self, user_id, name , is_public=True):
        deck = self.create(user_id, name, is_public)
        db.session.commit()
        return deck

    def get_deck_and_minimal_card_info(self, deck_id):
        single_deck = db.session.query(Deck).options(joinedload(Deck.card_in_deck).load_only(CardinDeck.card_id, CardinDeck.location)).filter(Deck.id==deck_id).first()
        return single_deck


    # def update(self, params_dict ,deck=None): 
    #     print(params_dict)
    #     print(deck)
    #     if deck is None:
    #         try:
    #             deck = self.get_item_by_id(params_dict["resource_id"]) 
    #         except SQLAlchemyError as se:
    #             print(se)                
    #     for key, value in params_dict.items():
    #         if hasattr(deck, key) and key in ALLOWED_ATTRIBUTES['Deck']:
    #             setattr(deck,key, value)
    #             print(f'We have set the {key} to {value}')
    #     db.session.add(deck)
    #     return deck
    
    # def update_and_commit(self, params_dict ,deck=None):
    #     updated_deck = self.update(params_dict,deck)        
    #     db.session.commit()
    #     return updated_deck

