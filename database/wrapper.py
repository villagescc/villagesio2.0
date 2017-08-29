from sqlalchemy import create_engine, Table, event
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from .exceptions import ApplicationError
from database.helpers import restart_savepoint
from .models import Base


class Database(object):
    """
    This class was a "bridge" between SQLAlchemy and Elasticsearch.
    Now it's only a wrapper to SQLAlchemy sessions/engine calls.
    """

    connection_string = None
    database = None
    host = None

    def __init__(self, username, password, application_name, echo=False, database=None, host=None, base=Base,
                 connection_string=None, use_scoped_session=True):
        """
        Initializes a connection to the database.
        :param username: The username that will be used to connect at the database.
        :param password: The password of the given user.
        :param application_name: The name of the application that is requesting this connection.
        :param echo (optional): If true the queries will sent to the console. (debugging purposes)
        :param database (optional): The name of the database to be connected.
        :param host (optional): The host where this database is located.
        :param scoped_session (optional): Indicates whether the session is scoped or not
        :return: None
        """
        self.username = username
        self.password = password
        self.application_name = application_name
        self.echo = echo
        self.database = database if database else self.__class__.database
        self.host = host if host else self.__class__.host
        self.connection_string = connection_string if connection_string else self.connection_string
        self.connection_string = self.connection_string.format(self.username, self.password, self.host, self.database)
        self.auto_commit = True
        self.engine = None
        self.base = base
        self.use_scoped_session = use_scoped_session
        self.session = self.open()

    def open_snapshot(self):
        """
        TODO:
        :return:
        """
        self.session.begin_nested()
        event.listen(self.session, "after_transaction_end", restart_savepoint)

    def close_snapshot(self):
        """
        TODO:
        :return:
        """
        self.close()
        self.session = self.open()

    def create_database(self, database_name):
        """
        Create a database and returns a new connection with this same user logged in.
        :param database_name: The name of the database.
        :return: None
        """
        if self.database == database_name:
            raise ApplicationError('You cannot create the database that you are logged in.')
        else:
            self.session.execute('COMMIT')
            self.session.execute('CREATE DATABASE {0}'.format(database_name))
            self.session.commit()

    def new_connection(self, username=None, password=None, application_name=None, database=None, host=None,
                       base=None, echo=None, connection_string=None, use_scoped_session=None, close_after_commit=None):
        """
        Creates a new connection exactly like this one.
        :return: SQLWrapper object
        """
        username = username if username else self.username
        password = password if password else self.password
        application_name = application_name if application_name else self.application_name
        database = database if database else self.database
        connection_string = connection_string if connection_string else self.connection_string
        host = host if host else self.host
        base = base if base else self.base
        echo = echo if echo else self.echo
        use_scoped_session = use_scoped_session if use_scoped_session else self.use_scoped_session
        return self.__class__(username, password, application_name, database=database, host=host, base=base, echo=echo,
                              connection_string=connection_string, use_scoped_session=use_scoped_session)

    def get_schemas(self):
        """
        Get all the names of the schemas that are being used by models.
        :return: Schemas list generator.
        """
        schemas = []
        for table_name in self.base.metadata.tables:
            schema = table_name.split('.')[0]
            if schema not in schemas:
                schemas.append(schema)
                yield schema

    def create_schemas(self):
        """
        Creates all needed schemas for the tables declared at the models.
        :return: self
        """
        for schema in self.get_schemas():
            self.raw_query('CREATE SCHEMA IF NOT EXISTS {0};'.format(schema))
        if self.auto_commit:
            self.commit()
        return self

    def drop_schemas(self, cascade=False):
        """
        Drop all schemas that are being used by tables declared at the models.
        :return: self
        """
        for schema in self.get_schemas():
            query = 'DROP SCHEMA IF EXISTS {0}'
            if cascade:
                query += ' CASCADE'
            self.raw_query(query.format(schema) + ';')
        if self.auto_commit:
            self.commit()
        return self

    def reset_id_sequence(self, model, value):
        """
        Resets the auto increment count for the id sequence
        :param model:
        :param value:
        :return:
        """
        if isinstance(model, Table):
            table_name = '{0}.{1}'.format(model.schema, model.name)
        else:
            if 'schema' in model.__table_args__:
                table_name = '{0}.{1}'.format(model.__table_args__['schema'], model.__tablename__)
            else:
                table_name = '{0}.{1}'.format(model.__table_args__[1]['schema'], model.__tablename__)
        self.raw_query('ALTER SEQUENCE {0} RESTART WITH {1};'.format(table_name + '_id_seq', value))

    def open(self):
        """
        Create a new database session replacing the old one if exists.
        :return: None
        """
        self.create_engine()
        sm = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False)
        if self.use_scoped_session:
            return scoped_session(sm)
        else:
            return sm()

    def close(self):
        """
        Closes the current session.
        :return: self
        """
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()
        return self

    def create_tables(self):
        """
        Create all tables declared on models.
        """
        self.base.metadata.create_all(self.engine)
        return self

    def drop_tables(self):
        """
        Drop all tables declared on models.
        """
        self.base.metadata.drop_all(self.engine)
        return self

    def create_engine(self):
        """
        Create the engine responsible to manage the connection pool.
        :return:
        """
        connection_args = {}
        if 'postgresql+psycopg2' in self.connection_string:
            connection_args['application_name'] = self.application_name
        self.engine = create_engine(self.connection_string, echo=self.echo, connect_args=connection_args)

    def create_table(self, model):
        """
        Create the respective table of the given model.
        :param model: The LSQL model.
        :return: self
        """
        if isinstance(model, Table):
            self.base.metadata.create_all(self.engine, [model])
        else:
            if '__table__' in model.__dict__:
                self.base.metadata.create_all(self.engine, [model.__table__])
            else:
                raise SyntaxError('Please use a model instance on model parameter.')
        return self

    def drop_table(self, model):
        """
        Drop the respective table of the given model.
        :param model:  The LSQL model.
        :return: self
        """
        if isinstance(model, Table):
            self.base.metadata.drop_all(self.engine, [model])
        else:
            if '__table__' in model.__dict__:
                self.base.metadata.drop_all(self.engine, [model.__table__])
            else:
                raise SyntaxError('Please use a model instance on model parameter.')
        return self

    def find(self, model_class, *args, **kwargs):
        """
        Return the objects created by executing the SQL Query.
        After calling this find you are free to call whatever you want from SQLAlchemy.
        :param model_class: The LSQL model, fields, lists.
        :return: Query Object
        """
        return QueryObject(self.session.query(model_class, *args, **kwargs), self)

    def raw_query(self, sql):
        """
        Performs a SQL query and returns the result.

        WARNING: This method DOES NOT perform a commit even though auto_commit is True. This is because the sql
        can contain a COMMIT command, resulting in the wrapper losing control of the commit commands.
        :param sql: The raw SQL query that will be executed.
        :return: None
        """
        return self.session.execute(sql)

    def save(self, model_instance):
        """
        Adds a object to the session and immediately commits the transaction if auto_commit is turned on.
        :param model_instance: The model instance to be saved.
        :return: self
        """
        self.session.add(model_instance)
        if self.auto_commit:
            self.commit()
        return self

    def add(self, model_instance):
        """
        Adds a object to the session
        :param model_instance: The model instance to be added.
        :return: self
        """
        self.session.add(model_instance)
        return self

    def commit(self):
        """
        Commits the current transaction and starts a new one.
        :return: None
        """
        self.session.commit()
        self.auto_commit = True

    def flush(self):
        """
        Flush the pending objects of this session to the database.
        :return: None
        """
        self.session.flush()

    def begin_nested(self):
        """
        Starts a new save point to the database.
        Please do not use this function in production since the performance impacts are probably high.
        :return: None
        """
        return self.session.begin_nested()

    def begin_transaction(self):
        """
        Commits current transaction, turn off auto_commit and starts a new one.
        :return: None
        """
        self.auto_commit = False
        return self

    def __enter__(self):
        """
        Provides the "with db.begin_transaction()" sintax
        :return:
        """
        return self

    def __exit__(self, *args):
        """
        Called when exiting from "with begin_transaction()" sintax
        :param args:
        :return:
        """
        if args[0]:
            return False
        else:
            self.commit()
            return True

    def rollback(self):
        """
        Rollback the current transaction. Please be in mind that SQLAlchemy probably will start another right after.
        There is no need to begin a new transaction manually.
        :return: None
        """
        self.session.rollback()
        self.auto_commit = True

    def delete(self, model_instance):
        """
        Deletes a given object from the database.
        :param model_instance: A model instance.
        :return: None
        """
        self.session.delete(model_instance)
        if self.auto_commit:
            self.commit()


