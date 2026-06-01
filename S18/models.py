from peewee import SqliteDatabase, Model, AutoField, CharField, IntegerField, BooleanField, ForeignKeyField, Check

db = SqliteDatabase("database.db")


class Table(Model):
    class Meta:
        database = db


class Equipment(Table):
    id = AutoField()
    name = CharField()


class RoomEquipment(Table):
    room_id = IntegerField(constraints=[Check('room_id > 0')])
    equipment_id = ForeignKeyField(Equipment, constraints=[Check('equipment_id > 0')])
    is_active = BooleanField(default=True)

    class Meta:
        primary_key = False
        indexes = (
            (('room_id', 'equipment_id'), True),
        )


if __name__ == "__main__":
    db.create_tables([
        Equipment,
        RoomEquipment
    ])
