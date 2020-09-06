""" MySql database API """
import mysql.connector
import re
import math
from .parameters import Parameters

class MysqlCommand:
  PARAMETER_EXPRESSION = r'\?[a-zA-Z0-9_-]{2,}(?=(?:[^"]*"[^"]*")*[^"]*$)'
  def __init__(
    self, commandstr: str = '',
    dbcon: mysql.connector.MySQLConnection = None):
    self.__validate_database_connection(dbcon)
    self.commandstr = commandstr
    self.table_data: dict = {}
    self.__dbcon = dbcon
    self.__database = dbcon.database
    self.__autocommit: bool = True
    self.parameters: Parameters = Parameters()

  def set_database(self, database):
    """
    set to use a different database
    """
    self.__database = database
    self.__dbcon.database = database

  def __create_cursor(self, buffered: bool = True):
    """
    create mysql connector cursor to use
    """
    if not hasattr(self, '__cursor') or self.__cursor is None:
      cursorArgs = {
        'dictionary' : True,
        'buffered': buffered,
      }
      self.__cursor = self.__dbcon.cursor(**cursorArgs)

    return True

  def execute_reader(self, buffered: bool = True):
    """
    execute a result set query
    """
    self.__create_cursor(buffered)
    self.process_query_parameters()
    self.__cursor.execute(self.prepared_query, self.prepared_args)

  def read_all(self):
    """
    execute a result set query and return the entire resultset
    """
    if self.commandstr:
      self.execute_reader()
      return self.__cursor.fetchall()
    return None

  def read(self) -> bool:
    """
    fetch the next record from cursor
    """
    self.__data = self.__cursor.fetchone()
    if self.__data is None:
      return False
    return True

  def execute_non_query(self, commit_query: bool = False):
    """
    execute a non result set query
    """
    self.__create_cursor()
    self.process_query_parameters()

    result = self.__cursor.execute(self.prepared_query, self.prepared_args)
    if (self.__dbcon.autocommit == False
      and (commit_query or self.__autocommit)):
      self.__dbcon.commit()

    return self.__cursor.rowcount

  def execute_scalar(self):
    """
    retrieve single first value of result set
    """
    tmp_cursor = self.__dbcon.cursor(dictionary=False)
    self.process_query_parameters()
    tmp_cursor.execute(self.prepared_query, self.prepared_args)

    row = tmp_cursor.fetchone();
    if row is not None:
      return row[0]

    return None

  def process_query_parameters(self):
    """
      create prepared query string from commandstr by replacing parameters
      with cursor respected parameters
      create argument dictionary of needed arguments
    """

    self.prepared_query = self.commandstr
    self.prepared_args: dict = {}

    parameter_list: list = re.findall(
      self.PARAMETER_EXPRESSION, self.commandstr)

    if not parameter_list:
      pass

    parameter_set: set = set(parameter_list)

    for parameter_name in parameter_set:
      if self.parameters.contains(parameter_name) == False:
        raise Exception(parameter_name + ' is not accessible')

      parameter_value = self.parameters.value(parameter_name)
      if isinstance(parameter_value, list):
        # parameter keys can't include -
        pv_dict: dict = {}
        for pv_i, pv_value in enumerate(parameter_value):
          pv_dict[parameter_name.lstrip('?') + '-' + str(pv_i)] = pv_value
        self.prepared_query = self.prepared_query.replace(parameter_name,
          '(' + (','.join(['%s'] * len(parameter_value)) % tuple(
            ['%(' + pv_i + ')s' for pv_i in pv_dict.keys()])) + ')')
        self.prepared_args.update(pv_dict)
        # print(self.prepared_query)
        # print(self.prepared_args)
        # exit()


      else:
        self.prepared_query = self.prepared_query.replace(parameter_name, '%('
        + parameter_name.lstrip('?') + ')s')

        self.prepared_args[parameter_name.lstrip('?')] = parameter_value

    return True

  def insert(self, db_table: str, insert_arr):
    """
    insert records into table
    """
    if not db_table:
      raise Exception('Table argument is empty')

    if not insert_arr:
      raise Exception('Insert Array is empty')

    self.__create_cursor()
    self.__retrieve_table_data(db_table)

    if self.table_data[db_table] is None:
      raise Exception('Was unable to receive table column information for '
      + db_table)

    single_insert = False
    if isinstance(insert_arr, dict):
      single_insert = True
      insert_arr = list([insert_arr])

    fields: list = list(insert_arr[0].keys())

    if not fields:
      return False

    insert_base_str = 'insert into `' + db_table + ('` (`'
    + '`,`'.join(self.table_data[db_table]['table_fields'])
    + '`) values ')

    insert_parameters:list = []

    # paginate over 2000
    insert_max = 10000
    page_count = math.ceil(len(insert_arr) / insert_max)
    total_inserted = 0

    table_column_defaults = self.table_data[db_table]['table_fields_default']
    for range_pg in range(page_count):
      insert_parameters = []

      insert_str = insert_base_str + (('(' + ','.join(['%s']
      * len(self.table_data[db_table]['table_fields'])) + '),')
      * len(insert_arr[range_pg*insert_max:(range_pg+1)
      * insert_max])).rstrip(',')

      for insertRow in (insert_arr[range_pg*insert_max:(range_pg+1)
      * insert_max]):
        for field in self.table_data[db_table]['table_fields']:
          if field in insertRow:
            insert_parameters.append(insertRow[field])
          elif field in table_column_defaults:
            insert_parameters.append(table_column_defaults[field])
          else:
            insert_parameters.append(None)

      self.__cursor.execute(insert_str, insert_parameters)
      total_inserted += self.__cursor.rowcount

    if self.__dbcon.autocommit == False and self.__autocommit:
      self.__dbcon.commit()

    # if single insert then return the autoincremement created id
    if single_insert and self.__cursor.lastrowid is not None:
      return self.__cursor.lastrowid

    return total_inserted

  def __retrieve_table_data(self, db_table) -> dict:
    """
    retrieve table data information - primary key, column names and types
    """
    if db_table in self.table_data:
      return self.table_data[db_table]

    self.__cursor.execute('show full columns from `' + db_table + '`')
    table_fields: list = []
    table_fields_default: dict = {}
    while self.read():
      table_fields.append(self.data['Field'])
      if self.data['Default']:
        table_fields_default[self.data['Field']] = self.data['Default']
      elif self.data['Null'] == 'YES':
        table_fields_default[self.data['Field']] = None

    if not table_fields:
      raise Exception(db_table + ' is an invalid table. No field found')

    self.table_data[db_table] = {
      'table_fields': table_fields,
      'table_fields_default': table_fields_default
    }

    return self.table_data[db_table]

  def set_autocommit(self, setting: bool = True):
    self.__autocommit = setting

  def commit(self):
    self.__dbcon.commit()

  def get_error(self):
    if self.__cursor.fetchwarnings() is not None:
      return self.__cursor.fetchwarnings()

  def get_table_primary_key(self, db_table):
    """
    get table primary key of table
    """
    self.__create_cursor()
    self.__cursor.execute('show keys from `'
    + db_table + '` where key_name = "PRIMARY"')

    row = self.__cursor.fetchone();
    if row is None:
      return False
    else:
      return row['Column_name']

  def has_rows(self):
    """
      check if cursor exists and still contains rows
    """
    if self.__cursor is not None and self.__cursor.with_rows:
      return True

    return False

  def last_insert_id(self):
    """
    retrieve the last inserted id
    """
    if self.__cursor.lastrowid:
      return self.__cursor.lastrowid

    return False

  def __validate_database_connection(
    self, dbcon: mysql.connector.MySQLConnection):
    if ((not isinstance(dbcon, mysql.connector.MySQLConnection)
        and not isinstance(dbcon, mysql.connector.CMySQLConnnection))
      or not dbcon.is_connected()):
      raise Exception('Database connection must be an open MySQLConnection')

  @property
  def database(self):
    return self.__database

  # allows read-only access to the row data
  @property
  def data(self):
    return self.__data