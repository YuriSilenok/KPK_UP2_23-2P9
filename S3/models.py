from peewee import *

db = SqliteDatabase('S3.db')

class BaseModel(Model):

    class Meta:
        database = db

class Role(BaseModel):
    role_name = CharField(unique=True)
    access_level = IntegerField(default=1)
    role_description = CharField(default=None, null=True)
    is_active = BooleanField(default=True)

class User(BaseModel):
    id_user = IntegerField()
    id_role = ForeignKeyField(Role, backref='user_roles')

def createTable():
    db.create_tables([Role, User])

if __name__ == '__main__':
    createTable()
    