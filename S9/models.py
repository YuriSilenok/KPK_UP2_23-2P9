from peewee import *
from datetime import date, datetime

db = SqliteDatabase('S9.db')

class BaseModel(Model):
    class Meta:
        database = db

class Movement(BaseModel):
    student_id = IntegerField()
    movement_type = CharField(max_length=30)
    start_date = DateField()
    source_group_id = IntegerField(default=0)
    target_group_id = IntegerField(default=0)
    reason = TextField(null=True)
    order_number = CharField(max_length=50, null=True)
    end_date = DateField(null=True)
    created_at = DateTimeField(default=datetime.now)
    is_active = BooleanField(default=True)

    @staticmethod
    def is_valid_movement_type(movement_type: str) -> bool:
        """Проверяет, допустим ли тип движения"""
        valid_types = ['expelled', 'reinstated', 'transferred', 'academic_leave', 'back_from_leave']
        return movement_type in valid_types

    @property
    def movement_type_rus(self) -> str:
        """Возвращает русское название типа движения"""
        types = {
            'expelled': 'Отчисление',
            'reinstated': 'Восстановление',
            'transferred': 'Перевод',
            'academic_leave': 'Академический отпуск',
            'back_from_leave': 'Выход из отпуска'
        }
        return types.get(self.movement_type, self.movement_type)

def createTable():
    db.create_tables([Movement])

if __name__ == '__main__':
    createTable()
