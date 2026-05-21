from peewee import (
    SqliteDatabase, Model, CharField, IntegerField, ForeignKeyField
)

db = SqliteDatabase('faculty_service.db')

class BaseModel(Model):
    class Meta:
        database = db

class Head(BaseModel):
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    phone_number = CharField(max_length=20, unique=True)

class Department(BaseModel):
    name = CharField(max_length=150, unique=True)
    abbreviation = CharField(max_length=20, unique=True)
    room_number = IntegerField()
    head = ForeignKeyField(Head, backref='departments', on_delete='RESTRICT')

class Specialty(BaseModel):
    code = CharField(max_length=20, unique=True)
    name = CharField(max_length=200)

class DepartmentSpecialty(BaseModel):
    department = ForeignKeyField(Department, backref='specialty_links', on_delete='CASCADE')
    specialty = ForeignKeyField(Specialty, backref='department_links', on_delete='CASCADE')
    
    class Meta:
        indexes = (
            (('department', 'specialty'), True),
        )

def init_db():
    db.connect()
    db.create_tables([Head, Department, Specialty, DepartmentSpecialty])

if __name__ == '__main__':
    init_db()