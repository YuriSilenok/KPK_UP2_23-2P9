from peewee import SqliteDatabase, Model, AutoField, CharField, IntegerField, BooleanField, ForeignKeyField


db = SqliteDatabase("database.db")


class Table(Model):
    class Meta:
        database = db


class Room(Table):
    id = AutoField()
    name = CharField(unique=True)


class Equipment(Table):
    id = AutoField()
    name = CharField()


class RoomEquipment(Table):
    id = AutoField()
    room_id = ForeignKeyField(Room)
    equipment_id = ForeignKeyField(Equipment)
    is_active = BooleanField(default=True)


if __name__ == "__main__":
    db.create_tables([
        Room,
        Equipment,
        RoomEquipment
    ])
