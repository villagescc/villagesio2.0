

def get_properties(obj):
    """
    Loops through every attribute and exclude private ones or functions.
    :param obj: The model instance to be inspected.
    :return: List of properties.
    """
    values = {}
    for property_name in obj.__dict__:
        if property_name[0] != '_':
            values[property_name] = getattr(obj, property_name)
    return values


def get_properties_names(obj):
    """
    Loops through every attribute and exclude private ones and functions.
    :param obj: The model instance to be inspected.
    :return:
    """
    if hasattr(obj.__class__, '__tablename__'):
        obj = obj.__class__

    values = []
    for property_name in obj.__dict__:
        if property_name[0] != '_':
            values.append(property_name)
    return values


def update_properties(obj, values):
    """
    
    :param obj: 
    :param values: 
    :return:
    """
    if not isinstance(values, dict):
        raise SyntaxError('Please pass values as a dict.')
    else:
        properties = get_properties_names(obj)
        for property_name in properties:
            if property_name in values:
                setattr(obj, property_name, fix_type(values[property_name]))
    return obj


def filter_properties(obj, values):
    """
    
    :param obj: 
    :param values: 
    :return:
    """
    if not isinstance(values, dict):
        raise SyntaxError('Please pass values as a dict.')
    else:
        properties = get_properties_names(obj)
        for property_name in properties:
            if property_name in values:
                properties[property_name] = fix_type(values[property_name])
        return properties


def normalize(obj):
    """
    
    :param obj: 
    :return:
    """
    for property_name in obj.__dict__:
        obj.__dict__[property_name] = fix_type(obj.__dict__[property_name])
    return obj


def fix_type(obj):
    """
    
    :param obj: 
    :return:
    """
    if isinstance(obj, str):
        if obj == 'True':
            return True
        elif obj == 'False':
            return False
    return obj


def as_dict(model_instance):
    """

    :param model_instance:
    :return:
    """
    return {c.name: getattr(model_instance, c.name) for c in getattr(getattr(model_instance, '__table__'), 'columns')}


def restart_savepoint(session, transaction):
    """

    :param session:
    :param transaction:
    :return:
    """
    if transaction.nested and not getattr(transaction, '_parent').nested:
        session.begin_nested()


def before_save(model, connection, instance):
        """
        Calls before save for a given instance.
        :param model: The parent of the instance.
        :param connection: The connection to the database in question.
        :param instance: The instance to be modified.
        :return: None
        """
        instance.before_save()


def before_insert(model, connection, instance):
        """
        Calls before insert for a given instance.
        :param model: The parent of the instance.
        :param connection: The connection to the database in question.
        :param instance: The instance to be modified.
        :return: None
        """
        instance.before_insert()


def before_update(model, connection, instance):
        """
        Calls before update for a given instance.
        :param model: The parent of the instance.
        :param connection: The connection to the database in question.
        :param instance: The instance to be modified.
        :return: None
        """
        instance.before_save()


def lower_and_encode(value):
    """
    This method should be used when a string has to be saved in binary mode and in lower case.
    :param value: Value to be saved (a string or encoded string is expected)
    :return: Value in lower case and encoded
    """
    value_for_work = value
    if value:
        if type(value) == bytes:
            value_for_work = value.decode('utf-8')
        value_for_work = value_for_work.lower()
        return value_for_work.encode('utf-8')
    return value
