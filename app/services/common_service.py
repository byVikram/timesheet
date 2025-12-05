from sqlalchemy.exc import SQLAlchemyError

def getIdFromCode(model, code):
    """
    Fetch the ID of a record from the database using its unique code.

    :param model: SQLAlchemy model class (e.g., User, UserRole)
    :param code: The unique code of the record
    :return: Tuple (id, error). id is None if not found, error is None if success.
    """
    try:
        record = model.query.filter_by(code=code).first()
        if not record:
            return None, f"{model.__name__} with code '{code}' not found."
        return record.id, None
    
    except SQLAlchemyError as e:
        return None, str(e)
