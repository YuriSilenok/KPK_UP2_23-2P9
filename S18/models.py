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
    name = CharField(null=False)
    is_active = BooleanField(default=True)

    def soft_delete(self):
        self.is_active = False
        self.save()

        self.room_equipment.model.update(is_active=False).where(
            self.room_equipment.model.equipment_id == self.id
        ).execute()

        return True


class RoomEquipment(BaseModel):
    id = AutoField()
    room_id = IntegerField(constraints=[Check('room_id > 0')])
    equipment_id = ForeignKeyField(Equipment, backref='room_equipment')
    is_active = BooleanField(default=True)

    class Meta:
        indexes = (
            (('room_id', 'equipment_id'), True),
        )

    def soft_delete(self):
        self.is_active = False
        self.save()
        return True


if __name__ == "__main__":
    db.create_tables([Equipment, RoomEquipment])
