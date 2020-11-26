from datetime import datetime
from typing import Any

def is_first_item_equal_to_second_item(first_item: Any, second_item: Any)-> bool:
    """
    Compare two items and check if they are equal
    :param first_item: The first item to compare
    :param second_item: The second item to compare
    :return: Boolean True or False
    """
    return first_item == second_item


def is_first_item_less_than_second_item(first_item: Any, second_item: Any)-> bool:
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


def is_first_item_greater_than_second_item(first_item: Any, second_item: Any)-> bool:
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


def is_first_item_less_or_equal_than_second_item(first_item: Any, second_item: Any)-> bool:
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


def is_first_item_greater_or_equal_than_second_item(first_item: Any, second_item: Any)-> bool:
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

def is_time_interval_less_or_equal(datetime1: Any, datetime2: Any, interval_in_seconds: int) -> bool:
    """
    Check if the interval between 2 date-times is less or equal than the given amount of seconds.
    :param datetime1: The first datetime object
    :param datetime2: The second datetime object
    :param interval_in_seconds: The interval in seconds
    :return: Boolean True or False
    """
    return (datetime2 - datetime1).total_seconds() <= interval_in_seconds

def is_time_number_of_seconds_ago(date_time: Any, interval_in_seconds: int) -> bool:
    """
    Check if the interval of a date-time is less or equal than the given amount of seconds compared to now.
    :param datetime1: The first datetime object
    :param datetime2: The second datetime object
    :param interval_in_seconds: The interval in seconds
    :return: Boolean True or False
    """
    return (date_time - datetime.now()).total_seconds() <= interval_in_seconds
