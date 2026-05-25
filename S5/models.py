from peewee import (
    SqliteDatabase, Model, CharField, IntegerField,
    ForeignKeyField, BooleanField, Check
)

db = SqliteDatabase('faculty_service.db')


class BaseModel(Model):
    class Meta:
        database = db


class Head(BaseModel):
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)


class Department(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=150, unique=True)
    abbreviation = CharField(max_length=20, unique=True)
    room_number = IntegerField(constraints=[Check('room_number > 0')])
    head_id = ForeignKeyField(Head, backref='departments', on_delete='RESTRICT', field='id')
    is_active = BooleanField(default=True)


def init_db():
    db.connect()
    db.create_tables([Head, Department])


if __name__ == '__main__':
    init_db() 