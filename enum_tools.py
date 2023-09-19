from enum import Enum

def keynum(my_enum):
    enum_list = list(my_enum)
    keyval_list = []
    for each_enum in enum_list:
        keyval_list.append({each_enum.name:each_enum.value})
    return keyval_list

