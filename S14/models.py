from peewee import *

db = SqliteDatabase('load_calculation.db')

class BaseModel(Model):
    is_active = BooleanField(default=True)
    class Meta:
        database = db

class Teacher(BaseModel):
    id = AutoField()
    full_name = CharField(max_length=100)
    department = CharField(max_length=50)

class StudyPlan(BaseModel):
    id = AutoField()
    name = CharField(max_length=100)
    semester = IntegerField()

class Group(BaseModel):
    id = AutoField()
    study_plan = ForeignKeyField(StudyPlan, backref='groups')
    name = CharField(max_length=50)

class Subject(BaseModel):
    id = AutoField()
    name = CharField(max_length=100)

class StudyPlanSubject(BaseModel):
    id = AutoField()
    study_plan = ForeignKeyField(StudyPlan, backref='subjects')
    subject = ForeignKeyField(Subject, backref='study_plans')
    hours = IntegerField()

class TeacherLoad(BaseModel):
    id = AutoField()
    teacher = ForeignKeyField(Teacher, backref='loads')
    group = ForeignKeyField(Group, backref='teacher_loads')
    study_plan_subject = ForeignKeyField(StudyPlanSubject, backref='teacher_loads')
    total_hours = IntegerField()

def initialize_db():
    with db:
        db.create_tables([Teacher, StudyPlan, Group, Subject, StudyPlanSubject, TeacherLoad])
    print("База данных и таблицы созданы успешно.")

if __name__ == '__main__':
    initialize_db()
