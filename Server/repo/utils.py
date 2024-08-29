class FilterAdapter:
    #Converts the generic stuff from the HTTP request, resource_id/etc to the specifics for that repo

    def __init__(self, repository_class):
        self.repo_class = repository_class
        self.mapping = getattr(repository_class, 'mapping')
        self.filters = getattr(repository_class, 'filters')

    def adaptfilters(self):
        adapted_filters = []

        for key,value in filters.items():
            specific_key = self.mapping.get(key,key)
            if specific_key in self.repo_filters