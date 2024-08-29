from .repository_interface import ReadOnlyRepositoryInterface
from models import Card


class SetsRepository(ReadOnlyRepositoryInterface):
    card_filters = {
        'releaseDate_exact' : '',
        'releaseDate_less_than' : '',
        'releaseDate_greater_than' : '',
        'name_exact' : '',
        'name_partial' : '',
    }

    def __init__(self):
        super().__init__(Card)