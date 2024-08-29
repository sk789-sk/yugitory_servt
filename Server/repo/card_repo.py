from .repository_interface import ReadOnlyRepositoryInterface
from models import Card
from flask_sqlalchemy import SQLAlchemy


class CardRepository(ReadOnlyRepositoryInterface):
    
    card_filters = {
        'name_partial' : lambda value: Card.name.ilike(f'%{value}%'),
        'name_exact' : lambda value: Card.name==value,
        'card_type' : lambda value: Card.card_type.ilike(f'%{value}%'), 
        'card_attribute' : lambda value: Card.card_attribute.ilike(f'%{value}%'),
        'card_race' : lambda value: Card.card_race.ilike(f'%{value}%'),
        'ygo_pro_id' : lambda value: Card.yg_pro_id==value,
        'atk_is_less' : lambda value : Card.attack < value,
        'atk_is_greater' : lambda value: Card,
        'atk_is_equal' : lambda value : Card
    }


    def __init__(self):
        super().__init__(Card)

    
