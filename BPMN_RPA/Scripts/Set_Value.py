from typing import List, Any


def value_to_variable(value: Any) -> Any:
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

def split_string_to_list(string: str, separator: str = " ", maxsplit:int = -1) -> List:
    """
    Convert a string with to a list
    :param string: The string to convert
    :param separator: Optional. Specifies the separator to use when splitting the string. By default any whitespace is a separator.
    :param maxsplit: Optional. Specifies how many splits to do. Default value is -1, which is "all occurrences".
    :return: A list created from the string
    """
    separator = separator.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')
    return string.split(separator, maxsplit=int(maxsplit))
