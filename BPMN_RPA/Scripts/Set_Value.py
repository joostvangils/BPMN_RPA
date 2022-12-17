import json

# The BPMN-RPA Set_Value module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA Set_Value module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import uuid


def value_to_variable(value: any, convert_to_list=False) -> any:
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
    if isinstance(value, str) and value.startswith("{") and value.endswith("}") and not convert_to_list:
        value = json.loads(value)
    return value


def json_to_object(json_string: str) -> any:
    """
    Convert a JSON string to an Object.
    :param json_string: The JSON string to convert.
    :return: The Object from the JSON string.
    """
    return json.loads(json_string)


def object_to_json(object: any) -> str:
    """
    Convert an Object to a JSON string.
    :param object: The Object to convert.
    :return: The JSON string.
    """
    return json.dumps(object)


def split_string_to_list(string: str, separator: str = " ", maxsplit: int = -1) -> list:
    """
    Convert a string with a separator to a list.
    :param string: The string to convert.
    :param separator: Optional. Specifies the separator to use when splitting the string. By default any whitespace is a separator.
    :param maxsplit: Optional. Specifies how many splits to do. Default value is -1, which is "all occurrences".
    :return: A list created from the string.
    """
    separator = separator.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')
    return string.split(separator, maxsplit=int(maxsplit))


def increment_counter(counter: any, step: int = 1) -> any:
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
        except (ValueError, Exception):
            newcounter = 0
    # handle all data types other than int, float and str
    else:
        newcounter = 0

    return newcounter


def create_unique_id():
    """
    Generate a unique ID
    :return: Unique ID as string
    """
    return uuid.uuid4().hex


def dummy_function():
    """
    Dummy function for testing purposes
    """
    pass
