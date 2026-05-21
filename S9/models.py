from peewee import *
from datetime import date

db = SqliteDatabase('S9.db')

class BaseModel(Model):
    class Meta:
        database = db

class OrderType(BaseModel):
    """Тип приказа (справочник)"""
    name = CharField(max_length=50, unique=True)
    is_active = BooleanField(default=True) 

class OrderDocument(BaseModel):
    """Содержание приказа"""
    order_type = ForeignKeyField(OrderType, backref='documents')
    student_ids = TextField()  # Список ID студентов (хранится как JSON)
    order_number = CharField(max_length=50)
    order_date = DateField()
    signed_by = CharField(max_length=100)
    is_active = BooleanField(default=True)

    class Meta:
        constraints = [SQL('UNIQUE(order_type_id, order_number)')]

def createTable():
    db.create_tables([OrderType, OrderDocument])

def add_default_order_types():
    default_types = [
        'Отчисление',
        'Перевод',
        'Восстановление',
        'Академический отпуск',
        'Выход из отпуска',
    ]
    for name in default_types:
        OrderType.get_or_create(name=name)

if __name__ == '__main__':
    createTable()
    add_default_order_types()
