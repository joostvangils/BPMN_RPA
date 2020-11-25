def main(value):
    """
    Function for returning a value to the WorkflowEngine
    :param value: Any value
    :return: The original input value
    """
    if ',' in str(value) and isinstance(value,str):
        values=[]
        value=value.split(',')
        for v in value:
            values.append(v.strip())
        value=values
    return value


def value_to_variable(value):
    return value
