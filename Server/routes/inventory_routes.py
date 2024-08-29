from flask import Blueprint, make_response , jsonify , request
from sqlalchemy.exc import SQLAlchemyError , IntegrityError
from psycopg2.errors import UniqueViolation

#Local imports
from utils.tokenutils import token_required , authorize , is_authorized_to_modify , is_authorized_to_create
from utils.server_responseutils import server_error_response , bad_request_response, item_not_found_response
from utils.constants import ALLOWED_ATTRIBUTES
from utils.flaskutils import get_filter_params
from models import Card, CardinSet, Inventory
from repo.inventory_repo import InventoryRepository
from repo.cardinSet_repo import CardinSetRepository
from config import db

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('/getUserInventory', methods = ["GET"])
@token_required
def getinventory(user_id):

    try:        
        filters = get_filter_params(InventoryRepository, request.args)
        page = request.args.get('page',default=1, type=int)
        per_page = request.args.get('per_page',default=20,type=int)

        repo = InventoryRepository()
        query = repo.get_inventory_detailed(filters,user_id)
        paginated_results = repo.paginate(query,page=page,per_page=per_page)
        card_list = [card.to_dict(rules=('-cardinSet.card.card_in_deck','-user','-cardinSet.releaseSet','-cardinSet.releaseSet.id''-cardinSet.card.card_on_banlist','-cardinSet.card')) for card in paginated_results.items]
        
        response_data = {
            'cards': card_list,
            'page': page,
            'per_page' : per_page,
            'total_pages' : paginated_results.pages,
            'total_items' : paginated_results.total
            }
        
        response = make_response(jsonify(response_data),200)
    except SQLAlchemyError as se:
        error_message = f'Error w/ SQLAlchemy {se}'
        return server_error_response()
    except Exception as e:
        error_message = f'Error {e}'
        return make_response(jsonify({'error': error_message}), 500)
    return response
    # return response

@inventory_bp.route('/deleteUsersInventory', methods = ["DELETE"])
@token_required
# @authorize(is_authorized_to_modify,edit=True)
def delete_Inventory(user_id):  

    try:
        repo = InventoryRepository()
        query = repo.filter(Inventory.user_id==user_id)
        query.delete()
        db.session.commit()
        response = make_response({},204)
    except SQLAlchemyError as se:
        print(se)   
        db.session.rollback()
        response = server_error_response()
    return response

