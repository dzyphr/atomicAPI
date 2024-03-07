from enum import Enum

def keynum(my_enum): 
    enum_list = list(my_enum) #turns an enum into a list
    keyval_list = [] #empty list to hold obj structure
    for each_enum in enum_list: #go through every item in the list
        keyval_list.append({each_enum.name:each_enum.value}) #append a {key:value} pair to the obj generator list
    return keyval_list #return the object built of the original enum's keys and values

