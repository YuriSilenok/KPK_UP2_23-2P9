from peewee import Model, SqliteDatabase, AutoField, BooleanField, CharField, IntegerField, ForeignKeyField, DateTimeField, Check
from datetime import datetime

db = SqliteDatabase('employee_service.db')

class Table(Model):
    id = AutoField()
    is_active = BooleanField(default=True)


    def mark_as_delete(self):
        self.is_active = False


    class Meta:
        database = db


class JobPosition(Table):
    name = CharField(max_length=255, null=False, unique=True)
    rate = IntegerField(null=False)
    is_part_time = BooleanField(null=False, default=False)

    
    class Meta:
        constraints = [Check('rate > 0')]


class EmployeeJobPosition(Table):
    employee_id = IntegerField(null=False)
    job_position_id = ForeignKeyField(JobPosition)

class Vacation(Table):
    employee_id = IntegerField(null=False)
    start_time = DateTimeField(null=False)
    end_time = DateTimeField(null=False)
    
    class Meta:
        constraints = [Check('end_time > start_time')]


class SickLeave(Table):
    employee_id = IntegerField(null=False)
    start_time = DateTimeField(null=False)
    end_time = DateTimeField(null=False)
    
    class Meta:
        constraints = [Check('end_time > start_time')]



def init_db():
    db.create_tables([JobPosition, SickLeave, Vacation, EmployeeJobPosition])


if __name__ == "__main__":
    init_db()