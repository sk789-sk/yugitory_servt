from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.exc import SQLAlchemyError , DataError , IntegrityError 
from sqlalchemy.exc import DataError

from utils.tokenutils import token_required
from config import db

from models import Inventory, Card, CardinSet , CardinDeck , Deck

reconcile_bp = Blueprint('reconcile',__name__)

@reconcile_bp.route('/reconcileInventory' ,methods=["POST"])
@token_required
def reconcile_selected_decks_with_inventory(user_id):
    deck_list = request.get_json()
    base = db.session.query(Inventory)
    invent = base.filter(Inventory.user_id==user_id).outerjoin(CardinSet,Inventory.cardinSet_id==CardinSet.id).outerjoin(Card,CardinSet.card_id==Card.id)

    id_count = {} #The amount of cards
    cards_by_deck = {} #All the decks that a card is used in 

    for val in deck_list:
        cards_in_deck = CardinDeck.query.filter(CardinDeck.deck_id==val).all() #All the cards in the deck
        deck_info = db.session.query(Deck.name,Deck.id).filter(Deck.id==val).first()

        # deck_name = db.session.query(Deck.name).filter(Deck.id==val).scalar() #Name of the Deck , we should pass id as well

        deck_name,deck_id = deck_info
        for card in cards_in_deck:
            id_count[card.card_id] = id_count.get(card.card_id,0) + card.quantity
            cards_by_deck.setdefault(card.card_id, []).append((card.quantity, deck_name, val,deck_id))

    recon_array = []
    for card_id,quantity in id_count.items():
        cards_owned = invent.filter(Card.id==card_id).all()
        card_name = db.session.query(Card.name).filter(Card.id==card_id).scalar() #or .first()[0]
        cards_owned_quantity = sum(record.quantity for record in cards_owned) if cards_owned else 0 
        card_quantity_needed = max(0,quantity-cards_owned_quantity)

        data_obj = {
            'name' :card_name,
            'id' : card_id,
            'owned' : cards_owned_quantity,
            'required' : quantity,
            'need' : card_quantity_needed,
            'usage' : cards_by_deck[card_id]
        }

        recon_array.append(data_obj)
    
    response = make_response(jsonify(recon_array) , 200)
    return response