class QueryObject:
    """
    Acts like a man-in-the-middle for SQLAlchemy queries.
    This is necessary for avoiding the "idle in transaction" state after queries with auto_commit.
    """

    def __init__(self, query, wrapper):
        self.query = query
        self.wrapper = wrapper

    def distinct(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.distinct.
        """
        self.query = self.query.distinct(*args, **kwargs)
        return self

    def delete(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.count.
        """
        self.query = self.query.delete(*args, **kwargs)
        return self

    def instances(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.instances.
        """
        self.query = self.query.instances(*args, **kwargs)
        return self

    def group_by(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.group_by.
        """
        self.query = self.query.group_by(*args, **kwargs)
        return self

    def intersect(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.intersect.
        """
        queries = []
        for wrapper_query in args:
            queries.append(wrapper_query.query)
        self.query = self.query.intersect(*queries, **kwargs)
        return self

    def intersect_all(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.intersect_all.
        """
        queries = []
        for wrapper_query in args:
            queries.append(wrapper_query.query)
        self.query = self.query.intersect_all(*queries, **kwargs)
        return self

    def label(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.label.
        """
        self.query = self.query.label(*args, **kwargs)
        return self

    def offset(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.offset.
        """
        self.query = self.query.offset(*args, **kwargs)
        return self

    def union_all(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.union_all.
        """
        queries = []
        for wrapper_query in args:
            queries.append(wrapper_query.query)
        self.query = self.query.union_all(*queries, **kwargs)
        return self

    def union(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.union.
        """
        queries = []
        for wrapper_query in args:
            queries.append(wrapper_query.query)
        self.query = self.query.union(*queries, **kwargs)
        return self

    def join(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.join.
        """
        self.query = self.query.join(*args, **kwargs)
        return self

    def outerjoin(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.outerjoin.
        """
        self.query = self.query.outerjoin(*args, **kwargs)
        return self

    def options(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.options.
        """
        self.query = self.query.options(*args, **kwargs)
        return self

    def having(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.having.
        """
        self.query = self.query.having(*args, **kwargs)
        return self

    def order_by(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.order_by.
        """
        self.query = self.query.order_by(*args, **kwargs)
        return self

    def with_for_update(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.with_for_update.
        """
        if self.wrapper.auto_commit:
            raise ApplicationError('Auto commit cannot be turned on when using with_for_update().')
        self.query = self.query.with_for_update(*args, **kwargs)
        return self

    def limit(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.limit.
        """
        self.query = self.query.limit(*args, **kwargs)
        return self

    def exists(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.exists.
        """
        self.query = self.query.exists(*args, **kwargs)
        return self

    def filter_by(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.filter_by.
        """
        self.query = self.query.filter_by(*args, **kwargs)
        return self

    def filter(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.filter.
        """
        self.query = self.query.filter(*args, **kwargs)
        return self

    def subquery(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.subquery.
        """
        return self.query.subquery(*args, **kwargs)

    def count(self, *args, **kwargs):
        """
        Better described at sqlalchemy.orm.query.count.
        """
        try:
            response = self.query.count(*args, **kwargs)
            if self.wrapper.auto_commit:
                self.wrapper.commit()
            return response
        except Exception as exception:
            if self.wrapper.auto_commit:
                self.wrapper.rollback()
            raise exception

    def all(self):
        """
        Better described at sqlalchemy.orm.query.all.
        """
        try:
            response = self.query.all()
            if self.wrapper.auto_commit:
                self.wrapper.commit()
            return response
        except Exception as exception:
            if self.wrapper.auto_commit:
                self.wrapper.rollback()
            raise exception

    def one(self):
        """
        Better described at sqlalchemy.orm.query.one.
        """
        try:
            response = self.query.one()
            if self.wrapper.auto_commit:
                self.wrapper.commit()
            return response
        except Exception as exception:
            if self.wrapper.auto_commit:
                self.wrapper.rollback()
            raise exception

    def scalar(self):
        """
        Better described at sqlalchemy.orm.query.scalar.
        """
        try:
            response = self.query.scalar()
            if self.wrapper.auto_commit:
                self.wrapper.commit()
            return response
        except Exception as exception:
            if self.wrapper.auto_commit:
                self.wrapper.rollback()
            raise exception

    def first(self):
        """
        Better described at sqlalchemy.orm.query.first.
        """
        try:
            response = self.query.first()
            if self.wrapper.auto_commit:
                self.wrapper.commit()
            return response
        except Exception as exception:
            if self.wrapper.auto_commit:
                self.wrapper.rollback()
            raise exception

    def __iter__(self):
        for each in self.query:
            yield each