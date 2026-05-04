from peewee import *

db = SqliteDatabase('S2_Profil_datebase.db')

class BaseModel(Model):
    class Meta:
        database = db

class Profil(BaseModel):
    first_name = CharField()
    second_name = CharField()
    last_name = CharField()
    telephone = IntegerField()
    e-mail = CharField()
    photo = CharField()
    profil_act = BooleanField(default=True)

class NotificationSettings(BaseModel):
    notification_turn = BooleanField(default=True)

if __name__ == '__main__':
    db.create_tables([Profil, NotificationSettings])
