from peewee import *
from datetime import date, datetime

db = SqliteDatabase('S8.db')

class BaseModel(Model):
    class Meta:
        database = db


class Subgroup(BaseModel):
    id_group = IntegerField() 
    subgroup_number = IntegerField()
    name = CharField(null=True, default=None)
    is_active = BooleanField(default=True) 
    count_student = IntegerField(default=0)

    class Meta:
        indexes = (
            (('id_group', 'subgroup_number'), True),
        )

    @property
    def full_name(self) -> str:
        """Полное наименование подгруппы"""
        return f"Group-{self.id_group}-{self.subgroup_number}"


class Student(BaseModel):
    id_student = IntegerField(unique=True) 
    id_subgroup = ForeignKeyField(Subgroup, backref='students', null=True, default=None, on_delete='SET NULL')


def createTables():
    db.create_tables([Subgroup, Student])


if __name__ == '__main__':
    createTables()
    print("Таблицы успешно созданы в БД S8.db")
