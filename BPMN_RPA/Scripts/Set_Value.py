from typing import List, Any


def value_to_variable(value: Any, convert_to_list = False) -> Any:
    """
    Function for returning a value to the WorkflowEngine.
    :param value: Any value.
    :param convert_to_list: Optional. Indicator whether to try to convert the value to a List.
    :return: The original input value.
    """
    if ',' in str(value) and isinstance(value, str) and convert_to_list:
        values = []
        value = value.split(',')
        for v in value:
            values.append(v.strip())
        value = values
    return value


def split_string_to_list(string: str, separator: str = " ", maxsplit: int = -1) -> List:
    """
    Convert a string with a separator to a list.
    :param string: The string to convert.
    :param separator: Optional. Specifies the separator to use when splitting the string. By default any whitespace is a separator.
    :param maxsplit: Optional. Specifies how many splits to do. Default value is -1, which is "all occurrences".
    :return: A list created from the string.
    """
    separator = separator.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')
    return string.split(separator, maxsplit=int(maxsplit))


def increment_counter(counter: any, step: int=1) -> Any:
    """
    Increment a counter variable by step (default = 1)
    :param counter: the variable to add step to
    :param step: the increase value
    :return: Any: the value after increase (int or float)
    """

    # handle int and float
    if isinstance(counter, int) or isinstance(counter, float):
        newcounter = counter + step
    # handle string, might convert to int of float or might not
    elif isinstance(counter, str):
        try:
            newcounter = int(counter) + step
        except:
            newcounter = 0
    # handle all data types other than int, float and str
    else:
        newcounter = 0

    return newcounter
