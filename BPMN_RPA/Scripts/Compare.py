from datetime import datetime


# The BPMN-RPA Compare module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA Compare module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

def is_first_item_equal_to_second_item(first_item: any, second_item: any) -> bool:
    """
    Compare two items and check if they are equal.
    :param first_item: The first item to compare.
    :param second_item: The second item to compare.
    :return: Boolean True or False.
    """
    return first_item == second_item


def is_first_item_less_than_second_item(first_item: any, second_item: any) -> bool:
    """
    Check if first item is less than second item.
    :param first_item: The first item to compare.
    :param second_item: The second item to compare.
    :return: Boolean True or False.
    """
    if not isinstance(first_item, int) or not isinstance(first_item, float):
        raise Exception("The first item isn't a number")
    if not isinstance(second_item, int) or not isinstance(second_item, float):
        raise Exception("The second item isn't a number")
    return first_item < second_item


def is_first_item_greater_than_second_item(first_item: any, second_item: any) -> bool:
    """
    Check if first item is greater than second item.
    :param first_item: The first item to compare.
    :param second_item: The second item to compare.
    :return: Boolean True or False.
    """
    if not isinstance(first_item, int) or not isinstance(first_item, float):
        raise Exception("The first item isn't a number")
    if not isinstance(second_item, int) or not isinstance(second_item, float):
        raise Exception("The second item isn't a number")
    return first_item > second_item


def is_first_item_less_or_equal_than_second_item(first_item: any, second_item: any) -> bool:
    """
    Check if first item is less or equal to second item.
    :param first_item: The first item to compare.
    :param second_item: The second item to compare.
    :return: Boolean True or False.
    """
    if not isinstance(first_item, int) or not isinstance(first_item, float):
        raise Exception("The first item isn't a number")
    if not isinstance(second_item, int) or not isinstance(second_item, float):
        raise Exception("The second item isn't a number")
    return first_item <= second_item


def is_first_item_greater_or_equal_than_second_item(first_item: any, second_item: any) -> bool:
    """
    Check if first item is greater or equal to second item.
    :param first_item: The first item to compare.
    :param second_item: The second item to compare.
    :return: Boolean True or False.
    """
    if not isinstance(first_item, int) or not isinstance(first_item, float):
        raise Exception("The first item isn't a number")
    if not isinstance(second_item, int) or not isinstance(second_item, float):
        raise Exception("The second item isn't a number")
    return first_item >= second_item


def is_time_interval_less_or_equal(datetime1: any, datetime2: any, interval_in_seconds: int) -> bool:
    """
    Check if the interval between 2 date-times is less or equal than the given amount of seconds.
    :param datetime1: The first datetime object.
    :param datetime2: The second datetime object.
    :param interval_in_seconds: The interval in seconds.
    :return: Boolean True or False.
    """
    if not isinstance(datetime1, datetime):
        datetime1 = datetime.combine(datetime1, datetime.now().time())
    if not isinstance(datetime2, datetime):
        datetime2 = datetime.combine(datetime2, datetime.now().time())
    return (datetime2 - datetime1).total_seconds() <= int(interval_in_seconds)


def is_time_number_of_seconds_ago(date_time: any, interval_in_seconds: int) -> bool:
    """
    Check if the interval of a date-time is less or equal than the given amount of seconds compared to now.
    :param date_time: The datetime object.
    :param interval_in_seconds: The interval in seconds.
    :return: Boolean True or False.
    """
    if not isinstance(date_time, datetime):
        date_time = datetime.combine(date_time, datetime.now().time())
    return (date_time - datetime.now()).total_seconds() <= int(interval_in_seconds)


def item1_contains_item2(first_item: any, second_item: any, exact_match: bool = True) -> bool:
    """
    Check if item 1 contains item2.
    :param exact_match:
    :param first_item: The first object.
    :param second_item: The second object.
    :return: True or False.
    """
    if isinstance(first_item, str) and isinstance(second_item, str):
        return str(first_item).__contains__(second_item)
    if isinstance(first_item, dict) and isinstance(second_item, str):
        if exact_match:
            return first_item.keys().__contains__(second_item)
        else:
            for x in first_item.keys():
                if str(x).__contains__(second_item):
                    return True
            return False
    if isinstance(first_item, list) and isinstance(second_item, str):
        if exact_match:
            return first_item.__contains__(second_item)
        else:
            for x in first_item:
                if str(x).__contains__(second_item):
                    return True
            return False
    return first_item.__contains__(second_item)


def does_list_contain_item(list_object: list, item: any) -> bool:
    """
    Check if list contains an item.
    :param list_object: The list object.
    :param item: The item to check for.
    :return: True or False.
    """
    return list_object.__contains__(item)


def does_list_contain_any_items(list_object: any) -> bool:
    """
    Check if a list contains items.
    :param list_object: The list object to check.
    :return: True or False.
    """
    if list_object is None:
        return False
    # region When working with email from ExchangeLib:
    if str(list_object).lower().__contains__("queryset"):
        count = int(str(list_object).split("=")[-1].replace(")", "").strip())
        if count == 0:
            return False
        else:
            return True
    if str(list_object).lower().__contains__("message(mime_content"):
        return True
    # endregion
    if not isinstance(list_object, list):
        list_object = [list_object]
    if len(list_object) > 0:
        tmp = str(list_object[0])
        if tmp.startswith("%") and tmp.endswith("%") and len(list_object) == 1:
            return False
        else:
            return True
    else:
        return False


def is_object_empty(inspected_object: any) -> bool:
    """
    Check if an item is empty.
    :return: Boolean True or False.
    """
    #  region When working with email from ExchangeLib:
    if str(inspected_object).lower().__contains__("queryset"):
        count = int(str(inspected_object).split("=")[-1].replace(")", "").strip())
        if count==0:
            return True
        else:
            return False
    if str(inspected_object).lower().__contains__("message(mime_content"):
            return False
    # endregion
    if isinstance(inspected_object, str):
        return inspected_object == ""
    if isinstance(inspected_object, list):
        return len(inspected_object) == 0
    if isinstance(inspected_object, tuple):
        return False
    if isinstance(inspected_object, set):
        return len(inspected_object) == 0
    if isinstance(inspected_object, dict):
        return len(inspected_object.keys()) == 0
    if isinstance(inspected_object, inspected_object):
        return inspected_object is None
    raise Exception("Cannot determine if given object is empty...")


def is_object_not_empty(inspected_object: any) -> bool:
    """
    Check if an item is not empty.
    :return: Boolean True or False.
    """
    return not is_object_empty(inspected_object)
