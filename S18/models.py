from peewee import SqliteDatabase, Model, AutoField, CharField, IntegerField, BooleanField, ForeignKeyField


db = SqliteDatabase("database.db")


class Table(Model):
    id = AutoField()

    class Meta:
        database = db


class Room(Table):
    name = CharField()


class Equipment(Table):
    name = CharField()
    is_active = BooleanField()


class RoomEquipment(Table):
    room_id = ForeignKeyField(Room)
    equipment_id = ForeignKeyField(Equipment)


if __name__ == "__main__":
    db.create_tables([
        Room,
        Equipment,
        RoomEquipment
    ])
