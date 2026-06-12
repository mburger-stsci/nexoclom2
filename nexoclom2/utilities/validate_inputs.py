from nexoclom2.utilities.database_operations import DatabaseOperations


def validate_inputs(inputs):
    """Inserts a set of inputs into the database if necessary"""
    db = DatabaseOperations()
    this_id = db.search_inputs(inputs)
    if this_id is None:
        this_id = db.insert_inputs(inputs)
    else:
        pass
