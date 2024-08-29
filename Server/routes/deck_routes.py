from flask import Blueprint, make_response , jsonify , request
from sqlalchemy.exc import SQLAlchemyError

#local imports
from utils.tokenutils import token_required , authorize , is_authorized_to_modify , is_authorized_to_create
from utils.server_responseutils import server_error_response , bad_request_response , item_not_found_response
from utils.constants import ALLOWED_ATTRIBUTES
from repo.deck_repo import DeckRepository
from repo.card_in_deck_repo import CardinDeckRepository
from utils.flaskutils import get_filter_params
from config import db
from models import Deck , CardinDeck


from error_handling.error_class import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from pprint import pprint
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


deck_bp = Blueprint('deck',__name__)

@deck_bp.route('/createSingleDeck', methods=["POST"])
@token_required
@authorize(is_authorized_to_create,edit=False)
def create_single_deck(user_id,**kwargs):
    try:
        data = request.get_json()
        name = data["name"]
        repo = DeckRepository()
        new_deck = repo.create_and_commit(user_id=user_id, name=name)
        response = make_response(jsonify(new_deck.to_dict()),201)
    except ValidationError as ve:
        print(ve)
        print(ve.value)
        print(ve.parameter)
        response = make_response({"Validation Error":ve.message},400)
    except SQLAlchemyError as se:
        print(se)
        print('lala')
        response = server_error_response()
    except Exception as e:
        print(e)
        return server_error_response()    

    return response

@deck_bp.route('/editSingleDeck', methods=["PATCH"])
@token_required
@authorize(is_authorized_to_modify, edit=True)
def edit_single_deck(user_id,**kwargs):
    
    try:
        users_deck = kwargs['resource']
        deck = DeckRepository()
        updated_deck = deck.update_and_commit(params_dict=kwargs,resource=users_deck)
        response = make_response(jsonify(updated_deck.to_dict()),202)
    except SQLAlchemyError as se:
        print(se)
        print('stop breaking the db')
        response = server_error_response()
    except ValidationError as ve:
        print('stop trying to fk it up')
        print(ve)
        response = server_error_response()
    except Exception as e:
        print(e)
        print('unhandled exception')
        response = server_error_response()
    # try:
    #     for key,value in kwargs.items():  #only allow select keys to be modified as well
    #         if hasattr(users_deck,key) and key in ALLOWED_ATTRIBUTES["Deck"]:
    #             setattr(users_deck,key,value)
    #     db.session.add(users_deck)
    #     db.session.commit()
    #     response = make_response({"Sucess":"Updated"},202)
    # except ValueError as ve:
    #     print(ve)
    #     db.session.rollback()
    #     response = bad_request_response()
    # except SQLAlchemyError as se:
    #     print(se)
    #     db.session.rollback()
    #     response = server_error_response()
    return response

@deck_bp.route('/deleteSingleDeck', methods=['POST'])
@token_required
@authorize(is_authorized_to_modify, edit=True)
def delete_single_deck(user_id,**kwargs):

    try:
        deck_to_delete = kwargs["resource"]
        deck_repo = DeckRepository()
        cardinDeck_repo = CardinDeckRepository()

        cards_in_deck_query = cardinDeck_repo.filter(CardinDeck.deck_id==deck_to_delete.id)
        card_list = cards_in_deck_query.all()

        for card in card_list:
            cardinDeck_repo.delete(resource=card)
        deck_repo.delete(resource=deck_to_delete)
        db.session.commit()
        response = make_response({},204)
    except SQLAlchemyError as se:
        db.session.rollback()
        print(se)
        response = server_error_response()
    return response

@deck_bp.route('/getUsersDecks' , methods=["GET"])
@token_required
def get_users_decks(user_id):
    try:
        filters = get_filter_params(DeckRepository, request.args)
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page',default=20,type=int)
        
        repo = DeckRepository()
        query = repo.filter(*filters)
        paginated_results = repo.paginate(query)

        deck_list = [deck.to_dict(rules=('-card_in_deck','-user')) for deck in paginated_results.items()]
        response_data = {
            'decks' : deck_list,
            'page' : page, 
            'per_page' : per_page,
            'total_pages' : paginated_results.pages,
            'total_items' : paginated_results.total
        }
        response = make_response(jsonify(response_data),200)
    except SQLAlchemyError as se:
        print(se)
        response = server_error_response()
    except KeyError as ke:
        print(ke)
    except Exception as e:
        print(e)
        response = server_error_response()

    # filter_mapping = {
    #     'user_id' : lambda value: Deck.user_id==value,
    #     'name' : lambda value: Deck.name.ilike(f'%{value}%'),
    #     'id' : lambda value: Deck.id==value
    # }
    # try:
    #     filter_elements = []
    #     for key,value in request.args.items():
    #         filter_element = filter_mapping[key](value)
    #         filter_elements.append(filter_element)
    #     deck_lists = Deck.query.filter(*filter_elements).all()
    #     deck_list = [deck.to_dict(rules=('-card_in_deck','-user')) for deck in deck_lists]
    #     response = make_response(jsonify(deck_list),200)
    # except SQLAlchemyError as se:
    #     db.session.rollback()
    #     print(se)
    #     response = server_error_response()
    # except KeyError as ke:
    #     print(ke)
    #     db.session.rollback()
    #     response = bad_request_response()
    return response

@deck_bp.route('/getSingleDeckCardInfo/<int:deck_id>', methods =['GET'])
def get_single_deck_card_info(deck_id):

    #Replace with access functions 
    deck_repo = DeckRepository()
    single_deck = deck_repo.get_deck_and_minimal_card_info(deck_id)


    # single_deck = Deck.query.filter(Deck.id==deck_id).first()


    if single_deck:
        try:
            response = make_response(jsonify(single_deck.to_dict()),200)  #single_deck.to_dict()
        except SQLAlchemyError as se:
            print(se)
            response = server_error_response()
    else:
        response = item_not_found_response()
    return response

@deck_bp.route('/createDeckFromYDK', methods=["POST"])
@token_required
def ydk_to_deck(user_id):
    pass
