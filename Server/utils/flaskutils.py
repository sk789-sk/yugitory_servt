

def get_filter_params(repoClass, request_args):
    """
    Extracts the filter parameters from request_args in URL, based on the filters defined in the repoClass, which is a subclass of the ReadWriteRepositoryInterface

    Args: repoClass: Some repository class
    request_args: the dict contianing the filter params
    
    Returns: A list of SQL alchemy filter expressions
    """
    filters = []

    filter_dict = repoClass.search_filters

    for key, value in request_args.items():
        if key in filter_dict:
            filters.append(filter_dict[key](value))
    return filters