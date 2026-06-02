from peewee import *
from datetime import datetime

db = SQLiteDatabase('employee_service.db')

class Table(Model):
    id = AutoField()
    is_deleted = BooleanField(default=False)


    def mark_as_delete(self):
        self.is_deleted = True


    class Meta:
        database = db


class JobPosition(Table):
    name = CharField(max_length=255, null=False, unique=True)
    rate = IntegerField(null=False)
    is_part_time = BooleanField(null=False, default=False)


class EmployeePosition(Table):
    employee_id = ForeignKeyField('Employee')
    position_id = ForeignKeyField(JobPosition)


class Vacation(Table):
    employee_id = ForeignKeyField("Employee")
    start_time = DateTimeField(null=False)
    end_time = DateTimeField(null=False)
    
    class Meta:
        constraints = [Check('end_time > start_time')]


class SickLeave(Table):
    employee_id = ForeignKeyField("Employee")
    start_time = DateTimeField(null=False)
    end_time = DateTimeField(null=False)
    
    class Meta:
        constraints = [Check('end_time > start_time')]



def seed():
    db.create_tables([JobPosition, Absence, EmployeePosition])


if __name__ == "__main__":
    seed()