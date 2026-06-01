from peewee import (
    SqliteDatabase, Model, AutoField, CharField,
    IntegerField, BooleanField, ForeignKeyField, Check
)

db = SqliteDatabase("database.db")


class BaseModel(Model):
    class Meta:
        database = db


class Equipment(BaseModel):
    id = AutoField()
    name = CharField()
    is_active = BooleanField(default=True)

    def delete(self):
        self.is_active = False
        self.save()


class RoomEquipment(BaseModel):
    room = IntegerField(constraints=[Check('room_id > 0')])
    equipment = ForeignKeyField(Equipment, backref='room_equipment')
    is_active = BooleanField(default=True)

    class Meta:
        indexes = (
            (('room', 'equipment'), True),
        )

    def delete(self):
        self.is_active = False
        self.save()


if __name__ == "__main__":
    db.create_tables([
        Equipment,
        RoomEquipment])
