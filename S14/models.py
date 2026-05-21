import peewee as pw

db = pw.SqliteDatabase('load_calculation.db')


class BaseModel(pw.Model):
    class Meta:
        database = db


class Department(BaseModel):
    """Кафедра"""
    name = pw.CharField(max_length=255, unique=True)
    is_active = pw.BooleanField(default=True)

    class Meta:
        table_name = 'departments'


class Teacher(BaseModel):
    """Преподаватель"""
    full_name = pw.CharField(max_length=255)
    position = pw.CharField(max_length=100)
    department = pw.ForeignKeyField(
        Department, backref='teachers', on_delete='RESTRICT'
    )
    max_hours = pw.IntegerField()
    is_active = pw.BooleanField(default=True)

    class Meta:
        table_name = 'teachers'


class Subject(BaseModel):
    """Дисциплина"""
    name = pw.CharField(max_length=255, unique=True)
    description = pw.TextField(default='')
    is_active = pw.BooleanField(default=True)

    class Meta:
        table_name = 'subjects'


class Group(BaseModel):
    """Учебная группа"""
    name = pw.CharField(max_length=50, unique=True)
    year = pw.IntegerField()
    student_count = pw.IntegerField()
    is_active = pw.BooleanField(default=True)

    class Meta:
        table_name = 'groups'


class Curriculum(BaseModel):
    """Учебный план (дисциплина в семестре с разбивкой часов)"""
    subject = pw.ForeignKeyField(
        Subject, backref='curricula', on_delete='RESTRICT'
    )
    semester = pw.IntegerField()
    lecture_hours = pw.IntegerField(default=0)
    practice_hours = pw.IntegerField(default=0)
    lab_hours = pw.IntegerField(default=0)
    is_active = pw.BooleanField(default=True)

    class Meta:
        table_name = 'curricula'
        indexes = (
            (('subject_id', 'semester'), True),
        )


class CurriculumGroup(BaseModel):
    """Транзитивная таблица: учебный план — группа (многие ко многим)"""
    curriculum = pw.ForeignKeyField(
        Curriculum, backref='curriculum_groups', on_delete='RESTRICT'
    )
    group = pw.ForeignKeyField(
        Group, backref='curriculum_groups', on_delete='RESTRICT'
    )

    class Meta:
        table_name = 'curriculum_groups'
        indexes = (
            (('curriculum_id', 'group_id'), True),
        )


class LoadAssignment(BaseModel):
    """Назначение нагрузки преподавателю"""
    teacher = pw.ForeignKeyField(
        Teacher, backref='load_assignments', on_delete='RESTRICT'
    )
    curriculum_group = pw.ForeignKeyField(
        CurriculumGroup, backref='load_assignments', on_delete='RESTRICT'
    )
    # Допустимые значения: 'lecture', 'practice', 'lab'
    load_type = pw.CharField(max_length=20)
    hours = pw.IntegerField()
    is_active = pw.BooleanField(default=True)

    class Meta:
        table_name = 'load_assignments'
        indexes = (
            (('teacher_id', 'curriculum_group_id', 'load_type'), True),
        )


def init_db() -> None:
    """Инициализация БД: создаёт подключение и все таблицы."""
    db.connect()
    db.create_tables(
        [
            Department,
            Teacher,
            Subject,
            Group,
            Curriculum,
            CurriculumGroup,
            LoadAssignment,
        ],
        safe=True,
    )
    print("База данных успешно инициализирована.")


if __name__ == '__main__':
    init_db()