@inventory_bp.route('/addSingleCardToUserInventory', methods = ["POST"])
@token_required
@authorize(is_authorized_to_create,edit=False)
def add_single_card_to_inventory(user_id, **kwargs):
    #Addition still needs to check for existance here
    #Check if resource_exists
    try:
        cardinset_repo = CardinSetRepository()
        resource_id = kwargs["resource_id"]
        new_card_addition = cardinset_repo.get_item_by_id(resource_id)
        
        if new_card_addition:
            inventory_repo = InventoryRepository()
            duplicate_filters = [Inventory.cardinSet_id==resource_id, Inventory.isFirstEd==kwargs["isFirstEd"]]
            isduplicate_query = inventory_repo.filter(*duplicate_filters,base_query=db.session.query(Inventory).filter(Inventory.user_id==user_id))
            isduplicate = isduplicate_query.first()
            if isduplicate:
                new_quantity = int(isduplicate.quantity) + int(kwargs['quantity'])
                inventory_repo.update_and_commit({'quantity':new_quantity},isduplicate)
                response = make_response({'Duplicate Entry':'Combined Total Quantity'},250)
            else:
                inventory_repo.create_and_commit(user_id,kwargs["resource_id"],kwargs["isFirstEd"],kwargs["quantity"])
                response = make_response({'Sucess':'Card Added'},201)
        else:
            response = item_not_found_response()
    except ValueError as ve:
        print(ve)
        response = bad_request_response()
    except SQLAlchemyError as se:
        print(se)
        db.session.rollback()
        response = server_error_response()
    return response

    # data = request.get_json() #handle this in kwargs instead 


    # # new_card_addition = CardinSet.query.filter(CardinSet.card_code==data['card_id'],CardinSet.rarity==data['rarity']).first()


    # new_card_addition = CardinSet.query.filter(CardinSet.id==resource_id).first()

    # if new_card_addition:
    #     isduplicate = Inventory.query.filter(Inventory.user_id==user_id,Inventory.cardinSet_id==new_card_addition.id,Inventory.isFirstEd==data['isFirstEd']).first()
    #     #This is duplicate block makes it so you can add negative quantities as long as it doesnt go under 1.     

    #     #CardinSetid and isFirstEd need to match, 
    #     if isduplicate:
    #         try:
    #             new_quantity = int(isduplicate.quantity) + int(data['quantity'])
    #             isduplicate.quantity = new_quantity
    #             db.session.add(isduplicate)
    #             db.session.commit()
    #             response = make_response({'Duplicate Entry':'Combined Total Quantity'},250)
    #         except SQLAlchemyError as se:
    #             print(se)
    #             db.session.rollback()
    #             response = server_error_response()
    #         except ValueError as ve:
    #             print(ve)
    #             db.session.rollback()
    #             response = bad_request_response()
    #     else:
    #         try:
    #             new_inventory_record = Inventory(
    #                 quantity = data['quantity'],
    #                 isFirstEd = data['isFirstEd'],
    #                 user_id = user_id,
    #                 cardinSet_id = new_card_addition.id
    #             )
    #             db.session.add(new_inventory_record)
    #             db.session.commit()
    #             response = make_response({'Sucess':'Card Added'},201)
    #         except ValueError as ve:
    #             print(ve)
    #             response = bad_request_response()
    #         except SQLAlchemyError as se:
    #             print(se)
    #             db.session.rollback()
    #             response = server_error_response()
    # else:
    #     response = item_not_found_response()

    # return response


@inventory_bp.route('/editCardInUserInventory', methods = ["PATCH"])
@token_required
@authorize(is_authorized_to_modify,edit=True)
def edit_card_in_inventory(user_id, **kwargs):
    '''
    expected params: resource_id: Inventory item's id
    '''
    try:
        card_to_edit = kwargs['resource']
        repo = InventoryRepository()
        updated_card = repo.update_and_commit(params_dict=kwargs,resource=card_to_edit)
        response = make_response({},202)
    except ValueError as ve:
        print(ve)
        print('this happened?')
        response = bad_request_response()
    # except IntegrityError as ie: 
    #     #This scenario is 
    #     print(ie)
    #     print(ie.orig)
    #     print(type(ie.orig))
    #     print('fdasfa')
    #     db.session.rollback()
    #     response = bad_request_response()
    except SQLAlchemyError as se:
        print(se.__class__)
        print(se)
        print('xd')
        print(se.orig)
        db.session.rollback()
        response = server_error_response()
    return response

    # try:
    #     for key, value in kwargs.items():
    #         if hasattr(card_to_edit, key) and key in ALLOWED_ATTRIBUTES["Inventory"]:
    #             setattr(card_to_edit, key ,value)
    #     db.session.add(card_to_edit)
    #     db.session.commit()
    #     response = make_response({},200)
    # except ValueError as ve:
    #     print(ve)
    #     print('this happened?')
    #     response = bad_request_response()
    # except SQLAlchemyError as se:
    #     print(se)
    #     db.session.rollback()
    #     response = server_error_response()
    # return response

@inventory_bp.route('/deleteCardInUserInventory', methods = ["POST"])
@token_required
@authorize(is_authorized_to_modify,edit=True)
def delete_card_in_inventory(user_id, **kwargs):
    
    card_to_delete = kwargs["resource"]
    
    try:
        db.session.delete(card_to_delete)
        db.session.commit()
        response = make_response({},204)
    except SQLAlchemyError as se:
        print(se)
        db.session.rollback()
        response = server_error_response()

    return response

