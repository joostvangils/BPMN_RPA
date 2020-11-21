
def is_first_item_equal_to_second_item(first_item, second_item):
    """
    Compare two items and check if they are equal
    :param first_item: The first item to compare
    :param second_item: The second item to compare
    :return: Boolean True or False
    """
    return first_item == second_item


def is_first_item_less_than_second_item(first_item, second_item):
    """
    Check if first item is less than second item
    :param first_item: The first item to compare
    :param second_item: The second item to compare
    :return: Boolean True or False
    """
    if not isinstance(first_item, int) or not isinstance(first_item, float):
        raise Exception("The first item isn't a number")
    if not isinstance(second_item, int) or not isinstance(second_item, float):
        raise Exception("The second item isn't a number")
    return first_item < second_item


def is_first_item_greater_than_second_item(first_item, second_item):
    """
    Check if first item is greater than second item
    :param first_item: The first item to compare
    :param second_item: The second item to compare
    :return: Boolean True or False
    """
    if not isinstance(first_item, int) or not isinstance(first_item, float):
        raise Exception("The first item isn't a number")
    if not isinstance(second_item, int) or not isinstance(second_item, float):
        raise Exception("The second item isn't a number")
    return first_item > second_item


def is_first_item_less_or_equal_than_second_item(first_item, second_item):
    """
    Check if first item is less or equal to second item
    :param first_item: The first item to compare
    :param second_item: The second item to compare
    :return: Boolean True or False
    """
    if not isinstance(first_item, int) or not isinstance(first_item, float):
        raise Exception("The first item isn't a number")
    if not isinstance(second_item, int) or not isinstance(second_item, float):
        raise Exception("The second item isn't a number")
    return first_item <= second_item


def is_first_item_greater_or_equal_than_second_item(first_item, second_item):
    """
    Check if first item is greater or equal to second item
    :param first_item: The first item to compare
    :param second_item: The second item to compare
    :return: Boolean True or False
    """
    if not isinstance(first_item, int) or not isinstance(first_item, float):
        raise Exception("The first item isn't a number")
    if not isinstance(second_item, int) or not isinstance(second_item, float):
        raise Exception("The second item isn't a number")
    return first_item >= second_item
