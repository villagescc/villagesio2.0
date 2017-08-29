from database.wrapper import Database
from .connection_strings import POSTGRESQL, SQLSERVER


class PostgresLocal(Database):
    connection_string = POSTGRESQL
    host = '127.0.0.1'
    database = 'teste'
    username = 'postgres'
    password = 'teste123!'


class Villages(Database):
    connection_string = POSTGRESQL
    host = 'localhost'
    database = 'villages'


class VillagesRipple(Database):
    connection_string = POSTGRESQL
    host = 'localhost'
    database = 'villagesripple'