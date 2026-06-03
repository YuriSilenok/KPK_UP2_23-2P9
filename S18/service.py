from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from models import Equipment, RoomEquipment


app = FastAPI()


class EquipmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class EquipmentResponse(BaseModel):
    id: int
    name: str
    is_active: bool


class EquipmentBindRoom(BaseModel):
    id: int = Field(..., gt=0)
    room_id: int = Field(..., gt=0)


class RoomEquipmentResponse(BaseModel):
    id: int
    name: str
    room_id: int
    is_active: bool


class SuccessResponse(BaseModel):
    success: bool


class EquipmentListResponse(BaseModel):
    id: int
    name: str
    room_id: Optional[int] = None
    is_active: bool


@app.post("/equipment/", response_model=EquipmentResponse)
def create_equipment(data: EquipmentCreate):
    equipment = Equipment.create(name=data.name, is_active=True)

    return EquipmentResponse(
        id=equipment.id,
        name=equipment.name,
        is_active=equipment.is_active)


@app.patch("/equipment/bind", response_model=RoomEquipmentResponse)
def bind_equipment_to_room(data: EquipmentBindRoom):
    try:
        equipment = Equipment.get(Equipment.id == data.id, Equipment.is_active)

    except Equipment.DoesNotExist as e:
        raise HTTPException(
            status_code=404,
            detail=f"Оборудование с id={data.id} не найдено") from e

    existing = RoomEquipment.select().where(
        RoomEquipment.equipment == data.id,
        RoomEquipment.is_active).first()

    if existing:
        existing.room_id = data.room_id
        existing.save()
        return RoomEquipmentResponse(
            id=existing.id,
            name=equipment.name,
            room_id=existing.room_id,
            is_active=existing.is_active)

    room_equipment = RoomEquipment.create(
        room_id=data.room_id,
        equipment=equipment,
        is_active=True)

    return RoomEquipmentResponse(
        id=room_equipment.id,
        name=equipment.name,
        room_id=room_equipment.room_id,
        is_active=room_equipment.is_active)


@app.delete("/equipment/{equipment_id}", response_model=SuccessResponse)
def delete_equipment(equipment_id: int):
    try:
        equipment = Equipment.get(Equipment.id == equipment_id)
        equipment.is_active = False
        equipment.save()

        RoomEquipment.update(is_active=False).where(
            RoomEquipment.equipment == equipment_id,
            RoomEquipment.is_active).execute()

        return SuccessResponse(success=True)

    except Equipment.DoesNotExist:
        return SuccessResponse(success=False)


@app.delete("/equipment/unbind/{equipment_id}", response_model=SuccessResponse)
def unbind_equipment_from_room(equipment_id: int):
    try:
        room_equipment = RoomEquipment.get(
            RoomEquipment.equipment == equipment_id,
            RoomEquipment.is_active)

        room_equipment.is_active = False
        room_equipment.save()

        return SuccessResponse(success=True)

    except RoomEquipment.DoesNotExist:
        return SuccessResponse(success=False)


@app.get("/equipment/room/{room_id}", response_model=List[EquipmentListResponse])
def get_equipment_by_room(room_id: int):
    if room_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="room_id должен быть положительным числом")

    room_equipments = RoomEquipment.select().where(
        RoomEquipment.room_id == room_id,
        RoomEquipment.is_active)

    result = []
    for re in room_equipments:
        if re.equipment.is_active:
            result.append(EquipmentListResponse(
                id=re.equipment.id,
                name=re.equipment.name,
                room_id=re.room_id,
                is_active=re.equipment.is_active))

    return result


@app.get("/equipment/", response_model=List[EquipmentListResponse])
def list_equipment(
        room_id: Optional[int] = Query(None),
        ids: Optional[List[int]] = Query(None),
        is_active: Optional[bool] = Query(None)):

    query = Equipment.select()

    if room_id is not None:
        subquery = RoomEquipment.select(RoomEquipment.equipment).where(
            RoomEquipment.room_id == room_id,
            RoomEquipment.is_active)

        query = query.where(Equipment.id.in_(subquery))

    if ids is not None:
        query = query.where(Equipment.id.in_(ids))

    if is_active is not None:
        query = query.where(Equipment.is_active == is_active)

    result = []
    for equipment in query:
        room_equipment = RoomEquipment.select().where(
            RoomEquipment.equipment == equipment.id,
            RoomEquipment.is_active
        ).first()

        result.append(EquipmentListResponse(
            id=equipment.id,
            name=equipment.name,
            room_id=room_equipment.room_id if room_equipment else None,
            is_active=equipment.is_active))

    return result
