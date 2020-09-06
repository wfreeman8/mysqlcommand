import re
from datetime import (datetime, date, time)

class Parameters:
  __PARAMETER_EXPRESSION = r"^\?[a-zA-Z0-9]{2,}"
  def __init__(self):
    self.__parameters: Dict = {}

  def add(self, name: str, value, type=None):
    if not re.match(self.__PARAMETER_EXPRESSION, name):
      raise Exception(name + ' is an invalid name, new parameters'
        ' must start with ? and be alphanumeric')
    self.__validate_value(name, value)
    self.__parameters[name] = value
    return value

  def set(self, name: str, value, type = None):
    if re.match(self.__PARAMETER_EXPRESSION, name) and self.contains(name):
      self.__validate_value(name, value)
      self.__parameters[name] = value
      return value

    raise Exception('name is either invalid or has not been set yet')

  def remove(self, name: str) -> bool:
    if re.match(self.__PARAMETER_EXPRESSION, name) and self.contains(name):
      del self.__parameters[name]
      return True
    return False

  def setadd(self, name: str, value):
    if self.contains(name):
      return self.set(name, value)
    else:
      return self.add(name, value)

  def value(self, name: str):
    if re.match(self.__PARAMETER_EXPRESSION, name) and self.contains(name):
      if isinstance(self.__parameters[name], datetime):
        return self.__parameters[name].strftime('%Y-%m-%d %H:%M:%S')
      elif isinstance(self.__parameters[name], date):
        return self.__parameters[name].isoformat()
      elif isinstance(self.__parameters[name], time):
        return self.__parameters[name].isoformat()

      return self.__parameters[name]


    raise Exception(name + ' Value does not exist')
    return False

  def __validate_value(self, name, value):
    if self.__is_scalar(value):
      return True
    if self.__is_datetime(value):
      return True
    if value is None:
      return True


    if isinstance(value, list):
      if not value:
        raise Exception(name + ' list cannot be empty')
      for list_value in value:
        if not self.__is_scalar(list_value) and list_value is not None:
          raise Exception(name + ' list contains invalid type '
            + type(list_value).__name__)
      return True

    raise Exception(type(value).__name__ + ' is not a valid type')

  def __is_datetime(self, value):
    return (isinstance(value, datetime)
      or isinstance(value, date)
      or isinstance(value, time)
    )

  def __is_scalar(self, value):
    return (isinstance(value, int)
      or isinstance(value, str)
      or isinstance(value, bool)
      or isinstance(value, float))

  def contains(self, name: str):
    return name in self.__parameters.keys()