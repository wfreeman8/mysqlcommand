# Python MysqlCommand

Python MysqlCommand is a MySql query builder that enables using keyword parameters. Inspired by the [MysqlCommand class](https://dev.mysql.com/doc/dev/connector-net/8.0/html/T_MySql_Data_MySqlClient_MySqlCommand.htm) by Mysql for ASP.net

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Python MysqlCommand

```bash
pip install mysqlcommand
```

## Usage

### Select Rows
```python
import mysql.connector
from mysqlcommand import MysqlCommand

dbcon = mysql.connector.connect(
  host='{host}',
  user='{username}',
  passwd='{password}'
)

dbcom = MysqlCommand('select * from {table}', dbcon)
dbcom.execute_reader()

while dbcom.read():
  dbcom.data['{columnName}']
```

### Select Rows using Parameter
```python
dbcom.commandstr = 'select * from {table} where {columnName} = ?columnValue'
dbcom.parameters.add('?columnValue', '{value}')
dbcom.execute_reader()
while dbcom.read():
  dbcom.data['{columnName}']
```

### Select Rows using Parameter with list value
```python
dbcom.commandstr = 'select * from {table} where {columnName} in ?columnValue'
dbcom.parameters.add('?columnValue', ['{value}', '{value2}', '{value3}'])
dbcom.execute_reader()
while dbcom.read():
  dbcom.data['{columnName}']
```
### Retrieve single value
Useful when just needing a boolean or count
```python
dbcom.commandstr = 'select count(*) from {table}'
table_count = dbcom.execute_scalar()
```

### Database Manipulation - Autocommit
```python
# For database manipulation to ensure data changes are saved automatically
dbcom.set_autocommit(True)
```

### Update/Delete using Parameters
```python
dbcom.commandstr = 'update {table} set '{columnName}' = ?columnNewValue where '{columnName}' = ?columnOldValue';
dbcom.parameters.add('?columnOldValue', 3)
dbcom.parameters.add('?columnNewValue', 5)
dbcom.execute_non_query()

# To commit database changes without autocommit
dbcom.commit()

```

### Insert Row
```python
new_row = {
  '{columnName}': 1
}
insert_id = dbcom.insert('{table}', new_row)
```

### Insert Rows
```python
new_rows = [{
  '{columnName}': 2
},
{
  '{columnName}': 3
}]

recordsInserted = dbcom.insert('{table}', new_rows)
```

## Other Parameter options

### Parameter update current parameter valuue
```python
dbcom.parameters.set('?columnOldValue', 5)
```

### Parameter upsert parameter value - update if existing, create if doesn't
```python
dbcom.parameters.setadd('?columnOldValue', 5)
```

### Remove all parameters
```python
dbcom.parameters.clear()
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)