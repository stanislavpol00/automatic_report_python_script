from sqlalchemy import create_engine, event, exc
from sqlalchemy.ext import compiler
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import Pool
from sqlalchemy.schema import DDLElement
from sqlalchemy.sql import table

from config import Config

__all__ = ['Session', 'get_slave_session', 'view']

#
# create views
#
class CreateView(DDLElement):
    def __init__(self, name, selectable):
        self.name = name
        self.selectable = selectable

class DropView(DDLElement):
    def __init__(self, name):
        self.name = name

@compiler.compiles(CreateView)
def compile(element, compiler, **kw):
    return "CREATE OR REPLACE VIEW  %s AS %s" % (
        element.name, 
        compiler.sql_compiler.process(element.selectable)
    )

@compiler.compiles(DropView)
def compile(element, compiler, **kw):
    return "DROP VIEW IF EXISTS %s" % (element.name)

def view(name, metadata, selectable):
    t = table(name)

    for c in selectable.c:
        c._make_proxy(t)

    CreateView(name, selectable).execute_at('after-create', metadata)
    DropView(name).execute_at('before-drop', metadata)

    return t

@event.listens_for(Pool, 'checkout')
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute('SELECT 1')
    except:
        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()

    cursor.close()

engine = create_engine(
    Config.db,
    pool_recycle=600,
    isolation_level='READ COMMITTED',
    use_batch_mode=True, 
)

'''
engine_slave_0 = create_engine(
    Config.db_slave_0,
    pool_recycle=600,
    isolation_level='READ COMMITTED',
)

engine_slave_1 = create_engine(
    Config.db_slave_1,
    pool_recycle=600,
    isolation_level='READ COMMITTED',
)
'''
Session = sessionmaker(bind=engine)
# SessionSlave0 = sessionmaker(bind=engine_slave_0)
# SessionSlave1 = sessionmaker(bind=engine_slave_1)

# get random slave session
def get_slave_session():
    # SessionSlave = random.choice([SessionSlave0, SessionSlave1])
    # return SessionSlave()
    return Session()
