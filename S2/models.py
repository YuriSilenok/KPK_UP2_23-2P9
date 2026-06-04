import re
from peewee import *

db = SqliteDatabase('S2_Profile_datebase.db')

class BaseModel(Model):
    class Meta:
        database = db

class Profile(BaseModel):
    id = PrimaryKeyField()
    full_name = CharField(max_length=255)
    telephone = CharField(min_length=10, max_length=10, unique=True)
    email = CharField(max_length=254, unique=True)
    path_to_photo = CharField(max_length=255)
    is_active = BooleanField(default=True)


class NotificationSettings(BaseModel):
    id = PrimaryKeyField()
    profile_id = ForeignKeyField(Profile, backref='notification_settings')
    parameter = CharField(max_length=255)
    value = CharField(max_length=255)

def init_db():
    db.create_tables([Profile, NotificationSettings])

if __name__ == '__main__':
    init_db()
