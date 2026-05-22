from peewee import *

# Инициализация базы данных
db = SqliteDatabase('load_calculation.db')

class BaseModel(Model):
    is_active = BooleanField(default=True)

    class Meta:
        database = db

# Преподаватель
class Teacher(BaseModel):
    id = AutoField()
    name = CharField(max_length=100)
    department = CharField(max_length=50)

# Учебный план (Curriculum)
class Curriculum(BaseModel):
    id = AutoField()
    course_name = CharField(max_length=100)
    total_hours = IntegerField()

# Группа
class Group(BaseModel):
    id = AutoField()
    curriculum_id = IntegerField()
    name = CharField(max_length=50)
    semester = IntegerField()

# Назначение преподавателя на группу
class TeacherGroup(BaseModel):
    id = AutoField()
    teacher_id = IntegerField()
    group_id = IntegerField()
    assigned_hours = IntegerField()

    class Meta:
        indexes = (
            (('teacher_id', 'group_id'), True),  # уникальная комбинация
        )

def initialize_db():
    with db:
        db.create_tables([Teacher, Curriculum, Group, TeacherGroup])
    print("База данных и таблицы созданы успешно.")

if __name__ == '__main__':
    initialize_db()
