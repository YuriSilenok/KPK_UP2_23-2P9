from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from models import Equipment, RoomEquipment, db


app = FastAPI()


class EquipmentCreate(BaseModel):
    """Схема валидации данных для создания нового оборудования."""
    name: str = Field(..., min_length=1, max_length=255)


class EquipmentResponse(BaseModel):
    """Схема ответа с базовой информацией об оборудовании."""
    id: int
    name: str
    is_active: bool


class EquipmentBindRoom(BaseModel):
    """Схема валидации данных для привязки оборудования к комнате."""
    id: int = Field(..., gt=0)
    room_id: int = Field(..., gt=0)


class RoomEquipmentResponse(BaseModel):
    """Схема ответа, подтверждающая успешную привязку оборудования к комнате."""
    id: int
    name: str
    room_id: int
    is_active: bool


class SuccessResponse(BaseModel):
    """Схема стандартного успешного ответа API."""
    success: bool


class EquipmentListResponse(BaseModel):
    """Схема ответа для расширенного списка оборудования с указанием комнаты."""
    id: int
    name: str
    room_id: Optional[int] = None
    is_active: bool


@app.post("/equipment/", response_model=EquipmentResponse)
def create_equipment(data: EquipmentCreate):
    """
    Назначение: Создает новую запись оборудования.

    HTTP-метод: POST
    Параметры запроса:
        - body: EquipmentCreate (JSON-объект с именем оборудования)

    Пример ответа:
    {
        "id": 1,
        "name": "Принтер HP",
        "is_active": true
    }
    """
    equipment = Equipment.create(name=data.name, is_active=True)

    return EquipmentResponse(
        id=equipment.id,
        name=equipment.name,
        is_active=equipment.is_active)


@app.patch("/equipment/bind", response_model=RoomEquipmentResponse)
def bind_equipment_to_room(data: EquipmentBindRoom):
    if data.room_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="room_id должен быть положительным числом"
        )

    try:
        equipment = Equipment.get(Equipment.id == data.id, Equipment.is_active)
    except Equipment.DoesNotExist as e:
        raise HTTPException(
            status_code=404,
            detail=f"Оборудование с id={data.id} не найдено"
        ) from e

    with db.atomic():
        RoomEquipment.update(is_active=False).where(
            RoomEquipment.equipment == equipment.id,
            RoomEquipment.is_active).execute()

        room_equipment = RoomEquipment.create(
            room_id=data.room_id,
            equipment=equipment,
            is_active=True)

    return RoomEquipmentResponse(
        id=equipment.id,
        name=equipment.name,
        room_id=room_equipment.room_id,
        is_active=room_equipment.is_active)


@app.delete("/equipment/{equipment_id}", response_model=SuccessResponse)
def delete_equipment(equipment_id: int):
    """
    Назначение: Логически удаляет оборудование и деактивирует все его связи с комнатами.

    HTTP-метод: DELETE
    Параметры запроса:
        - path: equipment_id (int) — идентификатор удаляемого оборудования

    Пример ответа:
    {
        "success": true
    }
    """
    try:
        equipment = Equipment.get(Equipment.id == equipment_id)
        equipment.is_active = False
        equipment.save()

        RoomEquipment.update(is_active=False).where(
            RoomEquipment.equipment == equipment_id,
            RoomEquipment.is_active).execute()

        return SuccessResponse(success=True)

    except Equipment.DoesNotExist as e:
        raise HTTPException(404, False) from e


@app.delete("/equipment/unbind/{equipment_id}", response_model=SuccessResponse)
def unbind_equipment_from_room(equipment_id: int):
    """
    Назначение: Отвязывает оборудование от комнаты (деактивирует связь).

    HTTP-метод: DELETE
    Параметры запроса:
        - path: equipment_id (int) — идентификатор отвязываемого оборудования

    Пример ответа:
    {
        "success": true
    }
    """
    try:
        room_equipment = RoomEquipment.get(
            RoomEquipment.equipment == equipment_id,
            RoomEquipment.is_active)

        room_equipment.is_active = False
        room_equipment.save()

        return SuccessResponse(success=True)

    except RoomEquipment.DoesNotExist as e:
        raise HTTPException(404, False) from e


@app.get("/equipment/room/{room_id}", response_model=List[EquipmentListResponse])
def get_equipment_by_room(room_id: int):
    """
    Назначение: Возвращает список активного оборудования, находящегося в конкретной комнате.

    HTTP-метод: GET
    Параметры запроса:
        - path: room_id (int) — идентификатор комнаты для поиска

    Пример ответа:
    [
        {
            "id": 1,
            "name": "Ноутбук",
            "room_id": 12,
            "is_active": true
        }
    ]
    """
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
    """
    Назначение: Возвращает отфильтрованный список оборудования со сведениями о текущей комнате.

    HTTP-метод: GET
    Параметры запроса:
        - query: room_id (Optional[int]) — фильтр по идентификатору комнаты
        - query: ids (Optional[List[int]]) — фильтр по списку идентификаторов оборудования
        - query: is_active (Optional[bool]) — фильтр по статусу активности оборудования

    Пример ответа:
    [
        {
            "id": 1,
            "name": "Сканер",
            "room_id": null,
            "is_active": true
        },
        {
            "id": 2,
            "name": "Монитор",
            "room_id": 15,
            "is_active": true
        }
    ]
    """
    query = Equipment.select()

    if room_id is not None:
        if room_id <= 0:
            raise HTTPException(
                status_code=400,
                detail="room_id должен быть положительным числом")

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
