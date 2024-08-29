from .repository_interface import ReadOnlyRepositoryInterface
from utils.constants import ALLOWED_ATTRIBUTES
from models import CardinSet
from flask_sqlalchemy import SQLAlchemy
from config import db
from sqlalchemy.exc import SQLAlchemyError

class CardinSetRepository(ReadOnlyRepositoryInterface):
    search_filters = {}

    def __init__(self):
        super().__init__(CardinSet)