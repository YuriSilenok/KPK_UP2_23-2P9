from peewee import *
from datetime import date, datetime

db = SqliteDatabase('S8.db')

class BaseModel(Model):
    class Meta:
        database = db


class Group(BaseModel):
    year_create = IntegerField()
    number = IntegerField()
    prefix = CharField()
    code = CharField()
    class_number = IntegerField()
    tutor_id = IntegerField(default=None, null=True)
    status = BooleanField(default=True)  # True - активна, False - закрыта
    count_student = IntegerField(default=0)

    @staticmethod
    def get_course_number(admission_year):
        current_date = date.today()
        current_year = current_date.year
        current_month = current_date.month
        
        if current_month >= 9:
            current_academic_year = current_year
        else:
            current_academic_year = current_year - 1
        if admission_year > current_academic_year:
            return None
        
        course = current_academic_year - admission_year + 1
        return course

    @property
    def name(self) -> str:
        course = Group.get_course_number(self.year_create)
        return f"{course}-{self.number}{self.prefix}{self.class_number}"


class Subgroup(BaseModel):
    id_group = ForeignKeyField(Group, backref='subgroups', on_delete='CASCADE')
    subgroup_number = IntegerField()
    name = CharField(null=True, default=None)
    status = BooleanField(default=True)
    count_student = IntegerField(default=0)

    class Meta:
        indexes = (
            (('id_group', 'subgroup_number'), True),
        )

    @property
    def full_name(self) -> str:
        group = self.id_group
        return f"{group.name}-{self.subgroup_number}"


class Student(BaseModel):
    id_student = IntegerField(unique=True)
    id_group = ForeignKeyField(Group, backref='students', on_delete='CASCADE')
    id_subgroup = ForeignKeyField(Subgroup, backref='students', null=True, default=None, on_delete='SET NULL')


def createTables():
    db.create_tables([Group, Subgroup, Student])


if __name__ == '__main__':
    createTables()
