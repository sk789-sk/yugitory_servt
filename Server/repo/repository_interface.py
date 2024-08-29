from abc import ABC , abstractmethod
from collections import namedtuple
from config import db
from utils.constants import ALLOWED_ATTRIBUTES

OperationResult = namedtuple('OperationResult',['status','return_data'])

class ReadWriteRepositoryInterface(ABC):
    def __init__(self, model):
        self.model = model


    @abstractmethod
    def create():
        pass

    
    def update(self, params_dict, resource=None):
        if resource is None:
            resource = self.get_item_by_id(params_dict['resource_id'])
        for key, value in params_dict.items():
            if hasattr(resource,key) and key in ALLOWED_ATTRIBUTES[self.model]:
                setattr(resource,key,value)
        db.session.add(resource)
        return resource

    def update_and_commit(self, params_dict, resource=None):
        updated_resource = self.update(params_dict, resource)
        db.session.commit()
        return updated_resource

    def delete(self,resource_id=None,resource=None):
        if resource is None:
            if resource_id is None:
                raise ValueError("I need something cmon man")
            resource = self.get_item_by_id(resource_id)
        db.session.delete(resource)
        return

    def delete_and_commit(self, resource_id=None,resource=None):
        self.delete(resource_id,resource)
        db.session.commit()
        return
        
    def get_item_by_id(self,id):
        q = self.get_query_by_id(id)
        return q.first_or_404()
    
    def get_query_by_id(self,id):
        query = self.model.query.filter(self.model.id==id)
        return query

    def filter(self, *filters,base_query=None):
        print(filters)
        print(base_query)
        query = base_query if base_query else self.model.query
        query = query.filter(*filters)
        return query
    
    def paginate(self,query,page=1,per_page=20):
        return query.paginate(page=page, per_page=per_page)


class ReadOnlyRepositoryInterface(ABC):

    def __init__(self, model):
        self.model = model
    
    def get_item_by_id(self,id):
        q = self.get_query_by_id(id)
        return q.first_or_404()
    
    def get_query_by_id(self,id):
        query = self.model.query.filter(self.model.id==id)
        return query

    def filter(self,*filters, base_query=None):
        query = base_query if base_query else self.model.query
        query = query.filter(*filters)
        return query
    
    def paginate(self,query,page=1,per_page=20):
        return query.paginate(page=page, per_page=per_page)
    
