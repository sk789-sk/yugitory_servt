from flask import Blueprint, make_response , jsonify , request
from sqlalchemy.exc import SQLAlchemyError


from models import ReleaseSet, Card
from utils.server_responseutils import server_error_response

set_bp = Blueprint('sets',__name__)

@set_bp.route('/getAllSets')
def get_all_sets_info():

    filter_mapping = {
        'name' : lambda value: ReleaseSet.name.ilike(f'%{value}%'),
        #'releaseDate' : lambda value: .card_type.ilike(f'%{value}%'), 
        'set_code' : lambda value: Card.card_attribute.ilike(f'%{value}%')
    }

    set_info = ReleaseSet.query.all()
    set_list = [pack.to_dict(only=('name','card_count','id','releaseDate','set_code')) for pack in set_info]
    response = make_response(jsonify(set_list),200)
    return response


@set_bp.route('/getSingleSet/<int:set_id>')
def get_single_set_info(set_id):
    try:
        set_info = ReleaseSet.query.filter(ReleaseSet.id==set_id).first()
        response = make_response(jsonify(set_info.to_dict(rules=('-card_in_set.card.card_in_deck','-card_in_set.card.card_on_banlist','-card_in_set.card_in_inventory','-card_in_set.releaseSet','card_in_set.releaseSet.id'))),200)
        #card image, id only thing we need from the card section. 
    except SQLAlchemyError as se:
        print(se)
        response = server_error_response()
    return response