
```python
import os
from peewee import *
from datetime import date, datetime
from typing import List

# Инициализация базы данных
db = SqliteDatabase('student_movement.db')


# Базовые модели (ссылки на внешние сервисы)
# В реальном проекте эти модели могут быть импортированы
# Здесь представлены упрощённые версии для демонстрации связей

class Student(Model):
 """Модель студента (из Profile Service / Group Service)"""
 id = IntegerField(primary_key=True)
 full_name = CharField(max_length=200)
 group_id = IntegerField()  # внешний ключ на Group
 is_active = BooleanField(default=True)

 class Meta:
     database = db
     table_name = 'students'


class Group(Model):
 """Модель учебной группы (из Group Service)"""
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
 student_id = IntegerField()  # внешний ключ на Student
 movement_type = CharField(max_length=20, constraints=[
     Check("movement_type IN ('expelled', 'reinstated', 'transferred', 'academic_leave', 'back_from_leave')")
 ])
 start_date = DateField()
 source_group_id = IntegerField(null=True)  # внешний ключ на Group
 target_group_id = IntegerField(null=True)  # внешний ключ на Group
 reason = CharField(max_length=255, null=True)
 order_number = CharField(max_length=50, null=True)
 end_date = DateField(null=True)
 created_at = DateTimeField(default=datetime.now)

 class Meta:
     database = db
     table_name = 'movements'


def init_db():
 """Инициализация базы данных: создание таблиц"""
 db.connect()
 db.create_tables([Student, Group, Movement], safe=True)
 print("База данных инициализирована. Таблицы созданы.")


def add_test_data():
 """Добавление тестовых данных (опционально)"""
 # Проверяем, есть ли уже данные
 if Student.select().count() > 0:
     return

 # Создаём тестовую группу
 group = Group.create(
     id=1,
     name="П-101",
     year_of_entry=2024,
     is_active=True
 )

 # Создаём тестового студента
 student = Student.create(
     id=1,
     full_name="Иванов Иван Иванович",
     group_id=group.id,
     is_active=True
 )

 # Создаём тестовую запись о движении (перевод)
 Movement.create(
     student_id=student.id,
     movement_type="transferred",
     start_date=date(2024, 9, 1),
     source_group_id=group.id,
     target_group_id=2,
     reason="Перевод на другую специальность",
     order_number="45-ст"
 )

 print("Тестовые данные добавлены.")


def main():
 """Точка входа"""
 print("Запуск Student Movement Service...")
 init_db()
 add_test_data()
 print("Готово.")


if __name__ == "__main__":
 main()
