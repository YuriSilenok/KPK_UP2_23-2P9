from peewee import *
from datetime import date

db = SqliteDatabase('S9.db')

class BaseModel(Model):
    class Meta:
        database = db

class OrderType(BaseModel):
    """Тип приказа (справочник)"""
    code = CharField(max_length=30, unique=True)  # expulsion, transfer, reinstatement, academic_leave, return_from_leave
    description = TextField(null=True)  # Описание

    @staticmethod
    def is_valid_code(code: str) -> bool:
        """Проверяет, допустим ли код типа приказа"""
        valid_codes = ['expulsion', 'transfer', 'reinstatement', 'academic_leave', 'return_from_leave']
        return code in valid_codes

    @property
    def code_rus(self) -> str:
        """Возвращает русское название типа приказа"""
        types = {
            'expulsion': 'Отчисление',
            'transfer': 'Перевод',
            'reinstatement': 'Восстановление',
            'academic_leave': 'Академический отпуск',
            'return_from_leave': 'Выход из отпуска'
        }
        return types.get(self.code, self.code)

class OrderDocument(BaseModel):
    """Содержание приказа"""
    order_type = ForeignKeyField(OrderType, backref='documents')
    student_id = IntegerField()  # ID студента (внешний ключ к сервису 7)
    order_number = CharField(max_length=50)
    order_date = DateField()
    signed_by = CharField(max_length=100)  # Кто подписал
    reason = TextField(null=True)  # Основание

    @property
    def document_name(self) -> str:
        """Возвращает название приказа"""
        return f"Приказ №{self.order_number} от {self.order_date}"

def createTable():
    """Создаёт таблицы в базе данных"""
    db.create_tables([OrderType, OrderDocument])

def add_default_order_types():
    """Добавляет стандартные типы приказов"""
    default_types = [
        ('expulsion', 'Отчисление студента из учебного заведения'),
        ('transfer', 'Перевод студента из одной группы в другую'),
        ('reinstatement', 'Восстановление отчисленного студента'),
        ('academic_leave', 'Предоставление академического отпуска'),
        ('return_from_leave', 'Выход из академического отпуска'),
    ]
    for code, desc in default_types:
        OrderType.get_or_create(code=code, defaults={'description': desc})

if __name__ == '__main__':
    createTable()
    add_default_order_types()
