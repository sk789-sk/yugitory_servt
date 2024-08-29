from repository_interface import ReadWriteRepositoryInterface
from models import User

class UserRepository(ReadWriteRepositoryInterface):

    card_filters = {

    }

    def __init__(self):
        super().__init__(User)