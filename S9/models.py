import os
from peewee import *
from datetime import date, datetime

db = SqliteDatabase('student_movement.db')


class Student(Model):
    """Модель студента"""
    id = IntegerField(primary_key=True)
    full_name = CharField(max_length=200)
    group_id = IntegerField()
    is_active = BooleanField(default=True)

    class Meta:
        database = db
        table_name = 'students'


class Group(Model):
    """Модель учебной группы"""
    id = IntegerField(primary_key=True)
    name = CharField(max_length=100)
    year_of_entry = IntegerField()
    is_active = BooleanField(default=True)

    class Meta:
        database = db
        table_name = 'groups'


class Movement(Model):
    """Модель движения студента"""
    id = AutoField()
    student_id = IntegerField()
    movement_type = CharField(max_length=20)
    start_date = DateField()
    source_group_id = IntegerField(null=True)
    target_group_id = IntegerField(null=True)
    reason = CharField(max_length=255, null=True)
    order_number = CharField(max_length=50, null=True)
    end_date = DateField(null=True)
    created_at = DateTimeField(default=datetime.now)
    is_active = BooleanField(default=True)

    class Meta:
        database = db
        table_name = 'movements'


def init_db():
    db.connect()
    db.create_tables([Student, Group, Movement], safe=True)


def main():
    init_db()


if __name__ == "__main__":
    main()
