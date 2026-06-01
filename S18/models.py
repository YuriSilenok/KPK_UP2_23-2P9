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
        return 1


class RoomEquipment(BaseModel):
    room_id = IntegerField(constraints=[Check('room > 0')])
    equipment_id = ForeignKeyField(Equipment, backref='room_equipment')
    is_active = BooleanField(default=True)

    def delete(self):
        return self.delete_instance(recursive=False)


if __name__ == "__main__":
    db.create_tables([Equipment, RoomEquipment])
