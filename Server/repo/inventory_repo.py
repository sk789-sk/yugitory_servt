from .repository_interface import ReadWriteRepositoryInterface
from models import Inventory , Card , CardinSet
from config import db

class InventoryRepository(ReadWriteRepositoryInterface):

    search_filters = {

        'isFirstEd' : lambda value: Inventory.isFirstEd==value,
        'name_partial' : lambda value: Card.name.contains(value),
        'card_code_partial' : lambda value: CardinSet.card_code.contains(value),
        'name_exact' : lambda value: Card.name==value,
        'rarity' : lambda value: CardinSet.rarity.ilike(f'%{value}%'),
        'card_type' : lambda value: Card.card_type.ilike(f'%{value}%'),
    }

    ALLOWED_ATTRIBUTES = {'quantity','isFirstEd'}

    mappings = {
        'resource_id': 'CardinSet'
    } #This is for the routes to repo since routes will return resource_id,location. Hold up wait a minute. 


    def __init__(self):
        super().__init__(Inventory)

    def create(self, user_id, cardinSet_id, isFirstEd , quantity):
        new_Inventory_item = Inventory(
            quantity = quantity,
            user_id = user_id,
            isFirstEd = isFirstEd,
            cardinSet_id = cardinSet_id
        )

        db.session.add(new_Inventory_item)
        return new_Inventory_item
    
    def create_and_commit(self, user_id, cardinSet_id, isFirstEd, quantity):
        new_item = self.create(user_id,cardinSet_id,isFirstEd,quantity)
        db.session.commit()
        return new_item

    def get_inventory_detailed(self, filters,user_id):
        base_query = db.session.query(Inventory).filter(Inventory.user_id==user_id).outerjoin(CardinSet,Inventory.cardinSet_id==CardinSet.id).outerjoin(Card,CardinSet.card_id==Card.id)
        filtered_query = self.filter(base_query=base_query, *filters)
        return filtered_query