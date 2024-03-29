from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
post = Table('post', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('timestamp', DATETIME),
    Column('user_id', INTEGER),
)

users = Table('users', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('social_id', VARCHAR(length=64), nullable=False),
    Column('nickname', VARCHAR(length=64), nullable=False),
    Column('email', VARCHAR(length=120)),
    Column('last_seen', DATETIME),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['post'].drop()
    pre_meta.tables['users'].columns['last_seen'].drop()
    pre_meta.tables['users'].columns['social_id'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['post'].create()
    pre_meta.tables['users'].columns['last_seen'].create()
    pre_meta.tables['users'].columns['social_id'].create()
